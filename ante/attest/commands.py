"""``ante sign``, ``ante verify`` and ``ante attest``.

    ante attest receipt ARTEFACT --at T [--out FILE]        unsigned execution receipt
    ante attest approval --base REV --head REV --scope apply --review-ref REF --author WHO --at T
                                                             unsigned D-020 approval
    ante attest key PUBLIC.pem --principal WHO --principal-type human
                                                             a trust-store entry to pin (through D-020)
    ante sign DOCUMENT --key KEY.pem --method ID --at T [--out FILE]
    ante verify SIGNED [--trust FILE] [--repo DIR] [--artefact FILE] [--head REV]

``ante sign`` reads an encrypted PKCS#8 Ed25519 key that lives outside the
checkout and belongs to a separate signing account, mode 600, and must itself
run as that account, never as the account that owns the checkout. It asks for
the passphrase on the terminal; it accepts no passphrase from arguments, environment or a pipe. An
agent shell may have a terminal too: what keeps it from signing is that it does
not know the passphrase. A signature does not prove that a person was present
(``foundation/ATTEST.md``, T01).

``ante verify`` is read-only. It never authorises anything: a verified approval
is input to the D-020 host gate, a verified receipt stays a system record.

Exit status: 0 verified or document written; 2 invalid input or refused
operation; 4 not verified (every failure has a reason code).
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import stat
import sys
from pathlib import Path

from ante.attest import documents, eddsa, jcs, multibase, trust
from ante.core import time as ante_time
from ante.paths import ROOT

EXIT_OK, EXIT_INVALID, EXIT_NOT_VERIFIED = 0, 2, 4
DEFAULT_PURPOSE = 'assertionMethod'


class SignError(ValueError):
    """Signing refused; nothing was signed."""


def _emit(document: dict, out: str | None) -> None:
    text = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=True) + '\n'
    if out is None:
        sys.stdout.write(text)
    else:
        Path(out).write_text(text, encoding='ascii')
        print(f'{document.get("kind", "document")} -> {out}')


def sign_document(document: dict, signer: eddsa.Signer, method: str, at: str,
                  purpose: str = DEFAULT_PURPOSE) -> dict:
    """Validate an unsigned document and add its proof. The signer holds the key."""
    if 'proof' in document:
        raise SignError('the document is already signed')
    documents.validate(document)
    return eddsa.create(document, method, purpose, documents.utc(at), signer)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def read_key_file(path: Path, root: Path = ROOT, checkout_uid: int | None = None) -> bytes:
    """Read a signing key only from a separate account that an agent in the checkout cannot be.

    The key must be outside the checkout, a regular file owned by the account
    running ``ante sign``, with mode 600 or stricter, and that account must not
    be the one that owns the checkout. Checks and read use one open descriptor.
    """
    if not hasattr(os, 'geteuid'):
        raise SignError('signing needs POSIX file ownership; this platform is not supported')
    resolved = path.expanduser().resolve()
    if _inside(resolved, root.resolve()):
        raise SignError('the private key is inside the checkout; keep it outside the repository')
    euid = os.geteuid()
    owner_of_checkout = root.resolve().stat().st_uid if checkout_uid is None else checkout_uid
    if euid == owner_of_checkout:
        raise SignError('ante sign is running as the account that owns the checkout; '
                        'run it as the separate signing account (for example sudo -u ante-signer)')
    try:
        fd = os.open(resolved, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    except OSError as exc:
        raise SignError(f'key file: {exc.strerror or exc}') from None
    with os.fdopen(fd, 'rb') as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise SignError('key file is not a regular file')
        if info.st_uid != euid:
            raise SignError('the key file is not owned by the account running ante sign')
        if info.st_mode & 0o077:
            raise SignError('key file is readable or writable by others; chmod 600 it')
        return handle.read()


def read_passphrase(prompt: str = 'Passphrase for the signing key: ') -> bytes:
    """Read from the controlling terminal only; a pipe, argument or variable is refused."""
    try:
        fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
    except OSError:
        raise SignError('no controlling terminal: the passphrase must be typed by a person') from None
    os.close(fd)
    try:
        value = getpass.getpass(prompt)
    except (EOFError, KeyboardInterrupt):
        raise SignError('no passphrase was typed') from None
    if not value:
        raise SignError('empty passphrase')
    return value.encode('utf-8')


def file_signer(path: Path, method: str, passphrase=read_passphrase, *, root: Path = ROOT,
                checkout_uid: int | None = None) -> eddsa.Signer:
    """An Ed25519 signer from an encrypted PKCS#8 file; the key never leaves this closure."""
    module, _ = eddsa.ed25519()
    from cryptography.hazmat.primitives import serialization
    data = read_key_file(path, root, checkout_uid)
    try:
        serialization.load_pem_private_key(data, password=None)
    except TypeError:
        pass                                    # encrypted, as required
    except ValueError:
        raise SignError('the key file is not a PEM private key') from None
    else:
        raise SignError('the key file is not encrypted; use an encrypted PKCS#8 key')
    try:
        key = serialization.load_pem_private_key(data, password=passphrase())
    except (TypeError, ValueError):
        raise SignError('wrong passphrase or unreadable key') from None
    if not isinstance(key, module.Ed25519PrivateKey):
        raise SignError('the key is not Ed25519')
    raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    if method.startswith('did:key:') and method != trust.did_key(raw):
        raise SignError('--method names a did:key that is not this key')
    return eddsa.key_signer(key)


