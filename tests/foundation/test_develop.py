"""Self-development loop and Turing lock.

The gate tests run against a throwaway clone of this checkout (``git clone
--shared``) whose base commit includes the working tree, so nothing here touches
the real repository, its branches or any remote.
"""
import contextlib
import io as stdio
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ante import cli  # noqa: E402
from ante.core import canon  # noqa: E402
from ante.develop import commands as develop  # noqa: E402
from ante.turing import lock  # noqa: E402

T = '2026-10-28T12:00:00Z'
ZERO = {name: 0 for name in lock.DIMENSIONS}
TARGET = 'academic/academic-anthropologist.md'
OLD = '- **Cultural ecology**: How environment shapes culture and culture shapes environment (Steward, Rappaport)'
NEW = '- **Cultural ecology**: How environment shapes culture, and culture shapes environment (Steward, Rappaport)'


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout


def clone_with_worktree(dest: Path) -> Path:
    """A clone whose HEAD is this checkout's working tree, committed."""
    subprocess.run(['git', 'clone', '-q', '--shared', str(ROOT), str(dest)], check=True)
    dirty = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-m', '-o', '--exclude-standard', '-z'],
                           check=True, capture_output=True, text=True).stdout.split('\0')
    deleted = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-d', '-z'],
                             check=True, capture_output=True, text=True).stdout.split('\0')
    for name in filter(None, dirty):
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    for name in filter(None, deleted):
        (dest / name).unlink(missing_ok=True)
    git(dest, 'add', '-A')
    git(dest, '-c', 'user.name=t', '-c', 'user.email=t@invalid', 'commit', '-q', '--allow-empty', '-m', 'base')
    return dest


class Sandbox(unittest.TestCase):
    repo = None

    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix='ante-develop-test-'))
        cls.repo = clone_with_worktree(cls.root / 'repo')
        cls.base = git(cls.repo, 'rev-parse', 'HEAD').strip()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix='case-', dir=self.root))
        self.state = str(self.dir / 'state.jsonl')
        subprocess.run(['git', '-C', str(self.repo), 'update-ref', '-d', develop.ANCHOR_REF], capture_output=True)

    def finding(self):
        path = self.dir / 'patterns.json'
        path.write_text(json.dumps({'kind': 'patterns', 'decisions_used': 40, 'proposals': [{'feature': 'pathology:x'}]}))
        return {'kind': 'patterns', 'path': str(path), 'sha256': canon.sha256_hex(path.read_bytes())}

    def spec(self, ident='p1', scope=(TARGET,), delta=None, cost=5):
        doc = {'id': ident, 'title': 'tighten frame wording', 'findings': [self.finding()],
               'hypothesis': 'clearer nominal-objective message lowers rework', 'kill_criterion': 'rework rises',
               'metric': {'name': 'rework_cycles', 'tolerances': {'cost_usd': 0.1}},
               'cost': {'usd_ceiling': cost}, 'scope': list(scope), 'autonomy_delta': dict(delta or ZERO)}
        path = self.dir / f'{ident}.json'
        path.write_text(json.dumps(doc))
        return str(path)

    def patch(self, edits: dict, name='change.patch'):
        """Diff of ``edits`` ({path: (old, new)}) against the base, made in a scratch worktree."""
        tree = self.dir / ('wt-' + name)
        git(self.repo, 'worktree', 'add', '-q', '--detach', str(tree), self.base)
        try:
            for path, (old, new) in edits.items():
                target = tree / path
                text = target.read_text() if target.exists() else ''
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text.replace(old, new, 1) if old else text + new)
            git(tree, 'add', '-A')
            diff = git(tree, 'diff', '--cached', '--binary')
        finally:
            git(self.repo, 'worktree', 'remove', '--force', str(tree))
        out = self.dir / name
        out.write_text(diff)
        return str(out)

    def frame_patch(self):
        return self.patch({TARGET: (OLD, NEW)})

    def propose(self, spec, patch, at=T):
        return develop.propose(spec, patch, self.base, self.state, at, self.repo)


