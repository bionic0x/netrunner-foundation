# Inventory of the base commit

Base: `bionic0x/Ante-agency-agents` at `86addea` (main, 28 Oct 2026).
Scope of the refactor: the 37 Python programs under `scripts/` that are not
tests. The shell installers and converters (`install.sh`, `convert*.sh`,
`lint-agents.sh`, `check-*.sh`, `lib.sh`) stay outside the refactor; the release
gate keeps covering them unchanged.

Columns: **P** = listed in `strategy/overdrive-protected.json` (changes only by
a separate, hand-reviewed `protected:` commit); **Writes** = files the program
can create or change; **External** = processes or network it can reach;
**Covered by** = existing tests that exercise it, plus the characterization
cases recorded in Phase 0 (`tests/characterization/cases.json`).

## 1. NEXUS engine and evaluation

| Script | P | Purpose | Inputs → outputs | Writes | External | Depends on | Covered by |
|---|---|---|---|---|---|---|---|
| `nexus-instance.py` | ✔ | Deterministic planner and event replay; never executes | instance JSON (+ events JSONL, checkpoint, `--at`) → plan / replay JSON | `--output` file | — | `build-catalog.py`, `nexus-options.py`, `contracts.json`, `vectors.json`, `challenger-pairs.json` | `test-nexus-instance.py`, `test-nexus-improve.py`; 13 cases |
| `nexus-options.py` |   | Factor comparison without weighted scores | options JSON → dominance JSON | — | — | — | `test-nexus-evaluation.py`; 2 cases |
| `nexus-routing.py` |   | Admissible execution targets by level, vector and factor | instance (+ observations, `--at`) → route/coverage JSON | — | — | `contracts.json`, `providers.json`, `vectors.json` | `test-nexus-routing.py`; 4 cases |
| `nexus-lint.py` |   | Plan-shape findings before adoption | instance → findings JSON, exit 1 on ERROR (or WARN with `--strict`) | — | — | `nexus-instance.py` | `test-nexus-lint.py`; 4 cases |
| `nexus-brief.py` |   | Owner's decision brief | instance + events + `--at` → Markdown or JSON | — | — | `nexus-instance.py`, `nexus-lint.py` | `test-nexus-brief.py`; 3 cases |
| `nexus-pilot.py` |   | Bounded live-execution pilot | `step` / `accept` / `replay` | events JSONL, packets | via adapter | `nexus-anthropic.py`, `nexus-instance.py`, `nexus-routing.py` | `test-nexus-pilot.py`; 2 cases |
| `nexus-anthropic.py` |   | Claude Code execution adapter | `observe` | run artefacts | `claude` CLI | `agent-capabilities.py` | `test-nexus-anthropic.py`; help/usage only |
| `nexus-plan.py` |   | Planner drafts a task graph; owner adopts | `draft` / `adopt` / `verify` | draft, adoption files | `claude` CLI (draft) | `nexus-instance.py`, `nexus-lint.py`, `nexus-anthropic.py`, `build-catalog.py` | `test-nexus-plan.py`; help/usage only |
| `evaluate-nexus.py` | ✔ | Join trials with blind judgments; no composite | trials (+ judgments, cases) → report JSON | — | — | `evaluation-cases.json` | `test-nexus-evaluation.py` and four more; 3 cases |
| `nexus-blind.py` | ✔ | Seal review packets without pipeline labels | `seal` / `submission-id` | review packet directory | — | `evaluate-nexus.py` | `test-nexus-evaluation.py`, `test-nexus-review.py`; 1 case |
| `nexus-casepack.py` | ✔ | Freeze and verify case packs | `validate` / `verify` / `freeze` / `list` / `new` | `frozen` block in pack | — | `nexus-instance.py`, `build-catalog.py` | `test-nexus-casepack.py` and three more; 12 cases |
| `nexus-trial.py` | ✔ | Run one evaluation trial | `run` / `accept` / `owner-event` / `resume` / `status` / `brief` | run directory | `claude` CLI | `nexus-anthropic.py`, `nexus-brief.py`, `nexus-casepack.py`, `nexus-instance.py`, `evaluate-nexus.py` | `test-nexus-trial.py`; help/usage only |
| `nexus-review.py` | ✔ | Blind reviewer kit and collection | `kit` / `collect` | kit directory | — | `evaluate-nexus.py`, `nexus-casepack.py` | `test-nexus-review.py`; help/usage only |
| `nexus-improve.py` | ✔ | Self-improvement gate: protected paths + held-out non-regression | `paths` / `compare` / `gate` | — | `git` | `evaluate-nexus.py`, `nexus-casepack.py`, `overdrive-protected.json` | `test-nexus-improve.py`; 1 case |
| `nexus-campaign.py` | ✔ | Phase 1 exit and kill rule fixed before results | `plan` / `status` / `throughput` | `--out` plan | — | `nexus-casepack.py`, `nexus-trial.py`, `evaluate-nexus.py` | `test-nexus-campaign.py`; 2 cases |
| `nexus-optimize.py` | ✔ | Bounded edit proposal to one profile | `propose` | proposal directory | `claude` CLI | `nexus-casepack.py`, `nexus-anthropic.py`, `build-catalog.py` | `test-nexus-optimize.py`; help/usage only |
| `marketplace-intake.py` |   | External marketplace observations → offline HOLD packets | snapshot + `--at` → packets JSON | — | — | — | `test-marketplace-intake.py`; 5 cases |
| `nexus-relay.py` |   | Entry point of NEXUS Relay | `init` / `invite` / `serve` / `verify` / `anchor` / `reconcile` | SQLite store | local server | `relay/nexus_relay` | `relay/tests`; help only |

## 2. Catalog, registry and adapters

