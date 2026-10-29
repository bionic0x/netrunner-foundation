# D-020 — Explicit owner authorization with truthful authorship

Status: **PROPOSED — awaiting the owner's decision**. Prepared 29 October 2026
on `foundation/codex/d020`, from `cc027eda68ea281ac80d194ac3c19821541b016b`.
Publishing or merging this document does not approve its protected patches.

## Recommended option C

Keep the prohibition on the self-development loop modifying its evaluator.
Allow a separate maintenance agent, outside that loop, to prepare or apply an
exact protected patch when the owner explicitly authorizes that specific change.
Record the actual author, the person who approves, and the person or agent who
applies it as separate roles. Review does not turn agent-generated code into
human-written code. This is an explicit amendment/exception to the handwritten
requirement, never a claim that it was already satisfied.

D-003's mechanical isolation and line-by-line review remain useful. Its claim
that review makes the owner the human author of record is not adopted. ADR-0003's
authorship distinction remains; a recorded owner exception supplies the route
for supervised maintenance. The default without that exception remains HOLD.

## Boundary that remains in force

- `ante develop` / Overdrive may not propose, apply, commit or merge changes to
  any protected path, including the policy itself. They cannot invoke the
  maintenance route or treat this packet as permission.
- The protected path list, evaluator logic, held-out separation, Turing rules,
  thresholds and owner pause/merge control are not relaxed by this proposal.
- Repository JSON is a receipt, not a credential or authorization source. A
  self-declared owner, a `protected:` title, CI success or a Git signature does
  not authenticate approval or independent review.
- Independent-operator requirements still need a real operator with the required
  access and ability to pause. This preparation is `SELF`; it is not an
  `INDEPENDENT_OPERATOR` review. Positive autonomy changes retain their own gate.

## Per-patch procedure

1. Prepare a separate maintenance branch and identify the review base, purpose,
   exact paths, patch SHA-256, input/output file hashes and intended checks.
2. Obtain explicit approval from the owner in the authorized human channel,
   referring to those patches. The agent must not approve its own packet.
3. Apply only the approved changes in separate `protected:` commits, recording
   real authorship and the approval's scope. Unrelated edits require a new patch.
4. Stop and renew approval if the patch, its scope or any protected input changes.
   An unrelated base update does not widen approval: revalidate the input hashes
   and rerun the affected checks on the new merge tree.
5. Keep proposed content and frozen reference outputs intact during validation.
   A failure requires repair and, if the approved diff changes, renewed approval.
6. Merge only after the required checks pass and the owner has authorized merge.
   Do not ask again when that exact scope is already authorized. Record the
   applied and merge commits, measured results and remaining limits.

No approval in this procedure becomes a standing grant to future changes.

## The observed Semgrep precedent

The owner explicitly authorized the two-file Semgrep rollback, applied by Codex
as `79cb744` and merged in PR #2 as `b793d22` after 13/13 hosted checks passed.
It restored Semgrep 1.179.0 and MCP 1.30.0 while retaining the other dependency
updates. That is evidence of a specific approved exception, not general
permission for the three patches below.

## Concrete decision packet

The machine-readable [approval packet](proposals/d020-approval-packet.json)
contains complete hashes and source fingerprints. Every approval is pending.

| ID | Decision or patch | Protected paths | Current state |
|---|---|---|---|
| P0 | Adopt option C and the per-patch procedure above | Rule amendment only | Owner decision pending |
| P1 | [Policy wording](proposals/d020-maintenance-policy.patch) | `strategy/overdrive-protected.json`, `strategy/NEXUS-OVERDRIVE.md` | Not applied |
| P2 | [Foundation CI wiring](proposals/ci-wiring.patch) | `.github/workflows/check-runbooks.yml`, `scripts/verify-release.sh` | Not applied |
| P3 | [Deterministic review test](proposals/test-nexus-review-glob.patch) | `scripts/test-nexus-review.py` | Not applied |
| R1 | Ratify the narrow exception for the already merged `7b213eb` | `strategy/contracts.json` | Ratification pending |

P1 changes only the policy description and its corresponding paragraph. The
protected array is identical. P2 adds both characterization runners, extraction
verification, Foundation tests, frozen reviewers, defence-layer checks and the
reported institutional self-test. P3 excludes `REVIEWER.md` and chooses a reviewed
artifact deterministically. Their exact patch fingerprints are:

- P1: `9d92cbd4c2cc1d2a7465a9705ae89e2ce9956550c754d70483fbc3db1d229f2b`
- P2: `64d1085836748b669906833b4c54e669da70f2bb20cb94756b6a86dd2df65d42`
- P3: `78e1ebfd20d33cdb8d925abf6a568ed3f3ee5857d9ec0d168a858b2be802b332`

R1 preserves `7b213ebfa876bc8f44c185b19d7484009bb8f205` and its actual provenance;
its diff SHA-256 is `eaf85e012af4cd7e27ae82883dcc8cbe420880c52292f4366559ba2840770003`. A prior merge establishes that
the commit was merged; it does not retroactively establish handwritten authorship
or independent review. If the owner chooses the handwritten-only alternative,
the owner supplies the replacement personally; this agent will not manufacture
that provenance or rewrite shared history.

The two other options remain available: require human-written protected changes
without this exception, or approve selected maintenance patches individually
without adopting a general maintenance procedure. An ambiguous answer approves
none of the pending items. An explicit approval of this entire identified packet
can cover P0–P3 and R1 once, without repeated confirmation for the same scope.

## Sources and validation limits

The supplied mandate §2.3 and §11 require handwritten protected changes and
consultation before a non-extraction edit. The current protected manifest's
purpose and NEXUS-OVERDRIVE's improvement-gate rule require a separate human-authored
PR. P1 is the proposed alignment of those texts; it is not yet in force.

The supplied Marco (12 September 2026 edition), VIII.9, distinguishes actual
independence, escalation and pause authority from labels and duplicated review.
D-020 applies those distinctions procedurally; no new authenticated approval or
independence mechanism is implemented here. No chapter XVII conjecture is used.

The [preparation evidence](evidence/d020-preparation.json) records ten passing
checks: eight remote source fingerprints, application of all three patches to
an isolated snapshot, unchanged protected patterns and other manifest fields,
Bash syntax, workflow YAML/command coverage, the seven patched legacy review
regressions on Python 3.12.14, decision-document scope, and no protected changes
in the actual checkout. The legacy test ran on an isolated `86addea` fixture
snapshot whose protected input files match the pinned review base. It was not
a complete Foundation-tree or hosted CI run. CI and the complete Foundation
release must run on the applied tree before operational adoption. D-018 and changes to frozen
recordings remain a separate owner decision being prepared by Claude.