class Propose(Sandbox):
    def test_protected_and_out_of_scope_paths_are_refused_before_any_gate(self):
        for path in ('ante/turing/lock.py', 'ante/strategy/commands/nodal.py', 'ante/strategy/commands/street.py',
                     'ante/strategy/chain.py', 'tests/characterization/run.py', 'foundation/develop-policy.json',
                     'scripts/nexus-improve.py', '.github/workflows/x.yml'):
            patch = self.patch({path: ('', '\n# touch\n')}, name=path.replace('/', '_') + '.patch')
            with self.assertRaisesRegex(develop.DevelopError, 'protected|outside'):
                self.propose(self.spec(scope=('**',)), patch)
        frozen_patch = self.patch({'specialized/strategic-red-team.md': ('', '\nBe gentler.\n')}, name='frozen.patch')
        with self.assertRaisesRegex(develop.DevelopError, 'frozen reviewer'):
            self.propose(self.spec(scope=('specialized/**',)), frozen_patch)
        with self.assertRaisesRegex(develop.DevelopError, 'outside the scope this proposal declared'):
            self.propose(self.spec(scope=('engineering/**',)), self.frame_patch())

    def resume(self, reason='leak traced and removed'):
        with contextlib.redirect_stdout(stdio.StringIO()):
            return cli.main(['develop', 'resume', '--by', 'Ana (owner)', '--reason', reason,
                             '--state', self.state, '--at', T, '--repo', str(self.repo)])

    def test_an_injected_canary_rejects_the_proposal(self):
        token = 'ANTE-CANARY-' + 'c3' * 16
        leaked = self.patch({TARGET: (OLD, f'{NEW} ({token})')}, name='leak.patch')
        with self.assertRaisesRegex(develop.DevelopError, 'canary'):
            self.propose(self.spec(), leaked)
        self.assertEqual(0, self.resume())
        spec = json.loads(Path(self.spec('p2')).read_text())
        finding = Path(spec['findings'][0]['path'])
        finding.write_text(json.dumps({'kind': 'patterns', 'proposals': [{'feature': token}]}))
        spec['findings'][0]['sha256'] = canon.sha256_hex(finding.read_bytes())
        path = self.dir / 'p2.json'
        path.write_text(json.dumps(spec))
        with self.assertRaisesRegex(develop.DevelopError, 'canary found in finding'):
            self.propose(str(path), self.frame_patch())

    def test_a_canary_halts_the_loop_until_a_named_human_resumes_it(self):
        token = 'ANTE-CANARY-' + 'd4' * 16
        leaked = self.patch({TARGET: (OLD, f'{NEW} ({token})')}, name='leak.patch')
        with self.assertRaisesRegex(develop.DevelopError, 'halted until a human resumes it'):
            self.propose(self.spec('leak'), leaked)
        state = develop.State(self.state, self.repo)
        self.assertEqual({'reason': 'canary', 'proposal': 'leak', 'stage': 'propose', 'where': ['patch']},
                         state.halt())
        self.assertNotIn('leak', state.proposals())
        with self.assertRaisesRegex(develop.DevelopError, 'stopped \\(halted by a held-out canary in patch\\)'):
            self.propose(self.spec('clean'), self.frame_patch())
        self.assertEqual(0, self.resume())
        self.assertIsNone(develop.State(self.state, self.repo).halt())
        self.propose(self.spec('clean'), self.frame_patch())

    def test_one_open_proposal_and_a_campaign_spend_ceiling(self):
        self.propose(self.spec('p1'), self.frame_patch())
        with self.assertRaisesRegex(develop.DevelopError, 'open proposal'):
            self.propose(self.spec('p2'), self.frame_patch())
        develop.State(self.state, self.repo).append('close', {'id': 'p1', 'outcome': 'withdrawn'}, T)
        with self.assertRaisesRegex(develop.DevelopError, 'campaign limit'):
            self.propose(self.spec('p3', cost=46), self.frame_patch())

    def test_findings_need_the_policy_floor_not_the_callers(self):
        spec = json.loads(Path(self.spec()).read_text())
        finding = Path(spec['findings'][0]['path'])
        cases = (({'kind': 'patterns', 'decisions_used': 5, 'proposals': [{'feature': 'x'}]}, 'rests on 5 decisions'),
                 ({'kind': 'calibration', 'groups': [{'result': 'MEASURED', 'n': 3}]}, 'at least 30'))
        for value, message in cases:
            finding.write_text(json.dumps(value))
            spec['findings'][0].update(kind=value['kind'], sha256=canon.sha256_hex(finding.read_bytes()))
            path = self.dir / 'floor.json'
            path.write_text(json.dumps(spec))
            with self.assertRaisesRegex(develop.DevelopError, message):
                self.propose(str(path), self.frame_patch())

    def test_findings_must_match_their_hash_and_say_something(self):
        spec = json.loads(Path(self.spec()).read_text())
        Path(spec['findings'][0]['path']).write_text('{"kind": "patterns", "proposals": []}')
        bad = self.dir / 'bad.json'
        bad.write_text(json.dumps(spec))
        with self.assertRaisesRegex(develop.DevelopError, 'sha256'):
            self.propose(str(bad), self.frame_patch())
        spec['findings'][0]['sha256'] = canon.sha256_hex(Path(spec['findings'][0]['path']).read_bytes())
        bad.write_text(json.dumps(spec))
        with self.assertRaisesRegex(develop.DevelopError, 'apophenia'):
            self.propose(str(bad), self.frame_patch())