| Script | Purpose | Writes | External | Covered by |
|---|---|---|---|---|
| `build-catalog.py` | Roster from frontmatter; `--check` compares `CATALOG.md` | `CATALOG.md`, `--json` | — | `test-runbook-contracts.py`; 1 case |
| `registry.py` | Canonical divisions/tools reads for shell | — | — | 14 shell suites; 2 cases |
| `resolve-agents.py` | IDs, names and runbooks → adapter slugs | — | — | `test-install-functional.py`; 3 cases |
| `integration-state.py` | Per-agent adapter state | state files | `subprocess` | conversion suites; usage only |
| `build-hermes-plugin.py` / `check-hermes-plugin.py` / `check-hermes-config-rewrite.py` | Hermes router plugin build and checks | plugin directory | `subprocess` (rewrite check) | `test-hermes-plugin.py` and conversion suites |
| `agent-capabilities.py` / `check-agent-privileges.py` | Declared and observed capability boundaries | `--output` profile | — | `test-agent-capabilities.py`, `test-agent-privileges.py`; 1 case |
| `check-security-engagement.py` | Engagement contract of security agents | — | — | `test-security-engagement.py`; 1 case |
| `check-challenger-pairs.py`, `check-htp-gate0.py`, `check-strategy-vocabulary.py` | Structural guards | — | — | release gate; 3 cases |
| `host-acceptance.py`, `host-session-evidence.py`, `probe-host-claude-code.py` | Live-host acceptance records and probe | probe output | `claude` CLI (probe) | `test-host-acceptance.py` |
| `import-openclaw-community.py` | Community import with provenance | agent files | network (`urllib`) | `test-openclaw-import-provenance.py` |
| `list-changed-agent-files.py` | Changed paths → canonical agents | — | — | `test-changed-agent-files.py` |
| `benchmark-conversion.py` | Conversion timing, never a gate | benchmark output | `git` | — |

## 3. Duplicated code

| Concern | Copies | Divergence that the extraction must preserve |
|---|---|---|
| Canonical JSON for hashing | `marketplace-intake.py:70`, `nexus-casepack.py:65`, `nexus-instance.py:32`, `nexus-pilot.py:228`, `nexus-anthropic.py:317`, `integration-state.py` | `ensure_ascii` differs (`True` in intake and instance, `False` in casepack, pilot and adapter); `allow_nan=False` only in casepack and instance. Frozen `inputs_hash` values depend on these exact settings, so `ante/core/canon.py` exposes them as explicit profiles, not as one function. |
| ISO-8601 parsing with mandatory timezone | `nexus-instance.py:61`, `nexus-pilot.py:47`, `nexus-routing.py:48`, `marketplace-intake.py:54`, `nexus-casepack.py:139`, and six more | `nexus-routing.py` does not translate `Z` (accepted natively by Python 3.11) and echoes the rejected value in its message; the others do not echo. |
| JSON loading | `nexus-pilot.py:57`, `nexus-plan.py:63`, `nexus-trial.py:113`, `integration-state.py:50`, inline `json.loads` elsewhere | Duplicate keys are rejected only by `marketplace-intake.py` and `check-security-engagement.py`. Everywhere else the last value silently wins (characterization: `routing--route-duplicate` exits 0, `instance--validate-duplicate-keys` fails on an unrelated field). |
| `require()` / domain error classes | 6 `require` copies, 11 `*Error(ValueError)` classes | Message prefix and exit status differ per CLI (`ERROR …` exit 1 in most; intake prints a generic message and exits 2). |
| Exact-key validation | `marketplace-intake.py:exact_keys`, hand-written checks in the engine | — |
| Module loading of sibling scripts | `spec_from_file_location` in 14 programs | Hyphenated filenames prevent ordinary imports; this is the main obstacle the `ante/` package removes. |

## 4. Discrepancies with the foundation prompt

| Prompt assumption | Repository fact | Consequence |
|---|---|---|
| `ante/doctrine` loads the seven tests and fourteen pathologies from `strategy/contracts.json` | `contracts.json` holds runbook modes, epistemic states, decision states and levels only. Tests and pathologies exist as prose in several documents. | Resolved: `contracts.json` now carries both tables (D-004, accepted). |
| The seven tests have one canonical form | `GENERAL-STRATEGY-DOCTRINE.md §14` names test 1 *Political/purpose* and has three finding classes; `STRATEGIC-CONTROL-PLANE.md §5` names it *Governing-object* and adds `NOT_APPLICABLE` as a fourth class (forbidden on Epistemic and Exit). Pathology 9 reads *competing where the other actor converts better* in one and *the response is chosen by the opponent's move* in the other. | Resolved by the owner: test 1 «Política / Political-purpose» with `Governing-object` as alias; pathology 9 definition and mechanism as in D-004. |
| Old scripts become thin wrappers in Phase 1 | 9 of the 18 programs in section 1, every `test-*.py`/`test-*.sh`, `verify-release.sh` and `.github/**` are protected. | Wrapping a protected script, wiring new tests into the release gate or adding workflows all need hand-reviewed `protected:` commits. See D-003. |
| Held-out packs live outside the checkout | Three exposed sample `held_out` packs are published in `examples/nexus/casepacks`; `nexus-campaign.py` and `nexus-improve.py` already refuse held-out roots inside the checkout. | Invariant 4 is already enforced mechanically for real campaigns; the samples remain fixtures. |
| `ante` runs on Python 3.11 | CI pins Python 3.11; this inventory and the recordings were produced with 3.11.18. | Recordings embed CPython's argparse text; a different minor version can change help output. The harness must run under 3.11. |

---

## Codex line — `foundation/phase-0` (raw-byte harness)

Recorded independently on `foundation/phase-0` (head `b60af82`) and kept verbatim below, headings one level down. It inventories 117 tracked source files; the inventory above covers the 37 non-test Python programs under `scripts/`. Neither replaces the other.

## Foundation inventory

Pinned source: `86addea22f6060f2c50e81c67c6dadf978ea3749`. Inventory covers **117** tracked Python, Bash and PowerShell source files, including runtime modules and test harnesses.

Static references identify tests that mention a file/module; they are **not coverage measurements** and do not prove assertions ran. `null` coverage: no instrumentation was run. The machine-readable companion records exact parser declarations, imports, cross-script references and source hashes.

Frozen characterization: **116** subprocess cases across **43** script entry points. Help/error cases cover interface only. Success-path coverage is concentrated on offline validation, planning, replay, routing, comparison, registries, review briefs and marketplace intake. No live host, private held-out evidence or external execution was used.

