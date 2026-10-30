# D-021 — Shared protection and retained independence controls

Status: **P0/P2 ratified; P1 applied and merged through #31.**
Reconciled on 30 October 2026. Claude applied the post-owner-key variant in
`260f0f43fe0a099a7d028b58d54392b44371aa94`, based on `bb759e2`, and it merged
as `9b93fae9b68df85cf4a25a05c29e430fba4a13de`. Codex verified the exact outputs
and records the integration here. This reconciliation changes no runtime code.

## Disposition

| ID | Decision | Recorded result |
|---|---|---|
| P0 / D-010 | Independence for `PROCEED` | Ratified by the direct owner reply. Only `INDEPENDENT_OPERATOR` admits `PROCEED`; the label is not authenticated identity or execution authority. |
| P1 / D-013 | Shared protected paths | Applied outside the development loop by Claude in #31; truthful agent authorship retained. |
| P2 / D-014 | Cumulative autonomy | Ratified by the same reply: existing 4-step / 90-day defaults and each positive delta's review retained. Policy choices, not measured safety guarantees. |

Both entry points now read the base revision's shared
`strategy/overdrive-protected.json`: **51 rules**, preserving every previous
Overdrive/Foundation pattern and the three frozen-reviewer paths. Schema 2
pins that source and rejects a shadow list or alternate source; historical
schema 1 remains supported. Editable scopes, budgets, proposal/regression
limits and sample floors are unchanged. T08 retains every target. The new
regression checks both entry points even if a candidate overwrites manifests.

## Exact applied scope

The retained [patch](d021-shared-protection.patch) has SHA-256
`7f8a49d631cc39edc263b64d17f32dbc2975d9c53a791a462d2a060bb6472fde`.
Its [scope packet](d021-approval-packet.json) records all seven input/output
hashes, blob IDs and modes, matching the applied commit and merged runtime.
The six protected paths are `ante/develop/policy.py`,
`foundation/develop-policy.json`, `strategy/overdrive-protected.json`,
`tests/foundation/test_shared_protection_policy.py`,
`tests/foundation/test_attest.py` and `foundation/DECISIONS.md`.
The seventh path, `foundation/ATTEST.md`, is an unprotected guide.

P1 preserves the signer, key generation, owner-key store and crypto locks.
The store had already been pinned through #29. No account or private key was
created or accessed by this reconciliation.

## Signed record and timing

The [public #31 comment](https://github.com/bionic0x/netrunner-foundation/pull/31#issuecomment-6511565544)
publishes a [signed approval](../evidence/d021-owner-approval.signed.json).
Codex recomputed its [verification](../evidence/d021-owner-approval-verification.json)
against the committed default trust store and candidate `260f0f4`: `VERIFIED`,
`signature_valid: true`, all six repository binding checks true, and
`authorizes_action: false`. An altered blob gives `BAD_SIGNATURE`.

It was issued at **2026-10-30T00:07:54Z**, after the merge at
**2026-10-29T17:11:53Z**. Its scope is `apply`, not `merge`. This is a post-merge
signed record, not evidence of a signed gate before application. The comment
also reports earlier manual approval; this audit does not independently
authenticate that earlier approval, human presence or operator independence.
A pinned-key signature grants no host permission and does not turn agent code
into handwritten code. Future protected changes retain D-020's procedure.

The signed pinned-diff hash is
`b49942422281db0a005a1606539a57a34da5643a1b4b27a8695e1b43fe434066`.
Its Git `index` lines use full object IDs; the preparation patch abbreviates
them to seven characters. Shortening only those IDs reproduces the preparation
patch byte for byte. A private-index application at the actual base reproduces
the signed and committed tree `637299fdd49ecb3208dffd270e2bbef71fd88158`.

## Validation and history

The exact candidate passed **268 Foundation tests without skips**, **15
nexus-improve tests**, **114/114 normalized** cases, **116/116 raw-byte** cases
plus three regressions, 8/8 extractions, 3/3 frozen reviewers and five layers.
All **14 hosted checks on the actual runtime head** passed, including security
and Linux/macOS installation. The [validation](../evidence/d021-validation.json)
separates hosted results from isolated runs. The
[review](../evidence/d021-review.json) found no actionable issue;
`SEPARATED_CONTEXT` is a coherence check, not authenticated independent review.
The complete local release gate remains unmeasured because Unix sockets are
denied; it is not claimed as passed or silently skipped.

Earlier preparation remains in history: `4810889f…` was approved but not
applied after #26 changed inputs; `1a8e34a5…` and pre-key variant `f0af758e…`
were superseded before renewed approval. The post-key variant was applied once
through #31. Recording that integration needs no second runtime application.

The [execution audit](../evidence/d021-execution.json) separates author,
applicator, recorder, signed evidence, merge and limits. Historical branches
remain reconciled in [HISTORICAL-BRANCHES.md](../HISTORICAL-BRANCHES.md).
