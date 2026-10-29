# D-021 — Shared protection and the remaining independence decisions

Status: **P0 and P2 accepted by owner; replacement P1 awaits renewed approval. No protected runtime change is applied.**
Prepared against Netrunner Foundation `main` at
`ae184df4e5e8a82740344c29f52223731ce6a07c` on 29 October 2026, after G1a, signer isolation and key generation were integrated through #23, #26 and #28.
The owner approved P0–P2 and the previous exact patch `4810889f…c87992f1`.
Before application, #26 changed the guide and a protected test input. D-020 step 4
therefore requires renewed approval of this replacement P1. P0 and P2 remain
ratified. The first replacement was published in #27 but was not approved or
applied. #28 then changed those two inputs again; this replacement preserves
its key-generation code, three tests and owner-setup guide. Earlier preparation
and approval remain recorded in the packet and Git history. The historical branch audit remains valid as its own dated snapshot.

The original D-020 approval covered its P0–P3/R1 packet. It is not a standing
grant for this new patch. This proposal is prepared outside `ante develop` and
cannot be used by that loop as authority to change its evaluator.

## Decisions presented to the owner

| ID | Existing decision | Proposed disposition |
|---|---|---|
| P0 | D-010, independence for `PROCEED` | Accepted by owner. Retain the existing floor: only `INDEPENDENT_OPERATOR` admits `PROCEED`; `SELF` and `SEPARATED_CONTEXT` remain conditional at best. The label is structurally checked, not authenticated identity or execution permission. |
| P1 | D-013, shared protection | Authorize the exact seven-file patch below, including six protected paths and the guide, to apply outside the loop and merge only after required checks pass. |
| P2 | D-014, cumulative autonomy | Accepted by owner. Retain the existing limit of 4 positive steps over 90 days and current review requirements. Every positive delta requires its own review; crossing the cumulative limit additionally requires acceptance of the accumulation. |

P0 and P2 settle pending choices without changing runtime behavior. Their
numeric defaults are policy choices, not measured guarantees of safety.
The direct owner reply ratifies P0/P2. The protected decision record will be
updated with the approved migration; publication alone cannot approve P1.

Authorizing P1 explicitly applies D-020's narrow exception to the mandate's
handwritten-only requirement to this exact new patch. It permits an external
maintenance agent to prepare and apply these bytes with truthful agent
authorship. Owner approval does not turn them into handwritten code or grant
the self-development loop access to the maintenance route.

## Concrete problem and resulting behavior

After #23, `ante develop` combines Overdrive's 25 patterns with 28 Foundation
patterns and the frozen-reviewer registry. `nexus-improve.py paths` reads only
the Overdrive list. Both now protect G1a, but the legacy path stage still does
not express all the newer Foundation protections. This is a difference in path
coverage, not a demonstrated end-to-end escape from the bounded optimizer.

P1 gives both entry points the same base-revision protected-path manifest:

- Preserve every pattern in both current lists, including G1a's `ante/attest/**`
  and `foundation/attest/**`. Add the three frozen reviewer paths explicitly:
  **51 patterns total**, with no old rule removed.
- Keep every editable scope, spend/proposal/regression limit and sample floor.
- Move `foundation/develop-policy.json` to schema 2: retain limits and scopes,
  pin `strategy/overdrive-protected.json`, and remove the duplicated list.
- Continue loading historical schema 1 bases. In schema 2, reject an alternate
  source, a shadow list, boolean versions and unsupported versions.
- Read policy at the base so candidate manifest replacement cannot loosen it.
- Migrate the post-#28 boundary test to the shared source. It still checks the
  verifier and trust store, and now checks all five listed evaluator/test paths
  in the Overdrive manifest. The new integration regression exercises both
  entry points, including the trust-store path and all frozen reviewer paths.

The post-#28 signature and key-generation implementation, trusted-key registry and dependency
locks are unchanged. No owner signing key or account is created by this patch. The guide retains #26's warning that manifest protection
is separate from HEAD/default-store and modified-verifier checks. Its guide is updated only to describe the shared protection
source; no signing authority or host execution permission is added.

## Exact maintenance patch

File: [d021-shared-protection.patch](d021-shared-protection.patch)

