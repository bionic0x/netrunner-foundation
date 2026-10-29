"""``ante sign``, ``ante verify`` and ``ante attest``.

    ante attest receipt ARTEFACT --at T [--out FILE]        unsigned execution receipt
    ante attest approval --base REV --head REV --scope apply --review-ref REF --author WHO --at T
                                                             unsigned D-020 approval
    ante attest key PUBLIC.pem --principal WHO --principal-type human
                                                             a trust-store entry to pin (through D-020)
    ante attest keygen --out KEY.pem --public PUBLIC.pem     new encrypted signing key (as the signing account)
    ante sign DOCUMENT --key KEY.pem --method ID --at T [--head REV] [--out FILE]
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

``ante sign`` first re-derives what the document binds from the checkout
(``--head`` for approvals) and shows it, and only then asks for the passphrase.
The default trust store is read from the checkout's HEAD commit; uncommitted
changes to the verifier or the store fail every verification.

Exit status: 0 verified or document written; 2 usage error, invalid input to
``attest`` or a refused signature; 4 not verified, with a reason code, which
includes unreadable or invalid documents given to ``verify``.
"""
from __future__ import annotations

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


def sign_document(document: dict, signer: eddsa.Signer, method: str, at: str) -> dict:
    """Validate an unsigned document and add an ``assertionMethod`` proof. The signer holds the key."""
    if 'proof' in document:
        raise SignError('the document is already signed')
    documents.validate(document)
    return eddsa.create(document, method, DEFAULT_PURPOSE, documents.utc(at), signer)


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
        with open(path, 'rb') as handle:
            data = handle.read(jcs.MAX_BYTES + 1)
    except OSError as exc:
        raise documents.DocumentError(f'cannot read the document ({exc.strerror or "error"})') from None
    return jcs.loads(data)


VERIFIER_PATHS = ['ante/attest', 'foundation/attest']


def load_trust(trust_path: str | None, root: Path = ROOT) -> tuple[trust.Store, dict]:
    """The default store is read from the commit the checkout is on, never from the working tree.

    A modified verifier or store in the working tree makes every verification fail.
    """
    if trust_path is not None:
        store = trust.Store.load(trust_path)
        return store, {'path': str(trust_path), 'sha256': store.sha256, 'default': False}
    try:
        changed = documents.dirty(root, VERIFIER_PATHS)
        data = documents.committed(root, 'HEAD', trust.STORE_PATH)
    except documents.DocumentError:
        raise trust.TrustError('the default trust store needs the git checkout it is committed in') from None
    if changed:
        raise VerifierModified(f'{len(changed)} uncommitted change(s) under {" or ".join(VERIFIER_PATHS)}')
    if data is None:
        raise trust.TrustError(f'{trust.STORE_PATH} is not committed at HEAD')
    store = trust.Store.from_bytes(data, f'HEAD:{trust.STORE_PATH}')
    return store, {'path': f'HEAD:{trust.STORE_PATH}', 'sha256': store.sha256, 'default': True}


class VerifierModified(ValueError):
    """The verifier or its trust store differs from the committed one."""


def verify_file(path: str, trust_path: str | None, repo: str | None, artefact: str | None,
                head: str | None, root: Path = ROOT) -> dict:
    """Read-only verification. Fields copied from the document appear only once it verified."""
    report = {'verified': False, 'signature_valid': False, 'reason': 'MALFORMED', 'detail': '', 'kind': None,
              'verification_method': None, 'principal': None, 'proof_purpose': None, 'created': None,
              'checks': {}, 'trust_store': None, 'authorizes_action': False, 'evidence_origin': 'UNVERIFIED'}
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
        store, identity = load_trust(trust_path, root)
    except VerifierModified as exc:
        report['reason'], report['detail'] = 'VERIFIER_MODIFIED', str(exc)
        return report
    except trust.TrustError as exc:
        report['reason'], report['detail'] = 'TRUST_STORE_INVALID', str(exc)
        return report
    report['trust_store'] = identity
    resolve = store.resolver(kind)
    result = eddsa.verify(secured, lambda method, purpose: resolve(method, purpose) if purpose == DEFAULT_PURPOSE else None)
    report.update({'reason': result.reason, 'detail': result.detail})
    if not result.verified:
        return report
    report.update({'signature_valid': True, 'verification_method': result.method, 'proof_purpose': result.purpose,
                   'created': result.created, 'principal': store.principal(result.method)})
    if kind == documents.APPROVAL and (repo is None or head is None):
        report['reason'] = 'CANDIDATE_REQUIRED'
        report['detail'] = 'the signature is valid; an approval verifies only against a candidate (--repo and --head)'
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
    elif artefact is not None:
        report['reason'], report['detail'] = 'MALFORMED', '--artefact needs --repo'
        return report
    report['verified'] = True
    if kind == documents.RECEIPT:
        report['evidence_origin'] = 'SYSTEM'
    else:
        report['evidence_origin'] = 'PINNED_HUMAN_KEY' if identity['default'] else 'CALLER_TRUST_STORE'
    return report


def _verify(args) -> int:
    report = verify_file(args.signed, args.trust, args.repo, args.artefact, args.head)
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
    return EXIT_OK if report['verified'] else EXIT_NOT_VERIFIED


