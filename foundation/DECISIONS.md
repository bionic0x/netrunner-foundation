# Foundation structural decisions

Source mandate: supplied “Ante Foundation: refactor fundacional…” dated by its
base commit to 2026-10-28. These ADRs describe the phase-0 preparation only.

## ADR-0001 — Pin the baseline and stop at the phase boundary

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

## ADR-0002 — Freeze actual byte output, including inconvenient behavior

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

## ADR-0003 — Do not generate protected evaluator changes

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

## ADR-0004 — One source of doctrine requires a human contract change first

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

## ADR-0005 — Add only necessary division-discovery infrastructure

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

## ADR-0006 — Report measured failures without treating labels as authority

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

## ADR-0007 — Follow the user-selected destination

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
