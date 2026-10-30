# PR #32 — Reviewed admission-gate candidate

Status: **PREPARED, NOT APPLIED; specific D-020 owner approval required.**
Prepared on 30 October 2026 against `ed31c60`, after the #33 documentation
reconciliation. D-021 is already integrated and is not reopened by this packet.

The original #32 head is `252382f744a902d9acb1ca6bcc74522c4c4b2281`.
Its informational gate had two independently reproduced issues:

| Finding | Original behavior | Corrected isolated behavior |
|---|---|---|
| P1: target-only input drift | A signed feature still reported `PROCEED` after the target changed another line of the same protected input; the merge was conflict-free. | Compare complete Git entries, including modes, for every reviewed input against the actual target. Drift returns `HOLD / STALE_BASE`; unrelated target updates remain admissible. |
| P2: renewal | Replacing an existing approval with a valid renewed signature was not recognised as the approval-only tip. | A final commit may add or replace exactly the approval file, with one parent. Verification still binds that parent; mixed renewal commits remain rejected. |

Five regressions cover content drift, mode drift, unrelated target advances,
renewal and mixed renewal commits. The report also names `target_base` separately
from the merge base. Neither correction turns the report into permission.

## Exact owner decision

The [full six-file patch](pr32-reviewed-admission-gate.patch) combines Claude's
original prototype with Codex's isolated corrections. SHA-256:

`1d268fad051bb0e308890983a0912a8257164728ea8ec4317268af9eb1b53bab`

The [scope packet](pr32-approval-packet.json) lists every input/output hash,
blob ID and mode, and the result tree reproduced with a private Git index.

| Path | Protection |
|---|---|
| `.github/workflows/check-runbooks.yml` | Protected |
| `ante/attest/commands.py` | Protected |
| `ante/attest/gate.py` | Protected, new file |
| `tests/foundation/test_attest.py` | Protected |
| `foundation/ATTEST.md` | Unprotected guide |
| `foundation/COMMANDS.md` | Unprotected guide |

The requested D-020 exception is limited to these exact outputs, outside the
self-development loop, with truthful agent authorship. It requests application,
preparation of the actual final candidate's unsigned merge approval for the
owner, and merge only after required checks and owner merge approval. It
creates no standing permission, private key, account or host authority.

The original #32 head is not this corrected candidate. Revalidate source inputs
and the PR head before application; changed inputs require renewed preparation.
The CI must run again on the corrected runtime head. If the admission report is
used, the owner signs `merge` scope against that final candidate and its merge
base, and the approval is added in a separate last commit.

## Evidence and limits

The [validation](../evidence/pr32-reviewed-validation.json) records **286
Foundation tests without skips**, **87 affected attestation tests**,
**114/114 normalized** cases and **116/116 raw-byte** cases plus three
regressions. No frozen recording changed. The
[review](../evidence/pr32-reviewed-review.json) is `SEPARATED_CONTEXT`, with
both findings resolved and no remaining actionable finding. The original
[reproduction](../evidence/pr32-stale-target-reproduction.json) uses ephemeral
fixture keys, not the owner's real signing key.

The prototype remains informational: CI uses `continue-on-error`, runs the PR's
gate code and reports `authorizes_action: false`. It is not mandatory
enforcement. Full local release remains unmeasured because Unix sockets are
denied. These prepared data files neither apply the code nor approve it.