class Gate(Sandbox):
    def test_a_clean_patch_without_held_out_evidence_holds(self):
        patch = self.frame_patch()
        self.propose(self.spec(), patch)
        report = develop.gate('p1', patch, self.state, T, None, None, None, self.repo)
        self.assertEqual('HOLD', report['decision'])
        self.assertEqual([], report['reasons'])
        self.assertEqual(0, report['checks']['characterization']['exit'])
        self.assertEqual([], report['checks']['paths']['violations'])
        self.assertIn('no held-out evidence supplied', report['holds'])
        self.assertIn('no self-test evidence register supplied', report['holds'])
        self.assertNotIn('ante-develop/p1', git(self.repo, 'branch', '--list'))

    def test_a_canary_that_appears_after_proposal_rejects_at_the_gate_and_halts_the_loop(self):
        patch = self.frame_patch()
        spec = self.spec()
        self.propose(spec, patch)
        finding = Path(json.loads(Path(spec).read_text())['findings'][0]['path'])
        finding.write_text(json.dumps({'kind': 'patterns', 'decisions_used': 40,
                                       'proposals': [{'feature': 'ANTE-CANARY-' + 'e5' * 16}]}))
        report = develop.gate('p1', patch, self.state, T, None, None, None, self.repo)
        self.assertEqual('REJECT', report['decision'])
        self.assertTrue(any('canary' in reason for reason in report['reasons']))
        state = develop.State(self.state, self.repo)
        self.assertEqual('gate', state.halt()['stage'])
        self.assertTrue(state.stopped(2))
        with self.assertRaisesRegex(develop.DevelopError, 'halted by a held-out canary'):
            develop.gate('p1', patch, self.state, T, None, None, None, self.repo)

    def test_a_forged_proposal_cannot_bring_its_own_evaluator(self):
        # Bypass propose (as a tampered state file would) with a patch that rewrites the
        # evaluator to report no violations and the harness to always pass.
        patch = self.patch({
            'scripts/nexus-improve.py': ("    return {'changed': changed, 'violations': violations}",
                                         "    return {'changed': changed, 'violations': []}"),
            'tests/characterization/run.py': ('def load_cases()', 'def load_cases_unused()'),
            TARGET: (OLD, NEW + ' ' + 'ANTE-CANARY-' + '9e' * 16)})
        paths = sorted(['scripts/nexus-improve.py', 'tests/characterization/run.py', TARGET])
        spec = json.loads(Path(self.spec(scope=('**',))).read_text())
        develop.State(self.state, self.repo).append('proposal', {
            'id': 'p1', 'spec': spec, 'findings': spec['findings'], 'base': self.base,
            'patch_sha256': canon.sha256_hex(Path(patch).read_bytes()), 'paths': paths}, T)
        report = develop.gate('p1', patch, self.state, T, None, None, None, self.repo)
        self.assertEqual('REJECT', report['decision'])
        flagged = {v['path'] for v in report['checks']['paths']['violations']}
        self.assertEqual({'scripts/nexus-improve.py'}, flagged & {'scripts/nexus-improve.py'})
        self.assertEqual(0, report['checks']['characterization']['exit'], 'base harness, not the forged one')
        self.assertTrue(any('develop policy' in r for r in report['reasons']))
        self.assertEqual(['patch'], report['checks']['canaries']['hits'])

    def test_held_out_packs_inside_the_checkout_are_refused(self):
        patch = self.frame_patch()
        self.propose(self.spec(), patch)
        evidence = {k: 'x' for k in ('variant', 'baseline_trials', 'baseline_judgments', 'candidate_trials',
                                     'candidate_judgments', 'improver')}
        evidence['held_out'] = str(self.repo / 'examples/nexus/casepacks')
        with self.assertRaisesRegex(develop.DevelopError, 'outside the checkout'):
            develop.gate('p1', patch, self.state, T, evidence, None, None, self.repo)

    def test_a_patch_changed_after_proposal_is_refused(self):
        patch = self.frame_patch()
        self.propose(self.spec(), patch)
        Path(patch).write_text(Path(patch).read_text().replace('culture, and', 'culture,  and'))
        with self.assertRaisesRegex(develop.DevelopError, 'differs'):
            develop.gate('p1', patch, self.state, T, None, None, None, self.repo)


