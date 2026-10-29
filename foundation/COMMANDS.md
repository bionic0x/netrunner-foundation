# `ante` strategy commands

`python3 scripts/ante <command> INPUT [--at ISO8601] [--from ARTEFACT ...] [--out DIR]`
(or `python3 -m ante`). Offline and deterministic: the same input and `--at`
produce the same bytes. Exit 0 artefact produced (any verdict, `HOLD` included),
2 invalid input or doctrinal rejection, 3 broken lineage.

Every input carries `claims` (`{id, text, status, source: {ref, origin}, date, limit}`),
and an optional `at`. Review commands also carry `independence_level`
(`SELF` · `SEPARATED_CONTEXT` · `INDEPENDENT_OPERATOR`). Each command module's
docstring is its full input specification.

| Command | Marco | Needs (`--from`) | Refuses |
|---|---|---|---|
| `frame` | XIII F1, I | — | objective without an observable condition (pathology 2) |
| `map` | XIII F2, II | frame | actor whose preference, representation and capacity are one statement |
| `cause` | XIII F3, I.3 | frame | chain without a rival or an observable refutation |
| `focus` | XIII F4, III | map | centre without substitution or horizon; concept confusion (pathology 4) |
| `options` | XIII F5, App. B | cause | one viable option plus decoys; no continuity baseline; same mechanism; scores |
| `react` | XIII F6, VI, IX | options | no competent opposition, no unexpected cooperation, no third-party shift |
| `street` | VIII.12, VI | frame (+ map) | instrument without a misuse scenario; scenario without its Goodhart variant (regressional, extremal, causal, adversarial); metric with no adversarial scenario; manipulation indicator that is the instrument itself; unknown actor. Variants a metric leaves unconsidered are reported. `cohere` records the interactive test as `CONDITIONAL` (pending evidence) while any plan metric lacks this analysis |
| `ach` | VIII.4 | frame | incomplete matrix; reports source groups, self-produced evidence, sensitivity |
| `watch` | XIII F7, VI.9 | options | indicator without a response; no pause or terminate threshold |
| `close` | XII, XIII F8 | frame | placeholder clauses; one clause pasted into several |
| `cohere` | XIV | frame | FAIL not fatal; `NOT_APPLICABLE` on Epistemic or Exit; unanswered test |
| `pathology` | XV | frame | unswept pathology; detection without false-positive check; culmination conflated with inversion or escalation |
| `nodal` | VIII.5 | frame (+ every artefact to examine) | reports load-bearing claims; one still `ASSUMPTION` or `ATTRIBUTED_INTENT` that must be corroborated blocks `PROCEED` in `decide` |
| `decide` | SDR | frame, cohere, pathology (+ close to activate) | verdict outside what `cohere` admits; `PROCEED` without `nodal` or with a blocking claim not accepted as a named risk, without independent review, with a detected pathology, without close or expectations |
| `selftest` | VIII.13 | — | `PASS` without evidence or dated in the future |

`ante run RUNBOOK --artifacts DIR` checks that a case directory holds the chain
the runbook declares (`strategy_commands` in `strategy/runbooks.json`), intact, of
one case, under the canonical doctrine. It executes nothing.

`--draft-with PROVIDER --model ID` writes an unsigned `<command>.draft.json` from a
brief; see `ante/strategy/draft.py`.

## Learning

| Command | What it does | What it refuses |
|---|---|---|
| `learn record DECIDE --ledger L --at T` | appends a sealed `decide` artefact, frozen, to a hash-chained ledger | anything but `decide`; a second record; a record dated before the decision |
| `learn reconcile OBS --ledger L --at T` | appends observed outcomes (`CONFIRMED`, `REFUTED`, `INCONCLUSIVE`, `NOT_YET_OBSERVABLE`) as new entries | system-produced sources confirming or refuting; observations before the decision or in the future; `NOT_YET_OBSERVABLE` after the horizon |
| `learn calibrate --ledger L --at T [--policy FILE]` | Brier and reliability by runbook, agent and claim kind, with Murphy decomposition on exact forecast groups, ECE and its binning sensitivity, distinct decisions; Brier skill only against a baseline declared in a policy dated before every evaluated decision (`foundation/CALIBRATION-CONTRACT.md`) | groups below the effective minimum answer `INSUFFICIENT_SAMPLE`, with no number; a policy floor is at least 30 distinct decisions and is not externally authenticated; `--at` is a cutoff |
| `learn patterns --ledger L --at T` | proposes differences in refutation rate that survive a permutation test with Bonferroni correction | patterns that only system-sourced evidence supports; synthetic decisions |
| `learn verify --ledger L` | checks the chain | — (a broken chain exits 3) |
| `learn review --ledger L --by NAME --reason TEXT --at T` | records a model review; resets cumulative drift | — |
| `jackpot --ledger L --at T [--state S] [--events E]` | cumulative drift: refutations, inconclusive outcomes, accepted risks, decide warnings, gate holds and rejects, release events; plus a one-sided CUSUM on the Brier error of each reconciled prediction since the last review (reference of 30, k = 0.5σ, h = 5σ, or `INSUFFICIENT_SAMPLE`); exit 1 when a model review is due | while a review is due, `learn record` refuses decisions that add accepted risks |

