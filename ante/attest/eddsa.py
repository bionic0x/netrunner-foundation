"""The W3C ``eddsa-jcs-2022`` Data Integrity proof, single proof, no network.

Creation (W3C Data Integrity EdDSA Cryptosuites v1.0, 3.3.1 and 3.3.3-3.3.6):

    options   {type, cryptosuite, created, verificationMethod, proofPurpose}
              plus the document's @context when it has one
    hashData  SHA-256(JCS(options)) || SHA-256(JCS(document without proof))
    proof     options + proofValue = multibase base58-btc of Ed25519(hashData)

Verification (3.3.2) removes ``proofValue``, checks that the document's
``@context`` starts with the proof's, recomputes ``hashData`` and checks the
signature with a key the caller resolves from a pinned trust store. A key is
never taken from the document, the proof or a DID resolver.

What is refused instead of interpreted: proof sets or chains, proof options
other than the five above and ``@context``, ``created`` in any form other than
``YYYY-MM-DDTHH:MM:SSZ``, values outside the signed subset (``jcs``).
"""
from __future__ import annotations

import copy
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from ante.attest import jcs, multibase

PROOF_TYPE = 'DataIntegrityProof'
CRYPTOSUITE = 'eddsa-jcs-2022'
OPTION_KEYS = ('type', 'cryptosuite', 'created', 'verificationMethod', 'proofPurpose')
PROOF_KEYS = frozenset(OPTION_KEYS + ('proofValue', '@context'))
CREATED = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

Signer = Callable[[bytes], bytes]
KeyResolver = Callable[[str, str], 'bytes | None']


class ProofError(ValueError):
    """A proof cannot be created from these inputs."""


class CryptoUnavailable(RuntimeError):
    """``cryptography`` is not installed; signing and verification fail closed."""


@dataclass
class Verification:
    verified: bool
    reason: str
    detail: str = ''
    document: dict | None = None
    method: str | None = None
    purpose: str | None = None
    created: str | None = None
    checks: dict = field(default_factory=dict)


def ed25519():
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric import ed25519 as module
    except ImportError:
        raise CryptoUnavailable('the "cryptography" package is required to sign or verify '
                                '(.github/requirements/attest.txt)') from None
    return module, InvalidSignature


def _check_created(value: Any) -> None:
    if not isinstance(value, str) or not CREATED.match(value):
        raise ProofError('created must be YYYY-MM-DDTHH:MM:SSZ')
    try:
        datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        raise ProofError(f'created {value!r} is not a real UTC time') from None


def valid_context(value: Any) -> bool:
    """``@context`` is a non-empty string or a non-empty list of non-empty strings."""
    if isinstance(value, str):
        return bool(value)
    return isinstance(value, list) and bool(value) and all(isinstance(v, str) and v for v in value)


def _contexts(value: Any) -> list:
    return list(value) if isinstance(value, list) else [value]


def hash_data(document: dict, options: dict) -> bytes:
    """SHA-256 of the canonical proof configuration, then of the canonical document."""
    if options.get('type') != PROOF_TYPE or options.get('cryptosuite') != CRYPTOSUITE:
        raise ProofError(f'proof must be {PROOF_TYPE} with cryptosuite {CRYPTOSUITE}')
    _check_created(options.get('created'))
    return hashlib.sha256(jcs.canonical(options)).digest() + hashlib.sha256(jcs.canonical(document)).digest()


def create(document: dict, method: str, purpose: str, created: str, sign: Signer) -> dict:
    """Return a copy of ``document`` with a proof. ``sign`` holds the key; this never sees it."""
    if not isinstance(document, dict):
        raise ProofError('only a JSON object can be signed')
    if 'proof' in document:
        raise ProofError('the document already carries a proof; proof sets are not supported')
    jcs.check(document)
    for name, value in (('verificationMethod', method), ('proofPurpose', purpose)):
        if not isinstance(value, str) or not value:
            raise ProofError(f'{name} is required')
    options = {'type': PROOF_TYPE, 'cryptosuite': CRYPTOSUITE, 'created': created,
               'verificationMethod': method, 'proofPurpose': purpose}
    if '@context' in document:
        if not valid_context(document['@context']):
            raise ProofError('@context must be a non-empty string or list of strings')
        options['@context'] = copy.deepcopy(document['@context'])
    signature = sign(hash_data(document, options))
    if not isinstance(signature, (bytes, bytearray)) or len(signature) != 64:
        raise ProofError('the signer must return a 64-byte Ed25519 signature')
    return {**copy.deepcopy(document), 'proof': {**options, 'proofValue': multibase.encode(bytes(signature))}}