def summary(document: dict) -> str:
    """What the signer is about to sign, shown on the terminal before the passphrase."""
    if document['kind'] == documents.RECEIPT:
        lines = ['execution receipt',
                 f'  artefact  {document["artifact_sha256"]}',
                 f'  commit    {document["source_commit_oid"]["oid"]}',
                 f'  ante/     {document["code_tree_oid"]["oid"]}',
                 f'  policy    {document["policy_sha256"]}']
    else:
        lines = [f'D-020 approval, scope {", ".join(document["scope"])}',
                 f'  base         {document["base_commit"]}',
                 f'  result tree  {document["result_tree"]}',
                 f'  patch        {document["patch_sha256"]}',
                 f'  author       {document["author"]}',
                 f'  review       {document["review_ref"]}',
                 f'  {len(document["paths"])} path(s):'] + [f'    {entry["path"]}' for entry in document['paths']]
    return '\n'.join(lines + [f'  issued_at {document["issued_at"]}'])


def check_before_signing(document: dict, head: str | None, root: Path = ROOT) -> None:
    """Re-derive what the document binds from the checkout; refuse on any difference."""
    with documents.trusting(root):
        if document['kind'] == documents.APPROVAL:
            if head is None:
                raise SignError('an approval is signed only with --head, checked against the checkout')
            expected = documents.bindings(document['base_commit'], head, root)
            different = [key for key in documents.BINDING_KEYS if expected[key] != document[key]]
            if different:
                raise SignError(f'the approval does not describe base..{head} in this checkout: '
                                f'{", ".join(different)} differ')
        else:
            failed = sorted(name for name, ok in documents.check_receipt(document, root, None).items() if not ok)
            if failed:
                raise SignError(f'the receipt does not match this checkout: {", ".join(failed)}')


def _sign(args) -> int:
    try:
        document = _load(args.document)
        if not isinstance(document, dict) or 'proof' in document:
            raise SignError('expected an unsigned JSON object')
        documents.validate(document)
        check_before_signing(document, args.head)
        print(summary(document), file=sys.stderr)
        signer = file_signer(Path(args.key), args.method)
        signed = sign_document(document, signer, args.method, args.at)
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


def _passphrase_twice() -> bytes:
    first = read_passphrase('New passphrase for the signing key: ')
    if read_passphrase('Type it again: ') != first:
        raise SignError('the two passphrases differ; nothing was written')
    return first


def _create_new(path: Path, data: bytes, mode: int) -> None:
    """Write a new file; an existing file or a symbolic link is never overwritten."""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), mode)
    except OSError as exc:
        raise SignError(f'{path}: {exc.strerror or exc}') from None
    with os.fdopen(fd, 'wb') as handle:
        handle.write(data)


def generate_key(out: Path, public: Path, passphrase=_passphrase_twice, *, root: Path = ROOT,
                 checkout_uid: int | None = None) -> str:
    """Create an encrypted PKCS#8 Ed25519 key (mode 600) and its public PEM; return the did:key.

    It follows the rules of ``read_key_file``: outside the checkout, run by an
    account that does not own the checkout, passphrase typed twice on the
    terminal. The private key is encrypted before it touches the disk.
    """
    if not hasattr(os, 'geteuid'):
        raise SignError('signing needs POSIX file ownership; this platform is not supported')
    if _inside(out.expanduser().resolve(), root.resolve()):
        raise SignError('the private key would be inside the checkout; keep it outside the repository')
    owner = root.resolve().stat().st_uid if checkout_uid is None else checkout_uid
    if os.geteuid() == owner:
        raise SignError('ante attest keygen is running as the account that owns the checkout; '
                        'run it as the separate signing account')
    module, _ = eddsa.ed25519()
    from cryptography.hazmat.primitives import serialization
    out = out.expanduser()
    public = public.expanduser()
    for target in (out, public):
        if target.exists() or target.is_symlink():
            raise SignError(f'{target} already exists; nothing was written')
    secret = passphrase()
    key = module.Ed25519PrivateKey.generate()
    private_pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                    serialization.BestAvailableEncryption(secret))
    public_pem = key.public_key().public_bytes(serialization.Encoding.PEM,
                                               serialization.PublicFormat.SubjectPublicKeyInfo)
    raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    _create_new(out, private_pem, 0o600)
    _create_new(public, public_pem, 0o644)
    return trust.did_key(raw)


def _keygen(args) -> int:
    try:
        method = generate_key(Path(args.out), Path(args.public))
    except (SignError, eddsa.CryptoUnavailable) as exc:
        print(f'REFUSED {exc}', file=sys.stderr)
        return EXIT_INVALID
    print(f'wrote {args.out} (private, encrypted, mode 600) and {args.public} (public)')
    print(f'verification method: {method}')
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
    signer.add_argument('--head', help='approvals: the candidate head; the approval is re-derived from the checkout and must match')
    signer.add_argument('--out', help='output file (else stdout)')
    signer.set_defaults(handler=_sign)

    verifier = sub.add_parser('verify', help='verify a signed receipt or approval against pinned keys (read-only)')
    verifier.add_argument('signed')
    verifier.add_argument('--trust', help='another trust store; the report then names it and never claims a pinned key')
    verifier.add_argument('--repo', help='also check commit, tree, policy or patch against this repository')
    verifier.add_argument('--artefact', help='receipts: also check this artefact file (needs --repo)')
    verifier.add_argument('--head', help='approvals: the candidate head; an approval verifies only with --repo and --head')
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
    gen = inner.add_parser('keygen', help='create an encrypted signing key; run it as the separate signing account')
    gen.add_argument('--out', required=True, help='private key file (new, outside the checkout, mode 600)')
    gen.add_argument('--public', required=True, help='public key PEM to write')
    gen.set_defaults(handler=_keygen)
