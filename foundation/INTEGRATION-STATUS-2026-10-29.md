# Integration status addendum — 29 October 2026

## Current consolidation update

The owner subsequently requested **Netrunner Foundation**. The public repository
is now `bionic0x/netrunner-foundation`; its CLI remains `ante`. Main includes the
Foundation integration and D-020 (#12, #13, #15), the public entrypoint (#20) and
the later Foundation stack (#16–#19, #21), inspected at `039e88da3f51947235c3e5114cdf6df39a4ecb0a`.

The owner directly approved D-020 option C, P0–P3 and R1 in the task conversation,
and later explicitly delegated the P2 variant decision and branch consolidation.
That direct instruction supplies the narrow maintenance authorization recorded
in the updated D-020 packet. It is not independent identity verification and
is not a standing grant to the self-development loop. The v7.1.0 revision is
scoped and hashed separately; it must pass CI on its own candidate head.

[NETRUNNER-FOUNDATION.md](NETRUNNER-FOUNDATION.md) and its branch inventory are
the current consolidation record. The earlier inspection below is retained as
a dated snapshot; its “pending” observations have been superseded where stated.

## Earlier inspection


**Live integration target at inspection:** `bionic0x/neuromancers-foundation`, public, `main` at `ff16cbe6c7c77799c3f4fc2bce987c68c5b29699`. Original source: `bionic0x/Ante-agency-agents`, source commit `86addea22f6060f2c50e81c67c6dadf978ea3749` (historical baseline).

This is an addendum, not an alteration of dated historical decisions. The initial private-repository statement in `foundation/FORK.md`, phase-0 HOLD in `foundation/TASKS.md`, and statuses in the original D-020 packet are snapshots of the preparation they describe, **not authoritative current deployment status**.

## Observed GitHub state

- PR [#12](https://github.com/bionic0x/neuromancers-foundation/pull/12) — merged Foundation into main.
- PR [#13](https://github.com/bionic0x/neuromancers-foundation/pull/13) — merged D-020 and the protected CI/review changes into the Foundation branch. Its descriptive text and a maintainer comment report owner approval; this GitHub merge **does not itself authenticate independent approval**.
- PR [#14](https://github.com/bionic0x/neuromancers-foundation/pull/14) — closed, **not** merged; its proposals were integrated through the other line.
- PR [#15](https://github.com/bionic0x/neuromancers-foundation/pull/15) — merged 29 October 2026; final main merge commit above.
- Foundation CI job and four security jobs succeeded at that main commit in the inspection. The macOS installer matrix was still pending at last checked observation; success for the *entire* workflow matrix was not claimed.
- Later check the same day: all 14 check runs at `ff16cbe` concluded `success`, the macOS installer job (`macos-15-intel`) included, last one completed at 09:14 UTC.

## D-020 governance disposition (fact vs approval)

- **Implemented in Git tree:** protected policy wording, `check-runbooks.yml` Foundation job (including `fetch-depth: 0`), release-gate wiring and deterministic legacy-review test. The set of protected paths is unchanged in the sampled manifest.
- **Not established by code:** who independently authorized each final byte, whether the authorization covered the subsequent additional `fetch-depth` change, or the real capability of the designated independent operator to halt execution. PR prose contains reported owner approvals; do not elevate that record to independently authenticated identity evidence.
- **Ratification R1:** the merge of `7b213eb` is observable. A separate independently verifiable ratification record was not demonstrated in this inspection. Do not replace it with a fabricated one.
- The original packet remains a historical `PROPOSED` document. This addendum says what subsequently landed without rewriting source history or granting the self-development loop authority over protected files.

## Candidate change being prepared

The calibration enhancements and README corrections in this delivery were prepared as **local candidate changes**. Status at publication: the calibration module, its tests and its contract are applied in [PR #16](https://github.com/bionic0x/neuromancers-foundation/pull/16) (open, owner merge pending); the README corrections and this addendum are the documentation pull request that adds this file. They avoid `.github/**`, `strategy/overdrive-protected.json`, `strategy/NEXUS-OVERDRIVE.md`, `scripts/verify-release.sh`, `scripts/test-*.py` and `strategy/contracts.json`. **However, statistics changes do touch protected paths under `foundation/develop-policy.json`: `ante/learn/**` and `tests/**`.** They must be reviewed and explicitly authorized by the owner as a separate maintenance patch; the `ante develop` loop cannot propose or apply them.

**Unresolved:** align `setup-python` v7.0.0 in the Foundation job with v7.1.0 only through a separately scoped, human-authorized protected PR pinned to exact hashes; do not alter it in a documentation/statistics PR.

**Decision boundary:** a working statistical module and green offline tests do not demonstrate empirical live-model improvement, independent held-out validation, authenticated governance or permission to merge unreviewed changes.
