"""The new directory exceptions must not suppress unknown agent divisions."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_legacy_cli import ROOT, cli_environment


class DivisionInfrastructure(unittest.TestCase):
    def check_with_index_paths(self, extra_paths):
        with tempfile.TemporaryDirectory(prefix="ante-division-index-") as directory:
            env = cli_environment()
            env["GIT_INDEX_FILE"] = str(Path(directory) / "index")
            subprocess.run(["git", "read-tree", "HEAD"], cwd=ROOT, env=env,
                           check=True, capture_output=True)
            blob = subprocess.check_output(["git", "rev-parse", "HEAD:README.md"],
                                           cwd=ROOT, env=env, text=True).strip()
            for name in extra_paths:
                subprocess.run(["git", "update-index", "--add", "--cacheinfo",
                                "100644", blob, name], cwd=ROOT, env=env,
                               check=True, capture_output=True)
            return subprocess.run(["bash", "scripts/check-divisions.sh"], cwd=ROOT,
                                  env=env, capture_output=True, timeout=60)

    def test_foundation_and_tests_are_infrastructure(self):
        proc = self.check_with_index_paths(["foundation/index-fixture.md", "tests/index-fixture.md"])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_unknown_division_remains_rejected(self):
        proc = self.check_with_index_paths(["unknown-division-fixture/index-fixture.md"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn(b"unknown-division-fixture", proc.stdout)
        self.assertIn(b"not in divisions.json", proc.stdout)


if __name__ == "__main__":
    unittest.main()
