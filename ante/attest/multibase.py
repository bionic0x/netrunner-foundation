"""Base58-btc multibase and the Ed25519 multicodec prefixes.

``proofValue`` is ``'z' + base58btc(signature)``. A public key in
``publicKeyMultibase`` or a ``did:key`` is ``'z' + base58btc(0xed 0x01 || key)``;
a private key in ``privateKeyMultibase`` uses the prefix ``0x80 0x26``.
"""
from __future__ import annotations

ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
_INDEX = {ch: i for i, ch in enumerate(ALPHABET)}
ED25519_PUB = b'\xed\x01'
ED25519_PRIV = b'\x80\x26'


class MultibaseError(ValueError):
    """Malformed multibase text."""


def b58encode(data: bytes) -> str:
    number = int.from_bytes(data, 'big')
    out = ''
    while number:
        number, rem = divmod(number, 58)
        out = ALPHABET[rem] + out
    pad = len(data) - len(data.lstrip(b'\0'))
    return '1' * pad + out


def b58decode(text: str) -> bytes:
    number = 0
    for ch in text:
        if ch not in _INDEX:
            raise MultibaseError(f'{ch!r} is not base58-btc')
        number = number * 58 + _INDEX[ch]
    body = number.to_bytes((number.bit_length() + 7) // 8, 'big') if number else b''
    pad = len(text) - len(text.lstrip('1'))
    return b'\0' * pad + body


def encode(data: bytes) -> str:
    return 'z' + b58encode(data)


def decode(text: str) -> bytes:
    if not isinstance(text, str) or not text.startswith('z') or len(text) < 2:
        raise MultibaseError('expected base58-btc multibase text starting with "z"')
    data = b58decode(text[1:])
    if encode(data) != text:
        raise MultibaseError('non-canonical base58-btc encoding')
    return data


def public_key(text: str) -> bytes:
    """The raw 32-byte Ed25519 key inside a ``z6Mk...`` multibase value."""
    data = decode(text)
    if not data.startswith(ED25519_PUB) or len(data) != 34:
        raise MultibaseError('not an Ed25519 public key (multicodec 0xed01, 32 bytes)')
    return data[2:]


def encode_public_key(raw: bytes) -> str:
    if len(raw) != 32:
        raise MultibaseError('an Ed25519 public key has 32 bytes')
    return encode(ED25519_PUB + raw)


def private_key(text: str) -> bytes:
    data = decode(text)
    if not data.startswith(ED25519_PRIV) or len(data) != 34:
        raise MultibaseError('not an Ed25519 private key (multicodec 0x1300, 32 bytes)')
    return data[2:]
