# Decision record — Ante Foundation

One entry per structural decision: context, decision, alternatives, consequences.
Status is `ACCEPTED` when the refactor relies on it, `PROPOSED` when it waits for
a human decision.

---

## D-001 · Where the foundation work lives — ACCEPTED

**Decision (owner, 28 Oct 2026).** The definitive destination is the private
repository `bionic0x/neuromancers-foundation`; no `ante-foundation` repository is
created. Work starts from `86addea` (branch `foundation/base-86addea`); `main`
there is the imported `9c54ba2` and is left as it is.

**Layout.** The original commits are kept unchanged and split into stacked
branches, one draft pull request per phase, each based on the previous phase:
`foundation/claude/phase-0` (on `foundation/base-86addea`) … `phase-6`, then
`foundation/claude/decisions` for the owner decisions and the consolidation of
the two characterization harnesses. Nothing is merged by the agent.

**Consequences.** `THIRD_PARTY_NOTICES.md` names the repository and its origin.
Bringing in `main`'s later commits is decision D-018.

---

## D-002 · Characterization contract — ACCEPTED

**Context.** The refactor must keep every existing CLI byte-identical (invariant 5).

**Decision.** `tests/characterization/run.py` runs 114 cases through the real
script paths and compares exit status, stdout, stderr and written files with
recordings taken at `86addea`. Paths are normalised to `<ROOT>` and `<TMP>`;
the environment is fixed (`TZ=UTC`, `LC_ALL=C.UTF-8`, `PYTHONHASHSEED=0`).
Each case was run twice before recording and none differed. `record` never
overwrites a recording: changing one is a behaviour change and goes in its own
pull request.

**Alternatives.** Rely on the existing unit tests (they import modules directly
and do not pin CLI text); snapshot only exit codes (misses output drift).

**Consequences.** Recordings depend on CPython 3.11 argparse wording; the harness
is run with the CI interpreter. Cases that need the `claude` CLI or a network
are characterised through `--help` and usage errors only.

---

## D-003 · Protected scripts during the extraction — PROPOSED

**Context.** Nine NEXUS programs, every `test-*` file, `verify-release.sh` and
`.github/**` are protected. The prompt asks for the old scripts to become thin
wrappers and for the new checks to join the release gate, and it allows protected
paths to change only in separate, hand-reviewed commits labelled `protected:`.

**Decision.** Phase 1 builds `ante/` and converts the unprotected scripts first.
Each protected script becomes a wrapper in its own `protected:` commit that is a
mechanical move (no logic change), listed file by file in the pull request, and
proven by its characterization cases. Wiring `tests/characterization` and
`ante selftest` into `verify-release.sh` and the workflows is likewise one
`protected:` commit per file.

**Alternatives.** Leave protected scripts untouched and duplicate their logic in
`ante/` (two implementations of the evaluator — rejected: the evaluator would
stop being one thing); wrap everything in one commit (not reviewable line by line).

**Consequences.** The owner reviews those commits as the human author of record.
Nothing in the self-development loop (Phase 4) can produce or modify them.

---

## D-004 · One machine source for the seven tests and fourteen pathologies — ACCEPTED

**Context.** `strategy/contracts.json` (protected) held modes, epistemic states,
decision states and levels. The seven tests and fourteen pathologies existed only
as prose, in two versions that disagreed on the name of test 1, on whether
`NOT_APPLICABLE` is a class, and on the wording of pathology 9.

**Decision (owner, 28 Oct 2026).**
1. `contracts.json` carries `coherence_tests` and `pathologies` with stable ids
   (`purpose`, `causal`, `interactive`, `conversion`, `legitimacy`, `epistemic`,
   `exit`; `level_inversion` … `chronic_personalization`).
2. The canonical name of test 1 follows the *Marco*: «Política /
   Political-purpose». `Governing-object` is a documented alias.
3. Pathology 9 is defined as competing where the adversary converts better;
   "each move of the adversary fixes our own response" is its mechanism of
   reproduction.
4. Test status (`PASS`, `CONDITIONAL`, `FAIL`, `NOT_APPLICABLE`) is separate
   from triage (`FATAL_DEFECT`, `ACCEPTED_RISK`, `PENDING_EVIDENCE`).
   `NOT_APPLICABLE` needs a reason, never counts as `PASS`, and is forbidden on
   Epistemic and Exit.