| Script | Kind / protected | Inputs | Outputs | Effects | Referenced tests / frozen cases |
| --- | --- | --- | --- | --- | --- |
| `integrations/mcp-memory/setup.sh` | CLI/runtime entry | Presence of user MCP config paths. | Printed memory integration guidance. | Reads config-file existence only; no installation/network. Output depends on user config; not characterized. | No direct reference found; 0 frozen cases |
| `relay/container/forwarder.py` | CLI/runtime entry | Container socket/environment and HTTP byte stream. | Forwarded proxy stream. | Starts a local socket and forwards to mounted Unix socket; exercised by container E2E, not a public argparse CLI. | No direct reference found; 0 frozen cases |
| `relay/nexus_relay/__init__.py` | library | Package metadata. | Version/module identity. | No direct effects. | `scripts/test-hermes-plugin.py`, `scripts/test-install-hermes-destination.sh`; 0 frozen cases |
| `relay/nexus_relay/auth.py` | library | Member/invite/session tokens, request limits. | Auth records, cookies and checks. | Random secrets, expiry/time and database auth updates; no outward messages. | `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/cli.py` | CLI/runtime entry | Parsed Relay commands/config/instance. | CLI diagnostics and state. | Init/config/database writes, invites, lock, HTTP service, reconciliation, container execution via service. | `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/config.py` | library | Local config, instance and runtime settings. | Validated configuration / paths. | Reads and initializes local config/state; no model call. | `relay/tests/e2e_container.py`, `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/evidence.py` | library | Run output, workspace paths and byte budget. | Bounded manifests and SHA-256 pins. | Local bounded file reads; verifies output/workspace hashes. | `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/media.py` | library | Message content, media and policy bounds. | Conservative token/input bounds. | Pure analysis of supplied data; no URL fetching. | `relay/tests/test_properties.py`, `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/nexus.py` | library | Instance/events and admission requests. | Replay/admission and projected events. | Reads engine/instance/events, appends admitted events. | `relay/tests/test_relay.py`, `scripts/test-nexus-evaluation.py`, `scripts/test-nexus-improve.py`, `scripts/test-nexus-review.py`, `scripts/test-nexus-trial.py`; 0 frozen cases |
| `relay/nexus_relay/policy.py` | library | Provider request JSON/headers. | Allowlisted request or policy rejection. | No transport; anti-egress rules reject server tools, mcp_servers and URL sources. | `relay/tests/test_properties.py`, `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/proxy.py` | library | Local socket, allowed provider requests and meter. | Metered/clamped provider responses. | Binds Unix socket, synchronized budget accounting; forwards permitted provider calls. | `relay/tests/e2e_container.py`, `relay/tests/test_properties.py`, `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/reconcile.py` | library | Store state, NEXUS contract and incomplete runs. | Repair plan / applied projection. | Planning reads; apply repairs local state/events, without retrying uncertain effects. | `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/runner.py` | library | Admitted instruction, workspace, runtime image. | Container command / bounded result. | Invokes docker/podman with isolation, streams output; no runtime available here. | `relay/tests/e2e_container.py`, `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/server.py` | library | Authenticated HTTP requests and Relay service. | Room API/static responses. | Binds HTTP socket; writes through service after auth and CSRF checks. | `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/service.py` | library | Authorized room/task actions, store, contract and runner. | Run/review receipts and evidence. | Coordinates database writes, NEXUS events, workspaces, proxy and container invocation. | `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/nexus_relay/store.py` | library | SQLite path, entries and optional chain key. | Durable rows, log head/hash verification. | Transactional SQLite writes and append-only hash/HMAC log; wall-clock timestamps. | `relay/tests/test_relay.py`; 0 frozen cases |
| `relay/tests/e2e_container.py` | test harness | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `relay/tests/test_properties.py` | test harness | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `relay/tests/test_relay.py` | test harness | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | `relay/tests/test_properties.py`; 0 frozen cases |
| `scripts/agent-capabilities.py` | CLI/runtime entry | Agent slug, observed capability and scope-policy JSON. | Capability report or scoped profile text. | render writes --output when supplied. | `scripts/test-agent-capabilities.py`; 2 frozen cases |
| `scripts/benchmark-conversion.py` | CLI/runtime entry | Scenario, repeats, tool and source fixture. | Measured benchmark summaries / optional JSON. | Copies sources into temporary directories; runs conversions; timing is intentionally variable. | No direct reference found; 2 frozen cases |
| `scripts/build-catalog.py` | CLI/runtime entry | Registries and agent frontmatter. | CATALOG.md and optional catalog JSON; --check prints status. | Default writes CATALOG.md; --json writes the specified destination. | `scripts/test-nexus-instance.py`, `scripts/test-runbook-contracts.py`; 3 frozen cases |
| `scripts/build-hermes-plugin.py` | CLI/runtime entry | Repo root, catalog, registries and profiles. | Generated Hermes plugin and data. | Writes --out (default integrations/hermes). | `scripts/test-convert-fence-model.sh`, `scripts/test-convert-parallel-failure.sh`, `scripts/test-hermes-plugin.py`; 2 frozen cases |
| `scripts/check-agent-originality.sh` | CLI/runtime entry | Candidate agent paths and full roster. | Similarity diagnostics. | Read-only; no-args mode compares the full roster. | No direct reference found; 1 frozen cases |
| `scripts/check-agent-privileges.py` | CLI/runtime entry | Agent frontmatter and privilege registry. | Validation result or inventory. | Read-only. | `scripts/test-agent-privileges.py`; 3 frozen cases |
| `scripts/check-challenger-pairs.py` | CLI/runtime entry | Pair registry, agents and runbooks. | Validation result. | Read-only. | `scripts/test-nexus-instance.py`; 1 frozen cases |
| `scripts/check-divisions.sh` | CLI/runtime entry | Tracked paths, divisions registry and lint workflow. | Validation result. | Read-only; git ls-files is part of its directory discovery. | No direct reference found; 1 frozen cases |
| `scripts/check-hermes-config-rewrite.py` | test harness | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | `scripts/check-hermes-config-rewrite.sh`; 0 frozen cases |
| `scripts/check-hermes-config-rewrite.sh` | test harness | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/check-hermes-plugin.py` | CLI/runtime entry | Generated plugin builder and synthetic profiles. | Validation result. | Builds and loads a temporary plugin; no live Hermes host. | No direct reference found; 1 frozen cases |
| `scripts/check-htp-gate0.py` | CLI/runtime entry | HTP machine-readable artifacts. | Structural validation result. | Read-only; no chain access. | `scripts/test-htp-gate0.py`; 1 frozen cases |
| `scripts/check-runbooks.sh` | CLI/runtime entry | Runbook registry, doctrine references and agent files. | Contract/reference validation result. | Read-only; structural validity does not establish closure adequacy. | `scripts/test-runbook-contracts.py`; 1 frozen cases |
| `scripts/check-security-engagement.py` | CLI/runtime entry | Agent frontmatter / engagement registry. | Validation result or inventory. | Read-only; strict YAML/JSON key loaders. | `scripts/test-security-engagement.py`; 3 frozen cases |
| `scripts/check-strategy-vocabulary.py` | CLI/runtime entry | contracts.json and handoff/finding templates. | Vocabulary alignment result. | Read-only. | No direct reference found; 1 frozen cases |
| `scripts/check-tools.sh` | CLI/runtime entry | Tools registry, installer and converter implementation. | Validation result and canonical order. | Read-only. | No direct reference found; 1 frozen cases |
| `scripts/convert-engine.sh` | CLI/runtime entry | Agent files, registries, --tool, --out. | Converted tool files and diagnostics. | Rebuilds output directories, removes stale generated files; use isolated output. | `scripts/test-convert-fence-model.sh`, `scripts/test-convert-parallel-failure.sh`, `scripts/test-convert-slug-collisions.sh`, `scripts/test-convert-symlink-output.sh`, `scripts/test-incremental-conversion.py`, `scripts/test-install-conversion-failure.sh`, `scripts/test-lint-fences.sh`; 2 frozen cases |
| `scripts/convert.sh` | CLI/runtime entry | Same CLI as converter, canonical integration state. | Generated adapters and state diagnostics. | Delegates to engine/state; default writes integrations/. | `scripts/test-cli-usage.sh`, `scripts/test-convert-fence-model.sh`, `scripts/test-convert-frontmatter.sh`, `scripts/test-convert-outputs.sh`, `scripts/test-convert-parallel-failure.sh`, `scripts/test-convert-slug-collisions.sh`, `scripts/test-convert-symlink-output.sh`, `scripts/test-incremental-conversion.py`, `scripts/test-install-conversion-failure.sh`, `scripts/test-install-functional.py`, `scripts/test-kimi-adapter.py`, `scripts/test-lint-fences.sh`; 2 frozen cases |
| `scripts/evaluate-nexus.py` | CLI/runtime entry / protected | Case definitions, trial rows and optional blind judgments. | Descriptive paired evaluation JSON. | Read-only; supplied measurements are not authenticated. | `scripts/test-nexus-evaluation.py`, `scripts/test-nexus-improve.py`, `scripts/test-nexus-review.py`, `scripts/test-nexus-trial.py`; 3 frozen cases |
| `scripts/host-acceptance.py` | CLI/runtime entry | Host acceptance records and evidence. | Validation / model observation JSON. | Read-only; does not run a host. | `scripts/test-host-acceptance.py`; 2 frozen cases |
| `scripts/host-session-evidence.py` | library | Recorded stream events and return code. | Conservative evidence assessment values. | Library only; no CLI or host invocation. | No direct reference found; 0 frozen cases |
| `scripts/i18n/localize-agents-zh.ps1` | CLI/runtime entry | -TargetDirs and translation map. | Localized profile files and counts. | Overwrites selected installed Markdown. PowerShell unavailable; not executed. | No direct reference found; 0 frozen cases |
| `scripts/import-openclaw-community.py` | CLI/runtime entry | Pinned source ref, registry and root. | Imported profiles and source registry. | Fetches remote raw files even for dry-run; writes imports/registry and removes obsolete imports unless dry-run. Help/errors only. | `scripts/test-openclaw-import-provenance.py`; 2 frozen cases |
| `scripts/install.sh` | CLI/runtime entry | Tool detection, selections, install mode and generated adapters. | Installed profiles, router/plugin registration, diagnostics. | Writes tool/user config and destinations; replacement/uninstall may remove owned files; only help/error captured here. | `scripts/check-hermes-config-rewrite.py`, `scripts/check-hermes-config-rewrite.sh`, `scripts/test-agent-selection.sh`, `scripts/test-cli-usage.sh`, `scripts/test-install-all-path-collision.sh`, `scripts/test-install-continue-after-failure.sh`, `scripts/test-install-conversion-failure.sh`, `scripts/test-install-functional.py`, `scripts/test-install-hermes-destination.sh`, `scripts/test-install-link-ownership.sh`, `scripts/test-install-openclaw-registration.sh`, `scripts/test-install-parallel-logs.sh`, `scripts/test-install-selection-completeness.sh`, `scripts/test-install.sh`, `scripts/test-kimi-adapter.py`; 2 frozen cases |
| `scripts/integration-state.py` | CLI/runtime entry | Mode, tool, source hashes and adapter state. | Freshness/check explanations and generated files. | check/explain read; record/sync write granular state/adapters and may remove stale generated files. | `scripts/test-convert-parallel-failure.sh`, `scripts/test-incremental-conversion.py`, `scripts/test-install-conversion-failure.sh`, `scripts/test-lint-fences.sh`; 2 frozen cases |
| `scripts/lib.sh` | library | Sourced shell helper arguments and environment. | Metadata / TUI helpers for callers. | Library; terminal manipulation is possible in TUI helpers; no standalone CLI. | `relay/tests/test_relay.py`, `scripts/test-agent-capabilities.py`, `scripts/test-convert-fence-model.sh`, `scripts/test-convert-frontmatter.sh`, `scripts/test-convert-outputs.sh`, `scripts/test-convert-parallel-failure.sh`, `scripts/test-convert-slug-collisions.sh`, `scripts/test-convert-symlink-output.sh`, `scripts/test-host-acceptance.py`, `scripts/test-incremental-conversion.py`, `scripts/test-install-all-path-collision.sh`, `scripts/test-install-continue-after-failure.sh`, `scripts/test-install-conversion-failure.sh`, `scripts/test-install-hermes-destination.sh`, `scripts/test-install-link-ownership.sh`, `scripts/test-install-openclaw-registration.sh`, `scripts/test-install-parallel-logs.sh`, `scripts/test-install-selection-completeness.sh`, `scripts/test-install.sh`, `scripts/test-lint-fences.sh`, `scripts/test-runbook-contracts.py`; 0 frozen cases |
| `scripts/lint-agents.sh` | CLI/runtime entry | Agent Markdown paths or complete division roster. | Frontmatter/section diagnostics. | Read-only; noargs validates all agents. | `scripts/test-changed-agent-files.py`, `scripts/test-convert-frontmatter.sh`, `scripts/test-folded-frontmatter.sh`, `scripts/test-frontmatter-closing.sh`, `scripts/test-lint-fences.sh`, `scripts/test-lint-qwen-placeholders.sh`; 1 frozen cases |
| `scripts/list-changed-agent-files.py` | CLI/runtime entry | Newline paths on stdin and division registry. | Canonical agent paths on stdout. | Read-only. | `scripts/test-changed-agent-files.py`; 3 frozen cases |
| `scripts/marketplace-intake.py` | CLI/runtime entry | Normalized snapshot JSON, --at and thresholds. | HOLD packets with input/payload hashes. | Read-only, offline; no replay events, signing, model calls or payload echo. | `scripts/test-marketplace-intake.py`; 7 frozen cases |
| `scripts/nexus-anthropic.py` | CLI/runtime entry | Scoped execution packets / observe options. | Observation / execution records. | observe and execution invoke the Claude host, may spend and write records; help/errors only. | `scripts/test-nexus-anthropic.py`; 2 frozen cases |
| `scripts/nexus-blind.py` | CLI/runtime entry / protected | Trial artifacts, cases, salt and seed. | Blinded packet or deterministic submission ID. | seal writes a new review directory; submission-id is read-only. | `scripts/test-nexus-evaluation.py`, `scripts/test-nexus-review.py`, `scripts/test-nexus-trial.py`; 3 frozen cases |
| `scripts/nexus-brief.py` | CLI/runtime entry | Instance, events, explicit --at. | Owner brief JSON or Markdown. | Read-only; no owner decisions or acceptance. | `scripts/test-nexus-brief.py`; 4 frozen cases |
| `scripts/nexus-campaign.py` | CLI/runtime entry / protected | External held-out root, trials/judgments and policies. | Campaign status, planned work or throughput comparison. | Read-only; reads evaluator-controlled packs only for an authorized evaluation, not in these captures. | `scripts/test-nexus-campaign.py`; 2 frozen cases |
| `scripts/nexus-casepack.py` | CLI/runtime entry / protected | Pack directory / root and author/freeze metadata. | Validation, frozen hash, listing or scaffold. | new/freeze write pack files; validate/verify/list read. | `scripts/test-nexus-campaign.py`, `scripts/test-nexus-casepack.py`, `scripts/test-nexus-improve.py`, `scripts/test-nexus-trial.py`; 5 frozen cases |
| `scripts/nexus-improve.py` | CLI/runtime entry / protected | Git base/head, protected rules and external held-out evaluations. | PROPOSE/REJECT plus path/metric reasons. | Git reads and evaluation reads; no writes, model calls, PR creation or merge. | `scripts/test-nexus-improve.py`; 4 frozen cases |
| `scripts/nexus-instance.py` | CLI/runtime entry / protected | NEXUS schema v1 JSON, optional events/checkpoint, --at. | Validation, plan or replay JSON. | Offline; --output writes atomically. Default json.loads accepts duplicate keys. | `scripts/test-nexus-improve.py`, `scripts/test-nexus-instance.py`; 11 frozen cases |
| `scripts/nexus-lint.py` | CLI/runtime entry | Instance JSON and optional --strict. | Shape and warnings JSON. | Read-only; strict changes exit status for warnings. | `scripts/test-nexus-lint.py`; 4 frozen cases |
| `scripts/nexus-optimize.py` | CLI/runtime entry / protected | Agent, evidence, scope limit and executor. | Bounded candidate, patch, attempts and proposal JSON. | Default claude executor invokes host and spends; fake still writes artifacts. Help/errors only. | `scripts/test-nexus-optimize.py`; 2 frozen cases |
| `scripts/nexus-options.py` | CLI/runtime entry | Factors, admissibility, options and scenarios JSON. | Dominance/frontier comparison, never weighted score. | Read-only; no human decision is executed. | `scripts/test-nexus-evaluation.py`; 3 frozen cases |
| `scripts/nexus-pilot.py` | CLI/runtime entry | Instance, authority assertions, observations and events. | Execution records, replay state, acceptance events. | step can invoke a host; accept appends owner-supplied events; replay reads. Help/errors only in captures. | `scripts/test-nexus-pilot.py`; 2 frozen cases |
| `scripts/nexus-plan.py` | CLI/runtime entry | Objective, executor, draft/adoption and owner/time. | Draft instance and adoption verification. | draft defaults to host invocation; draft/adopt write files. Help/errors only. | `scripts/test-nexus-plan.py`; 2 frozen cases |
| `scripts/nexus-relay.py` | CLI/runtime entry | Relay subcommand and data-dir. | Delegates to nexus_relay.cli. | init/invite/serve/reconcile --apply write state; serve listens and may invoke containers/provider; help/errors only. | No direct reference found; 2 frozen cases |
| `scripts/nexus-review.py` | CLI/runtime entry / protected | Blinded index, packs, sheets and optional trials. | Reviewer kit / collected judgments. | Writes review directories or judgment JSON; no independent operator is authenticated by a label. | `scripts/test-nexus-review.py`; 2 frozen cases |
| `scripts/nexus-routing.py` | CLI/runtime entry | Instance, optional observations and --at. | Coverage and admissible target sets. | Read-only; does not invoke selected targets. | `scripts/test-nexus-routing.py`; 4 frozen cases |
| `scripts/nexus-trial.py` | CLI/runtime entry / protected | Frozen pack, variant, policy, owner events and executor. | Trial run state/artifacts and trial rows. | Default executor invokes host; fake writes synthetic fixtures; owner accept/resume modifies run state. | `scripts/test-nexus-campaign.py`, `scripts/test-nexus-improve.py`, `scripts/test-nexus-review.py`, `scripts/test-nexus-trial.py`; 2 frozen cases |
| `scripts/probe-host-claude-code.py` | CLI/runtime entry | Agent, policy, output, model and probe options. | Host acceptance record / optional raw stream. | Runs live Claude, installs temporary profile, writes probe files/records and restores installed profile; help/errors only. | No direct reference found; 2 frozen cases |
| `scripts/registry.py` | CLI/runtime entry | Canonical divisions/tools registry and selector. | Keys / field values in canonical order. | Read-only. | `scripts/test-cli-usage.sh`, `scripts/test-convert-fence-model.sh`, `scripts/test-convert-parallel-failure.sh`, `scripts/test-convert-slug-collisions.sh`, `scripts/test-convert-symlink-output.sh`, `scripts/test-incremental-conversion.py`, `scripts/test-install-all-path-collision.sh`, `scripts/test-install-continue-after-failure.sh`, `scripts/test-install-conversion-failure.sh`, `scripts/test-install-hermes-destination.sh`, `scripts/test-install-link-ownership.sh`, `scripts/test-install-openclaw-registration.sh`, `scripts/test-install-parallel-logs.sh`, `scripts/test-lint-fences.sh`; 7 frozen cases |
| `scripts/resolve-agents.py` | CLI/runtime entry | Agent/division/runbook selectors and optional list file. | Resolved adapter slugs or runbook list. | Read-only. | `scripts/test-install-functional.py`; 4 frozen cases |
| `scripts/test-agent-capabilities.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-agent-privileges.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-agent-selection.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-alpha-research-suite.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-changed-agent-files.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-cli-usage.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-convert-fence-model.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-convert-frontmatter.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-convert-outputs.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | `scripts/test-convert-fence-model.sh`; 0 frozen cases |
| `scripts/test-convert-parallel-failure.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-convert-slug-collisions.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-convert-symlink-output.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-folded-frontmatter.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-frontmatter-closing.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-hermes-plugin.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-host-acceptance.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-htp-gate0.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-incremental-conversion.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-all-path-collision.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-continue-after-failure.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-conversion-failure.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-functional.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-hermes-destination.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-link-ownership.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-openclaw-registration.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-parallel-logs.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install-selection-completeness.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-install.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-kimi-adapter.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-lint-fences.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-lint-qwen-placeholders.sh` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-marketplace-intake.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-anthropic.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-brief.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-campaign.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-casepack.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-evaluation.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-improve.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-instance.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | `scripts/test-nexus-improve.py`; 0 frozen cases |
| `scripts/test-nexus-lint.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-optimize.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-pilot.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-plan.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-review.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-routing.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-nexus-trial.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-openclaw-import-provenance.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-runbook-contracts.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/test-security-engagement.py` | test harness / protected | Synthetic test fixtures / configured property count; see source. | Test assertions, diagnostics and process status. | Harness may create/delete temporary fixtures, invoke CLIs or bind sockets; not an operational record. | No direct reference found; 0 frozen cases |
| `scripts/verify-release.sh` | CLI/runtime entry / protected | Working checkout and conversion test flags. | Release-gate logs / exit status. | Runs test/check suites, including temporary fixture conversions and Relay sockets. Stops at first failing command. | No direct reference found; 0 frozen cases |

