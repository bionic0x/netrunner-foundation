# Delivery checkpoint — 28 October 2026

Ten pull requests are verified merged: #1 and #3–#11. Foundation and both
characterization harnesses are integrated in `foundation/base-86addea` at
`d2d57a7`. Main retains its later imported source history plus #1 (`15ffb29`).

PR #11 brings the frozen 116-case raw-byte corpus alongside Claude's 114-case
normalized corpus. Review of its full 268-file diff found no production path
beyond the documentation and corpus. All 237 raw corpus files (golden files,
manifest and regression harnesses) matched this operator's Git blob ids. No
output was regenerated. Claude reports 169 Foundation tests and passing raw and
normalized harnesses on its head; this operator did not rerun those suites.

## Remaining PR

#2 is OPEN. OSV reports four fixable vulnerabilities (one high, three medium)
in `mcp==1.29.0`, which the PR downgrades from 1.30.0. The fixed version is
1.30.0. The scanner failure is a dependency finding, not an infrastructure
failure. No bypass or new exception was introduced, and no agent-authored
protected dependency change was made.

Observed job:
https://github.com/bionic0x/neuromancers-foundation/actions/runs/40733306601/job/122975085995?pr=2

## Verification limits

- Consolidation head `3955813`: 12 successful checks, macOS queued.
- PR #11 head `275ab22`: 10 successful checks at merge, runbooks/tools running,
  macOS queued. The final merged-tree release is not claimed fully green.
- The protected CI wiring and deterministic legacy-review test fix remain
  proposals for human-authored application under invariant 3 (D-020).
- Bringing the later 71 source commits from main into Foundation requires the
  deliberate compatibility/rebaseline decision documented in D-018.

Individual merge receipts are in `merges-2026-10-28.json`. The prior local
phase-0 release failures and their logs remain in `results.json`; merging does
not change their measured outcomes.
