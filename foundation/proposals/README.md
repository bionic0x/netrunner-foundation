# Approved maintenance patches and historical proposals

D-020 option C and the original P0–P3/R1 packet were explicitly approved by the
owner. Original protected maintenance landed through PRs #13 and #15. These
files are retained as provenance; do not reapply them to the current tree.

| File | Status |
|---|---|
| `d020-maintenance-policy.patch` | P1 applied; all 23 protected patterns unchanged. |
| `ci-wiring.patch` | Original P2 applied; superseded reference using Python action v7.0.0. |
| `ci-wiring-v7.1.patch` | Revised full P2 reference, based on #12's integrated tree; includes full history and the current main-compatible v7.1.0 pin. |
| `ci-python-v7.1-delta.patch` | Actual one-line protected delta from the consolidation base; selected under the owner's explicit instruction to decide P2. |
| `test-nexus-review-glob.patch` | P3 applied; deterministic reviewed-artifact choice. |

The exact digests and per-file inputs/outputs are in
[d020-approval-packet.json](d020-approval-packet.json). Actual agent authorship
is retained. This receipt grants no standing authority; `ante develop` and
Overdrive cannot use this maintenance route to modify protected files.