### Direct script dependencies

Imports and filename references are extracted conservatively; dynamic/runtime dependencies may require inspection. Full imports and CLI declarations are in `inventory.json`.

- `relay/nexus_relay/auth.py` → `scripts/lib.sh`
- `relay/nexus_relay/config.py` → `relay/nexus_relay/policy.py`
- `relay/nexus_relay/evidence.py` → `scripts/lib.sh`
- `relay/nexus_relay/nexus.py` → `scripts/nexus-instance.py`
- `relay/nexus_relay/runner.py` → `relay/container/forwarder.py`, `scripts/build-catalog.py`, `scripts/lib.sh`
- `relay/nexus_relay/service.py` → `relay/nexus_relay/reconcile.py`
- `relay/nexus_relay/store.py` → `scripts/lib.sh`
- `relay/tests/test_properties.py` → `relay/nexus_relay/policy.py`, `relay/tests/test_relay.py`
- `relay/tests/test_relay.py` → `relay/nexus_relay/policy.py`, `relay/nexus_relay/reconcile.py`, `scripts/lib.sh`
- `scripts/agent-capabilities.py` → `scripts/check-agent-privileges.py`, `scripts/lib.sh`
- `scripts/benchmark-conversion.py` → `scripts/convert.sh`
- `scripts/build-catalog.py` → `scripts/lib.sh`, `scripts/lint-agents.sh`
- `scripts/build-hermes-plugin.py` → `relay/nexus_relay/__init__.py`, `scripts/check-divisions.sh`, `scripts/convert.sh`, `scripts/install.sh`
- `scripts/check-agent-originality.sh` → `scripts/check-divisions.sh`
- `scripts/check-agent-privileges.py` → `scripts/lib.sh`
- `scripts/check-challenger-pairs.py` → `scripts/build-catalog.py`
- `scripts/check-divisions.sh` → `scripts/convert.sh`, `scripts/lint-agents.sh`, `scripts/registry.py`
- `scripts/check-hermes-config-rewrite.py` → `scripts/install.sh`
- `scripts/check-hermes-config-rewrite.sh` → `scripts/check-hermes-config-rewrite.py`, `scripts/install.sh`
- `scripts/check-hermes-plugin.py` → `relay/nexus_relay/__init__.py`, `scripts/build-hermes-plugin.py`
- `scripts/check-htp-gate0.py` → `scripts/build-catalog.py`
- `scripts/check-runbooks.sh` → `scripts/build-catalog.py`
- `scripts/check-tools.sh` → `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/install.sh`, `scripts/registry.py`
- `scripts/convert-engine.sh` → `scripts/build-hermes-plugin.py`, `scripts/check-tools.sh`, `scripts/convert.sh`, `scripts/install.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/convert.sh` → `scripts/convert-engine.sh`, `scripts/integration-state.py`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/evaluate-nexus.py` → `relay/nexus_relay/nexus.py`
- `scripts/host-acceptance.py` → `relay/nexus_relay/evidence.py`, `scripts/agent-capabilities.py`, `scripts/host-session-evidence.py`, `scripts/lib.sh`
- `scripts/import-openclaw-community.py` → `scripts/lib.sh`
- `scripts/install.sh` → `relay/nexus_relay/__init__.py`, `scripts/check-tools.sh`, `scripts/convert.sh`, `scripts/integration-state.py`, `scripts/lib.sh`, `scripts/registry.py`, `scripts/resolve-agents.py`
- `scripts/integration-state.py` → `scripts/build-hermes-plugin.py`, `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/lib.sh` → `scripts/convert.sh`, `scripts/install.sh`
- `scripts/lint-agents.sh` → `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/marketplace-intake.py` → `scripts/lib.sh`
- `scripts/nexus-anthropic.py` → `scripts/agent-capabilities.py`, `scripts/lib.sh`, `scripts/nexus-instance.py`, `scripts/nexus-routing.py`
- `scripts/nexus-blind.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/lib.sh`
- `scripts/nexus-brief.py` → `scripts/nexus-instance.py`, `scripts/nexus-lint.py`
- `scripts/nexus-campaign.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/nexus-casepack.py`, `scripts/nexus-trial.py`
- `scripts/nexus-casepack.py` → `scripts/build-catalog.py`, `scripts/lib.sh`, `scripts/nexus-instance.py`
- `scripts/nexus-improve.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/nexus-campaign.py`, `scripts/nexus-casepack.py`
- `scripts/nexus-instance.py` → `scripts/build-catalog.py`, `scripts/lib.sh`, `scripts/nexus-options.py`
- `scripts/nexus-lint.py` → `scripts/nexus-instance.py`
- `scripts/nexus-optimize.py` → `scripts/build-catalog.py`, `scripts/lint-agents.sh`, `scripts/nexus-anthropic.py`, `scripts/nexus-casepack.py`, `scripts/nexus-improve.py`
- `scripts/nexus-pilot.py` → `scripts/lib.sh`, `scripts/nexus-anthropic.py`, `scripts/nexus-instance.py`, `scripts/nexus-routing.py`
- `scripts/nexus-plan.py` → `scripts/build-catalog.py`, `scripts/lib.sh`, `scripts/nexus-anthropic.py`, `scripts/nexus-instance.py`, `scripts/nexus-lint.py`
- `scripts/nexus-review.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/lib.sh`, `scripts/nexus-blind.py`, `scripts/nexus-casepack.py`
- `scripts/nexus-routing.py` → `scripts/nexus-options.py`
- `scripts/nexus-trial.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/lib.sh`, `scripts/nexus-anthropic.py`, `scripts/nexus-blind.py`, `scripts/nexus-brief.py`, `scripts/nexus-casepack.py`, `scripts/nexus-instance.py`
- `scripts/probe-host-claude-code.py` → `relay/nexus_relay/evidence.py`, `scripts/agent-capabilities.py`, `scripts/host-acceptance.py`, `scripts/host-session-evidence.py`, `scripts/lib.sh`
- `scripts/resolve-agents.py` → `scripts/build-catalog.py`
- `scripts/test-agent-capabilities.py` → `scripts/agent-capabilities.py`, `scripts/lib.sh`
- `scripts/test-agent-privileges.py` → `scripts/check-agent-privileges.py`
- `scripts/test-agent-selection.sh` → `scripts/install.sh`
- `scripts/test-changed-agent-files.py` → `scripts/lint-agents.sh`, `scripts/list-changed-agent-files.py`
- `scripts/test-cli-usage.sh` → `scripts/convert.sh`, `scripts/install.sh`, `scripts/registry.py`
- `scripts/test-convert-fence-model.sh` → `scripts/build-hermes-plugin.py`, `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/lib.sh`, `scripts/registry.py`, `scripts/test-convert-outputs.sh`
- `scripts/test-convert-frontmatter.sh` → `scripts/convert.sh`, `scripts/lib.sh`, `scripts/lint-agents.sh`
- `scripts/test-convert-outputs.sh` → `scripts/convert.sh`, `scripts/lib.sh`
- `scripts/test-convert-parallel-failure.sh` → `scripts/build-hermes-plugin.py`, `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/integration-state.py`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-convert-slug-collisions.sh` → `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-convert-symlink-output.sh` → `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-folded-frontmatter.sh` → `scripts/lint-agents.sh`
- `scripts/test-frontmatter-closing.sh` → `scripts/lint-agents.sh`
- `scripts/test-hermes-plugin.py` → `relay/nexus_relay/__init__.py`, `scripts/build-hermes-plugin.py`
- `scripts/test-host-acceptance.py` → `scripts/host-acceptance.py`, `scripts/lib.sh`
- `scripts/test-htp-gate0.py` → `scripts/check-htp-gate0.py`
- `scripts/test-incremental-conversion.py` → `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/integration-state.py`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-all-path-collision.sh` → `scripts/install.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-continue-after-failure.sh` → `scripts/install.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-conversion-failure.sh` → `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/install.sh`, `scripts/integration-state.py`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-functional.py` → `scripts/convert.sh`, `scripts/install.sh`, `scripts/resolve-agents.py`
- `scripts/test-install-hermes-destination.sh` → `relay/nexus_relay/__init__.py`, `scripts/install.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-link-ownership.sh` → `scripts/install.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-openclaw-registration.sh` → `scripts/install.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-parallel-logs.sh` → `scripts/install.sh`, `scripts/lib.sh`, `scripts/registry.py`
- `scripts/test-install-selection-completeness.sh` → `scripts/install.sh`, `scripts/lib.sh`
- `scripts/test-install.sh` → `scripts/install.sh`, `scripts/lib.sh`
- `scripts/test-kimi-adapter.py` → `scripts/convert.sh`, `scripts/install.sh`
- `scripts/test-lint-fences.sh` → `scripts/convert-engine.sh`, `scripts/convert.sh`, `scripts/integration-state.py`, `scripts/lib.sh`, `scripts/lint-agents.sh`, `scripts/registry.py`
- `scripts/test-lint-qwen-placeholders.sh` → `scripts/lint-agents.sh`
- `scripts/test-marketplace-intake.py` → `scripts/marketplace-intake.py`
- `scripts/test-nexus-anthropic.py` → `scripts/nexus-anthropic.py`
- `scripts/test-nexus-brief.py` → `scripts/nexus-brief.py`
- `scripts/test-nexus-campaign.py` → `scripts/nexus-campaign.py`, `scripts/nexus-casepack.py`, `scripts/nexus-trial.py`
- `scripts/test-nexus-casepack.py` → `scripts/nexus-casepack.py`
- `scripts/test-nexus-evaluation.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/nexus-blind.py`, `scripts/nexus-options.py`
- `scripts/test-nexus-improve.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/nexus-casepack.py`, `scripts/nexus-improve.py`, `scripts/nexus-instance.py`, `scripts/nexus-trial.py`, `scripts/test-nexus-instance.py`
- `scripts/test-nexus-instance.py` → `scripts/build-catalog.py`, `scripts/check-challenger-pairs.py`, `scripts/nexus-instance.py`
- `scripts/test-nexus-lint.py` → `scripts/nexus-lint.py`
- `scripts/test-nexus-optimize.py` → `scripts/nexus-optimize.py`
- `scripts/test-nexus-pilot.py` → `scripts/nexus-pilot.py`
- `scripts/test-nexus-plan.py` → `scripts/nexus-plan.py`
- `scripts/test-nexus-review.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/nexus-blind.py`, `scripts/nexus-review.py`, `scripts/nexus-trial.py`
- `scripts/test-nexus-routing.py` → `scripts/nexus-routing.py`
- `scripts/test-nexus-trial.py` → `relay/nexus_relay/nexus.py`, `scripts/evaluate-nexus.py`, `scripts/nexus-blind.py`, `scripts/nexus-casepack.py`, `scripts/nexus-trial.py`
- `scripts/test-openclaw-import-provenance.py` → `scripts/import-openclaw-community.py`
- `scripts/test-runbook-contracts.py` → `scripts/build-catalog.py`, `scripts/check-runbooks.sh`, `scripts/lib.sh`
- `scripts/test-security-engagement.py` → `scripts/check-security-engagement.py`
- `scripts/verify-release.sh` → `scripts/agent-capabilities.py`, `scripts/build-catalog.py`, `scripts/check-agent-privileges.py`, `scripts/check-challenger-pairs.py`, `scripts/check-hermes-plugin.py`, `scripts/check-htp-gate0.py`, `scripts/check-security-engagement.py`, `scripts/check-strategy-vocabulary.py`, `scripts/host-acceptance.py`, `scripts/install.sh`, `scripts/marketplace-intake.py`, `scripts/nexus-anthropic.py`, `scripts/nexus-brief.py`, `scripts/nexus-campaign.py`, `scripts/nexus-casepack.py`, `scripts/nexus-improve.py`, `scripts/nexus-instance.py`, `scripts/nexus-lint.py`, `scripts/nexus-optimize.py`, `scripts/nexus-pilot.py`, `scripts/nexus-plan.py`, `scripts/nexus-review.py`, `scripts/nexus-routing.py`, `scripts/nexus-trial.py`, `scripts/test-agent-capabilities.py`, `scripts/test-agent-privileges.py`, `scripts/test-agent-selection.sh`, `scripts/test-alpha-research-suite.py`, `scripts/test-changed-agent-files.py`, `scripts/test-convert-frontmatter.sh`, `scripts/test-convert-outputs.sh`, `scripts/test-hermes-plugin.py`, `scripts/test-host-acceptance.py`, `scripts/test-htp-gate0.py`, `scripts/test-incremental-conversion.py`, `scripts/test-install-functional.py`, `scripts/test-install.sh`, `scripts/test-kimi-adapter.py`, `scripts/test-marketplace-intake.py`, `scripts/test-nexus-anthropic.py`, `scripts/test-nexus-brief.py`, `scripts/test-nexus-campaign.py`, `scripts/test-nexus-casepack.py`, `scripts/test-nexus-evaluation.py`, `scripts/test-nexus-improve.py`, `scripts/test-nexus-instance.py`, `scripts/test-nexus-lint.py`, `scripts/test-nexus-optimize.py`, `scripts/test-nexus-pilot.py`, `scripts/test-nexus-plan.py`, `scripts/test-nexus-review.py`, `scripts/test-nexus-routing.py`, `scripts/test-nexus-trial.py`, `scripts/test-openclaw-import-provenance.py`, `scripts/test-runbook-contracts.py`, `scripts/test-security-engagement.py`