SHA-256:
`f0af758efe74714d420eeb82cd9f177411c51f2ba3963a6176b39dfde07e949c`

| Path | Protection | Intended change |
|---|---|---|
| `strategy/overdrive-protected.json` | Protected | Shared union plus frozen reviewer paths; preserve G1a rules. |
| `foundation/develop-policy.json` | Protected | Schema 2 pointer; limits and scopes retained. |
| `ante/develop/policy.py` | Protected | Schema 2 loading, historical schema 1 support and frozen-reviewer diagnostics. |
| `tests/foundation/test_shared_protection_policy.py` | Protected | Three new regressions for shared enforcement, base inheritance, legacy loading and invalid sources. |
| `tests/foundation/test_attest.py` | Protected | Migrate T08 to the canonical manifest without dropping its targets. |
| `foundation/DECISIONS.md` | Protected | Record D-010/D-013/D-014 and D-021 upon owner-approved application. |
| `foundation/ATTEST.md` | Unprotected guide | Describe the same shared source in the boundary and threat tables. |

The decision record is in the exact scope so implementation and governance land
together. Input/output hashes, blob IDs, modes and requested actions are in
[d021-approval-packet.json](d021-approval-packet.json). The new test's input is
explicitly absent. Authorship, approval and application remain separate roles.
The preparation packet describes scope; a future execution receipt records the
actual owner decision and application. No approval is authenticated by a JSON file.

## Relationship to G0 and G1a

`G0-TRUST-BOUNDARIES.md` and `G1A-INTEGRATION-CONTRACT.md` were read at version 1.
They distinguish historical receipts, owner approval objects and host authority.
G1a subsequently landed in #23, followed by signer isolation and review fixes in #26 and key-generation support in #28. Its current repository guide is
[ATTEST.md](../ATTEST.md); D-021 preserves that implementation.

The earlier drafts and G1a's current guide use two protection lists. D-013 asks
for one policy source. P1 explicitly reconciles that wording by pinning the
shared manifest, preserving both G1a patterns and migrating the boundary test.
It does not reauthorize the G1a delivery or turn a signature into independent
evidence, human presence or permission to execute. Host admission, key ownership,
rotation/revocation and actual operator independence retain their own controls.

## Validation

[d021-validation.json](../evidence/d021-validation.json) retains the earlier runs separately from this post-#28 candidate. The refreshed run uses Python 3.11.17,
the hash-locked attestation dependencies already in main and
`ANTE_REQUIRE_ATTEST=1`, so missing crypto dependencies fail instead of skipping.
The refreshed candidate passes **268 Foundation tests with zero skips**,
**15 nexus-improve tests**, **114/114 normalized** cases and **116/116 raw-byte**
cases plus three regressions. Every old protection pattern is retained. The
seven-file patch applies at the pinned base and reproduces the measured result
tree and output fingerprints. Both frozen corpora, the signer implementation,
trust store and crypto dependency locks are unchanged. No owner signing key or account is created by this patch.

The complete local release gate is unmeasured because this environment refuses
Unix socket creation. No test is skipped or weakened. Hosted checks for the
unapplied runtime patch are still required after approval: green CI for this
documentation/proposal PR exercises production code, not the patch stored as data.

The [post-#28 final review](../evidence/d021-review.json) reports no actionable
findings and confirms that the boundary test and the #28 delivery are preserved. It uses
`SEPARATED_CONTEXT`, a coherence check. It does not claim
authenticated independent-operator review or a real host authorization boundary.

## Application after an explicit owner decision

1. Retain the owner's existing P0/P2 ratification and obtain renewed approval
   of this exact replacement P1 digest in the trusted owner channel.
2. Recheck protected input hashes at the current integration tree; changed input
   or patch bytes require a new packet.
3. Apply this exact patch in separately reviewable, agent-authored `protected:`
   maintenance commits. No self-development proposal applies it.
4. Run affected suites, both corpora, security checks and complete socket-capable
   release validation; merge only in the approved scope after required checks.
5. Record the actual owner decision, application and merge in
   `foundation/evidence/d021-execution.json`. The preparation history stays intact.

The [historical branch audit](../HISTORICAL-BRANCHES.md) needs no protected patch.
