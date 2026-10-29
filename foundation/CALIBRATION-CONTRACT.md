# Ante Foundation — Calibration diagnostics contract (additive proposal)

**Status:** implemented in `ante/learn/calibration.py` and wired into `ante learn calibrate`, on the owner's instruction of 29 October 2026. `ante/learn/**` and `tests/**` are outside what `ante develop` may change (`foundation/develop-policy.json`); this change was made outside that loop and lands only by the owner's merge. Passing tests describe the arithmetic, not scientific validation or authenticated approval. **Source alignment:** architectural mandate §6.2–6.4; *Marco Teórico General de la Estrategia* VIII (uncertainty, evidence and decision). This is repo-specific synthesis, not historical doctrine.

## Scope and invocation

```bash
python3 scripts/ante learn calibrate \
  --ledger path/to/decisions.jsonl \
  --at 2026-12-31T12:00:00Z \
  --policy path/to/preregistered-calibration-policy.json \
  --out /tmp/ante-calibration.json
```

`--policy` is optional for *exploratory diagnostics*. Without it, the original API remains available, Brier and its five-bin reliability curve remain, and Brier Skill Score is deliberately **null** (`NO_PREDECLARED_REFERENCE`). With it, the analysis uses the higher of the CLI `--min-sample` and the policy minimum; the policy minimum must be at least 30. In policy-controlled reports, the minimum must also be met by **distinct originating decisions**, preventing correlated expectations inside one decision from manufacturing sufficient sample size. A policy and its hash do **not** establish authenticated prior registration or authorize profile, routing or threshold updates.

Example policy, to be externally stored and fixed **before any forecast in the evaluation sample**:

```json
{
  "schema_version": 1,
  "policy_id": "runbook-x-2026-q4-v1",
  "minimum_sample": 30,
  "bin_edges": [0, 0.2, 0.4, 0.6, 0.8, 1.0],
  "baseline": {
    "kind": "fixed_probability",
    "probability": 0.5,
    "registered_at": "2026-09-30T00:00:00Z",
    "source": "external-immutable-reference-id-to-be-supplied-by-owner"
  }
}
```

The `0.5` value above is **illustrative, not a measured climatology or recommended baseline**. Choose the reference probability using an external, *earlier* population or an agreed naive forecasting method. For heterogeneous runbooks, one constant comparator can be a poor baseline; split evaluation into comparable predeclared domains rather than adapting the comparator to observed test outcomes. To omit BSS explicitly, set `"baseline": null`. Neither the reference ID nor its nominal timestamp is cryptographically authenticated by the implementation.

## Mathematics and outputs

For decisive, non-synthetic reconciliations only, `CONFIRMED` maps to 1 and `REFUTED` to 0. Forecast probability is the midpoint of the interval recorded in the immutable decision snapshot, not a model-inferred posterior. Events not yet observed, inconclusive observations and synthetic trials are excluded.

- **Brier:** mean of `(p-y)²`, with *no* assumption that its numerical value proves forecast skill.
- **Brier Skill Score:** `1 - BS_model/BS_reference`; only when `BS_reference > 0` and the reference's declared registration precedes every decision evaluated. Otherwise `null` with an explicit reason. The baseline is compared on the *same outcomes* but its probability is **fixed independently of them**.
- **Murphy identity:** `BS ≈ REL − RES + UNC` using groups formed by **exact forecast probabilities**, not coarse bins. The identity is checked to floating-point precision and its residual is reported. The decomposition is descriptive; if probabilities are nearly unique, individual groups provide little population-level calibration evidence. No statistical-significance inference follows from an exact identity.
- **ECE:** binary-event L1 calibration error computed with explicit, versioned policy bin edges (default five equal-width bins). The report also computes ten-width-bin and tie-preserving five-equal-mass alternatives and their range to expose binning sensitivity. ECE is not a formal test or guarantee against Goodhart.
- **Dependence:** records the number of distinct originating decisions. Correlated expectations from the same decision remain correlated; nominal row count is not an effective independent sample size. No confidence interval is manufactured without a justified clustered sampling model.

## Integrity and temporal constraints

`calibrate --at T` may inspect only ledger entries whose own recorded timestamps are at or before `T`. It reads and validates the full chain first; it does not permit outcomes reconciled *after* the evaluation time to leak into a retrospective analysis. The inclusion horizon and exact ledger head are recorded in output.

A policy's SHA-256 is a **receipt**, not a signature. A rewritten policy with a false earlier `registered_at` is not detectable without an independently held copy. A hash-chained local ledger is not an append-only WORM store against a privileged adversary capable of replacing the entire file. Outsourced attestation, reviewer identity, protected evaluation and real held-out independence remain separate governance gates.

All metrics are informational. Neither a positive BSS nor a low ECE auto-enters `ante develop`; no evaluator path or self-development policy is edited by this patch.

## Acceptance and falsification

Run the new tests and the repository's full gate in Python 3.11 before merge:

```bash
python3 -m unittest discover -s tests/foundation -p 'test_calibration_diagnostics.py' -v
python3 -m unittest discover -s tests/foundation -p 'test_calibration_integration.py' -v
python3 -m unittest discover -s tests/foundation -p 'test_*.py'
python3 tests/characterization/run.py
python3 -m unittest discover -s tests/characterization
bash scripts/verify-release.sh
```

Falsification cases include: Brier/Murphy algebra disagreement, BSS with zero denominator, late baseline, negative skill, insufficient sample, false independent sample size, sensitivity to bins, non-finite inputs, synthetic data inclusion and retroactive future-outcome leakage. Reject any PR that breaks frozen v1 characterization or the original return fields.
