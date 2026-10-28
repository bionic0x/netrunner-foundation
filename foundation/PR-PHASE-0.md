# foundation: capture legacy CLI contracts before extraction

Tracking `foundation/` and `tests/` previously made the division checker treat
documentation and test infrastructure as two new agent divisions. This change
exempts exactly those directories and freezes the existing CLI behavior before
the package extraction.

Adds an inventory of 117 baseline sources, 116 byte-level subprocess cases over
43 CLI entry points, structural ADRs, baseline logs, measured limitations and a
visible delivery checklist. The new checker regression cases require accepted
infrastructure paths and continued rejection of an unknown division.
The runner also terminates timed-out process groups; a regression covers an
exited parent with a descendant holding its output pipes open.

Operational command implementations, NEXUS schema v1, Relay anti-egress, MIT
license, copyright, doctrine and existing third-party notices remain unchanged.
**Protected paths touched: none.** No additional application dependency, model
call, hidden held-out access or self-improvement mechanism is introduced.

Validation is detailed in `BASELINE.md`, `REVIEW.md` and `evidence/results.json`.
The final local characterization/harness suite passes all four methods: 116
frozen subprocess cases plus two directory and one timeout regression.
The baseline complete release gate exits 1 in Python 3.11 at Relay: 131 tests,
24 Unix-socket-permission errors, no skips. This is a **draft/HOLD**, not a green
phase-0 exit. Steps after Relay and local security/container checks remain
unmeasured. Historical base-commit Actions results are recorded separately.

Risks: coverage is not exhaustive; live/provider/host behavior is not exercised
by help snapshots. New fixture/evaluator paths need a separate human-authored
protection update before a self-development loop can exist. The canonical
contracts file lacks the requested coherence/pathology tables, and protected
engine extraction cannot be generated under the current human-authorship rule.

Destination: private `bionic0x/neuromancers-foundation`, created by the authorized
full-history import. Compare against `foundation/base-86addea` at the exact
pinned base; imported `main` has advanced and is preserved. Upload uses the
browser because the connector cannot access the new private repository.

Claude separately reports a passing full baseline and 114 frozen cases on local
commit `5e74ff3`. Those logs and files were not available for inspection here;
they are not substituted for the measured runs or the 116 cases in this PR.
The doctrine comparison with `STRATEGIC-CONTROL-PLANE` is corrected in the ADR.
Remaining prerequisites are in `TASKS.md`.
