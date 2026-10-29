"""The two development entry points share protection at their base revision."""
import json
import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path

from ante.develop import policy

ROOT = Path(__file__).resolve().parents[2]
IMPROVE = runpy.run_path(str(ROOT / 'scripts/nexus-improve.py'))


class SharedProtectionPolicy(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='ante-shared-policy-')
        self.addCleanup(self.scratch.cleanup)
        self.repo = Path(self.scratch.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Policy test fixture')
        self.git('config', 'user.email', 'fixture@invalid')
        for name in (policy.POLICY_PATH, policy.OVERDRIVE_PATH, 'ante/constructs/frozen.json'):
            self.write(name, (ROOT / name).read_text())
        self.base = self.commit()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, name, text):
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self):
        self.git('add', '-A')
        self.git('commit', '-qm', 'test fixture')
        return self.git('rev-parse', 'HEAD')

    def test_both_entry_points_refuse_foundation_and_frozen_evaluators(self):
        loaded = policy.at_ref(self.repo, self.base)
        frozen = json.loads((self.repo / 'ante/constructs/frozen.json').read_text())
        protected = [policy.POLICY_PATH, policy.OVERDRIVE_PATH, 'ante/develop/policy.py',
                     'ante/turing/lock.py', 'ante/attest/kernel.py',
                     'foundation/attest/trusted-keys.json',
                     'tests/foundation/future_test.py', 'scripts/future-evaluator.py',
                     '.github/workflows/future.yml']
        protected += [entry['path'] for entry in frozen['frozen_reviewers']]
        for name in protected:
            self.assertIsNotNone(loaded.classify(name), name)
            self.write(name, 'candidate tries to replace an evaluator\n')
        self.write('academic/example.md', 'ordinary editable agent profile\n')
        # Even replacing both candidate manifests cannot change the base rules.
        head = self.commit()
        report = IMPROVE['check_paths'](self.base, head, self.repo)
        self.assertEqual(set(protected), {row['path'] for row in report['violations']})
        self.assertIsNone(loaded.classify('academic/example.md'))
        self.assertEqual((), loaded.protected)

    def test_legacy_base_revision_keeps_its_extra_protected_list(self):
        legacy = json.loads((self.repo / policy.POLICY_PATH).read_text())
        legacy.update(schema_version=1, protected=['ante/turing/**'])
        legacy.pop('protected_manifest')
        self.write(policy.POLICY_PATH, json.dumps(legacy))
        self.write(policy.OVERDRIVE_PATH, json.dumps({'protected': [policy.OVERDRIVE_PATH]}))
        ref = self.commit()
        loaded = policy.at_ref(self.repo, ref)
        self.assertIn('foundation/develop-policy.json', loaded.classify('ante/turing/lock.py'))

    def test_current_schema_refuses_a_redirect_shadow_list_or_unknown_version(self):
        original = json.loads((self.repo / policy.POLICY_PATH).read_text())
        for change in ({'protected_manifest': 'candidate-controlled.json'}, {'protected': []},
                       {'schema_version': 3}, {'schema_version': True}):
            with self.subTest(change=change):
                self.write(policy.POLICY_PATH, json.dumps({**original, **change}))
                ref = self.commit()
                with self.assertRaises(policy.PolicyError):
                    policy.at_ref(self.repo, ref)