5. Existing enums and v1 compatibility are kept; chapter XVII stays in quarantine.

**Implementation.** One commit labelled `protected:` changes only
`strategy/contracts.json` (the owner's text transcribed; existing keys untouched;
all 114 characterization recordings and the existing contract checks pass).
`cohere` records the canonical names and lists `passed` and `not_applicable`
separately with per-status counts. The proposal file is withdrawn; the hidden
`--contracts` option remains for tests that need a different doctrine.

**Consequences.** `cohere`, `pathology` and `decide` read the canonical file.
Every `cohere` and `pathology` artefact records the hash of the doctrine it used,
and `decide` and `ante run` refuse or flag artefacts produced under another one.
The example chain was rebuilt under the canonical tables (its artefacts carry the
new doctrine hash); no characterization recording changed.

---|---|---|
| Test 1 name | Political/purpose | Governing-object |
| Finding classes | fatal defect · accepted risk · pending information | `FATAL_DEFECT` · `ACCEPTED_RISK` · `PENDING_EVIDENCE` · `NOT_APPLICABLE` (never on Epistemic or Exit) |
| Pathology 9 | Reflex symmetry: competing where the other actor converts resources better | Mirrored symmetry: the response is chosen by the opponent's move |

The *Marco* (XIV, XV.9) supports both readings of pathology 9: its definition
names the domain where the other converts better, its mechanism column names the
move that fixes our response.

**Proposal for the owner to decide.**
1. Add `coherence_tests` and `pathologies` to `contracts.json` with stable ids
   (`purpose`, `causal`, `interactive`, `conversion`, `legitimacy`, `epistemic`,
   `exit`; `level_inversion` … `chronic_personalization`), each carrying both
   display names as aliases so neither document is edited to fit the code.
2. Keep test status (`PASS`, `CONDITIONAL`, `FAIL`, `NOT_APPLICABLE`) separate
   from finding class (`FATAL_DEFECT`, `ACCEPTED_RISK`, `PENDING_EVIDENCE`),
   with `NOT_APPLICABLE` forbidden on Epistemic and Exit — the control plane's
   rule, which the prompt's `ante cohere` already assumes.
3. Pathology 9 keeps the *Marco* definition (domain where the other converts
   better) as its description and the mirrored-response mechanism as its
   `mechanism` field.

The SDR template (`strategy/templates/strategic-decision-record.md` §8) already
separates *result* (`PASS` / `CONDITIONAL` / `FAIL` / `NOT_APPLICABLE`) from
*classification* and uses *Governing-object*: points 1 and 2 follow it.

The complete proposed file is `foundation/proposals/contracts-v2.json`; the
strategy tests run against it.

**Consequences.** Until the owner decides, `ante/doctrine` loads only what
`contracts.json` already contains: `cohere`, `pathology` and `decide` exit 2 with
a pointer to this entry unless they are given the proposal explicitly
(`--contracts`, a hidden option kept for tests). Every `cohere` and `pathology`
artefact records the hash of the doctrine it used, and `decide` refuses parents
produced under another one, so a proposal file cannot be mixed into a real chain.

---

## D-005 · Canonical JSON keeps its historical profiles — ACCEPTED

**Context.** Six programs serialise JSON for hashing with different settings
(see `INVENTORY.md §3`). Frozen pack hashes and replay digests depend on them.

**Decision.** `ante/core/canon.py` exposes named profiles (`ascii`, `ascii_strict`,
`unicode_strict`, …) that reproduce each historical byte stream; new code uses
one profile, `unicode_strict`. Unifying the old callers would change existing
hashes and therefore breaks v1 compatibility.

**Alternatives.** One canonical function for everything (invalidates frozen packs).

---

## D-006 · Refactor scope — ACCEPTED

The extraction covers the Python programs under `scripts/` and adds the `ante/`
package. The shell installers and converters are out of scope; the release gate
continues to cover them, and the baseline records their result.

---

## D-007 · Duplicate JSON keys stay accepted where they were — ACCEPTED

`ante/core/io.py` rejects duplicate keys for every new command. The existing CLIs
that accept them today (characterization `routing--route-duplicate`,
`instance--validate-duplicate-keys`) keep doing so through Phase 1. Tightening
them is a behaviour change with its own pull request and rebaselined recordings.

---

## D-008 · The installer runtime stays self-contained in `scripts/` — ACCEPTED

