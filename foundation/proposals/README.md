# Proposals awaiting the owner

Changes this branch prepared but must not make itself, because they touch
protected paths or settle a doctrinal conflict.

| File | Decision | What applying it does |
|---|---|---|
| `ci-wiring.patch` | D-017 | Adds the foundation checks and the published self-test to `scripts/verify-release.sh` and a job to `.github/workflows/check-runbooks.yml`. Apply with `git apply` in a commit labelled `protected:`. |
| `test-nexus-review-glob.patch` | D-020 | Fixes an order-dependent test in `scripts/test-nexus-review.py`: the kit root holds `REVIEWER.md` next to the reviewed artefacts, and `glob` order is filesystem order, so the "edited during review" test sometimes edited a file no sheet references and failed. The patch picks a reviewed artefact deterministically. Present at the base; seen failing once in CI on this stack. |

Who writes the `protected:` commit that applies either patch is open (D-020).
