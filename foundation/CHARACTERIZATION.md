# Two characterization harnesses, one contract

Two harnesses froze the legacy command lines at `86addea` independently, before
any code moved:

| Harness | Location | Cases | Storage |
|---|---|---|---|
| Normalised (this branch, phase 0, `5e74ff3`) | `tests/characterization/cases.json`, `golden/<id>.json`, `run.py` | 114 over 37 Python programs | exit code, stdout, stderr and written files as text; the checkout path becomes `<ROOT>`, the per-case temporary directory `<TMP>` |
| Raw bytes (`foundation/phase-0`, Codex) | `tests/characterization/manifest.json`, `golden/<id>.stdout`/`.stderr`, `test_legacy_cli.py` | 116 over 43 entry points, shell scripts included | raw bytes, no normalisation, SHA-256 per stream in the manifest |

Neither set is regenerated. Frozen outputs are evidence about the base commit;
re-recording them after the refactor would make them evidence about the
refactor instead.

## Comparison

`foundation/tools/compare_characterization.py` reads both manifests and the
frozen outputs and classifies each invocation (script plus arguments, with
`{ROOT}/` removed because both run from the repository root). The result, with
the SHA-256 of both input manifests, is in
`foundation/evidence/characterization-comparison.json`.

| Class | Cases | Meaning |
|---|---:|---|
| `same_bytes` | 50 | Same invocation, same exit code, byte-identical stdout and stderr in both frozen sets |
| `disagree` | 0 | — |
| only in the normalised set | 64 | Mostly cases that write files, use temporary directories or fixtures (registry, resolve-agents, routing, plans with `--output`, replay checkpoints) |
| only in the raw set | 66 | Mostly shell entry points (`install.sh`, `convert*.sh`, `check-*.sh`, `lint-agents.sh`), Relay and host-probe help, unknown-option errors |
| **Union** | **180** | distinct invocations under contract |

Fifty cases recorded by different harnesses, with different interpreters
(CPython 3.11.17 and 3.11.18) and different environment rules, agree byte for
byte. That is the strongest available evidence that both recordings describe
the base and not their harness.

## What the comparison found

Running the raw-byte contract against each phase of this branch (manifest
hashes, read-only):

| Phase tip | Raw-byte contract | Difference |
|---|---|---|
| phase 0 `5e74ff3` | 115/116 | `check-divisions.sh` reports `foundation/` and `tests/` as unknown divisions: phase 0 added the directories, phase 1 (`f3ee0dc`) registers them. Codex's phase 0 registers them in the same change. |
| phase 1 `fc93d9c` | 116/116 | — |
| phases 2–6 | 115/116 | `check-runbooks.sh` appended "9/9 strategy command chains declared." to its success line (D-009, `23dcdd6`). This is a v1 output change the normalised set did not cover. |
| decisions branch | **116/116** | the success line is restored byte for byte; the `strategy_commands` validation stays and only speaks on failure |

The normalised harness passes 114/114 at every phase.

## Consolidation

1. Both harnesses stay, each with its own frozen outputs and its own runner;
   file names do not collide (`<id>.json` against `<id>.stdout`/`<id>.stderr`),
   and the raw harness's orphan guard looks only at `.stdout`/`.stderr`.
2. The 50 overlapping cases stay in both sets: they cost seconds and they are
   the cross-check above. Where a future difference appears in one set and not
   the other, the raw-byte record governs, because it carries no normalisation.
3. The release gate runs both (`tests/characterization/run.py` and
   `python3 -m unittest discover -s tests/characterization`), proposed for the
   protected `verify-release.sh` and the workflow in
   `foundation/proposals/ci-wiring.patch`.
4. Codex's branch (`foundation/phase-0` at `b60af82`, all three batches of
   frozen streams) is merged into this one without regenerating anything. Its
   manifest is byte-identical to the one the comparison above was run on; after
   the merge each of the 50 overlapping cases also checks the `.stdout` and
   `.stderr` files against their manifest hashes, and all 50 match.

On the merged tree: raw-byte harness 116/116 plus its two division regressions
and its runner-timeout regression (4 unittest methods, 14.8 s); normalised
harness 114/114. Codex's records (`BASELINE.md`, `DECISIONS.md`,
`INVENTORY.md`) are kept verbatim after this branch's, in their own section.

## Rebaselines

A recording changes only by a reviewed rebaseline in its own commit, recorded
on the case itself (`rebaselined`: decision, original commit, commit recorded
at, reason). Every other recording still describes `86addea`.

| Decision | Cases (normalised / raw) | From → at | Reason |
|---|---|---|---|
| D-018 | `catalog--check` / `catalog-current`; `check--check-agent-privileges` / `agent-privileges-check` | `86addea` → `b793d22` | `main` added one agent profile upstream; both commands now count 507 agents instead of 506. Recorded from `main`'s own scripts (not the merged tree) with each harness's own runner, two identical runs per case. |

Before re-recording, `main` at `b793d22` reproduced the other 112 normalised
recordings unchanged. The two cases still agree byte for byte across harnesses,
so the comparison above is unchanged: 50 shared, 0 disagreeing, 180 in the union.