### Duplication and semantic differences

| Concern | Evidence | Compatibility consequence |
| --- | --- | --- |
| Timestamp parsing | `nexus-instance.py:58` (`when`), `nexus-routing.py:48`, `nexus-pilot.py:47`, `marketplace-intake.py:51`, `relay/nexus_relay/store.py:75`; also agent capabilities, evaluation and review | Timezone validation, replacement of Z, error text and conversion differ. Extract mechanically per legacy behavior before considering normalization. |
| Canonical JSON / hashing | `nexus-instance.py:32`, `nexus-casepack.py:65`, `marketplace-intake.py:70`, `nexus-pilot.py:227`, `relay/nexus_relay/store.py:79`, `relay/nexus_relay/evidence.py:94` | Distinguish bytes vs text, ensure_ascii, allow_nan, separators and domain separation. Equal function names do not establish byte equivalence. |
| Duplicate keys | `marketplace-intake.py:171,192`, `check-security-engagement.py:63,97,122`; default json.loads in `nexus-instance.py:674` | NEXUS legacy accepts duplicate schema_version (captured), marketplace rejects it (captured). A universal strict loader would change old behavior. YAML mapping rejection also exists separately. |
| Error privacy | `marketplace-intake.py:197` suppresses raw exception text; `nexus-instance.py:686`, routing/options/review include exception messages | Do not silently standardize errors during extraction; changed stderr is a behavior change. |
| Strict schema primitives | `nexus-instance.py:number/indexed/strings`, `marketplace-intake.py:exact_keys/integer/text`, Relay `config.py:_keys` | Strict bool/int behavior and exact-field policies differ. Preserve legacy boundaries. |
| Atomic writes / dynamic script loading | NEXUS instance/pilot/trial implement local temporary-write patterns; many NEXUS scripts use runpy/importlib against scripts/ | Moving a protected engine or changing __file__ resolution can alter both public imports and relative root lookup. Characterization must cover both paths. |