**Context.** Moving `resolve-agents.py` into the package made six cases of the
protected `test-install-functional.py` fail with `No module named 'ante'`: the
test installs from a copy of `scripts/` plus `tools.json`, which is how the
installer is meant to run. Moving `registry.py` broke `check-tools.sh`, which
verifies capabilities by reading that file's source.

**Decision.** `install.sh`'s Python dependencies — `resolve-agents.py`,
`build-catalog.py`, `registry.py`, `integration-state.py`, `build-hermes-plugin.py`,
`check-hermes-config-rewrite.py` — stay where they are, unchanged.
`ante.registry` loads them by path (`ante._compat.load_script`) and adds only
readers for `strategy/runbooks.json`. One implementation, no copies.

**Alternatives.** Ship `ante/` with the installer (changes the distribution
contract the protected test encodes); duplicate the catalog code in the package
(two implementations of one roster).

**Consequences.** The prompt's "every old script is a wrapper" holds for the
NEXUS programs; for the installer runtime the rule is inverted on purpose, and
the inventory says so.

---

## D-009 · Runbooks declare their command chain — ACCEPTED

**Context.** `ante run <runbook>` must know which artefacts a runbook expects;
the prompt makes `cohere`, `pathology`, `close` and `decide` mandatory for
material runbooks.

**Decision.** Each runbook in `strategy/runbooks.json` gains `strategy_commands`.
Sprint and Full runbooks use the whole method
(`frame map cause focus options react ach watch close cohere pathology decide`);
Micro runbooks use `frame cause options close cohere pathology decide`. A runbook is
material unless it sets `material` to a stated reason. `check-runbooks.sh`
enforces the four controls and that the chain ends in `decide`; it stays
self-contained because the protected `test-runbook-contracts.py` runs it from a
copy without `ante/`. `scripts/convert-outputs.sha256` records the new
`runbooks.json` hash (a contract line, reviewed here).

**Alternatives.** Infer chains from the mode at run time (invisible to the app
that reads `runbooks.json`).

---

## D-010 · `PROCEED` requires an independent coherence review — PROPOSED

**Context.** Invariant 10 says a review by the same operator, model and context
is a coherence function, not a barrier; VIII.9 is satisfied only by
`INDEPENDENT_OPERATOR`.

**Decision.** `ante decide` accepts `PROCEED` only when the `cohere` parent was
produced at `INDEPENDENT_OPERATOR`. With `SELF` or `SEPARATED_CONTEXT` the owner
can still decide `PROCEED_WITH_CONDITIONS` and name the independent review as a
condition. This is a design choice of the foundation, made explicit for the owner
to confirm or relax.

---

## D-011 · Lineage is the set of artefacts supplied, bound by case and time — ACCEPTED

Each artefact names its parents by hash, carries the `case_id` set by `frame`,
and is sealed by `artifact_sha256`. A command verifies every parent's seal,
refuses parents of two cases, parents dated after its own decision time, and the
absence of the parents its step needs (exit 3). Claims are visible downstream
only through the parents actually supplied, so a reference to an upstream claim
proves that artefact was present.

---

## D-012 · Model drafting is opt-in and never signed — ACCEPTED

`--draft-with PROVIDER --model ID` asks a declared provider's adapter to draft a
command input from a brief. The output is `<command>.draft.json`: every claim is
forced to `HYPOTHESIS` with `origin: system`, the proposal sits under `input`
beside a `draft` header with `signed: false`, and running a command on the file
as written fails. Only Anthropic has an adapter (the existing Claude Code adapter);
other providers in `providers.json` are refused until one is written.

---

## D-013 · The develop loop's own protected list lives beside Overdrive's — PROPOSED

`ante develop` must never change the evaluator that judges it. Overdrive already
protects its evaluator in `strategy/overdrive-protected.json`, and
`nexus-improve.py paths` enforces it. The foundation adds parts that need the
same protection (the gate, the Turing lock, ICE layers, constructs, doctrine and
claims discipline, the ledger, characterization tests) and declares which scopes
a proposal may edit at all.

Changing `overdrive-protected.json` is itself a change to a protected path, so
this branch does not touch it. Instead `foundation/develop-policy.json` holds the
foundation's protected list, the editable scopes and the loop's limits (one open
proposal, 50 USD committed per campaign, stop after two consecutive held-out
regressions), and protects itself. The gate applies both lists, read at the base
revision, and the stricter wins.

