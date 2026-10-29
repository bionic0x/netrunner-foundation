# Baseline at the base commit

Recorded before any code moved. Every later phase is compared with this state.

| Item | Value |
|---|---|
| Repository | `bionic0x/Ante-agency-agents` |
| Commit | `86addea` — merge of PR #62 (`feat/act-marketplace-intake`), `main` on 28 Oct 2026 |
| Interpreter | CPython 3.11.18 in a virtual environment |
| Dependencies | `.github/requirements/validation.txt` installed with `--require-hashes` (PyYAML 6.0.3); `relay/tests/requirements-property.txt` for the property run |
| Date of run | 28 Oct 2026 (Europe/Madrid) |

## Release gate — `scripts/verify-release.sh`

**Result: `PASSED: complete release gate`, exit 0, 16 min 20 s wall time.**

| Component | Measured result |
|---|---|
| Python `unittest` suites run by the gate | 430 tests across all suites, all OK; 1 module skipped (see relay) |
| Agent lint | 506 files, 0 errors, 14 warnings |
| Divisions | 19 consistent across `divisions.json`, discovery, directories and CI |
| Tools | 17 validated from `tools.json`, 15 converted, 2 source/identity |
| Runbooks | 9 runbooks, 134 slug references, 28 required artefacts, 9/9 termination contracts structurally valid |
| Catalog | `CATALOG.md` current — 506 agents, 9 runbooks |
| Security engagement | 22/22 security agents pass |
| Conversion outputs | 32 passed, 0 failed (506 roster agents × 15 tools) |
| Installer and converter regressions | all shell suites PASS |

## NEXUS Relay — `relay/tests`

| Run | Result |
|---|---|
| Inside the gate (no `hypothesis`) | 122 tests OK, `test_properties` skipped: *hypothesis is not installed* |
| With `relay/tests/requirements-property.txt` | 131 tests OK, 0 skipped |

## Characterization — `tests/characterization`

| Item | Value |
|---|---|
| Cases | 114 (31 `--help`, 20 usage errors, 63 behavioural cases on repository fixtures) |
| Stability | every case executed twice before recording; 0 unstable |
| Replay against the recordings | 114/114 match |

## Not measured

| Item | Reason |
|---|---|
| `.github/workflows/security.yml` (gitleaks, zizmor, semgrep, osv-scanner) | Runs on GitHub; not reproduced locally. The PR's own CI run is the measurement. |
| Live-host behaviour of `nexus-anthropic`, `nexus-trial`, `nexus-plan draft`, `nexus-optimize`, `probe-host-claude-code` | Requires the `claude` CLI and credentials; characterised through help and usage errors only. |
| macOS installer run | CI-only. |

The 14 lint warnings and the stale counts in `UNIFIED_AGENCY_BUILD_INFO.json`
(8 runbooks there, 9 in the tree) exist at the base commit and are left as they are.

---

## Codex line — `foundation/phase-0` (raw-byte harness)

Recorded independently on `foundation/phase-0` (head `b60af82`) and kept verbatim below, headings one level down. Its baseline was measured by another operator in another environment (Python 3.12/3.11.17, Unix sockets denied), so its release-gate result differs from the one above; both are kept as measured.

## Foundation baseline — 28 October 2026

**Exit: HOLD.** The baseline is recorded, but the phase-0 exit is not satisfied.
The complete release gate stops at Relay in this environment. No extraction,
learning loop, self-development loop or Gibson mechanism is implemented here.

Pinned source: `bionic0x/Ante-agency-agents` at
`86addea22f6060f2c50e81c67c6dadf978ea3749` (the supplied base). All baseline
runs completed before this branch changed any production file. `LICENSE`,
upstream copyright, `THIRD_PARTY_NOTICES.md` and protected paths stay unchanged.

| Execution on original checkout | Runtime | Exit | Observed result |
| --- | --- | --- | --- |
| `bash scripts/verify-release.sh` | Python 3.12.14, supplied runtime | 1 | Reaches Relay: 122 tests, 24 errors, 1 skip (Hypothesis unavailable). |
| `python3 -m unittest discover -s relay/tests -v` | Python 3.12.14 | 1 | 122 tests, 25 errors, 1 skip. Initial diagnostic run; not the target runtime. |
| `bash scripts/verify-release.sh` | CPython 3.11.17 | 1 | Reaches Relay: 131 tests, 24 errors, no skips. `RELAY_REQUIRE_HYPOTHESIS=1`, `RELAY_PROPERTY_EXAMPLES=1000`. |
| `python3 -m unittest discover -s relay/tests -v` | CPython 3.11.17 | 1 | 131 tests in 60.360s; 24 errors, no skips, with the same property settings. |
| Frozen CLI characterization on original source | CPython 3.11.17 | 0 | 116 subprocess cases, 43 entry points; one unittest containing named subtests, 10.216s. |
| Final phase-0 patch validation | CPython 3.11.17 | 0 | 116 frozen cases, 2 directory regressions and 1 timeout regression; four unittest methods, 9.562s. |

