# D-021 — Shared protection and the remaining independence decisions

Status: **PROPOSED; owner decision required. No protected runtime change is applied.**
Prepared against Netrunner Foundation `main` at
`b719f5789b20288d8fa519f747ed4dac1d560674` on 29 October 2026.

The original D-020 approval covered its P0–P3/R1 packet. It is not a standing
grant for this new patch. This proposal is prepared outside `ante develop` and
cannot be used by that loop as authority to change its evaluator.

## Decisions presented to the owner

| ID | Existing decision | Proposed disposition |
|---|---|---|
| P0 | D-010, independence for `PROCEED` | Ratify the existing floor: only `INDEPENDENT_OPERATOR` admits `PROCEED`; `SELF` and `SEPARATED_CONTEXT` remain conditional at best. The label is structurally checked, not authenticated identity or permission to execute. |
| P1 | D-013, shared protection | Authorize the exact five-file patch below to apply outside the loop and merge only after the required checks pass. |
| P2 | D-014, cumulative autonomy | Ratify the current limit of 4 positive steps over 90 days and the existing reviews: every positive change needs its own independent review; crossing the cumulative limit additionally needs acceptance of the accumulation. No threshold or review requirement changes. |

P0 and P2 settle pending owner choices without changing their runtime behavior.
The numeric defaults are policy choices, not measured guarantees of safety.
Publication of this proposal does not mark D-010, D-013 or D-014 accepted.

Authorizing P1 explicitly applies D-020's narrow exception to the mandate's
handwritten-only requirement to this exact new patch. It permits an external
maintenance agent to prepare and apply these bytes with truthful agent
authorship. Owner approval does not turn them into handwritten code or grant
the self-development loop access to the maintenance route.

## Concrete problem and resulting behavior

Today, `ante develop` combines the original Overdrive manifest's 23 patterns
with 26 Foundation patterns and the frozen-reviewer registry. The legacy
`nexus-improve.py paths` stage reads only the Overdrive manifest. Its path stage
therefore does not express all the newer Foundation protections. This is a
coverage difference between the path checks, not a demonstrated end-to-end
escape from the bounded optimizer.

P1 gives both entry points the same base-revision protected-path manifest:

- Preserve every existing pattern from both lists, without broadening any
  editable scope or changing a spend, proposal, regression or sample limit.
- Add the three currently frozen reviewer paths and `ante/attest/**` explicitly
  to the shared manifest, bringing it to 50 patterns. The latter protects a
  future verifier; this patch implements no attestation or signing service.
- Move `foundation/develop-policy.json` to schema 2: it retains loop limits and
  editable scopes, names `strategy/overdrive-protected.json`, and carries no
  duplicate protection list.
- Keep schema 1 loading for historical base revisions. In schema 2, reject an
  alternate manifest, a shadow list, boolean versions and unsupported versions.
- Read every policy from the base, so replacing manifests in the candidate
  cannot change the rules judging that candidate.

The frozen-reviewer registry continues to pin content hashes and retains its
specific refusal diagnostic. The new integration regression also catches a
future frozen reviewer added without shared path protection.

## Exact protected patch

File: [d021-shared-protection.patch](d021-shared-protection.patch)

SHA-256:
`fdea84af57869af77b3aa49bcdff175e40ccc096c6220821c2fde5189f6d929a`

| Protected path | Intended change |
|---|---|
| `strategy/overdrive-protected.json` | Preserve and extend the protected array to the shared union, frozen profiles and future attestation module. |
| `foundation/develop-policy.json` | Schema 2 pointer to the shared manifest; limits and editable scopes retained. |
| `ante/develop/policy.py` | Read schema 2 without a duplicate list; keep historical schema 1 support and frozen-reviewer diagnostics. |
| `foundation/DECISIONS.md` | Record D-010/D-013/D-014 and D-021 upon owner-approved application; keep historical ADRs intact. |
| `tests/foundation/test_shared_protection_policy.py` | Three new regressions for both path checks, base-policy inheritance, legacy loading and invalid schema 2 sources. |

The decision record is included in the exact protected scope so implementation
and governance can land together after approval.

Input/output SHA-256 values, Git blob IDs, modes and the precise requested
actions are recorded in [d021-approval-packet.json](d021-approval-packet.json).
For the new test file the input is explicitly absent. Actual agent authorship,
human approval and application must be recorded separately under D-020.

## Relationship to the supplied G0 and G1a candidates

The current `G0-TRUST-BOUNDARIES.md` and `G1A-INTEGRATION-CONTRACT.md` were read
at version 1. They are pre-PR design candidates, not adopted authorization
infrastructure. They separate historical execution receipts, owner approval
objects and actual host authorization; a valid signature or a local record
does not establish independent evidence or human presence by itself.

Those drafts request `ante/attest/**` in both protection lists. D-013 instead
asks for one policy source. P1 proposes reconciling this by removing the schema
2 duplicate list, pinning its pointer to the shared manifest, and proving both
entry points protect `ante/attest/**`. This design adjustment is explicit for
the owner to approve; neither supplied draft is silently rewritten or adopted.

D-021 adds no crypto dependency, key registry, private-key input, network call,
RFC serializer, signed receipt, approval broker or host signer. A future G1a
implementation needs its own exact protected patch, conformity evidence and
real host/key isolation. Ratifying D-010 or D-014 cannot supply that boundary.

## Measured on the isolated candidate

- Python 3.11.17: **199 Foundation tests**, including three new integration
  regressions; **15 legacy nexus-improve tests**.
- Both immutable harnesses: **114/114 normalized** and **116/116 raw-byte**
  cases, plus the two division regressions and timeout regression.
- All original protection patterns retained. Limits, editable scopes and sample
  floor unchanged. Frozen recordings unchanged.

[d021-validation.json](../evidence/d021-validation.json) records these results
and hashes of the retained local logs. The full local release gate is
unmeasured because this environment refuses Unix socket creation. No tests were
skipped or weakened. Hosted checks on the eventual applied runtime patch are
still required; green CI for this documentation/proposal PR cannot certify it.

The [final review](../evidence/d021-review.json) resolved both documentation
findings and reports no remaining actionable finding. It uses
`SEPARATED_CONTEXT`, a coherence check, and does not claim
an authenticated `INDEPENDENT_OPERATOR` review or a real host authority boundary.

## Application after an explicit owner decision

1. Record approval of P0–P2 and the exact P1 digest in the trusted owner channel.
2. Recheck the pinned protected input hashes against the current integration
   tree. If a protected input or the patch changes, return with a new packet.
3. Apply the exact patch in separate agent-authored `protected:` maintenance
   commits; no self-development proposal applies it.
4. Run the affected suites, both harnesses, security checks and complete
   socket-capable release validation. Merge only within the approved scope.
5. Record actual application/merge commits and update the owner decisions.

The historical branch audit is independent of this proposed policy change and
requires no protected patch: [HISTORICAL-BRANCHES.md](../HISTORICAL-BRANCHES.md).