def _load(path: str):
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise documents.DocumentError(f'{path}: {exc.strerror or exc}') from None
    return jcs.loads(data)


def verify_file(path: str, trust_path: str | None, repo: str | None, artefact: str | None,
                head: str | None) -> dict:
    report = {'verified': False, 'reason': 'MALFORMED', 'detail': '', 'kind': None,
              'verification_method': None, 'principal': None, 'proof_purpose': None, 'created': None,
              'checks': {}, 'authorizes_action': False, 'evidence_origin': 'UNVERIFIED'}
    try:
        secured = _load(path)
    except (documents.DocumentError, jcs.CanonicalError) as exc:
        report['detail'] = str(exc)
        return report
    if not isinstance(secured, dict):
        report['detail'] = 'expected a JSON object'
        return report
    unsigned = {key: value for key, value in secured.items() if key != 'proof'}
    try:
        kind = documents.validate(unsigned)
    except (documents.DocumentError, jcs.CanonicalError, ante_time.TimeError) as exc:
        report['reason'], report['detail'] = 'SCHEMA_INVALID', str(exc)
        return report
    report['kind'] = kind
    try:
        store = trust.Store.load(trust_path or trust.STORE)
    except trust.TrustError as exc:
        report['reason'], report['detail'] = 'TRUST_STORE_INVALID', str(exc)
        return report
    result = eddsa.verify(secured, store.resolver(kind))
    report.update({'reason': result.reason, 'detail': result.detail, 'verification_method': result.method,
                   'proof_purpose': result.purpose, 'created': result.created,
                   'principal': store.principal(result.method) if result.verified else None})
    if not result.verified:
        return report
    if repo is not None:
        try:
            if kind == documents.RECEIPT:
                checks = documents.check_receipt(unsigned, Path(repo), artefact)
            else:
                checks = documents.check_approval(unsigned, Path(repo), head)
        except documents.DocumentError as exc:
            report['reason'], report['detail'] = 'REPOSITORY_UNAVAILABLE', str(exc)
            return report
        report['checks'] = checks
        failed = sorted(name for name, ok in checks.items() if not ok)
        if failed:
            report['reason'], report['detail'] = 'REPOSITORY_MISMATCH', 'failed: ' + ', '.join(failed)
            return report
    elif artefact is not None or head is not None:
        report['reason'], report['detail'] = 'MALFORMED', '--artefact and --head need --repo'
        return report
    report['verified'] = True
    report['evidence_origin'] = 'SYSTEM' if kind == documents.RECEIPT else 'PINNED_HUMAN_KEY'
    return report


def _verify(args) -> int:
    report = verify_file(args.signed, args.trust, args.repo, args.artefact, args.head)
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
    return EXIT_OK if report['verified'] else EXIT_NOT_VERIFIED


def _sign(args) -> int:
    try:
        document = _load(args.document)
        if not isinstance(document, dict):
            raise SignError('expected a JSON object')
        signer = file_signer(Path(args.key), args.method)
        signed = sign_document(document, signer, args.method, args.at, args.purpose)
    except (SignError, documents.DocumentError, jcs.CanonicalError, eddsa.ProofError,
            eddsa.CryptoUnavailable, ante_time.TimeError) as exc:
        print(f'REFUSED {exc}', file=sys.stderr)
        return EXIT_INVALID
    _emit(signed, args.out)
    return EXIT_OK