## Self-development

| Command | What it does |
|---|---|
| `develop propose SPEC --patch P --base REF` | registers one bounded change with its findings, hypothesis, pre-registered metric, kill criterion, cost ceiling, scope and autonomy delta; refuses protected or out-of-scope paths, a second open proposal, spend beyond the campaign, a stopped loop |
| `develop gate ID --patch P [held-out evidence] [--selftest-register R] [--independent-review F]` | applies the patch at the base and runs the base evaluator: Overdrive paths, develop policy, characterization, self-test, held-out Pareto comparison, Turing lock; answers `PROPOSE`, `HOLD` or `REJECT` |
| `develop pr ID [--execute]` | after a `PROPOSE`, prints (or with `--execute` runs) the push and `gh pr create --draft`; once per proposal |
| `develop resume --by NAME --reason TEXT` | a named human restarts a loop stopped after two consecutive held-out regressions or halted by a held-out canary |
| `develop close ID --outcome merged\|rejected\|withdrawn` | frees the open-proposal slot |
| `develop status` | proposals, gates and committed spend |

Every `develop` command takes `--state FILE` (a hash-chained log, anchored in
`refs/ante/develop-state` so it cannot be swapped or truncated) and, except
`status`, `--at`. Decisions D-013 and D-014 describe the policy and the lock.

## Shadow trials, drift and defences

| Command | What it does |
|---|---|
| `stub record SPEC --log S --ledger L --at T` | records a candidate's recommendation for a real decision in a separate shadow log; refused once the decision has outcomes |
| `stub compare --log S --ledger L --at T` | compares shadow and real forecasts on reconciled expectations only; `INSUFFICIENT_HISTORY` below 30; eligibility permits an `ante develop` proposal, never an adoption |
| `stub status --log S` | counts only; recommendations stay hidden until reconciled |
| `constructs list\|verify` | frozen reviewer profiles and their pinned hashes |
| `ice seed PACK --registry R` / `ice scan PATH...` / `ice layers` | canaries in held-out packs; contamination scan; independence of the five defensive layers. A canary found by `develop propose` or `gate` rejects the change and halts the loop until `develop resume` |
| `ghosts --artifacts DIR --at T [--regimes R]` | expired claims, or claims dated before a declared regime change, that live artefacts still cite; exit 1 until renewed or withdrawn |
| `learn box build\|recombine` | archive of discarded options, rejected hypotheses, refuted expectations and rejected proposals with their reasons; recombined items come back as `HYPOTHESIS` with `origin: system` |
| `signals add\|export --register R --at T` | weak-signal register (first observation, where, provenance); exported as `HYPOTHESIS` claims for `frame` or `react`, without probabilities |
| `deck --artifacts DIR [--ledger L] [--log S] [--plain]` | read-only terminal view: chain, epistemic states, nodal load, defence layers, shadow trials, drift |

## Signatures (offline; never authorise anything)

| Command | What it does |
|---|---|
| `attest receipt ARTEFACT --at T` | unsigned execution receipt: the artefact's sealed digest, the commit, the `ante/` tree object and the committed `strategy/contracts.json`; refused with uncommitted code or policy |
| `attest approval --base B --head H --scope apply --review-ref R --author A --at T` | unsigned D-020 approval of the exact change from B to H: result tree, changed paths with blob ids, patch hash |
| `attest key PUBLIC.pem --principal P --principal-type human` | trust-store entry for an Ed25519 public key; pinning it is a D-020 change |
| `sign DOCUMENT --key KEY.pem --method M --at T [--head H]` | adds an `eddsa-jcs-2022` proof after re-deriving the document from the checkout (`--head` for approvals) and showing it; runs only as a separate signing account that owns an encrypted key outside the checkout, mode 600; the passphrase is typed at the terminal |
| `verify SIGNED [--trust F] [--repo D] [--artefact A] [--head H]` | read-only check against the keys pinned at HEAD (or a named store) and, with `--repo`, against git; approvals need `--repo` and `--head`; exit 0 verified, 4 not verified, with a reason |

`foundation/ATTEST.md` has the schemas, the trust model and the threat table.
