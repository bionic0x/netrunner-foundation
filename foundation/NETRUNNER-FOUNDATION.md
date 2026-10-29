# Netrunner Foundation consolidation — 29 October 2026

Canonical repository: **[bionic0x/netrunner-foundation](https://github.com/bionic0x/netrunner-foundation)**.
Canonical integration branch: **`main`**. Source inspected for this consolidation:
`039e88da3f51947235c3e5114cdf6df39a4ecb0a`. The owner requested the new name and consolidation of the branches.
The repository has been renamed; Git history, upstream attribution and MIT
license are retained. The installed package and CLI stay `ante` for compatibility.

## Mandate and implementation boundary

The attached “Ante Foundation” mandate governs the architecture under the new
project name. Its SHA-256 is `358774e4d71028c212e3eb10a7a68e57a18fd206e686c1a638b882945821c35e`;
the supplied Marco's SHA-256 is `98f86e611cc89f04ec871f27d72339bc8671955d1a97ef1074f85fbbdd5412a1`.
The mandate's phase structure remains: characterization before extraction,
shared core, strategy, evidence-based learning, bounded self-development,
defence layers and documentation. [INVARIANTS.md](INVARIANTS.md),
[MIGRATION.md](MIGRATION.md) and [COMMANDS.md](COMMANDS.md) map those requirements
to the current implementation. No live-model improvement or independent
operator validation follows from passing these offline checks.

The owner's explicit D-020 exception permits only the approved maintenance
patches outside the self-development loop. It does not make agent code
handwritten, authenticate a review label, grant standing maintenance authority,
or let `ante develop` edit its evaluator. R1 ratifies retaining `7b213eb` with
its original provenance. D-018 separately authorized two invocation rebaselines
in each characterization corpus; this consolidation changes no frozen output.

## Active Foundation branches

| Work | Disposition |
|---|---|
| Phase stack #3–#11 | Consolidated through #12 into `main`. |
| #12 / D-018 | Merged as `b374ce5`; only the two approved invocations were rebaselined. |
| #13 / D-020 | Merged into the Foundation base as `f3adcc4`. |
| #15 | Carries #13 to `main` as `ff16cbe`; eight hosted workflow groups succeeded on its source commit. |
| #14 | Closed without merge; its full-history and v7.1.0 wiring is the reference for the bounded P2 revision. |
| #16–#19 and #21 | Subsequent calibration, canary halt, Goodhart and CUSUM work is already on the inspected `main` and is preserved. |
| #20 | Public entrypoint documentation is on `main`; its current identity is updated here. |
| Consolidation candidate | Updates the one remaining Foundation action pin to v7.1.0, records accepted D-020/R1, and applies the Netrunner identity. |

P2 keeps `fetch-depth: 0`: the raw-byte harness needs the historical `86addea`
commit. Its final one-line delta and the complete revised wiring reference are
both hashed in [the approval receipt](proposals/d020-approval-packet.json).
The original patches remain available as historical provenance.

## Complete branch inventory

[branch-consolidation.json](evidence/branch-consolidation.json) pins all
**87 remote branch tips** observed at the snapshot. Of these,
**68 are ancestors of the canonical main**. Three Foundation tips are superseded
references. Sixteen older non-Foundation tips remain historical references with
commits not reachable from main; this record does not claim they were merged.
No branch is deleted, reset or force-pushed. New development should branch from
current `main`; old tips are preserved for traceability and selective future
reconciliation rather than silently reintroduced into the validated code tree.

| Retained non-ancestor reference | Tip | Commits outside main |
|---|---|---:|
| `arch/registry-driven-tools-ci-hardening` | `4246fcbf181a7c710848d020c09d0517719a7b36` | 13 |
| `docs/sync-operating-metadata` | `15813df192350d708c0d422bf3ad22578a803c15` | 3 |
| `doctrine/complete-termination-contracts` | `426fe8fd9585969a450314d3017814243007230f` | 8 |
| `feat/challenger-veto` | `49c37b596b932e84b88acedea5cc910b9725db0a` | 1 |
| `feat/doctrine-alignment` | `5ba3f9c3c87a51b8c3aaea327cdb499d3e610b78` | 1 |
| `feat/mispriced-cmo-hardening` | `efa53ab5428c7f7a432184218a77645ec0009a10` | 4 |
| `feat/solana-program-engineer` | `3b23356e92794476ebdfcc871d89919ec86f569a` | 23 |
| `fix/functional-installation` | `cedb2a0804eb3007b95fd424e2ed9248e93ec116` | 1 |
| `fix/nexus-review-artifact-selection` | `e20147a47e4d495a3eab3f2ff228b1093c3096db` | 1 |
| `fix/relay-audit` | `860a48c55aac078c81a27119f88b6ae32730461f` | 5 |
| `fix/review-provenance-and-ci` | `d567d82669faf3328e2ee295653fcb1d11e314da` | 1 |
| `foundation/claude/ice-halt` | `2baeae7978c302c7f6c0f2609b8ba16e12e30c14` | 1 |
| `foundation/claude/protected-wiring` | `da5aa0bc398f2c21c074932a1a553391383cd99f` | 4 |
| `foundation/phase-0` | `4cfb22840caf57e2cd0f7277a6ac5ce8aae730b4` | 1 |
| `overdrive/planner-agent` | `621af9d63e8c7cb34fd33ca2749a21758a26f21f` | 1 |
| `perf/benchmark-canonical-agent-loading` | `8ec5fc76af126f45a36c5e824264142afed6aa7b` | 12 |
| `perf/reduce-conversion-overhead` | `40b4338926eb4099edfbb94284d0629ceaefa16a` | 2 |
| `security/privilege-provenance-hardening` | `4a3086baabadaa792bec73ca57bf79949189efbe` | 1 |
| `strategic-overhaul-v2` | `314cba94399b9078f54601a1962fb10540757485` | 23 |

## Validation and limits

Fresh Python 3.11 checks cover the consolidation tree: Foundation unit tests,
both characterization runners, mechanical extraction, frozen reviewers,
defence-layer independence, division/runbook contracts and workflow YAML.
Results are retained in `evidence/netrunner-validation.json`.
Hosted checks must cover the final PR head; an earlier green source commit is
not a substitute. Full release is not claimed locally: this environment denies
Unix socket creation required by Relay. Tests are not skipped or weakened.

A final reviewer receives only the diff, mandate and test results. Its level is
`SEPARATED_CONTEXT`, not `INDEPENDENT_OPERATOR`; actual operator independence,
live-model superiority and institutional self-test evidence remain unestablished.