class HeldOut(Sandbox):
    """The gate on real held-out evidence: copies of the example packs, refrozen outside the checkout."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import importlib.util

        def load(name, path):
            spec = importlib.util.spec_from_file_location(name, ROOT / path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        cls.tr = load('trial_for_develop', 'scripts/nexus-trial.py')
        cp = load('casepack_for_develop', 'scripts/nexus-casepack.py')
        cls.held = cls.root / 'held'
        for source in sorted((ROOT / 'examples/nexus/casepacks').iterdir()):
            target = cls.held / source.name
            shutil.copytree(source, target)
            data = json.loads((target / 'pack.json').read_text())
            data.pop('frozen')
            data['split'], data['author'] = 'held_out', 'independent-author'
            (target / 'pack.json').write_text(json.dumps(data))
            for name in data['materials']:
                with open(target / name, 'a', encoding='utf-8') as out:
                    out.write('\n<!-- held-out copy -->\n')
            cp.freeze(target, 'independent-author', '2026-10-10T12:00:00Z')
        cls.policies = cls.root / 'policies.json'
        cls.policies.write_text(json.dumps({'schema_version': 1, 'policies': {'p': {
            'max_cost_usd': 2.0, 'max_tokens': 400000, 'max_calls': 8, 'max_wall_seconds': 1800}}}))

    def record(self, label):
        trials = self.dir / f'{label}-trials.json'
        for pack in sorted(self.held.iterdir()):
            for variant in ('single_agent', 'fixed_team', 'nexus_instance'):
                self.tr.start(pack, variant, 't1', 'claude-test', 'p', self.policies, 'op-1', self.dir / label / 'runs',
                              self.dir / label / 'art', trials, self.tr.fake_executor)
            run = self.dir / label / 'runs' / pack.name / 't1' / 'nexus_instance'
            for task in ('A', 'B', 'C'):
                self.tr.accept(run, task, True, 'trial-owner', {'contract_met': True}, use_proposed=task != 'C',
                               executor=self.tr.fake_executor)
        return trials

    def judge(self, label, trials, fatal=0):
        rows = json.loads(trials.read_text())
        path = self.dir / f'{label}-judgments.json'
        path.write_text(json.dumps([{
            'submission_id': r['submission_id'], 'reviewer': 'blind-reviewer', 'judged_at': '2099-01-01T00:00:00Z',
            'evidence_ref': 'review', 'factual_errors': 0,
            'fatal_defects': fatal if r['variant'] == 'nexus_instance' else 0, 'constraint_violations': 0,
            'evidence_coverage': {'covered': 2, 'required': 2}} for r in rows]))
        return path

    def evidence(self, baseline_fatal, candidate_fatal):
        self.runs = getattr(self, 'runs', 0) + 1
        b, c = self.record(f'b{self.runs}'), self.record(f'c{self.runs}')
        return {'variant': 'nexus_instance', 'held_out': str(self.held), 'improver': 'ante-develop',
                'baseline_trials': str(b), 'baseline_judgments': str(self.judge(f'b{self.runs}', b, baseline_fatal)),
                'candidate_trials': str(c), 'candidate_judgments': str(self.judge(f'c{self.runs}', c, candidate_fatal))}

    def fatal_spec(self, ident):
        doc = json.loads(Path(self.spec(ident)).read_text())
        doc['metric']['name'] = 'fatal_defects'
        path = self.dir / f'{ident}-fatal.json'
        path.write_text(json.dumps(doc))
        return str(path)

    def test_a_held_out_regression_is_rejected_and_two_stop_the_loop(self):
        for number in (1, 2):
            patch = self.patch({TARGET: (OLD, NEW + ' ' * number)}, name=f'r{number}.patch')
            self.propose(self.fatal_spec(f'r{number}'), patch)
            report = develop.gate(f'r{number}', patch, self.state, T, self.evidence(0, 1),
                                  str(self.repo / 'foundation/selftest-register.json'), None, self.repo)
            self.assertEqual('REJECT', report['decision'])
            self.assertTrue(report['held_out_regression'])
            self.assertTrue(any(r.startswith('fatal_defects') for r in report['checks']['held_out']['reasons']))
            develop.State(self.state, self.repo).append('close', {'id': f'r{number}', 'outcome': 'rejected'}, T)
        with self.assertRaisesRegex(develop.DevelopError, 'stopped'):
            self.propose(self.fatal_spec('r3'), self.frame_patch())

    def test_measured_improvement_with_every_check_is_proposed_as_one_draft(self):
        patch = self.frame_patch()
        self.propose(self.fatal_spec('ok'), patch)
        report = develop.gate('ok', patch, self.state, T, self.evidence(1, 0),
                              str(self.repo / 'foundation/selftest-register.json'), None, self.repo)
        self.assertEqual('PROPOSE', report['decision'], (report['reasons'], report['holds']))
        self.assertEqual([], report['checks']['selftest']['new_fail_rows'])
        self.assertIn('ante-develop/ok', git(self.repo, 'branch', '--list'))
        plan = develop.pr('ok', self.state, 'main', T, execute=False, repo=self.repo)
        self.assertEqual('ante-develop/ok', plan['branch'])


def gate_entry(ident, decision, regression=None, branch=None, changed=(TARGET,), review=None):
    payload = {'id': ident, 'base': 'b', 'decision': decision, 'held_out_regression': regression,
               'checks': {'paths': {'changed': list(changed), 'violations': []},
                          'autonomy': {'review': review}}, 'reasons': [], 'holds': []}
    if branch:
        payload['branch'] = branch
    return payload


class Anchor(Sandbox):
    def test_a_fresh_or_truncated_state_cannot_reset_the_loop(self):
        self.propose(self.spec('p1'), self.frame_patch())
        fresh = str(self.dir / 'fresh.jsonl')
        with self.assertRaisesRegex(develop.DevelopError, 'anchor'):
            develop.propose(self.spec('p2'), self.frame_patch(), self.base, fresh, T, self.repo)
        develop.State(self.state, self.repo).append('close', {'id': 'p1', 'outcome': 'withdrawn'}, T)
        lines = Path(self.state).read_text().splitlines(keepends=True)
        Path(self.state).write_text(''.join(lines[:-1]))          # cut the last entry
        with self.assertRaisesRegex(develop.DevelopError, 'anchor'):
            develop.State(self.state, self.repo)

    def test_an_unanchored_log_with_entries_is_refused(self):
        self.propose(self.spec('p1'), self.frame_patch())
        subprocess.run(['git', '-C', str(self.repo), 'update-ref', '-d', develop.ANCHOR_REF], check=True)
        with self.assertRaisesRegex(develop.DevelopError, 'no anchor'):
            develop.State(self.state, self.repo)


class Loop(Sandbox):
    def seed(self, ident, delta=None):
        spec = json.loads(Path(self.spec(ident, delta=delta)).read_text())
        develop.State(self.state, self.repo).append('proposal', {'id': ident, 'spec': spec, 'findings': [], 'base': self.base,
                                                      'patch_sha256': 'x', 'paths': [TARGET]}, T)

    def test_two_consecutive_held_out_regressions_stop_the_loop_until_a_human_resumes(self):
        state = develop.State(self.state, self.repo)
        self.seed('a')
        state = develop.State(self.state, self.repo)
        state.append('gate', gate_entry('a', 'REJECT', regression=True), T)
        state.append('close', {'id': 'a', 'outcome': 'rejected'}, T)
        self.seed('b')
        state = develop.State(self.state, self.repo)
        state.append('gate', gate_entry('b', 'REJECT', regression=True), T)
        state.append('close', {'id': 'b', 'outcome': 'rejected'}, T)
        with self.assertRaisesRegex(develop.DevelopError, 'stopped'):
            self.propose(self.spec('c'), self.frame_patch())
        with contextlib.redirect_stdout(stdio.StringIO()):
            code = cli.main(['develop', 'resume', '--by', 'Ana (owner)', '--reason', 'regressions understood',
                             '--state', self.state, '--at', T, '--repo', str(self.repo)])
        self.assertEqual(0, code)
        self.propose(self.spec('c'), self.frame_patch())

    def test_a_pull_request_needs_a_propose_gate_and_happens_once(self):
        self.seed('a')
        with self.assertRaisesRegex(develop.DevelopError, 'not PROPOSE'):
            develop.pr_plan('a', self.state, 'main', self.repo)
        develop.State(self.state, self.repo).append('gate', gate_entry('a', 'PROPOSE', regression=False,
                                                            branch='ante-develop/a'), T)
        plan = develop.pr('a', self.state, 'main', T, execute=False, repo=self.repo)
        self.assertFalse(plan['executed'])
        self.assertIn('--draft', plan['commands'][1])
        self.assertNotIn('--force', plan['commands'][0])
        develop.State(self.state, self.repo).append('pr', {'id': 'a', 'url': 'u', 'branch': 'ante-develop/a', 'draft': True}, T)
        with self.assertRaisesRegex(develop.DevelopError, 'at most one'):
            develop.pr_plan('a', self.state, 'main', self.repo)

    def test_the_loop_never_opens_a_pull_request_touching_github(self):
        self.seed('a')
        develop.State(self.state, self.repo).append('gate', gate_entry('a', 'PROPOSE', branch='ante-develop/a',
                                                            changed=['.github/workflows/ci.yml']), T)
        with self.assertRaisesRegex(develop.DevelopError, '.github'):
            develop.pr_plan('a', self.state, 'main', self.repo)

    def test_execute_refuses_to_overwrite_an_existing_remote_branch(self):
        remote = self.dir / 'remote.git'
        subprocess.run(['git', 'init', '-q', '--bare', str(remote)], check=True)
        work = self.dir / 'work'
        subprocess.run(['git', 'clone', '-q', '--shared', str(self.repo), str(work)], check=True)
        git(work, 'remote', 'set-url', 'origin', str(remote))
        empty = subprocess.run(['git', '-C', str(work), 'hash-object', '-t', 'tree', '-w', '--stdin'], input='',
                               check=True, capture_output=True, text=True).stdout.strip()
        orphan = git(work, '-c', 'user.name=t', '-c', 'user.email=t@invalid', 'commit-tree', empty, '-m', 'x').strip()
        git(work, '-c', 'push.negotiate=false', 'push', '-q', 'origin', f'{orphan}:refs/heads/ante-develop/a')
        self.seed('a')
        develop.State(self.state, self.repo).append('gate', gate_entry('a', 'PROPOSE', branch='ante-develop/a'), T)
        content = git(self.repo, 'cat-file', 'blob', develop.ANCHOR_REF)
        blob = subprocess.run(['git', '-C', str(work), 'hash-object', '-w', '--stdin'], input=content,
                              capture_output=True, text=True, check=True).stdout.strip()
        git(work, 'update-ref', develop.ANCHOR_REF, blob)
        with self.assertRaisesRegex(develop.DevelopError, 'already exists on the remote'):
            develop.pr('a', self.state, 'main', T, execute=True, repo=work)


class TuringLock(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix='ante-turing-'))
        self.count = 0

    def one(self, name='budget', value=1):
        return dict(ZERO, **{name: value})

    def review(self, proposal_id, accepts, reviewer='Ana (independent operator)', level='INDEPENDENT_OPERATOR',
               at=T):
        body = {'reviewer': reviewer, 'independence_level': level, 'proposal': proposal_id,
                'accepts_cumulative': accepts, 'at': at, 'statement': 'reviewed this change'}
        self.count += 1
        path = self.dir / f'review-{self.count}.json'
        path.write_text(json.dumps({**body, 'record_sha256': canon.digest(body)}))
        return str(path)

    def admit(self, entries, ident, delta, verdict, at=T):
        entries.append({'kind': 'proposal', 'at': at, 'payload': {'id': ident, 'spec': {'autonomy_delta': delta}}})
        payload = gate_entry(ident, 'PROPOSE' if verdict['decision'] == 'PASS' else 'HOLD')
        payload['checks']['autonomy'] = verdict
        entries.append({'kind': 'gate', 'at': at, 'payload': payload})

    def test_any_positive_delta_needs_an_independent_review(self):
        proposal = {'id': 'a', 'spec': {'autonomy_delta': self.one()}}
        self.assertEqual('HOLD', lock.assess([], proposal, None, T)['decision'])
        self.assertEqual('PASS', lock.assess([], proposal, self.review('a', 1), T)['decision'])
        self.assertEqual('PASS', lock.assess([], {'id': 'z', 'spec': {'autonomy_delta': ZERO}}, None, T)['decision'])

    def test_five_individually_reviewed_steps_are_held_on_the_fifth(self):
        names = ['budget', 'scope', 'frequency', 'permissions', 'gate_thresholds']
        entries, decisions = [], []
        for index, name in enumerate(names):
            ident = f'p{index}'
            delta = self.one(name)
            verdict = lock.assess(entries, {'id': ident, 'spec': {'autonomy_delta': delta}},
                                  self.review(ident, 1), T)
            decisions.append(verdict['decision'])
            self.admit(entries, ident, delta, verdict)
        self.assertEqual(['PASS'] * 4 + ['HOLD'], decisions)
        self.assertIn('accumulated steps need their own review', lock.assess(
            entries[:-2], {'id': 'p4', 'spec': {'autonomy_delta': self.one()}}, self.review('p4', 1), T)['reason'])

    def test_a_review_of_the_accumulation_releases_and_resets_it(self):
        entries = []
        for index in range(4):
            ident = f'p{index}'
            verdict = lock.assess(entries, {'id': ident, 'spec': {'autonomy_delta': self.one()}},
                                  self.review(ident, 1), T)
            self.admit(entries, ident, self.one(), verdict)
        verdict = lock.assess(entries, {'id': 'p4', 'spec': {'autonomy_delta': self.one()}}, self.review('p4', 5), T)
        self.assertEqual(('PASS', True), (verdict['decision'], verdict['accumulation_reviewed']))
        self.admit(entries, 'p4', self.one(), verdict)
        self.assertEqual(0, lock.cumulative(entries, T))

    def test_old_steps_leave_the_window(self):
        entries = []
        for index in range(4):
            ident = f'p{index}'
            verdict = lock.assess(entries, {'id': ident, 'spec': {'autonomy_delta': self.one()}},
                                  self.review(ident, 1, at='2026-01-01T00:00:00Z'), '2026-01-01T00:00:00Z')
            self.admit(entries, ident, self.one(), verdict, at='2026-01-01T00:00:00Z')
        self.assertEqual(4, lock.cumulative(entries, '2026-01-02T00:00:00Z'))
        self.assertEqual(0, lock.cumulative(entries, T))

    def test_reviews_by_the_loop_by_a_lower_level_for_another_proposal_or_forged_are_refused(self):
        proposal = {'id': 'a', 'spec': {'autonomy_delta': self.one()}}
        forged = self.review('a', 1)
        record = json.loads(Path(forged).read_text())
        record['accepts_cumulative'] = 99
        Path(forged).write_text(json.dumps(record))
        for path in (self.review('a', 1, reviewer='ante develop'), self.review('a', 1, level='SEPARATED_CONTEXT'),
                     self.review('other', 1), self.review('a', 1, at='2026-12-01T00:00:00Z'), forged):
            self.assertEqual('REJECT', lock.assess([], proposal, path, T)['decision'], path)

    def test_netting_dimensions_does_not_hide_a_step(self):
        netted = dict(ZERO, budget=1, human_review_reduction=-1)
        self.assertEqual(1, lock.positive(netted))
        self.assertEqual('HOLD', lock.assess([], {'id': 'a', 'spec': {'autonomy_delta': netted}}, None, T)['decision'])

    def test_undeclared_autonomy_trips_the_wire(self):
        patch = '+++ b/x\n+max_spend_usd: 500\n'
        verdict = lock.assess([], {'id': 'a', 'spec': {'autonomy_delta': ZERO}}, None, T, patch)
        self.assertEqual('HOLD', verdict['decision'])
        self.assertIn('UNDECLARED_AUTONOMY', verdict['reason'])


if __name__ == '__main__':
    unittest.main()