**Proposal for the owner.** Merge the develop protected list into
`overdrive-protected.json` in a hand-written `protected:` commit, so a single
policy file governs every self-improvement path. Until then both lists apply.

**How the gate keeps its evaluator honest.** The candidate is applied in a
worktree at the base; `nexus-improve.py` and the characterization harness with
its recordings run from a second worktree at the base, never from the candidate.
A forged proposal that rewrites the evaluator is judged by the old one (tested).
Held-out packs must be outside the checkout. Missing held-out evidence is HOLD,
never PROPOSE. `pr` opens at most one draft per proposal, only with `--execute`,
refuses an existing remote branch, never force-pushes, never merges and never
touches `.github/**`.

---

## D-014 · The Turing lock counts autonomy cumulatively — PROPOSED

Each proposal declares an integer `autonomy_delta` on six dimensions
(permissions, budget, scope, gate thresholds, frequency, human-review reduction).
Only positive components count, so lowering one does not pay for raising another.
Any positive delta is held until a review record by an `INDEPENDENT_OPERATOR`
names the proposal. The lock also sums the positive deltas the gate let through
in the last 90 days, since the last review of the accumulation: above 4, a review
of the single step is not enough, and the record must accept the accumulated
total. Five one-step proposals, each reviewed on its own, therefore pass four
times and are held on the fifth — the erosion lives in the sum, which no
single-step reviewer saw. A proposal that declares no change but adds lines about
budgets, limits, approvals, permissions or thresholds trips a heuristic wire
(`UNDECLARED_AUTONOMY`) and is held. Review records are self-declared like every
independence label in Ante: the lock checks form, coverage, date, hash and that
the loop did not write them, not who the reviewer is. The limit and window are
constants in `ante/turing/lock.py`, a protected path, for the owner to set.

---

## D-015 · Canaries are seeded before freezing, and kept outside the checkout — ACCEPTED

A canary is `ANTE-CANARY-` plus 32 hex digits, written as an HTML comment into
each markdown or text material of a held-out pack by `ante ice seed`, before
`nexus-casepack.py freeze` (afterwards the material is fixed by `inputs_hash`).
The registry that maps canaries to packs lives beside the packs, outside the
checkout; the format alone is enough to detect contamination. `ante develop`
rejects any proposal whose spec, patch or cited findings contain a canary, at
proposal time and again at the gate. The held-out examples already frozen in
`examples/nexus/casepacks/` are public teaching material: they carry no canary,
and the gate refuses any held-out root inside the checkout. A test asserts that
the checkout contains no canary string at all.

The five ICE layers (`ante/ice/layers.json`) — canary scan (detect), autonomy and
spend margins (absorb), base-revision evaluation (contain), draft-only branch
(recover), held-out regression stop (learn) — each declare their data and their
assumption; `ante ice layers` fails if two share either.

---

## D-016 · Literary names stay in the CLI; artefacts use functional names — ACCEPTED

The prompt names the mechanisms after Gibson (`nodal`, `street`, `stub`,
`jackpot`, `ghosts`, `deck`, constructs, ICE, the Turing lock). They are kept as
command and module names, which are internal conventions. Everything a third
party reads uses functional names: `load_bearing_claims`, `misuse_analysis`,
`snapshot`, `frozen_reviewer`, `shadow_trial`, `cumulative_drift`,
`stale_claims`, `discard_archive`, finding codes such as
`MISUSE_ANALYSIS_MISSING` and `LOAD_BEARING_UNVERIFIED`. One residue remains for
the owner to decide: an artefact's `command` field records the command that
produced it, so a decision's lineage lists `nodal` and `street`. Renaming those
two commands (for example `load` and `misuse`) would remove it.

---

## D-017 · CI wiring for the foundation checks — APPLIED, owner approval pending

The prompt asks for the new checks in `verify-release.sh` and the runbook
workflow. Both `scripts/verify-release.sh` and `.github/**` are protected paths,
and adding steps is not a mechanical extraction, so this branch does not edit
them (§11). `foundation/proposals/ci-wiring.patch` adds, as a `protected:`
commit applied under D-020 once the owner approves its two files: the characterization recordings, the
extraction check, the foundation tests, the frozen-reviewer and defence-layer
checks, and the institutional self-test run on `foundation/selftest-register.json`
and published to the job summary (reported, never failing the build, as the
self-test doctrine requires). The patch applies cleanly to this branch and the
release gate was run with it applied.

