"""A child holding stdout must not outlive the capture timeout."""
import subprocess
import sys
import time
import unittest

from test_legacy_cli import run_case


class RunnerTimeout(unittest.TestCase):
    def test_exited_parent_with_child_holding_pipes_is_bounded(self):
        program = (
            "import subprocess,sys; "
            "subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'])"
        )
        started = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            run_case([sys.executable, "-c", program], timeout=0.2)
        self.assertLess(time.monotonic() - started, 5)


if __name__ == "__main__":
    unittest.main()
