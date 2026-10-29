"""Cumulative drift: small deviations that add up (normalisation of deviance, Marco VIII.8.4).

No single event here is alarming. The monitor adds them up across decisions,
reconciliations, gates and releases, and when the running total crosses a
threshold it requires a **model review** — revisiting the assumptions that keep
producing exceptions — instead of one more exception. While a review is due,
``ante learn record`` refuses decisions that add new accepted risks.

Weighted anomalies (all inside ``WINDOW_DAYS`` and after the last model review):

    reconciliation REFUTED                     2
    reconciliation INCONCLUSIVE                1
    accepted risk in a recorded decision       1 each
    warning in a recorded decide artefact      1 each
    develop gate HOLD / REJECT                 1 / 2   (with --state)
    release event                              its declared weight, 1-3 (with --events)

An event of weight ``INDIVIDUAL_THRESHOLD`` or more requires review on its own;
a total of ``CUMULATIVE_THRESHOLD`` requires it however small each event was.
A model review is a ``note`` in the ledger: ``ante learn review --by --reason``.
Synthetic decisions do not count. In decision records this is ``cumulative_drift``.

**Brier CUSUM.** The weighted count sees events; it does not see forecasts that
get slowly worse while each one still looks acceptable. A one-sided CUSUM watches
the squared error of every decisive, non-synthetic prediction, in the order its
outcome was reconciled, since the last model review:

    reference   the first ``CUSUM_BASELINE`` errors: mean m and standard deviation s
    statistic   S = max(0, S + error - m - k), with k = ``CUSUM_K`` x s
    alarm       the first time S exceeds h = ``CUSUM_H`` x s; it stands until a review

k = 0.5 s and h = 5 s are the textbook choice for detecting a shift of one
standard deviation (Montgomery, *Introduction to Statistical Quality Control*);
they are fixed here, not tunable per call. The errors are bounded and not
normal, so the alarm is a trigger for a model review, not a significance test.
Until the reference is complete the answer is ``INSUFFICIENT_SAMPLE``.
"""
from __future__ import annotations

from ante.core import io, schema
from ante.core import time as ante_time
from ante.learn import ledger

INDIVIDUAL_THRESHOLD = 3
CUMULATIVE_THRESHOLD = 8
WINDOW_DAYS = 180
CUSUM_BASELINE = 30
CUSUM_K = 0.5
CUSUM_H = 5.0
EVENT_KEYS = ('at', 'source', 'kind', 'weight', 'note')


def _events(path: str | None) -> list[dict]:
    if path is None:
        return []
    doc = io.load_document(path)
    schema.exact_keys(doc, ('events',), 'events file')
    out = []
    for index, event in enumerate(schema.array(doc['events'], 'events')):
        where = f'events[{index}]'
        schema.exact_keys(event, EVENT_KEYS, where)
        ante_time.parse(event['at'], f'{where}.at')
        for key in ('source', 'kind', 'note'):
            schema.text(event[key], f'{where}.{key}')
        schema.integer(event['weight'], f'{where}.weight', 1)
        out.append({'at': event['at'], 'source': f'release:{event["source"]}', 'kind': event['kind'],
                    'weight': min(3, event['weight']), 'note': event['note']})
    return out


def anomalies(entries: list[dict], state_entries: list[dict] = (), events: list[dict] = ()) -> list[dict]:
    found = []
    synthetic = {e['payload']['artifact']['artifact_sha256'] for e in entries
                 if e['kind'] == 'decision' and e['payload']['synthetic']}
    for entry in entries:
        payload = entry['payload']
        if entry['kind'] == 'decision' and not payload['synthetic']:
            art = payload['artifact']
            risks = (art['body'].get('load_bearing_claims') or {}).get('accepted_risks', [])
            for risk in risks:
                found.append({'at': entry['at'], 'source': f'ledger:{entry["seq"]}', 'kind': 'accepted_risk',
                              'weight': 1, 'note': risk['claim']})
            for warning in art['findings']:
                found.append({'at': entry['at'], 'source': f'ledger:{entry["seq"]}', 'kind': 'decide_warning',
                              'weight': 1, 'note': warning['code']})
        elif entry['kind'] == 'reconciliation' and payload['decision'] not in synthetic:
            weight = {'REFUTED': 2, 'INCONCLUSIVE': 1}.get(payload['outcome'])
            if weight:
                found.append({'at': entry['at'], 'source': f'ledger:{entry["seq"]}',
                              'kind': payload['outcome'].lower(), 'weight': weight, 'note': payload['expectation']})
    for entry in state_entries:
        if entry['kind'] == 'gate' and entry['payload']['decision'] in ('HOLD', 'REJECT'):
            found.append({'at': entry['at'], 'source': f'develop:{entry["seq"]}',
                          'kind': f'gate_{entry["payload"]["decision"].lower()}',
                          'weight': 1 if entry['payload']['decision'] == 'HOLD' else 2, 'note': entry['payload']['id']})
    found += list(events)
    return sorted(found, key=lambda a: (ante_time.parse(a['at'], 'at'), a['source']))