**Applied** in `54d4cce` as an agent-authored `protected:` commit (D-020), with
`setup-python` pinned to the v7.1.0 SHA `main` uses. It lands when the owner
approves `.github/workflows/check-runbooks.yml` and `scripts/verify-release.sh`.

---

## D-018 · Bringing main's newer commits in — ACCEPTED

**Context.** `main` moved past `86addea` to `b793d22`: the upstream sync (one
new agent, 507 in total), held-out packs outside the checkout, and the
dependency updates of #1 and #2 with the owner-authorized Semgrep/MCP rollback.

**Measured on a trial merge.** Only `CHANGELOG.md` conflicts (both entries
kept). Every foundation test, `check-divisions`, `check-runbooks`, the 8/8
extraction proof and the frozen reviewers pass. Two invocations differ in both
harnesses: `build-catalog.py --check` and `check-agent-privileges.py` print
"507 agents" where the recordings say 506. `main` prints exactly those lines,
and reproduces the other 112 normalised recordings unchanged.

**Decision (owner, 29 Oct 2026).** Merge `main`; in a separate commit re-record
only those two cases in each harness, from `main`'s own scripts at `b793d22`,
each case carrying a `rebaselined` record. Nothing else is regenerated.

**Implementation.** Merge commit, then the rebaseline commit
(`foundation/CHARACTERIZATION.md` § Rebaselines).

---

## D-019 · Findings of the final clean-context review — ACCEPTED

A reviewer with a clean context (`SEPARATED_CONTEXT`: same model family, so a
coherence function, not an independent barrier) received only the diff, the
mandate and the test results. Every finding was checked against the code before
acting on it; all were confirmed.

| Finding | Disposition |
|---|---|
| P1 · The gate could answer `PROPOSE` without the self-test | A gate without a self-test register now holds (`no self-test evidence register supplied`). |
| P1 · Every loop limit read a state file the caller chose | The state is anchored in `refs/ante/develop-state` (absolute path and head hash). A fresh, different or truncated file is refused; only a human resets the loop by deleting the ref. Tested. |
| P1 · The loop could edit checks that `decide` and `cohere` rely on (`nodal`, `street`, `close`, chain loading) | `ante/strategy/**`, `ante/cli.py`, `ante/deck.py` and the package entry points are protected; the strategy commands are no longer an editable scope. `strategy/*.md` already covers every Markdown file under `strategy/` (fnmatch semantics, now stated in the policy), so the playbook and runbook scopes were dead and are removed. |
| P1 · `ATTRIBUTED_INTENT` could be laundered by restating the id one step removed | Artefacts carry `claim_history` (schema version 2): every status any ancestor recorded, through the whole lineage. Restating as `HYPOTHESIS` and then as `EVIDENCE` downstream needs the upgrade. Tested. |
| P1 · No test showed the gate rejecting a held-out regression | New tests run the gate on refrozen held-out copies of the example packs outside the checkout: a regression is `REJECT`, two stop the loop, and a measured improvement with every check passes as `PROPOSE` and one draft plan. |
| P2 · A system-origin reconciliation could supersede an external one | A system entry never replaces an external or owner outcome. Tested. |
| P2 · A caller-set sample floor could manufacture a finding | `develop` requires the policy's `finding_min_sample` (30) for calibration groups and pattern decisions; a lowered `stub --min-history` never makes a candidate eligible. |
| P2 · The upgrading observation's origin was unchecked | `upgrade.source` is `{ref, origin}`; `system` is refused. |
| P2 · Three documentation overclaims | Self-test docstring, ledger truncation note and the test count corrected. |
| P3 · No lock on ledger appends | Appends take an exclusive file lock; a concurrency test appends from eight processes. |

What the review could not settle from its inputs, and stays as stated before:
independence labels, Turing reviews and model reviews are self-declared; the
self-test and the CI steps run in CI only after the owner applies
`ci-wiring.patch` (D-017).

---

## D-020 · Who may author a change to a protected path — ACCEPTED

**Context.** D-003 (this line) let the owner's review of a mechanical or
dictated `protected:` commit make the owner its author of record. ADR-0003
(Codex line) held that a `protected:` title does not make agent-generated code
human-authored. The mandate and `strategy/NEXUS-OVERDRIVE.md` speak of
"hand-written" and "human-authored" changes.

