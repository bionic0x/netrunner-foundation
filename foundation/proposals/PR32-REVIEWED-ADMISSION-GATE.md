# PR #32 — Reviewed admission-gate candidate

Status: **OWNER-APPROVED AND APPLIED TO #32; merge awaits the owner's signature.**

The owner answered `si` to the exact six-file patch below in the authorized
ChatGPT channel on 30 October 2026. Codex applied its outputs to the existing
PR #32 after revalidating every input hash and mode. The original Claude commit
is preserved; the two correction commits have `protected:` titles and truthful
agent-authorship descriptions. A title does not establish human authorship.
The corrected runtime head is `e83222a2d18fdbffb2a2f8601c3103d4cb918c97`.
The [application record](../evidence/pr32-execution.json) distinguishes the
owner's direct approval, the applied bytes, CI and the still-missing signature.
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

The approved D-020 exception is limited to these exact outputs, outside the
self-development loop, with truthful agent authorship. It covers application,
preparation of the actual final candidate's unsigned merge approval for the
owner, and merge only after required checks and owner merge approval. It
creates no standing permission, private key, account or host authority.

The original #32 head is not this corrected candidate. Revalidate source inputs
and the PR head before application; changed inputs require renewed preparation.
The CI must run again on the corrected runtime head. If the admission report is
used, the owner signs `merge` scope against that final candidate and its merge
base, and the approval is added in a separate last commit.

## Owner signing step for the applied candidate

The [unsigned merge approval](pr32-merge-approval.unsigned.json) binds the actual
candidate above, with scope `merge` and review reference to #32. Its merge base
is `9b93fae9b68df85cf4a25a05c29e430fba4a13de`. The later #33 update to `main`
changed only unrelated documentation; all six reviewed input blobs and modes
are identical at the preparation base and the real merge base.

The canonical patch digest used by `ante sign` is
`b669128653c29c7096453993bf9b296fb676c03e00ec1f069214cfa830c945fd`.
The reviewed patch digest `1d268fad...` below remains unchanged. Replacing the
canonical patch's 40-character `index` IDs with their seven-character prefixes
reproduces the reviewed patch byte for byte. No code or mode differs. The
actual candidate tree is `6e250a8822ace074dd836279a0dd4960cd5cafb8`; the
preparation tree includes #33's unrelated documents and is recorded separately.

Use the existing signing account and key, from a checkout that has fetched
`foundation/d020-gate` and `netrunner/pr32-review-packet`. Export the public
unsigned document from the packet branch before signing it:

```sh
git fetch origin foundation/d020-gate netrunner/pr32-review-packet
git show origin/netrunner/pr32-review-packet:foundation/proposals/pr32-merge-approval.unsigned.json > /tmp/pr32-merge-approval.unsigned.json
git diff 9b93fae9b68df85cf4a25a05c29e430fba4a13de e83222a2d18fdbffb2a2f8601c3103d4cb918c97
```

Then run the existing `ante sign` procedure as the signing account, with this
document, `--head e83222a2d18fdbffb2a2f8601c3103d4cb918c97`, scope already
fixed to `merge`, the pinned owner verification method, and the current UTC
time. The signing command re-derives the bindings and refuses any difference
before accessing the key. The agent has validated those bindings read-only and
has not signed or accessed the private key.

The returned signed JSON is the only content to add as
`foundation/approvals/PR-32.json` in a final, separate commit on #32. After
verification and the required final-head checks, the already-authorized merge
can proceed. A code change after this candidate requires renewed preparation.

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
