"""The JSON a signature may cover, parsed strictly and written canonically.

The signed subset is chosen so that its canonical form is the same under RFC 8785
(JCS) and under ``json.dumps(sort_keys=True, separators=(',', ':'),
ensure_ascii=True)``:

    objects     keys are printable ASCII and never repeated
    strings     printable ASCII (U+0020-U+007E) only
    integers    within +-(2**53 - 1); ``bool`` is not an integer
    literals    true, false, null
    arrays      of any of the above

With these limits the three places where JCS and Python differ cannot arise:
key order (UTF-16 code units against code points), string escaping outside
ASCII, and number formatting. Anything outside the subset is refused, never
repaired. ``tests/foundation/test_attest.py`` checks the equality against an
independent RFC 8785 implementation; this module does not depend on it.
"""
from __future__ import annotations

import json
from typing import Any

MAX_SAFE_INTEGER = 2 ** 53 - 1
MAX_DEPTH = 32


class CanonicalError(ValueError):
    """The value is outside the signed subset."""


def _check_text(text: str, where: str) -> None:
    for ch in text:
        if not ' ' <= ch <= '~':
            raise CanonicalError(f'{where}: only printable ASCII is signed (found U+{ord(ch):04X})')


def check(value: Any, where: str = '$', depth: int = 0) -> None:
    """Raise ``CanonicalError`` unless ``value`` lies inside the signed subset."""
    if depth > MAX_DEPTH:
        raise CanonicalError(f'{where}: nested deeper than {MAX_DEPTH}')
    if value is None or value is True or value is False:
        return
    if type(value) is int:
        if abs(value) > MAX_SAFE_INTEGER:
            raise CanonicalError(f'{where}: integer outside +-(2**53 - 1)')
        return
    if type(value) is str:
        _check_text(value, where)
        return
    if type(value) is list:
        for index, item in enumerate(value):
            check(item, f'{where}[{index}]', depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise CanonicalError(f'{where}: object key is not a string')
            _check_text(key, f'{where} key')
            check(item, f'{where}.{key}', depth + 1)
        return
    raise CanonicalError(f'{where}: {type(value).__name__} is not signed (no floats, no other types)')


def canonical(value: Any) -> bytes:
    """The canonical bytes of ``value``; equal to RFC 8785 inside the subset."""
    check(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise CanonicalError(f'duplicate key {key!r}')
        result[key] = value
    return result


def _no_float(text: str) -> Any:
    raise CanonicalError(f'number {text} is not an integer (no floats are signed)')


def _no_constant(text: str) -> Any:
    raise CanonicalError(f'{text} is not JSON')


def loads(data: bytes | str) -> Any:
    """Parse JSON strictly: UTF-8, no duplicate keys, no floats, no NaN, subset only."""
    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise CanonicalError(f'not UTF-8: {exc}') from None
    if data.startswith('﻿'):
        raise CanonicalError('byte order mark is not accepted')
    try:
        value = json.loads(data, object_pairs_hook=_no_duplicates,
                           parse_float=_no_float, parse_constant=_no_constant)
    except json.JSONDecodeError as exc:
        raise CanonicalError(f'not JSON: {exc}') from None
    check(value)
    return value
