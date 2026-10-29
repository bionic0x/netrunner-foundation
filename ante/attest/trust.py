"""The keys a verifier accepts: pinned in a local file, never resolved.

``foundation/attest/trusted-keys.json`` (protected; changed only through D-020):

    {"schema_version": 1,
     "keys": [{"verification_method": "did:key:z6Mk...#z6Mk...",
               "public_key_multibase": "z6Mk...",
               "principal": "owner:...",
               "principal_type": "human" | "process",
               "proof_purposes": ["assertionMethod"],
               "kinds": ["ante.execution.receipt", "ante.d020.approval"]}]}

A key is trusted for exactly the purposes and document kinds listed. A
``did:key`` method must encode the pinned key, so a store entry cannot pair a
method with somebody else's key. An approval verifies only with a ``human`` key;
G1a has no process keys, and a later process identity must use its own key.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from ante.attest import jcs, multibase
from ante.paths import ROOT

STORE_PATH = 'foundation/attest/trusted-keys.json'
STORE = ROOT / STORE_PATH
PRINCIPAL_TYPES = ('human', 'process')
ENTRY_KEYS = {'verification_method', 'public_key_multibase', 'principal', 'principal_type',
              'proof_purposes', 'kinds'}
HUMAN_ONLY_KINDS = ('ante.d020.approval',)


class TrustError(ValueError):
    """The trust store is unreadable or inconsistent; nothing verifies."""


@dataclass(frozen=True)
class Key:
    method: str
    raw: bytes
    principal: str
    principal_type: str
    purposes: tuple[str, ...]
    kinds: tuple[str, ...]


def did_key(raw: bytes) -> str:
    """The ``did:key`` verification method of a raw Ed25519 public key."""
    value = multibase.encode_public_key(raw)
    return f'did:key:{value}#{value}'


def _entry(item: object, index: int) -> Key:
    where = f'keys[{index}]'
    if not isinstance(item, dict) or set(item) != ENTRY_KEYS:
        raise TrustError(f'{where}: expected exactly {", ".join(sorted(ENTRY_KEYS))}')
    try:
        raw = multibase.public_key(item['public_key_multibase'])
    except multibase.MultibaseError as exc:
        raise TrustError(f'{where}.public_key_multibase: {exc}') from None
    method = item['verification_method']
    if not isinstance(method, str) or not method:
        raise TrustError(f'{where}.verification_method is required')
    if method.startswith('did:key:') and method != did_key(raw):
        raise TrustError(f'{where}: the did:key method does not encode the pinned key')
    if item['principal_type'] not in PRINCIPAL_TYPES:
        raise TrustError(f'{where}.principal_type must be one of {", ".join(PRINCIPAL_TYPES)}')
    for name in ('proof_purposes', 'kinds'):
        values = item[name]
        if not isinstance(values, list) or not values or not all(isinstance(v, str) and v for v in values):
            raise TrustError(f'{where}.{name} must be a non-empty list of strings')
    if not isinstance(item['principal'], str) or not item['principal']:
        raise TrustError(f'{where}.principal is required')
    return Key(method, raw, item['principal'], item['principal_type'],
               tuple(item['proof_purposes']), tuple(item['kinds']))


class Store:
    def __init__(self, keys: list[Key], source: str):
        self.keys = {key.method: key for key in keys}
        self.source = source
        self.sha256: str | None = None

    @classmethod
    def from_bytes(cls, data: bytes, source: str) -> 'Store':
        try:
            value = jcs.loads(data)
        except jcs.CanonicalError as exc:
            raise TrustError(f'{source}: {exc}') from None
        if not isinstance(value, dict) or value.get('schema_version') != 1 or not isinstance(value.get('keys'), list):
            raise TrustError(f'{source}: expected {{"schema_version": 1, "keys": [...]}}')
        keys = [_entry(item, index) for index, item in enumerate(value['keys'])]
        methods = [key.method for key in keys]
        if len(set(methods)) != len(methods):
            raise TrustError(f'{source}: a verification method is pinned twice')
        store = cls(keys, source)
        store.sha256 = hashlib.sha256(data).hexdigest()
        return store

    @classmethod
    def load(cls, path: Path | str = STORE) -> 'Store':
        target = Path(path)
        try:
            data = target.read_bytes()
        except OSError as exc:
            raise TrustError(f'{target}: {exc.strerror or exc}') from None
        return cls.from_bytes(data, str(target))

    def resolver(self, kind: str):
        """A key resolver for documents of ``kind``; ``None`` means untrusted."""
        def resolve(method: str, purpose: str) -> bytes | None:
            key = self.keys.get(method)
            if key is None or purpose not in key.purposes or kind not in key.kinds:
                return None
            if kind in HUMAN_ONLY_KINDS and key.principal_type != 'human':
                return None
            return key.raw
        return resolve

    def principal(self, method: str | None) -> str | None:
        key = self.keys.get(method) if method else None
        return key.principal if key else None
