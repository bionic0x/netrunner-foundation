"""Frozen byte contracts captured on 86addea, before any production edit.

There is deliberately no update/snapshot-writing mode. Run with Python 3.11.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def cli_environment():
    env = os.environ.copy()
    env.update(LC_ALL="C", LANG="C", TZ="UTC", TERM="dumb", NO_COLOR="1",
               COLUMNS="80", PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
    # Shell entry points must use the same Python interpreter as this harness.
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    return env


def run_case(command, stdin=b"", *, timeout=60):
    process = subprocess.Popen(command, cwd=ROOT, env=cli_environment(),
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = process.communicate(stdin, timeout=timeout)
    except subprocess.TimeoutExpired:
        # Killing Bash alone can leave children holding the captured pipes open.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.stdout.close()
            process.stderr.close()
            process.kill()
            process.wait(timeout=5)
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


class LegacyCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((HERE / "manifest.json").read_text())
        expected = {case["id"] + "." + stream for case in cls.manifest["cases"]
                    for stream in ("stdout", "stderr")}
        actual = {path.name for path in (HERE / "golden").iterdir()
                  if path.suffix in (".stdout", ".stderr")}
        if actual != expected:
            raise AssertionError("missing or orphan frozen streams")

    def test_frozen_contracts(self):
        for case in self.manifest["cases"]:
            with self.subTest(case=case["id"]):
                command = [sys.executable if x == "{python}" else x for x in case["argv"]]
                result = run_case(command, case.get("stdin", "").encode())
                self.assertEqual(result.returncode, case["returncode"])
                for stream in ("stdout", "stderr"):
                    expected = (HERE / "golden" / (case["id"] + "." + stream)).read_bytes()
                    self.assertEqual(hashlib.sha256(expected).hexdigest(), case[stream + "_sha256"],
                                     "frozen fixture changed")
                    self.assertEqual(getattr(result, stream), expected, stream + " changed")


if __name__ == "__main__":
    unittest.main()