### Characterization exclusions and limits

- `scripts/verify-release.sh`, `scripts/test-*`, Relay test suites and Hermes config regression runners are verification harnesses, not stable product-output snapshots. Their measured runs are recorded in `BASELINE.md`. Optional user Hermes backups affect the regression case count.
- `scripts/lib.sh`, `scripts/host-session-evidence.py` and Relay library modules have no separate public executable CLI contract. Their callers and existing unit tests supply coverage.
- `relay/container/forwarder.py` requires mounted sockets; container E2E remains unmeasured because no Docker/Podman executable is installed.
- `scripts/i18n/localize-agents-zh.ps1`: PowerShell unavailable, so this Windows migration helper is inventoried but uncharacterized.
- `integrations/mcp-memory/setup.sh`: reads the presence of user configuration. It is inventoried; its environment-dependent guidance output is not frozen.
- Live execution paths in pilot/trial/optimizer/planner/provider/probe and stateful Relay commands have help/error snapshots only. Their existing fake-executor/unit tests are not proof of real host behavior.
- The new `foundation/` and `tests/` directories must be excluded from division discovery when they become tracked. The phase-0 patch adjusts only that unprotected infrastructure allowlist; the expected check output remains the baseline bytes.

No claim of complete behavioral coverage, independent review, successful release, learning quality or live execution follows from this inventory.
