"""Auditable binary-forecast diagnostics for Ante Foundation.

Pure reporting code: no I/O, model calls, credentials or policy mutation.
Exact-forecast Murphy identity and binned ECE are intentionally distinct.
No result is a claim of independent validation or causal improvement.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from bisect import bisect_right
import json
import math

DEFAULT_EDGES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
POLICY_SCHEMA_VERSION = 1


class CalibrationError(ValueError):
    pass


def _probability(value, name: str) -> float:
    if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
        raise CalibrationError(f'{name}: finite probability in [0, 1] required')
    return float(value)


def _timestamp(value, name: str) -> datetime:
    if not isinstance(value, str):
        raise CalibrationError(f'{name}: offset-aware ISO-8601 timestamp required')
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise CalibrationError(f'{name}: invalid ISO-8601 timestamp') from None
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise CalibrationError(f'{name}: timezone offset required')
    return dt.astimezone(timezone.utc)


def _edges(value) -> tuple[float, ...]:
    if not isinstance(value, list) or not 3 <= len(value) <= 31:
        raise CalibrationError('bin_edges: provide 3–31 boundaries')
    edges = tuple(_probability(x, 'bin_edges') for x in value)
    if edges[0] != 0 or edges[-1] != 1 or any(a >= b for a, b in zip(edges, edges[1:])):
        raise CalibrationError('bin_edges: must increase strictly from 0 to 1')
    return edges


def parse_policy(doc: dict) -> dict:
    """Validate a versioned analysis policy (self-declared, not authenticated)."""
    if not isinstance(doc, dict) or set(doc) != {
            'schema_version', 'policy_id', 'minimum_sample', 'bin_edges', 'baseline'}:
        raise CalibrationError('calibration policy: exact fields schema_version, policy_id, '
                               'minimum_sample, bin_edges, baseline required')
    if type(doc['schema_version']) is not int or doc['schema_version'] != POLICY_SCHEMA_VERSION:
        raise CalibrationError('calibration policy: unsupported schema_version')
    if not isinstance(doc['policy_id'], str) or not doc['policy_id'].strip():
        raise CalibrationError('policy_id: non-empty text required')
    floor = doc['minimum_sample']
    if type(floor) is not int or floor < 30:
        raise CalibrationError('minimum_sample: policy floor must be at least 30')
    edges = _edges(doc['bin_edges'])
    baseline = doc['baseline']
    if baseline is not None:
        if not isinstance(baseline, dict) or set(baseline) != {
                'kind', 'probability', 'registered_at', 'source'}:
            raise CalibrationError('baseline: exact fields kind, probability, registered_at, source required')
        if baseline['kind'] != 'fixed_probability':
            raise CalibrationError('baseline.kind: only fixed_probability supported')
        _probability(baseline['probability'], 'baseline.probability')
        _timestamp(baseline['registered_at'], 'baseline.registered_at')
        if not isinstance(baseline['source'], str) or not baseline['source'].strip():
            raise CalibrationError('baseline.source: source reference required')
    # A digest detects later changed bytes in a receipt; it is not a signature or proof of preregistration.
    canonical = json.dumps(doc, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return {
        'document': doc, 'sha256': sha256(canonical.encode('utf-8')).hexdigest(),
        'policy_id': doc['policy_id'], 'minimum_sample': floor,
        'bin_edges': edges, 'baseline': baseline,
    }


def policy_receipt(policy: dict | None) -> dict | None:
    if policy is None:
        return None
    return {'id': policy['policy_id'], 'sha256': policy['sha256'],
            'minimum_sample': policy['minimum_sample'],
            'bin_edges': list(policy['bin_edges']),
            'attestation': 'NOT_AUTHENTICATED',
            'note': 'File hash and dates are self-declared; verify original preregistration out-of-band.'}


def _ece(rows: list[dict], edges: tuple[float, ...]) -> tuple[float, list[dict]]:
    buckets: list[list[dict]] = [[] for _ in range(len(edges) - 1)]
    for row in rows:
        idx = min(bisect_right(edges, row['p']) - 1, len(buckets) - 1)
        buckets[idx].append(row)
    detail = []
    for i, members in enumerate(buckets):
        count = len(members)
        pbar = math.fsum(x['p'] for x in members) / count if count else None
        obar = math.fsum(x['o'] for x in members) / count if count else None
        detail.append({'edges': [edges[i], edges[i + 1]], 'n': count,
                       'mean_forecast': pbar, 'observed_rate': obar})
    return math.fsum((len(rows_in_bin) / len(rows)) *
                     abs(row['mean_forecast'] - row['observed_rate'])
                     for rows_in_bin, row in zip(buckets, detail) if rows_in_bin), detail


def _ece_equal_mass_tie_safe(rows: list[dict], target_bins: int = 5) -> float:
    """Quantile sensitivity check, preserving identical probabilities as one group."""
    groups: dict[float, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row['p']].append(row)
    buckets: list[list[dict]] = []
    current: list[dict] = []
    threshold = len(rows) / target_bins
    for _, group in sorted(groups.items()):
        if current and len(buckets) < target_bins - 1 and len(current) >= threshold:
            buckets.append(current)
            current = []
        current.extend(group)
    if current:
        buckets.append(current)
    return math.fsum(len(members) / len(rows) *
                     abs(math.fsum(x['p'] - x['o'] for x in members) / len(members))
                     for members in buckets)


def summarize(rows: list[dict], policy: dict | None = None) -> dict:
    """Compute descriptive diagnostics after the caller enforced the sample floor.

    Rows have p (point estimate), o (binary result), decision and decided_at.
    Independence between forecasts is *not* assumed or certified.
    """
    if not rows:
        raise CalibrationError('cannot calculate diagnostics from an empty sample')
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or 'p' not in row or 'o' not in row:
            raise CalibrationError(f'rows[{index}]: p and o required')
        _probability(row['p'], f'rows[{index}].p')
        if type(row['o']) is not int or row['o'] not in (0, 1):
            raise CalibrationError(f'rows[{index}].o: integer zero or one required')
    n = len(rows)
    mean_outcome = math.fsum(x['o'] for x in rows) / n
    brier = math.fsum((x['p'] - x['o']) ** 2 for x in rows) / n

    # Exact partition by the actual issued forecast. Coarse bins would not have an
    # exact Murphy identity when forecasts vary inside a bin.
    groups: dict[float, list[dict]] = defaultdict(list)
    for row in rows:
        groups[float(row['p'])].append(row)
    reliability = 0.0
    resolution = 0.0
    for p, g in groups.items():
        frequency = math.fsum(x['o'] for x in g) / len(g)
        weight = len(g) / n
        reliability += weight * (p - frequency) ** 2
        resolution += weight * (frequency - mean_outcome) ** 2
    uncertainty = mean_outcome * (1 - mean_outcome)
    reconstructed = reliability - resolution + uncertainty
    # Murphy decomposition is algebraically exact at forecast resolution, up to floating error.
    if not math.isclose(brier, reconstructed, abs_tol=2e-12, rel_tol=1e-12):
        raise CalibrationError('Murphy decomposition did not reconcile with Brier')

    edges = policy['bin_edges'] if policy is not None else DEFAULT_EDGES
    ece, bins = _ece(rows, edges)
    ece_w10, _ = _ece(rows, tuple(i / 10 for i in range(11)))
    ece_equal = _ece_equal_mass_tie_safe(rows)

    bs_ref = None
    bss = None
    reference_status = 'NO_PREDECLARED_REFERENCE'
    if policy is not None and policy['baseline'] is not None:
        baseline = policy['baseline']
        # Temporal consistency is checkable; authenticity of the declared date is not.
        try:
            prior = all(_timestamp(row['decided_at'], 'row.decided_at') >
                        _timestamp(baseline['registered_at'], 'baseline.registered_at') for row in rows)
        except (KeyError, TypeError):
            prior = False
        if not prior:
            reference_status = 'REFERENCE_DATE_NOT_BEFORE_ALL_PREDICTIONS'
        else:
            q = baseline['probability']
            bs_ref = math.fsum((q - row['o']) ** 2 for row in rows) / n
            if bs_ref == 0:
                reference_status = 'ZERO_REFERENCE_BRIER'
            else:
                bss = 1.0 - brier / bs_ref
                reference_status = 'MEASURED_REFERENCE_SELF_DECLARED'
    clusters = {row.get('decision') for row in rows if row.get('decision') is not None}
    unique = len(groups)
    singles = sum(1 for g in groups.values() if len(g) == 1)
    return {
        'n': n, 'distinct_decisions': len(clusters),
        'forecast_probability': 'midpoint of original declared interval',
        'brier_score_unrounded': brier,
        'brier_skill_score': bss, 'reference_brier_score': bs_ref,
        'reference_status': reference_status,
        'baseline_comparator': 'fixed probability (not re-estimated on evaluated outcomes)' if bs_ref is not None else None,
        'murphy': {'reliability': reliability, 'resolution': resolution,
                   'uncertainty': uncertainty, 'reconstructed_brier': reconstructed,
                   'identity_error': brier - reconstructed, 'forecast_groups': unique,
                   'singleton_groups': singles, 'note': 'Exact forecast groups; sparse groups are descriptive, not robust estimates of skill.'},
        'ece': {'value': ece, 'kind': 'binary-forecast calibration ECE (L1)',
                'bin_edges': list(edges), 'bins': bins,
                'sensitivity': {'fixed_width_10': ece_w10, 'equal_mass_5_ties_intact': ece_equal},
                'range_across_three_schemes': max(ece, ece_w10, ece_equal) - min(ece, ece_w10, ece_equal),
                'note': 'ECE changes with binning; it is not a hypothesis test or certification.'},
        'uncertainty_interval': None,
        'uncertainty_interval_reason': 'No IID assumption or independently verified decision-cluster sampling model.',
        'analysis_scope': 'DESCRIPTIVE_NON_CERTIFYING',
    }
