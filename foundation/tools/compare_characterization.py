#!/usr/bin/env python3
"""Compare two characterization manifests taken at the same base commit.

Two harnesses froze the legacy CLIs at ``86addea`` independently:

- ``tests/characterization/cases.json`` + ``golden/<id>.json`` — 114 cases; stdout,
  stderr and written files stored as text with the checkout path replaced by
  ``<ROOT>`` and the per-case temporary directory by ``<TMP>``;
- ``tests/characterization/manifest.json`` + ``golden/<id>.stdout|.stderr`` — 116
  cases; raw bytes, no normalisation, SHA-256 per stream.

This tool regenerates nothing. It reads both manifests and the frozen outputs and
classifies every case:

    same_bytes        same invocation, same exit code, byte-identical streams
    same_invocation   same invocation; streams not byte-comparable because one
                      side normalised a path (reported with the reason)
    disagree          same invocation, different exit code or different bytes
    only_normalised   present only in cases.json
    only_raw          present only in manifest.json

An invocation is the script plus its arguments, with ``{ROOT}/`` removed (both
harnesses run from the repository root, so ``{ROOT}/x`` and ``x`` name the same
file; whether the program prints the path it was given is what
``same_invocation`` records).

    compare_characterization.py --normalised CASES.json --normalised-golden DIR \\
                                --raw MANIFEST.json [--raw-golden DIR] [--json OUT]
Exit 0 when nothing disagrees, 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EMPTY = hashlib.sha256(b'').hexdigest()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def normalised_cases(manifest: Path, golden: Path) -> dict[tuple, dict]:
    out = {}
    for case in json.loads(manifest.read_text())['cases']:
        args = tuple(a[len('{ROOT}/'):] if a.startswith('{ROOT}/') else a for a in case.get('args', []))
        key = (case['script'], args, case.get('stdin', ''))
        recorded = json.loads((golden / f"{case['id']}.json").read_text())
        out[key] = {'id': case['id'], 'exit': recorded['exit'], 'stdout': recorded['stdout'],
                    'stderr': recorded['stderr'], 'files': recorded['files'],
                    'uses_tmp': any('{TMP}' in a for a in case.get('args', [])) or bool(case.get('setup_copy'))}
    return out


def raw_cases(manifest: Path) -> dict[tuple, dict]:
    out = {}
    for case in json.loads(manifest.read_text())['cases']:
        argv = case['argv']
        script = Path(argv[1]).name
        key = (script, tuple(argv[2:]), case.get('stdin', ''))
        out[key] = case
    return out


def compare(normalised: dict, raw: dict, raw_golden: Path | None) -> dict:
    rows = []
    for key in sorted(set(normalised) | set(raw), key=lambda k: (k[0], k[1])):
        n, r = normalised.get(key), raw.get(key)
        row = {'script': key[0], 'args': list(key[1]), 'normalised_id': n and n['id'], 'raw_id': r and r['id']}
        if n and not r:
            row['class'] = 'only_normalised'
        elif r and not n:
            row['class'] = 'only_raw'
        else:
            placeholders = [s for s in ('stdout', 'stderr') if '<ROOT>' in n[s] or '<TMP>' in n[s]]
            exit_same = n['exit'] == r['returncode']
            streams = {s: _sha(n[s]) == r[f'{s}_sha256'] for s in ('stdout', 'stderr')}
            if raw_golden is not None:
                for s in ('stdout', 'stderr'):
                    path = raw_golden / f"{r['id']}.{s}"
                    if path.exists():
                        row[f'{s}_file_matches_manifest'] = hashlib.sha256(path.read_bytes()).hexdigest() == r[f'{s}_sha256']
            if exit_same and all(streams.values()):
                row['class'] = 'same_bytes'
            elif exit_same and placeholders and all(streams[s] for s in ('stdout', 'stderr') if s not in placeholders):
                row['class'] = 'same_invocation'
                row['reason'] = f"{', '.join(placeholders)} normalised (<ROOT>/<TMP>) on one side; raw bytes on the other"
            else:
                row['class'] = 'disagree'
                row['detail'] = {'exit': [n['exit'], r['returncode']], 'streams_equal': streams}
        rows.append(row)
    counts = {}
    for row in rows:
        counts[row['class']] = counts.get(row['class'], 0) + 1
    return {'counts': counts, 'normalised_total': len(normalised), 'raw_total': len(raw),
            'union': len(rows), 'rows': rows}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--normalised', required=True, type=Path)
    parser.add_argument('--normalised-golden', required=True, type=Path)
    parser.add_argument('--raw', required=True, type=Path)
    parser.add_argument('--raw-golden', type=Path)
    parser.add_argument('--json', type=Path)
    args = parser.parse_args(argv)
    result = compare(normalised_cases(args.normalised, args.normalised_golden), raw_cases(args.raw), args.raw_golden)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('normalised_total', 'raw_total', 'union', 'counts')}, sort_keys=True))
    for row in result['rows']:
        if row['class'] == 'disagree':
            print(f"DISAGREE {row['script']} {' '.join(row['args'])}: {row['detail']}")
    return 1 if result['counts'].get('disagree') else 0


if __name__ == '__main__':
    sys.exit(main())