**Decision (owner, 29 Oct 2026).** The rule already applied to the Semgrep/MCP
rollback (`79cb744`) becomes general:
1. An agent may write a change to a protected path.
2. The owner approves each protected file explicitly before it lands; merging
   the pull request is that approval only when its description lists every
   protected file it changes.
3. The commit says so in plain words — `protected:` title, "agent-authored",
   who approved, when, and which files — and is never presented as written by
   hand. Authorship stays the agent's; authority stays the owner's.
4. The self-development loop (`ante develop`) still cannot propose or modify a
   protected path; this rule covers changes an owner requested.

This replaces the authorship clause of D-003 and settles ADR-0003.

**Existing commit.** `7b213eb` (`strategy/contracts.json`, D-004) was written by
an agent from the owner's dictated decision and merged by the owner in #10.
Under this rule it is recorded as agent-authored, owner-approved; it is not
rewritten.

**Consequences.** `ci-wiring.patch` and `test-nexus-review-glob.patch` can be
applied as agent-authored `protected:` commits in a pull request that lists
their files for approval. The wording "human-authored" in
`strategy/overdrive-protected.json` and `strategy/NEXUS-OVERDRIVE.md` predates
this rule; aligning it is itself a protected change and is offered separately.

---

## Codex line — `foundation/phase-0` (raw-byte harness)

Recorded independently on `foundation/phase-0` (head `b60af82`) and kept verbatim below, headings one level down. Its ADR numbers are a separate series from the D-numbers above. ADR-0003 (no agent-generated change to protected paths, even under a `protected:` title) is stricter than D-003; that disagreement is open and belongs to the owner (see D-020).

## Foundation structural decisions

Source mandate: supplied “Ante Foundation: refactor fundacional…” dated by its
base commit to 2026-10-28. These ADRs describe the phase-0 preparation only.

### ADR-0001 — Pin the baseline and stop at the phase boundary

**Context.** The mandate requires baseline and characterization to be green before
any extraction. The available source HEAD is precisely
`86addea22f6060f2c50e81c67c6dadf978ea3749`.

**Decision.** Capture the original behavior before editing production code. Prepare
one local phase-0 branch. Do not implement phases 1–6 while the exit is blocked.
Keep the original MIT license, copyright and third-party notices intact.

**Alternatives.** A single large implementation or a partial unverified extraction
would bypass the required gate and make regressions harder to locate.

**Consequences.** This is a reviewable preparation, not a completed foundation
refactor or successful release. Human merge remains required for later PRs.

### ADR-0002 — Freeze actual byte output, including inconvenient behavior

**Context.** Compatibility covers stdout, stderr and status, not only parsed JSON.
The source uses several different parsers, canonical encodings and error styles.

**Decision.** Freeze unnormalized bytes from subprocesses in Python 3.11, including
help, malformed arguments, NEXUS v1 validation/replay, deterministic plans,
briefs, routing, registries, marketplace HOLD/error cases and option comparison.
Store SHA-256 checksums of each expected stream. Ship a read-only runner without
an update mode. Keep synthetic fixture records explicitly labeled.

**Alternatives.** Normalizing paths, parsing away formatting, testing only JSON
semantics or silently updating expected files would weaken the declared contract.

**Consequences.** These are 116 cases, not exhaustive coverage. Live providers,
mutable host state, container/HTTP execution and PowerShell remain outside the
frozen cases. Legacy NEXUS duplicate-key acceptance is intentionally captured;
a future strict shared loader cannot silently replace that behavior.

### ADR-0003 — Do not generate protected evaluator changes

**Context.** The protected manifest explicitly requires a separate human-authored
PR. It covers the instance engine, evaluator, casepacks, improvement/review/
campaign/optimizer scripts, all existing test scripts, release gate, doctrine,
contracts and `.github/**`. The attached mandate also says no system agent may
generate those protected refactors.

**Decision.** No protected path changes in this preparation. Record the required
human work as a blocking dependency, instead of generating a protected patch and
calling it “manual”. New characterization lives in `tests/characterization/`,
outside the existing protected script patterns; this does not make it safe for a
future improver to rewrite. A human-authored protection update should cover the
new fixtures, harness and future package evaluator modules before that loop exists.

**Alternatives.** A `protected:` commit title does not make agent-generated code
human-authored. Leaving old protected scripts as wrappers would still modify them.

