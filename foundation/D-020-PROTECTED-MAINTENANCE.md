# D-020 — Explicit owner authorization with truthful authorship

Status: **ACCEPTED BY OWNER — original changes merged through #13 and #15; revised P2 prepared below**.
Prepared and approved 29 October 2026 on `foundation/codex/d020`, from review
base `cc027eda68ea281ac80d194ac3c19821541b016b`. The owner answered “si” to the
specific request to adopt option C and apply P0–P3 plus R1. This direct approval,
not publication of this document, authorizes the exact packet.

## Accepted option C

Keep the prohibition on the self-development loop modifying its evaluator.
Allow a separate maintenance agent, outside that loop, to prepare or apply an
exact protected patch when the owner explicitly authorizes that specific change.
Record the actual author, the person who approves, and the person or agent who
applies it as separate roles. Review does not turn agent-generated code into
human-written code. The owner approved this explicit amendment/exception to the handwritten
requirement; approval does not retroactively make generated code handwritten.

D-003's mechanical isolation and line-by-line review remain useful. Its claim
that review makes the owner the human author of record is superseded. ADR-0003's
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
updates. That was a specific approved exception. The owner separately approved
the three patches below and R1 after reviewing PR #13; neither approval grants
standing authority for future changes.

## Concrete decision packet

The machine-readable [approval packet](proposals/d020-approval-packet.json)
contains complete hashes, source fingerprints and the scope of the direct owner
approval. The original three patches were applied in separate protected commits and merged
through #13 and #15. Their hosted workflows passed. The owner subsequently asked
Codex to decide P2 and consolidate the branches as Netrunner Foundation. That
explicit delegated decision selects the v7.1.0 variant and retains full history;
it does not grant standing permission for future protected edits.

| ID | Decision or patch | Protected paths | Current state |
|---|---|---|---|
| P0 | Adopt option C and the per-patch procedure above | Rule amendment only | Accepted by owner |
| P1 | [Policy wording](proposals/d020-maintenance-policy.patch) | `strategy/overdrive-protected.json`, `strategy/NEXUS-OVERDRIVE.md` | Merged through #13 and #15 |
| P2 | [Foundation CI wiring, revised](proposals/ci-wiring-v7.1.patch) | `.github/workflows/check-runbooks.yml`, `scripts/verify-release.sh` | Original merged; v7.1.0 delta prepared for the consolidation PR |
| P3 | [Deterministic review test](proposals/test-nexus-review-glob.patch) | `scripts/test-nexus-review.py` | Merged through #13 and #15 |
| R1 | Ratify the narrow exception for the already merged `7b213eb` | `strategy/contracts.json` | Ratified by owner; history retained |

P1 changes only the policy description and its corresponding paragraph. The
protected array is identical. P2 adds both characterization runners, extraction
verification, Foundation tests, frozen reviewers, defence-layer checks and the
reported institutional self-test. P3 excludes `REVIEWER.md` and chooses a reviewed
artifact deterministically. Their exact patch fingerprints are:

- P1: `9d92cbd4c2cc1d2a7465a9705ae89e2ce9956550c754d70483fbc3db1d229f2b`
- P2 revised full wiring: `51d0a1f053d6faeafb85dfb8bf8f95bffb01831acaf676f2c1c1522d38757e09`
- P2 delta from the current main (one action pin): `5d4659fc3bd36f98412b11e40f1ea91df78417dbc9663b27c125a10f09fdb119`
- P2 original, retained for provenance: `64d1085836748b669906833b4c54e669da70f2bb20cb94756b6a86dd2df65d42`
- P3: `78e1ebfd20d33cdb8d925abf6a568ed3f3ee5857d9ec0d168a858b2be802b332`

R1 preserves `7b213ebfa876bc8f44c185b19d7484009bb8f205` and its actual provenance;
its diff SHA-256 is `eaf85e012af4cd7e27ae82883dcc8cbe420880c52292f4366559ba2840770003`. The owner explicitly ratified retaining that agent-authored commit under the
narrow mandate exception. Its history and co-author record remain intact;
ratification does not establish handwritten authorship or independent review.

The owner selected option C rather than the handwritten-only alternative.
Future protected changes still require specific approval of their own exact
patches. The approval of this packet is retained once for P0–P3 and R1; the agent
must not ask repeatedly for that same already-authorized scope.

## Sources and validation limits

The supplied mandate §2.3 and §11 originally required handwritten protected
changes and consultation before a non-extraction edit. The owner explicitly
approved this limited amendment. P1 aligns the manifest purpose and the
NEXUS-OVERDRIVE paragraph; their self-improvement prohibition and all 23
protected patterns are retained.

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
a complete Foundation-tree or hosted CI run. The original applied source received successful hosted checks in #13 and #15.
D-018 was separately accepted and merged in #12, with only its two approved
invocations rebaselined in both corpora. No frozen recording changes in this
consolidation. Fresh checks must cover the revised P2 candidate before merge.

## Application record

The exact approved outputs were prepared and checked locally, then published in
separate `protected:` commits. P2 is split into a release-script commit and a
workflow commit for per-file review and preservation of executable modes.
The owner-approved scope and observed results are recorded in
[`evidence/d020-execution.json`](evidence/d020-execution.json). The seven legacy
review tests pass after application on this operator's Python 3.12.14 checkout;
the original hosted Foundation job subsequently passed. The revised candidate
is checked separately and must not borrow that earlier green result.

## G1a local signatures (#23)

| Field | Value |
|---|---|
| Purpose | `ante sign` / `ante verify` / `ante attest`, the pinned trust store and their protection ([ATTEST.md](ATTEST.md)) |
| Review base | `b719f5789b20288d8fa519f747ed4dac1d560674` (main after #22) |
| Approved head | `53286803359579685ce07b3d34536f1c80ff1138` |
| Result tree | `cf06b56cdd12579d7ae3eeed3da22b945c161be0` |
| Patch SHA-256 | `b70b706222dad41dbbe1d3dfd8bc1f027ffc74188eb3570858a8297b21cda67e` (`ante attest approval`, fixed git options) |
| Paths | 31 changed, 27 of them protected; listed in the #23 description |
| Author | Claude (agent), in separate `protected:` commits; not handwritten |
| Approver and applicator | The owner, by merging #23 on GitHub at 2026-10-29T13:44:25Z (merge `284275f`) |
| Checks | 14/14 hosted checks succeeded on the approved head and on the merge commit |

The approval packet was published unsigned: no owner key was pinned yet, so this
approval exists only as the owner's merge action. It authorises this exact
patch and nothing after it. From the moment the owner's key is pinned, later
packets can be signed with `ante sign` and checked with `ante verify --head`;
the signature records the approval, and D-020 still decides what it permits.
