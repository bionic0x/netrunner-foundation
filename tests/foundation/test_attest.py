"""G1a: local eddsa-jcs-2022 signatures for receipts and D-020 approvals.

foundation/ATTEST.md maps the threats T01-T12 to these tests. The suite needs
``cryptography`` and, for the canonical-form cross-check, ``rfc8785``
(.github/requirements/attest.txt). Without them it skips locally; CI sets
ANTE_REQUIRE_ATTEST=1, which turns a missing dependency into a failure.
"""
import ast
import contextlib
import copy
import io as stdio
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ante import cli  # noqa: E402
from ante.attest import commands, documents, eddsa, jcs, multibase, trust  # noqa: E402
from ante.strategy import artifact  # noqa: E402

REQUIRED = os.environ.get('ANTE_REQUIRE_ATTEST') == '1'
VECTORS = Path(__file__).resolve().parent / 'vectors' / 'eddsa-jcs-2022'


def _available(module: str) -> bool:
    try:
        __import__(module)
        return True
    except ImportError:
        if REQUIRED:
            raise
        return False


HAS_CRYPTO = _available('cryptography')
HAS_RFC8785 = _available('rfc8785')
needs_crypto = unittest.skipUnless(HAS_CRYPTO, 'cryptography not installed (see .github/requirements/attest.txt)')
needs_rfc8785 = unittest.skipUnless(HAS_RFC8785, 'rfc8785 not installed (test-only dependency)')

if HAS_CRYPTO:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

AT = '2026-10-29T12:00:00Z'
OTHER = (os.geteuid() + 1) if hasattr(os, 'geteuid') else 1   # a checkout owner that is not the signer


def vector(name: str) -> bytes:
    return (VECTORS / name).read_bytes()


def new_key():
    key = Ed25519PrivateKey.generate()
    raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return key, raw, trust.did_key(raw)


def store_file(directory: Path, entries: list[dict]) -> Path:
    path = directory / 'trusted-keys.json'
    path.write_text(json.dumps({'schema_version': 1, 'keys': entries}))
    return path


def entry(raw: bytes, principal_type: str = 'human', kinds=None, purposes=None) -> dict:
    return {'verification_method': trust.did_key(raw), 'public_key_multibase': multibase.encode_public_key(raw),
            'principal': 'owner:test', 'principal_type': principal_type,
            'proof_purposes': purposes or ['assertionMethod'], 'kinds': kinds or sorted(documents.KINDS)}


def git(repo: Path, *args: str) -> str:
    env = {**os.environ, 'GIT_AUTHOR_DATE': '2026-10-29T10:00:00Z', 'GIT_COMMITTER_DATE': '2026-10-29T10:00:00Z'}
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True,
                          env=env).stdout.strip()