**Consequences.** The core extraction and later release-CI wiring cannot proceed
under the current instructions without a human-authored change or an explicit
revision of the mandate. The current Overdrive mechanism remains unchanged.

### ADR-0004 — One source of doctrine requires a human contract change first

**Context.** `strategy/contracts.json` has schema_version, runbook_modes,
epistemic_states, decision_states and levels only. Doctrine sections 14–15 list
seven tests and fourteen pathologies, but those tables, correction fields and
false-positive cautions do not exist in the JSON contract.

**Decision.** Do not duplicate or invent a second canonical table in Python. Ask
for a separate human-authored contract/schema addition grounded in the doctrine
and the supplied Marco (12 September 2026 edition). Preserve all existing enums.
Chapter XVII remains quarantined; it supplies no extra blocking check.

**Alternatives.** Scraping prose at runtime, inventing machine identifiers silently
or editing the protected JSON as part of an automated extraction conflicts with
the mandate's single-source or evaluator constraints.

**Consequences.** A later comparison with `STRATEGIC-CONTROL-PLANE.md` corrected
an omission in the initial inventory: its first test uses `Governing-object`
instead of `Political/purpose`, pathology 9 names the response-selection mechanism
instead of the Marco's definition, and it lists `NOT_APPLICABLE` under findings.
The supplied mandate already separates test status from triage. The Marco XIV
and XV distinguish pathology definition from reproduction mechanism. Stable IDs,
source-labelled aliases and separate status/triage are a supported proposed
resolution, pending the user's doctrinal decision and the protected contract
change. Neither aliases nor human review of generated code satisfy handwritten
authorship requirements. Preserve existing v1 enums and output bytes.

### ADR-0005 — Add only necessary division-discovery infrastructure

**Context.** The existing division checker regards every tracked top-level
nonexcluded directory as an agent division. Tracking `foundation/` and `tests/`
would otherwise create two spurious division errors.

**Decision.** Add these exact two infrastructure directory names to its existing
nondivision allowlist. Change no division keys, agent discovery rules or output.
Characterize the check before that edit and verify identical bytes afterwards.

**Alternatives.** Misregistering documentation and tests as agent divisions or
moving them elsewhere would corrupt the registry or violate the requested layout.

**Consequences.** This one unprotected infrastructure file changes. All operational
CLI implementations stay at the baseline. No broader cleanup is included.

### ADR-0006 — Report measured failures without treating labels as authority

**Context.** Relay socket creation is denied here; there is no container runtime.
GitHub returned 404 for the original `bionic0x/ante-foundation` destination, and the available GitHub API
tools do not expose repository creation/forking. The upstream checkout is readable.

**Decision.** Keep exact run results and nulls/reasons for unmeasured checks. Do not
disable socket tests, claim full CI success, read private held-out packs, invoke
live models or push work into the upstream repository as a substitute target.
Prepare a patch and concrete next decision.

**Alternatives.** Skipping failures, changing the target repository silently or
calling exposed fixture measurements real learning would breach the mandate.

**Consequences.** A socket-capable CI run and a usable destination are required.
A separate agent review, if performed, is `SEPARATED_CONTEXT`: same operator/model
family, no independent operator with pause authority. It is a coherence check,
not the independent barrier required by doctrine VIII.9.

### ADR-0007 — Follow the user-selected destination

**Context.** The user subsequently selected `bionic0x/neuromancers-foundation` and
authorized browser creation, upload of phase 0 and a draft PR.

**Decision.** Use that exact destination. Preserve the pinned source, frozen
outputs, phase boundary and human-authored protection requirements. The first
secure sign-in request was declined. Later user-requested retries completed
authentication, verified on the signed-in GitHub dashboard. A private import
form is prepared, but automatic approval review rejected submission pending
explicit authorization to import the source's full history.

**Alternatives.** The old default name or the upstream repository would not match
the user's explicit destination. A GitHub connector session does not authenticate
the separate browser session.

**Consequences.** The phase-0 package and PR description are retargeted locally.
The user subsequently explicitly authorized the private full-history import.
The repository and imported history are now visible in GitHub. The connector
cannot access this private repository; browser upload is the authorized path.
The imported `main` has advanced to `9c54ba2`, so the phase-0 comparison must use
a separate base reference at the pinned `86addea`, without resetting `main`.