def verify(secured: Any, resolve: KeyResolver) -> Verification:
    """Verify one ``eddsa-jcs-2022`` proof. Every failure is a reason, never success."""
    if not isinstance(secured, dict) or not isinstance(secured.get('proof'), dict):
        return Verification(False, 'MALFORMED', 'expected a JSON object with a single "proof" object')
    proof = secured['proof']
    extra = sorted(set(proof) - PROOF_KEYS)
    if extra:
        return Verification(False, 'UNSUPPORTED_PROOF', f'proof options not supported: {", ".join(extra)}')
    missing = [key for key in OPTION_KEYS + ('proofValue',) if key not in proof]
    if missing:
        return Verification(False, 'MALFORMED', f'proof lacks {", ".join(missing)}')
    method, purpose = proof['verificationMethod'], proof['proofPurpose']
    result = Verification(False, 'MALFORMED', method=method if isinstance(method, str) else None,
                          purpose=purpose if isinstance(purpose, str) else None,
                          created=proof['created'] if isinstance(proof['created'], str) else None)
    if proof['type'] != PROOF_TYPE or proof['cryptosuite'] != CRYPTOSUITE:
        result.reason, result.detail = 'UNSUPPORTED_PROOF', f'only {PROOF_TYPE} / {CRYPTOSUITE} is verified'
        return result
    if not isinstance(method, str) or not isinstance(purpose, str):
        result.detail = 'verificationMethod and proofPurpose must be strings'
        return result
    try:
        signature = multibase.decode(proof['proofValue'])
    except multibase.MultibaseError as exc:
        result.detail = f'proofValue: {exc}'
        return result
    if len(signature) != 64:
        result.detail = 'proofValue does not hold a 64-byte signature'
        return result
    unsecured = {key: value for key, value in secured.items() if key != 'proof'}
    options = {key: value for key, value in proof.items() if key != 'proofValue'}
    for where, holder in (('document', unsecured), ('proof', options)):
        if '@context' in holder and not valid_context(holder['@context']):
            result.detail = f'{where} @context must be a non-empty string or list of strings'
            return result
    if '@context' in options:
        expected = _contexts(options['@context'])
        actual = _contexts(unsecured.get('@context'))
        if '@context' not in unsecured or actual[:len(expected)] != expected:
            result.reason, result.detail = 'CONTEXT_MISMATCH', 'the document @context does not start with the proof @context'
            return result
        unsecured['@context'] = copy.deepcopy(options['@context'])
    try:
        data = hash_data(unsecured, options)
    except (ProofError, jcs.CanonicalError) as exc:
        result.detail = str(exc)
        return result
    key = resolve(method, purpose)
    if key is None:
        result.reason, result.detail = 'UNTRUSTED_KEY', f'{method} is not pinned for {purpose}'
        return result
    try:
        module, invalid = ed25519()
    except CryptoUnavailable as exc:
        result.reason, result.detail = 'CRYPTO_UNAVAILABLE', str(exc)
        return result
    try:
        module.Ed25519PublicKey.from_public_bytes(key).verify(signature, data)
    except invalid:
        result.reason, result.detail = 'BAD_SIGNATURE', 'the signature does not match the document and the pinned key'
        return result
    except ValueError as exc:
        result.reason, result.detail = 'UNTRUSTED_KEY', f'pinned key unusable: {exc}'
        return result
    result.verified, result.reason, result.detail, result.document = True, 'VERIFIED', '', unsecured
    return result


def key_signer(private_key) -> Signer:
    """Wrap an ``Ed25519PrivateKey``; the key object stays with the caller."""
    return lambda data: private_key.sign(data)