def _receipt(args) -> int:
    try:
        document = documents.receipt(args.artefact, args.at, Path(args.repo))
    except (documents.DocumentError, ante_time.TimeError) as exc:
        print(f'INVALID {exc}', file=sys.stderr)
        return EXIT_INVALID
    _emit(document, args.out)
    return EXIT_OK


def _approval(args) -> int:
    try:
        document = documents.approval(args.base, args.head, args.scope, args.review_ref, args.author,
                                      args.at, Path(args.repo))
    except (documents.DocumentError, ante_time.TimeError) as exc:
        print(f'INVALID {exc}', file=sys.stderr)
        return EXIT_INVALID
    _emit(document, args.out)
    return EXIT_OK


def _key(args) -> int:
    try:
        module, _ = eddsa.ed25519()
        from cryptography.hazmat.primitives import serialization
        key = serialization.load_pem_public_key(Path(args.public_key).read_bytes())
        if not isinstance(key, module.Ed25519PublicKey):
            raise SignError('not an Ed25519 public key')
        raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    except (OSError, ValueError, SignError, eddsa.CryptoUnavailable) as exc:
        print(f'INVALID {exc}', file=sys.stderr)
        return EXIT_INVALID
    entry = {'verification_method': trust.did_key(raw), 'public_key_multibase': multibase.encode_public_key(raw),
             'principal': args.principal, 'principal_type': args.principal_type,
             'proof_purposes': [DEFAULT_PURPOSE], 'kinds': sorted(set(args.kind or documents.KINDS))}
    try:
        jcs.check(entry)
    except jcs.CanonicalError as exc:
        print(f'INVALID {exc}', file=sys.stderr)
        return EXIT_INVALID
    _emit(entry, None)
    return EXIT_OK


def add_parser(sub) -> None:
    signer = sub.add_parser('sign', help='sign a receipt or a D-020 approval (eddsa-jcs-2022, local key)')
    signer.add_argument('document', help='unsigned receipt or approval (JSON)')
    signer.add_argument('--key', required=True, help='encrypted PKCS#8 Ed25519 key of the separate signing account, outside the checkout, mode 600')
    signer.add_argument('--method', required=True, help='verificationMethod, e.g. the key\'s did:key')
    signer.add_argument('--at', required=True, help='signing time, ISO-8601 with offset')
    signer.add_argument('--purpose', default=DEFAULT_PURPOSE, help=argparse.SUPPRESS)
    signer.add_argument('--out', help='output file (else stdout)')
    signer.set_defaults(handler=_sign)

    verifier = sub.add_parser('verify', help='verify a signed receipt or approval against pinned keys (read-only)')
    verifier.add_argument('signed')
    verifier.add_argument('--trust', help='trust store (default foundation/attest/trusted-keys.json)')
    verifier.add_argument('--repo', help='also check commit, tree, policy or patch against this repository')
    verifier.add_argument('--artefact', help='receipts: also check this artefact file (needs --repo)')
    verifier.add_argument('--head', help='approvals: also check this candidate head (needs --repo)')
    verifier.set_defaults(handler=_verify)

    attest = sub.add_parser('attest', help='prepare unsigned receipts, D-020 approvals and trust entries')
    inner = attest.add_subparsers(dest='attest_command', required=True, metavar='KIND')
    rec = inner.add_parser('receipt', help='execution receipt for a sealed artefact at HEAD')
    rec.add_argument('artefact')
    rec.add_argument('--at', required=True)
    rec.add_argument('--repo', default=str(ROOT))
    rec.add_argument('--out')
    rec.set_defaults(handler=_receipt)
    app = inner.add_parser('approval', help='D-020 approval of the exact change from --base to --head')
    app.add_argument('--base', required=True)
    app.add_argument('--head', required=True)
    app.add_argument('--scope', action='append', required=True, choices=documents.SCOPES)
    app.add_argument('--review-ref', required=True)
    app.add_argument('--author', required=True, help='who prepared the change (agent or person)')
    app.add_argument('--at', required=True)
    app.add_argument('--repo', default=str(ROOT))
    app.add_argument('--out')
    app.set_defaults(handler=_approval)
    key = inner.add_parser('key', help='trust-store entry for an Ed25519 public key (pin it through D-020)')
    key.add_argument('public_key', help='PEM public key')
    key.add_argument('--principal', required=True)
    key.add_argument('--principal-type', required=True, choices=trust.PRINCIPAL_TYPES)
    key.add_argument('--kind', action='append', choices=documents.KINDS)
    key.set_defaults(handler=_key)
