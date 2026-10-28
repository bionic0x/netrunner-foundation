# Legacy CLI byte contracts

These **116 cases across 43 entry points** were captured from the unchanged
`86addea22f6060f2c50e81c67c6dadf978ea3749` tree with CPython 3.11.17 on Linux.
Cases use existing public/synthetic examples, never real learning data or a
private held-out set. `manifest.json` records the exact argv, stdin, return code
and SHA-256 of each raw stream. The expected files contain original bytes with
**no normalization**.

Run from the repository root with Python 3.11 and the existing hash-locked
validation dependency (PyYAML):

```bash
python3 -m pip install --require-hashes --no-deps -r .github/requirements/validation.txt
python3 -m unittest discover -s tests/characterization -v
```

The runner fixes locale, terminal width/color, timezone and Python hash seed. It
uses its own interpreter for shell-invoked Python. It performs no snapshot
updates. Neither stdout, stderr nor nonzero exit codes are normalized away.
Each subprocess has a 60-second timeout; a timeout is a failure. The runner kills
the process group and separately bounds output collection during cleanup. A
regression covers an exited parent whose child keeps the output pipes open.
Read-only cases
operate on the real checkout; help/error cases do not invoke providers or install
profiles. `/dev/stdin` cases require a POSIX host, matching the Linux CI target.
The scoped golden-file Git attribute permits trailing spaces in raw stdout:
the original Markdown brief uses two-space line breaks that must remain intact.

Coverage includes both NEXUS v1 example replays, plans at an explicit time,
duplicate-key acceptance by legacy NEXUS, duplicate-key and bool/int rejection by
marketplace intake, redacted marketplace parse errors, ordinary/strict lint,
JSON/Markdown briefs, routing, casepack verification, registry order and the
unchanged-path Overdrive gate. Help/error snapshots cover the live command entry
points, but do not prove live execution.

`foundation/INVENTORY.md` lists scope exclusions. Existing upstream unit tests
remain in place. These fixtures must not be rewritten to make a future refactor
pass. The new fixtures/harness also need a human-authored protection update before
any self-development loop is allowed to modify the repository.