The 24 errors in the target-runtime Relay suite all report
`PermissionError: [Errno 1] Operation not permitted` at Unix-socket creation.
This identifies an execution-environment limitation; it does not establish that
all socket/container behaviors work. The initial 3.12 diagnostic also encountered
`FileNotFoundError` for a temporary Markdown path during `test_events_file_is_private`
in the engine's `collect()` call. Its cause was not established. Raw
stdout and stderr are retained in `evidence/`; logs include upstream synthetic
test outputs, never observations of real decisions or genuine learned outcomes.

The release script uses `set -e`, so steps after its Relay stage **did not run**
in either complete-gate attempt. Passing checks before that point include the
catalog, vocabulary, runbooks, NEXUS instance/routing, marketplace intake,
execution-adapter/pilot fakes, evaluation/casepack/trial/improvement/campaign and
planning/optimization unit suites. No overall release PASS follows from them.

During harness hardening, the new fixture-inventory guard rejected an orphaned
empty output file left by an incomplete cleanup. That failed attempt is retained
as `phase0-orphan-guard.*.log`. Both unreferenced files were removed, every frozen
stream in the manifest stayed unchanged, and the final four-method suite passed.

### Reproduction in the target runtime

Use Python 3.11 in a host that permits local Unix sockets. Dependencies used here
are the repository's existing locked versions: PyYAML 6.0.3, Hypothesis 6.168.3
and sortedcontainers 2.4.0. No application dependency or lock file changed.

```bash
python3 -m pip install --require-hashes --no-deps \
  -r .github/requirements/validation.txt -r relay/tests/requirements-property.txt
RELAY_REQUIRE_HYPOTHESIS=1 RELAY_PROPERTY_EXAMPLES=1000 bash scripts/verify-release.sh
RELAY_REQUIRE_HYPOTHESIS=1 RELAY_PROPERTY_EXAMPLES=1000 \
  python3 -m unittest discover -s relay/tests -v
python3 -m unittest discover -s tests/characterization -v
```

No tests were suppressed or rewritten to make this environment green. No
privilege/sandbox escalation was attempted. Docker and Podman are unavailable;
the container escape probe was not executed. PowerShell is unavailable.

### Existing GitHub Actions evidence — separate from this execution

The repository API reports successful **push** runs for this exact base commit
for Relay, runbooks, divisions, Hermes rewrite, tools, installer, lint and
security. They are historical remote results, observed during this session; they
are **not** a new run of the complete release script or validation of this patch.
The separate dependency-update run for opentelemetry-api failed. See
`evidence/base-workflows.json` for all returned run IDs, status, scope and URLs.

- [Existing Relay run](https://github.com/bionic0x/Ante-agency-agents/actions/runs/40654933444)
- [Existing security run](https://github.com/bionic0x/Ante-agency-agents/actions/runs/40654933409)
- [Existing runbook run](https://github.com/bionic0x/Ante-agency-agents/actions/runs/40654933471)

The existing `GHSA-xcq7-p3pf-p88h` exception expires on 2027-01-31 in the checked-in
policy. That policy and all security workflows remain unchanged. Security tools
were not rerun locally; their current-patch result is `null` with that reason.

### Unmeasured values and independence

`evidence/results.json` records nulls and reasons for unmeasured checks, including
container isolation, current-patch hosted CI/security, operational improvement,
learning/calibration quality and full behavioral coverage. No synthetic outcomes
are added to a real ledger. No private held-out materials were read.

Baseline/characterization are `SELF`. A separate clean-context agent review is
`SEPARATED_CONTEXT` if recorded in `REVIEW.md`; it cannot stand in for an
independent operator with authority to pause. No authority is created by these
reports, labels or successful parsings.

### Separate Claude execution reported during delivery

The user supplied a phase-0 report for local commit `5e74ff3`. Its checked-in
`foundation/BASELINE.md` was subsequently read from
`bionic0x/Ante-agency-agents` at that ref. It records CPython 3.11.18, complete
release exit 0 (430 unittest tests, one Hypothesis module skipped; 32/32
conversions), a separate Relay run with Hypothesis (131 tests, zero skips), and
114 stable characterization cases. These are that execution's reported results,
not reruns or independent measurements by this operator. The raw logs were not
inspected. The 114-case corpus and this PR's 116-case corpus remain distinct.

A fresh Unix-socket probe in this environment still returns
`PermissionError: [Errno 1] Operation not permitted`. It does not invalidate the
other environment's reported result and does not make this patch's gate green.