class Repo:
    """A throwaway git repository with ante/ and strategy/contracts.json."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp())
        git(self.dir, 'init', '-q', '-b', 'main')
        git(self.dir, 'config', 'user.email', 'test@example.invalid')
        git(self.dir, 'config', 'user.name', 'test')
        (self.dir / 'ante').mkdir()
        (self.dir / 'ante' / 'core.py').write_text('VALUE = 1\n')
        (self.dir / 'strategy').mkdir()
        (self.dir / 'strategy' / 'contracts.json').write_text('{"tables": 1}\n')
        (self.dir / 'notes.md').write_text('base\n')
        self.commit('base')

    def commit(self, message: str) -> str:
        git(self.dir, 'add', '-A')
        git(self.dir, 'commit', '-q', '-m', message)
        return git(self.dir, 'rev-parse', 'HEAD')

    def artefact(self) -> Path:
        body = {'schema_version': artifact.SCHEMA_VERSION, 'command': 'frame', 'case_id': 'case-1', 'at': AT,
                'input_sha256': '0' * 64, 'parents': [], 'independence_level': None, 'claims': [],
                'claim_history': {}, 'body': {}, 'findings': [], 'verdict': None, 'next_decision': 'x'}
        path = Path(tempfile.mkdtemp()) / 'frame.json'
        path.write_text(json.dumps(artifact.seal({**body, 'artifact_sha256': ''})))
        return path

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = stdio.StringIO(), stdio.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(argv)
    return code, out.getvalue(), err.getvalue()


# --------------------------------------------------------------------------- canonical form

class SignedSubset(unittest.TestCase):
    def test_refuses_what_jcs_and_python_would_write_differently(self):
        refused = [b'{"a":1.5}', b'{"a":1e3}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1,"a":2}',
                   '{"a":"€"}'.encode(), '{"é":1}'.encode(), b'{"a":"\\ud800"}', b'{"a":"\\u0007"}',
                   b'{"a":9007199254740992}', b'\xef\xbb\xbf{"a":1}', b'{"a":"\xff"}', b'{"a":1', b'[1,]']
        for data in refused:
            with self.subTest(data=data), self.assertRaises(jcs.CanonicalError):
                jcs.loads(data)

    def test_hostile_input_is_refused_with_a_reason_not_a_crash(self):
        for data in (b'[' * 100000, b'{"a":' + b'9' * 5000 + b'}', b'"' + b'a' * (jcs.MAX_BYTES + 1) + b'"'):
            with self.assertRaises(jcs.CanonicalError):
                jcs.loads(data)

    def test_errors_do_not_echo_the_input(self):
        secret = 'k' + 'Z' * 200
        for data in ('{"%s":1,"%s":2}' % (secret, secret), '{"a":1.%s}' % ('5' * 50), '{"%s":"\u00e9"}' % secret):
            with self.assertRaises(jcs.CanonicalError) as caught:
                jcs.loads(data.encode())
            self.assertNotIn('ZZZZ', str(caught.exception))
            self.assertNotIn('5555', str(caught.exception))

    def test_booleans_are_not_integers_and_safe_integers_pass(self):
        self.assertEqual(b'{"a":true,"b":9007199254740991,"c":-9007199254740991,"d":null}',
                         jcs.canonical({'b': 2 ** 53 - 1, 'a': True, 'd': None, 'c': -(2 ** 53 - 1)}))
        with self.assertRaises(jcs.CanonicalError):
            jcs.canonical({'a': 1.0})

    @needs_rfc8785
    def test_outside_the_subset_python_and_rfc8785_really_disagree(self):
        import rfc8785
        value = {'': 1, '\U0001f600': 2}       # code-point order differs from UTF-16 order
        python = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
        self.assertNotEqual(python, rfc8785.dumps(value))
        self.assertNotEqual(json.dumps({'a': 100.0}, separators=(',', ':')).encode(), rfc8785.dumps({'a': 100.0}))
        self.assertNotEqual(json.dumps({'a': 1e-7}, separators=(',', ':')).encode(), rfc8785.dumps({'a': 1e-7}))
        for item in (value, {'a': 100.0}, {'a': 1e-7}):
            with self.assertRaises(jcs.CanonicalError):
                jcs.canonical(item)

    @needs_rfc8785
    def test_inside_the_subset_the_bytes_equal_rfc8785(self):
        import rfc8785
        rng = random.Random(8785)
        printable = [chr(c) for c in range(0x20, 0x7f)]

        def text():
            return ''.join(rng.choice(printable) for _ in range(rng.randint(0, 12)))

        def value(depth):
            pick = rng.randint(0, 6 if depth < 4 else 3)
            if pick == 0:
                return rng.choice([True, False, None])
            if pick == 1:
                return rng.randint(-(2 ** 53 - 1), 2 ** 53 - 1)
            if pick in (2, 3):
                return text()
            if pick == 4:
                return [value(depth + 1) for _ in range(rng.randint(0, 4))]
            return {text(): value(depth + 1) for _ in range(rng.randint(0, 5))}

        for _ in range(2000):
            document = {text(): value(0) for _ in range(rng.randint(1, 6))}
            self.assertEqual(rfc8785.dumps(document), jcs.canonical(document))

    def test_production_code_does_not_import_rfc8785(self):
        for path in (ROOT / 'ante').rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            names = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
            names |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
            self.assertNotIn('rfc8785', names, str(path))


class Multibase(unittest.TestCase):
    def test_round_trip_and_leading_zeros(self):
        for data in (b'\0', b'\0\0\x01', bytes(range(64))):
            self.assertEqual(data, multibase.decode(multibase.encode(data)))

    def test_malformed_values_are_refused(self):
        for text in ('', 'z', 'Q123', 'z0OIl'):
            with self.subTest(text=text), self.assertRaises(multibase.MultibaseError):
                multibase.decode(text)
        with self.assertRaises(multibase.MultibaseError):
            multibase.public_key(multibase.encode(b'\xed\x01' + b'\1' * 31))


# --------------------------------------------------------------------------- W3C vector

@needs_crypto
class W3CVector(unittest.TestCase):
    """W3C Data Integrity EdDSA Cryptosuites v1.0, Annex B.3 test vector (eddsa-jcs-2022)."""

    def setUp(self):
        self.signed = jcs.loads(vector('signedJCS.json'))
        self.unsigned = jcs.loads(vector('unsigned.json'))
        pair = json.loads(vector('keyPair.json'))
        self.public = multibase.public_key(pair['publicKeyMultibase'])
        self.private = Ed25519PrivateKey.from_private_bytes(multibase.private_key(pair['privateKeyMultibase']))
        self.method = self.signed['proof']['verificationMethod']

    def resolve(self, method, purpose):
        return self.public if method == self.method and purpose == 'assertionMethod' else None

    def test_canonical_document_and_hashes_match(self):
        self.assertEqual(vector('canonDocJCS.txt').strip(), jcs.canonical(self.unsigned))
        options = {k: v for k, v in self.signed['proof'].items() if k != 'proofValue'}
        self.assertEqual(json.loads(vector('proofConfigJCS.json')), options)
        data = eddsa.hash_data(self.unsigned, options)
        self.assertEqual(vector('proofHashJCS.txt').strip().decode(), data[:32].hex())
        self.assertEqual(vector('docHashJCS.txt').strip().decode(), data[32:].hex())
        self.assertEqual(vector('combinedHashJCS.txt').strip().decode(), data.hex())

    def test_signing_reproduces_the_published_signature(self):
        created = self.signed['proof']['created']
        signed = eddsa.create(self.unsigned, self.method, 'assertionMethod', created, self.private.sign)
        self.assertEqual(self.signed, signed)
        self.assertEqual(vector('sigHexJCS.txt').strip().decode(),
                         multibase.decode(signed['proof']['proofValue']).hex())

    def test_the_published_credential_verifies(self):
        result = eddsa.verify(self.signed, self.resolve)
        self.assertTrue(result.verified, result.detail)
        self.assertEqual(self.unsigned, result.document)

    def test_the_did_key_of_the_vector_encodes_its_key(self):
        self.assertEqual(self.method, trust.did_key(self.public))


# --------------------------------------------------------------------------- proof negatives

@needs_crypto
class ProofNegatives(unittest.TestCase):
    def setUp(self):
        self.key, self.raw, self.method = new_key()
        self.document = {'schema_version': 1, 'kind': 'x', 'value': 'a'}
        self.signed = eddsa.create(self.document, self.method, 'assertionMethod', AT, self.key.sign)

    def resolve(self, method, purpose):
        return self.raw if method == self.method and purpose == 'assertionMethod' else None

    def reason(self, secured, resolve=None):
        return eddsa.verify(secured, resolve or self.resolve).reason

    def test_valid_signature_verifies(self):
        self.assertEqual('VERIFIED', self.reason(self.signed))

    def test_altered_document_fails(self):
        altered = copy.deepcopy(self.signed)
        altered['value'] = 'b'
        self.assertEqual('BAD_SIGNATURE', self.reason(altered))

    def test_altered_created_fails(self):
        altered = copy.deepcopy(self.signed)
        altered['proof']['created'] = '2026-10-29T12:00:01Z'
        self.assertEqual('BAD_SIGNATURE', self.reason(altered))

    def test_altered_purpose_fails_whether_or_not_the_key_is_pinned_for_it(self):
        altered = copy.deepcopy(self.signed)
        altered['proof']['proofPurpose'] = 'authentication'
        self.assertEqual('UNTRUSTED_KEY', self.reason(altered))
        self.assertEqual('BAD_SIGNATURE', self.reason(altered, lambda m, p: self.raw))

    def test_key_substitution_fails(self):
        _, other_raw, _ = new_key()
        self.assertEqual('BAD_SIGNATURE', self.reason(self.signed, lambda m, p: other_raw))

    def test_unknown_method_fails(self):
        self.assertEqual('UNTRUSTED_KEY', self.reason(self.signed, lambda m, p: None))

    def test_malformed_proof_value_fails(self):
        for value in ('Q' + self.signed['proof']['proofValue'][1:], 'z0', multibase.encode(b'\1' * 63)):
            altered = copy.deepcopy(self.signed)
            altered['proof']['proofValue'] = value
            self.assertEqual('MALFORMED', self.reason(altered), value)

    def test_malformed_created_fails(self):
        for value in ('2026-10-29T12:00:00+00:00', '2026-02-30T12:00:00Z', '2026-10-29T12:00:00.5Z', 5):
            altered = copy.deepcopy(self.signed)
            altered['proof']['created'] = value
            self.assertEqual('MALFORMED', self.reason(altered), value)

    def test_unsupported_proof_options_and_sets_are_refused(self):
        altered = copy.deepcopy(self.signed)
        altered['proof']['nonce'] = 'abc'
        self.assertEqual('UNSUPPORTED_PROOF', self.reason(altered))
        self.assertEqual('MALFORMED', self.reason({**self.document, 'proof': [self.signed['proof']]}))
        other = copy.deepcopy(self.signed)
        other['proof']['cryptosuite'] = 'eddsa-rdfc-2022'
        self.assertEqual('UNSUPPORTED_PROOF', self.reason(other))

    def test_context_must_match_the_proof(self):
        document = {'@context': ['https://example.invalid/a'], 'value': 'a'}
        signed = eddsa.create(document, self.method, 'assertionMethod', AT, self.key.sign)
        self.assertEqual('VERIFIED', self.reason(signed))
        altered = copy.deepcopy(signed)
        altered['@context'] = ['https://example.invalid/b']
        self.assertEqual('CONTEXT_MISMATCH', self.reason(altered))

    def test_an_empty_or_malformed_context_is_refused(self):
        for context in ([], '', [''], [1], {'a': 'b'}):
            with self.subTest(context=context), self.assertRaises(eddsa.ProofError):
                eddsa.create({'@context': context, 'value': 'a'}, self.method, 'assertionMethod', AT, self.key.sign)
        signed = eddsa.create({'@context': ['https://example.invalid/a'], 'value': 'a'}, self.method,
                              'assertionMethod', AT, self.key.sign)
        for context in ([], ['']):
            altered = copy.deepcopy(signed)
            altered['@context'] = context
            altered['proof']['@context'] = context
            self.assertEqual('MALFORMED', self.reason(altered), context)

    def test_missing_cryptography_fails_closed(self):
        with mock.patch.object(eddsa, 'ed25519', side_effect=eddsa.CryptoUnavailable('missing')):
            self.assertEqual('CRYPTO_UNAVAILABLE', self.reason(self.signed))

    def test_a_document_with_a_proof_cannot_be_signed_again(self):
        with self.assertRaises(eddsa.ProofError):
            eddsa.create(self.signed, self.method, 'assertionMethod', AT, self.key.sign)


# --------------------------------------------------------------------------- trust store

@needs_crypto
class TrustStore(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)

    def test_the_shipped_store_pins_only_the_owner_human_key(self):
        keys = list(trust.Store.load().keys.values())
        self.assertEqual(['owner:bionic0x'], [key.principal for key in keys])
        self.assertEqual(['human'], [key.principal_type for key in keys])
        self.assertEqual(('ante.d020.approval', 'ante.execution.receipt'), keys[0].kinds)
        self.assertEqual(('assertionMethod',), keys[0].purposes)

    def test_a_did_key_must_encode_the_pinned_key(self):
        _, raw, _ = new_key()
        _, other, _ = new_key()
        bad = {**entry(raw), 'verification_method': trust.did_key(other)}
        with self.assertRaises(trust.TrustError):
            trust.Store.load(store_file(self.dir, [bad]))

    def test_a_method_cannot_be_pinned_twice(self):
        _, raw, _ = new_key()
        with self.assertRaises(trust.TrustError):
            trust.Store.load(store_file(self.dir, [entry(raw), entry(raw)]))

    def test_keys_are_scoped_by_purpose_kind_and_principal_type(self):
        _, raw, method = new_key()
        store = trust.Store.load(store_file(self.dir, [entry(raw, kinds=[documents.RECEIPT])]))
        self.assertEqual(raw, store.resolver(documents.RECEIPT)(method, 'assertionMethod'))
        self.assertIsNone(store.resolver(documents.APPROVAL)(method, 'assertionMethod'))
        self.assertIsNone(store.resolver(documents.RECEIPT)(method, 'authentication'))
        process = trust.Store.load(store_file(self.dir, [entry(raw, principal_type='process')]))
        self.assertIsNone(process.resolver(documents.APPROVAL)(method, 'assertionMethod'))

    def test_a_malformed_store_verifies_nothing(self):
        path = self.dir / 'store.json'
        path.write_text('{"schema_version": 1, "keys": [], "keys": []}')
        with self.assertRaises(trust.TrustError):
            trust.Store.load(path)


# --------------------------------------------------------------------------- documents and repository

@needs_crypto
class Documents(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.close)
        self.key, self.raw, self.method = new_key()
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.store = store_file(self.tmp, [entry(self.raw)])

    def sign(self, document: dict) -> Path:
        signed = commands.sign_document(document, self.key.sign, self.method, AT)
        path = self.tmp / f'{document["kind"]}.signed.json'
        path.write_text(json.dumps(signed, indent=2))
        return path

    def verify(self, path: Path, **kwargs) -> dict:
        return commands.verify_file(str(path), str(self.store), kwargs.get('repo'), kwargs.get('artefact'),
                                    kwargs.get('head'))

    def test_receipt_names_git_object_ids_as_such(self):
        document = documents.receipt(self.repo.artefact(), AT, self.repo.dir)
        self.assertNotIn('code_sha256', document)
        self.assertEqual('sha1', document['source_commit_oid']['object_format'])
        self.assertEqual(git(self.repo.dir, 'rev-parse', 'HEAD:ante'), document['code_tree_oid']['oid'])
        self.assertEqual(git(self.repo.dir, 'rev-parse', 'HEAD'), document['source_commit_oid']['oid'])

    def test_receipt_carries_no_authority(self):
        document = documents.receipt(self.repo.artefact(), AT, self.repo.dir)
        for field in ('mandate_ref', 'expires_at', 'nonce', 'scope', 'principal_id'):
            with self.subTest(field=field), self.assertRaises(documents.DocumentError):
                documents.validate({**document, field: 'x'})

    def test_uncommitted_code_or_policy_is_refused(self):
        artefact = self.repo.artefact()
        (self.repo.dir / 'ante' / 'core.py').write_text('VALUE = 2\n')
        with self.assertRaises(documents.DocumentError):
            documents.receipt(artefact, AT, self.repo.dir)
        git(self.repo.dir, 'checkout', '--', 'ante')
        (self.repo.dir / 'ante' / 'new.py').write_text('')
        with self.assertRaises(documents.DocumentError):
            documents.receipt(artefact, AT, self.repo.dir)

    def test_an_altered_artefact_cannot_get_a_receipt(self):
        artefact = self.repo.artefact()
        data = json.loads(artefact.read_text())
        data['next_decision'] = 'changed'
        artefact.write_text(json.dumps(data))
        with self.assertRaises(documents.DocumentError):
            documents.receipt(artefact, AT, self.repo.dir)

    def test_signed_receipt_verifies_against_repository_and_artefact(self):
        artefact = self.repo.artefact()
        path = self.sign(documents.receipt(artefact, AT, self.repo.dir))
        report = self.verify(path, repo=str(self.repo.dir), artefact=str(artefact))
        self.assertTrue(report['verified'], report)
        self.assertEqual('SYSTEM', report['evidence_origin'])
        self.assertFalse(report['authorizes_action'])
        self.assertEqual('owner:test', report['principal'])

    def test_receipt_for_other_code_or_policy_or_artefact_fails(self):
        artefact = self.repo.artefact()
        document = documents.receipt(artefact, AT, self.repo.dir)
        tree = document['code_tree_oid']['oid']
        other = {**document, 'code_tree_oid': {'object_format': 'sha1', 'oid': ('0' if tree[0] != '0' else '1') + tree[1:]}}
        self.assertEqual('REPOSITORY_MISMATCH', self.verify(self.sign(other), repo=str(self.repo.dir))['reason'])
        policy = {**document, 'policy_sha256': 'f' * 64}
        self.assertEqual('REPOSITORY_MISMATCH', self.verify(self.sign(policy), repo=str(self.repo.dir))['reason'])
        good = self.sign(document)
        stranger = self.repo.artefact()
        data = json.loads(stranger.read_text())
        data['case_id'] = 'case-2'
        stranger.write_text(json.dumps(artifact.seal(data)))
        report = self.verify(good, repo=str(self.repo.dir), artefact=str(stranger))
        self.assertEqual(('REPOSITORY_MISMATCH', False), (report['reason'], report['checks']['artefact']))

    def test_approval_binds_base_result_tree_paths_and_patch(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        (self.repo.dir / 'added.txt').write_text('new\n')
        head = self.repo.commit('change')
        document = documents.approval(base, head, ['apply'], 'PR#0', 'agent:test', AT, self.repo.dir)
        self.assertEqual(['added.txt', 'notes.md'], [p['path'] for p in document['paths']])
        self.assertIsNone(document['paths'][0]['base_blob'])
        self.assertEqual(git(self.repo.dir, 'rev-parse', 'HEAD^{tree}'), document['result_tree'])
        path = self.sign(document)
        report = self.verify(path, repo=str(self.repo.dir), head=head)
        self.assertTrue(report['verified'], report)
        self.assertEqual('CALLER_TRUST_STORE', report['evidence_origin'])
        self.assertEqual((False, str(self.store)), (report['trust_store']['default'], report['trust_store']['path']))
        self.assertFalse(report['authorizes_action'])
        (self.repo.dir / 'notes.md').write_text('changed again\n')
        later = self.repo.commit('different change')
        report = self.verify(path, repo=str(self.repo.dir), head=later)
        self.assertEqual('REPOSITORY_MISMATCH', report['reason'])
        self.assertFalse(report['checks']['result_tree'])

    def test_an_approval_never_covers_a_different_base(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        head = self.repo.commit('change')
        path = self.sign(documents.approval(base, head, ['apply'], 'PR#0', 'agent:test', AT, self.repo.dir))
        # the same edit replayed on a base that has moved on is a different candidate
        git(self.repo.dir, 'checkout', '-q', base)
        (self.repo.dir / 'other.md').write_text('x\n')
        moved = self.repo.commit('base moved')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        replay = self.repo.commit('same change on the moved base')
        report = self.verify(path, repo=str(self.repo.dir), head=replay)
        self.assertEqual('REPOSITORY_MISMATCH', report['reason'])
        self.assertFalse(report['checks']['result_tree'])
        self.assertNotEqual(moved, base)

    def test_approval_schema_refuses_unknown_scope_and_unsorted_paths(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        head = self.repo.commit('change')
        document = documents.approval(base, head, ['apply'], 'PR#0', 'agent:test', AT, self.repo.dir)
        for bad in ({**document, 'scope': ['execute']}, {**document, 'scope': ['merge', 'apply']},
                    {**document, 'scope': [{'a': 'b'}]}, {**document, 'object_format': ['sha1']},
                    {**document, 'paths': document['paths'] * 2}, {**document, 'policy': 'D-021'},
                    {**document, 'author': ' '}):
            with self.assertRaises(documents.DocumentError):
                documents.validate(bad)

    def test_a_process_key_cannot_sign_an_approval(self):
        store = store_file(self.tmp, [entry(self.raw, principal_type='process')])
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        head = self.repo.commit('change')
        path = self.sign(documents.approval(base, head, ['apply'], 'PR#0', 'agent:test', AT, self.repo.dir))
        report = commands.verify_file(str(path), str(store), None, None, None)
        self.assertEqual('UNTRUSTED_KEY', report['reason'])

    def test_verification_is_read_only_and_repeatable(self):
        artefact = self.repo.artefact()
        path = self.sign(documents.receipt(artefact, AT, self.repo.dir))
        before = {p: p.read_bytes() for p in [path, artefact, self.store]}
        status = git(self.repo.dir, 'status', '--porcelain')
        first = self.verify(path, repo=str(self.repo.dir), artefact=str(artefact))
        second = self.verify(path, repo=str(self.repo.dir), artefact=str(artefact))
        self.assertEqual(first, second)
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertEqual(status, git(self.repo.dir, 'status', '--porcelain'))

    def test_duplicate_keys_in_a_signed_file_are_malformed(self):
        artefact = self.repo.artefact()
        path = self.sign(documents.receipt(artefact, AT, self.repo.dir))
        text = path.read_text().replace('"kind":', '"kind": "x", "kind":', 1)
        path.write_text(text)
        self.assertEqual('MALFORMED', self.verify(path)['reason'])

    def commit_store(self, entries: list[dict]) -> None:
        (self.repo.dir / 'foundation' / 'attest').mkdir(parents=True, exist_ok=True)
        (self.repo.dir / 'foundation' / 'attest' / 'trusted-keys.json').write_text(
            json.dumps({'schema_version': 1, 'keys': entries}))
        self.repo.commit('pin')

    def approval_and_head(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        head = self.repo.commit('change')
        return self.sign(documents.approval(base, head, ['apply'], 'PR#0', 'agent:test', AT, self.repo.dir)), head

    def test_a_store_without_the_signing_key_verifies_nothing(self):
        self.commit_store([])
        artefact = self.repo.artefact()
        path = self.sign(documents.receipt(artefact, AT, self.repo.dir))
        report = commands.verify_file(str(path), None, None, None, None, root=self.repo.dir)
        self.assertEqual(('UNTRUSTED_KEY', False, 'UNVERIFIED'),
                         (report['reason'], report['verified'], report['evidence_origin']))

    def test_the_default_store_is_read_from_head_and_claims_a_pinned_key(self):
        self.commit_store([entry(self.raw)])
        path, head = self.approval_and_head()
        report = commands.verify_file(str(path), None, str(self.repo.dir), None, head, root=self.repo.dir)
        self.assertTrue(report['verified'], report)
        self.assertEqual('PINNED_HUMAN_KEY', report['evidence_origin'])
        self.assertEqual('HEAD:foundation/attest/trusted-keys.json', report['trust_store']['path'])
        self.assertTrue(report['trust_store']['default'])

    def test_an_uncommitted_verifier_or_store_fails_every_verification(self):
        self.commit_store([entry(self.raw)])
        path, head = self.approval_and_head()
        for target in ('foundation/attest/trusted-keys.json', 'ante/attest/eddsa.py'):
            with self.subTest(target=target):
                file = self.repo.dir / target
                file.parent.mkdir(parents=True, exist_ok=True)
                original = file.read_bytes() if file.exists() else None
                file.write_text('{"schema_version": 1, "keys": []}' if target.endswith('json') else '# patched\n')
                report = commands.verify_file(str(path), None, str(self.repo.dir), None, head, root=self.repo.dir)
                self.assertEqual(('VERIFIER_MODIFIED', False), (report['reason'], report['verified']))
                if original is None:
                    file.unlink()
                else:
                    file.write_bytes(original)

    def test_an_approval_verifies_only_against_a_candidate(self):
        path, head = self.approval_and_head()
        for repo, candidate in ((None, None), (str(self.repo.dir), None)):
            report = self.verify(path, repo=repo, head=candidate)
            self.assertEqual(('CANDIDATE_REQUIRED', False, True),
                             (report['reason'], report['verified'], report['signature_valid']))

    def test_blob_ids_are_checked(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        (self.repo.dir / 'added.txt').write_text('new\n')
        head = self.repo.commit('change')
        document = documents.approval(base, head, ['apply'], 'PR#0', 'agent:test', AT, self.repo.dir)
        document['paths'][0]['result_blob'] = 'e' * 40
        report = self.verify(self.sign(document), repo=str(self.repo.dir), head=head)
        self.assertEqual(('REPOSITORY_MISMATCH', False), (report['reason'], report['checks']['blobs']))

    def test_a_file_name_cannot_hide_the_patch(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        (self.repo.dir / ':(exclude)notes.md').write_text('x\n')
        head = self.repo.commit('change with pathspec magic in a name')
        names = [entry['path'] for entry in documents.approval(base, head, ['apply'], 'PR', 'a', AT,
                                                                self.repo.dir)['paths']]
        patch = documents._patch(self.repo.dir, base, head, names)
        self.assertIn(b'b/notes.md', patch)
        self.assertIn(b'+changed', patch)

    def test_the_patch_hash_ignores_local_git_configuration_and_attributes(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        head = self.repo.commit('change')
        before = documents.bindings(base, head, self.repo.dir)
        git(self.repo.dir, 'config', 'diff.noprefix', 'true')
        git(self.repo.dir, 'config', 'diff.mnemonicPrefix', 'true')
        git(self.repo.dir, 'config', 'diff.context', '9')
        (self.repo.dir / '.gitattributes').write_text('* -diff\n')
        self.assertEqual(before, documents.bindings(base, head, self.repo.dir))

    def test_unverified_reports_do_not_echo_the_document(self):
        artefact = self.repo.artefact()
        path = self.sign(documents.receipt(artefact, AT, self.repo.dir))
        data = json.loads(path.read_text())
        data['proof']['verificationMethod'] = 'did:example:' + 'A' * 5000
        path.write_text(json.dumps(data))
        report = self.verify(path)
        self.assertEqual('UNTRUSTED_KEY', report['reason'])
        self.assertIsNone(report['verification_method'])
        self.assertNotIn('AAAA', json.dumps(report))

    def test_only_assertion_method_proofs_verify(self):
        store = store_file(self.tmp, [entry(self.raw, purposes=['assertionMethod', 'authentication'])])
        artefact = self.repo.artefact()
        document = documents.receipt(artefact, AT, self.repo.dir)
        signed = eddsa.create(document, self.method, 'authentication', AT, self.key.sign)
        path = self.tmp / 'auth.json'
        path.write_text(json.dumps(signed))
        report = commands.verify_file(str(path), str(store), None, None, None)
        self.assertEqual('UNTRUSTED_KEY', report['reason'])

    def test_signing_rederives_the_approval_from_the_checkout(self):
        base = git(self.repo.dir, 'rev-parse', 'HEAD')
        (self.repo.dir / 'notes.md').write_text('changed\n')
        head = self.repo.commit('change')
        document = documents.approval(base, head, ['apply'], 'PR#0', 'agent:test', AT, self.repo.dir)
        commands.check_before_signing(document, head, self.repo.dir)
        with self.assertRaisesRegex(commands.SignError, '--head'):
            commands.check_before_signing(document, None, self.repo.dir)
        forged = {**document, 'result_tree': ('0' if document['result_tree'][0] != '0' else '1') + document['result_tree'][1:]}
        with self.assertRaisesRegex(commands.SignError, 'result_tree'):
            commands.check_before_signing(forged, head, self.repo.dir)
        self.assertIn('notes.md', commands.summary(document))
        receipt = documents.receipt(self.repo.artefact(), AT, self.repo.dir)
        commands.check_before_signing(receipt, None, self.repo.dir)
        with self.assertRaisesRegex(commands.SignError, 'policy'):
            commands.check_before_signing({**receipt, 'policy_sha256': 'f' * 64}, None, self.repo.dir)


# --------------------------------------------------------------------------- signing guards and CLI

@needs_crypto
class SigningGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.key, self.raw, self.method = new_key()

    def write_key(self, directory: Path, encrypted: bool = True, mode: int = 0o600) -> Path:
        algorithm = (serialization.BestAvailableEncryption(b'correct horse') if encrypted
                     else serialization.NoEncryption())
        path = directory / 'owner.pem'
        path.write_bytes(self.key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                algorithm))
        path.chmod(mode)
        return path

    def test_a_key_inside_the_checkout_is_refused(self):
        inside = Path(tempfile.mkdtemp(dir=ROOT))
        self.addCleanup(shutil.rmtree, inside, True)
        with self.assertRaisesRegex(commands.SignError, 'inside the checkout'):
            commands.file_signer(self.write_key(inside), self.method, lambda: b'correct horse', checkout_uid=OTHER)

    def test_the_account_that_owns_the_checkout_cannot_sign(self):
        with self.assertRaisesRegex(commands.SignError, 'separate signing account'):
            commands.file_signer(self.write_key(self.tmp), self.method, lambda: b'correct horse',
                                 checkout_uid=os.geteuid())

    def test_the_signing_account_must_own_the_key(self):
        path = self.write_key(self.tmp)
        with mock.patch.object(os, 'geteuid', return_value=OTHER + 1):
            with self.assertRaisesRegex(commands.SignError, 'not owned by the account'):
                commands.file_signer(path, self.method, lambda: b'correct horse', checkout_uid=OTHER)

    def test_a_key_readable_by_others_is_refused(self):
        with self.assertRaisesRegex(commands.SignError, 'chmod 600'):
            commands.file_signer(self.write_key(self.tmp, mode=0o644), self.method, lambda: b'correct horse',
                                  checkout_uid=OTHER)

    def test_an_unencrypted_key_is_refused(self):
        with self.assertRaisesRegex(commands.SignError, 'not encrypted'):
            commands.file_signer(self.write_key(self.tmp, encrypted=False), self.method, lambda: b'x',
                                  checkout_uid=OTHER)

    def test_without_a_terminal_there_is_no_passphrase(self):
        with mock.patch.object(os, 'open', side_effect=OSError('no tty')):
            with self.assertRaisesRegex(commands.SignError, 'typed by a person'):
                commands.read_passphrase()

    def test_the_cli_refuses_to_sign_without_a_terminal(self):
        repo = Repo()
        self.addCleanup(repo.close)
        unsigned = self.tmp / 'receipt.json'
        unsigned.write_text(json.dumps(documents.receipt(repo.artefact(), AT, repo.dir)))
        key_bytes = self.write_key(self.tmp).read_bytes()
        with mock.patch.object(commands, 'read_key_file', return_value=key_bytes), \
                mock.patch.object(commands, 'check_before_signing'), \
                mock.patch.object(os, 'open', side_effect=OSError('no tty')):
            code, out, err = run(['sign', str(unsigned), '--key', str(self.write_key(self.tmp)),
                                  '--method', self.method, '--at', AT])
        self.assertEqual((2, ''), (code, out))
        self.assertIn('REFUSED', err)

    def test_wrong_passphrase_and_wrong_did_key_are_refused(self):
        path = self.write_key(self.tmp)
        with self.assertRaisesRegex(commands.SignError, 'wrong passphrase'):
            commands.file_signer(path, self.method, lambda: b'wrong', checkout_uid=OTHER)
        _, _, other = new_key()
        with self.assertRaisesRegex(commands.SignError, 'not this key'):
            commands.file_signer(path, other, lambda: b'correct horse', checkout_uid=OTHER)

    def test_a_typed_passphrase_signs_a_document_that_verifies(self):
        repo = Repo()
        self.addCleanup(repo.close)
        signer = commands.file_signer(self.write_key(self.tmp), self.method, lambda: b'correct horse',
                                      checkout_uid=OTHER)
        signed = commands.sign_document(documents.receipt(repo.artefact(), AT, repo.dir), signer, self.method, AT)
        path = self.tmp / 'signed.json'
        path.write_text(json.dumps(signed))
        store = store_file(self.tmp, [entry(self.raw)])
        code, out, _ = run(['verify', str(path), '--trust', str(store), '--repo', str(repo.dir)])
        self.assertEqual(0, code, out)
        self.assertTrue(json.loads(out)['verified'])

    def test_keygen_creates_a_key_that_signs_and_is_never_overwritten(self):
        out, public = self.tmp / 'new.pem', self.tmp / 'new.pub.pem'
        method = commands.generate_key(out, public, lambda: b'correct horse', checkout_uid=OTHER)
        self.assertEqual(0o600, out.stat().st_mode & 0o777)
        self.assertIn(b'ENCRYPTED PRIVATE KEY', out.read_bytes())
        signer = commands.file_signer(out, method, lambda: b'correct horse', checkout_uid=OTHER)
        self.assertTrue(callable(signer))
        code, shown, err = run(['attest', 'key', str(public), '--principal', 'owner:test', '--principal-type', 'human'])
        self.assertEqual(0, code, err)
        self.assertEqual(method, json.loads(shown)['verification_method'])
        with self.assertRaisesRegex(commands.SignError, 'already exists'):
            commands.generate_key(out, self.tmp / 'other.pub.pem', lambda: b'x', checkout_uid=OTHER)

    def test_keygen_refuses_the_checkout_and_its_owner(self):
        with self.assertRaisesRegex(commands.SignError, 'inside the checkout'):
            commands.generate_key(commands.ROOT / 'k.pem', self.tmp / 'k.pub', lambda: b'x', checkout_uid=OTHER)
        with self.assertRaisesRegex(commands.SignError, 'owns the checkout'):
            commands.generate_key(self.tmp / 'k2.pem', self.tmp / 'k2.pub', lambda: b'x', checkout_uid=os.geteuid())
        self.assertFalse((self.tmp / 'k2.pem').exists())

    def test_keygen_needs_two_matching_typed_passphrases(self):
        answers = iter([b'one', b'two'])
        with mock.patch.object(commands, 'read_passphrase', side_effect=lambda *_: next(answers)):
            with self.assertRaisesRegex(commands.SignError, 'differ'):
                commands._passphrase_twice()
        with mock.patch.object(os, 'open', side_effect=OSError('no tty')):
            with self.assertRaisesRegex(commands.SignError, 'typed by a person'):
                commands._passphrase_twice()

    def test_cli_builds_documents_and_trust_entries(self):
        repo = Repo()
        self.addCleanup(repo.close)
        code, out, err = run(['attest', 'receipt', str(repo.artefact()), '--at', AT, '--repo', str(repo.dir)])
        self.assertEqual(0, code, err)
        self.assertEqual(documents.RECEIPT, documents.validate(jcs.loads(out)))
        public = self.tmp / 'owner.pub.pem'
        public.write_bytes(self.key.public_key().public_bytes(serialization.Encoding.PEM,
                                                             serialization.PublicFormat.SubjectPublicKeyInfo))
        code, out, err = run(['attest', 'key', str(public), '--principal', 'owner:test', '--principal-type', 'human'])
        self.assertEqual(0, code, err)
        self.assertEqual(entry(self.raw), json.loads(out))

    def test_cli_verify_exits_4_when_not_verified(self):
        path = self.tmp / 'bad.json'
        path.write_text('{"a": 1.5}')
        code, out, _ = run(['verify', str(path)])
        self.assertEqual(4, code)
        self.assertEqual('MALFORMED', json.loads(out)['reason'])


# --------------------------------------------------------------------------- boundaries

class Boundaries(unittest.TestCase):
    def test_no_strategy_learning_or_construct_module_reads_a_signature(self):
        """T07: a signature cannot reach a claim status; only the CLI and attest itself import attest."""
        allowed = {'ante/cli.py'}
        for path in (ROOT / 'ante').rglob('*.py'):
            name = str(path.relative_to(ROOT))
            if name in allowed or name.startswith('ante/attest/'):
                continue
            tree = ast.parse(path.read_text(encoding='utf-8'))
            modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
            modules |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
            from_ante = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                         and node.module == 'ante' for alias in node.names}
            self.assertFalse({m for m in modules if m.startswith('ante.attest')} or 'attest' in from_ante, name)

    def test_the_verifier_and_the_trust_store_are_protected_from_self_development(self):
        """T08: both manifests protect the verifier, the trust store and their tests."""
        import fnmatch
        targets = ('ante/attest/eddsa.py', 'ante/attest/trust.py', 'foundation/attest/trusted-keys.json',
                   'tests/foundation/test_attest.py', 'tests/foundation/vectors/eddsa-jcs-2022/signedJCS.json')
        develop = json.loads((ROOT / 'foundation/develop-policy.json').read_text())['protected']
        overdrive = json.loads((ROOT / 'strategy/overdrive-protected.json').read_text())['protected']
        for target in targets:
            self.assertTrue(any(fnmatch.fnmatch(target, pattern) for pattern in develop), target)
        for target in targets[:3]:
            self.assertTrue(any(fnmatch.fnmatch(target, pattern) for pattern in overdrive), target)


if __name__ == '__main__':
    unittest.main()