def last_review(entries: list[dict]) -> dict | None:
    reviews = [e for e in entries if e['kind'] == 'note' and e['payload'].get('type') == 'model_review']
    return reviews[-1] if reviews else None


def brier_stream(entries: list[dict], since=None) -> list[dict]:
    """Squared error of every decisive, non-synthetic prediction, in reconciliation order."""
    from ante.learn import commands   # commands imports this module
    decided = ledger.decisions(entries)
    stream = []
    for (sha, expectation_id), record in commands._latest_outcomes(entries).items():
        decision = decided.get(sha)
        if decision is None or decision['payload']['synthetic']:
            continue
        if record['payload']['outcome'] not in commands.DECISIVE:
            continue
        if since is not None and ante_time.parse(record['at'], 'at') <= since:
            continue
        expectation = {e['id']: e for e in commands._frozen_expectations(decision)}[expectation_id]
        outcome = 1 if record['payload']['outcome'] == 'CONFIRMED' else 0
        stream.append({'seq': record['seq'], 'at': record['at'], 'decision': sha, 'expectation': expectation_id,
                       'error': (commands._midpoint(expectation) - outcome) ** 2})
    return sorted(stream, key=lambda r: r['seq'])


def cusum(stream: list[dict]) -> dict:
    method = {'baseline': CUSUM_BASELINE, 'k_sigmas': CUSUM_K, 'h_sigmas': CUSUM_H}
    if len(stream) < CUSUM_BASELINE:
        return {'result': 'INSUFFICIENT_SAMPLE', 'n': len(stream), **method, 'alarm': None,
                'reason': f'{len(stream)} decisive predictions since the last review; '
                          f'{CUSUM_BASELINE} form the reference'}
    reference = [r['error'] for r in stream[:CUSUM_BASELINE]]
    mean = sum(reference) / len(reference)
    sigma = (sum((x - mean) ** 2 for x in reference) / len(reference)) ** 0.5
    if sigma == 0:
        return {'result': 'NO_VARIATION', 'n': len(stream), **method, 'alarm': None,
                'reason': 'every reference error is identical; a deviation scale cannot be estimated'}
    k, h, statistic, alarm = CUSUM_K * sigma, CUSUM_H * sigma, 0.0, None
    for row in stream[CUSUM_BASELINE:]:
        statistic = max(0.0, statistic + row['error'] - mean - k)
        if alarm is None and statistic > h:
            alarm = {'at': row['at'], 'decision': row['decision'], 'expectation': row['expectation']}
    return {'result': 'MEASURED', 'n': len(stream), **method, 'reference_mean': round(mean, 6),
            'reference_sigma': round(sigma, 6), 'k': round(k, 6), 'h': round(h, 6),
            'monitored': len(stream) - CUSUM_BASELINE, 'statistic': round(statistic, 6), 'alarm': alarm}


def assess(entries: list[dict], at: str, state_entries: list[dict] = (), events: list[dict] = ()) -> dict:
    now = ante_time.parse(at, 'at')
    entries = [e for e in entries if ante_time.parse(e['at'], 'at') <= now]
    review = last_review(entries)
    since = ante_time.parse(review['at'], 'at') if review else None
    counted = []
    for anomaly in anomalies(entries, state_entries, events):
        when = ante_time.parse(anomaly['at'], 'at')
        if when > now or (now - when).days >= WINDOW_DAYS or (since is not None and when <= since):
            continue
        counted.append(anomaly)
    total = sum(a['weight'] for a in counted)
    individual = [a for a in counted if a['weight'] >= INDIVIDUAL_THRESHOLD]
    if individual:
        status, reason = 'REVIEW_REQUIRED', f'{len(individual)} event(s) at or above the individual threshold'
    elif total >= CUMULATIVE_THRESHOLD:
        status, reason = 'REVIEW_REQUIRED', (f'cumulative drift {total} reached {CUMULATIVE_THRESHOLD} although no '
                                             f'event reached {INDIVIDUAL_THRESHOLD}: review the model, not the case')
    else:
        status, reason = 'WITHIN_LIMITS', f'cumulative drift {total} below {CUMULATIVE_THRESHOLD}'
    brier = cusum(brier_stream(entries, since))
    if brier['alarm'] is not None:
        drift = (f'Brier CUSUM crossed {brier["h"]} at {brier["alarm"]["at"]}: forecasts have been getting '
                 'worse; review the model')
        reason = drift if status == 'WITHIN_LIMITS' else f'{reason}; {drift}'
        status = 'REVIEW_REQUIRED'
    return {'kind': 'cumulative_drift', 'at': ante_time.iso(now), 'status': status, 'reason': reason,
            'brier_cusum': brier,
            'total': total, 'thresholds': {'individual': INDIVIDUAL_THRESHOLD, 'cumulative': CUMULATIVE_THRESHOLD,
                                           'window_days': WINDOW_DAYS},
            'since_review': review['at'] if review else None, 'counted': counted}


def review(ledger_path: str, by: str, reason: str, at: str) -> dict:
    schema.text(by, 'by')
    schema.text(reason, 'reason')
    return ledger.append(ledger_path, 'note', {'type': 'model_review', 'by': by, 'reason': reason}, at)
