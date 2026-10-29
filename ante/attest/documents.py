"""The two signed document kinds, their schemas and their git references.

Execution receipt (``ante.execution.receipt``) — a statement about a finished
event: this sealed artefact, this code, this policy. It carries no mandate,
scope, expiry, nonce or permission, and presenting it again triggers nothing.

    schema_version     1
    kind               ante.execution.receipt
    artifact_sha256    the artefact's own sealed digest, checked before building
    source_commit_oid  {object_format, oid}: the commit the receipt describes
    code_tree_oid      {object_format, oid}: the tree object of ante/ in that commit
    policy_sha256      SHA-256 of strategy/contracts.json as committed there
    issued_at          the signer's statement of time, not a time witness

D-020 approval (``ante.d020.approval``) — the owner's approval of one exact
maintenance change. It is not a receipt and not an authorisation to act: the
host still checks D-020, the patch and the one-time scope before applying.

    schema_version  1
    kind            ante.d020.approval
    policy          D-020
    object_format   sha1 | sha256, as reported by git
    base_commit     the reviewed base
    result_tree     the root tree after the change; this is the binding
    patch_sha256    SHA-256 of the diff bytes the reviewer saw (fixed git options)
    paths           [{path, base_blob, result_blob}] for every changed path
    scope           subset of ["apply", "merge"]
    review_ref      where the review happened
    author          who prepared the change (agent or human), recorded apart from the signer
    issued_at       as above

Git object ids are named as such; a SHA-1 tree id is never called a SHA-256.
"""
from __future__ import annotations

import contextlib
import hashlib
import subprocess
from pathlib import Path

from ante.attest import jcs
from ante.core import time as ante_time
from ante.paths import ROOT
from ante.strategy import artifact

RECEIPT = 'ante.execution.receipt'
APPROVAL = 'ante.d020.approval'
KINDS = (RECEIPT, APPROVAL)
OBJECT_FORMATS = {'sha1': 40, 'sha256': 64}
SCOPES = ('apply', 'merge')
CODE_PATH = 'ante'
POLICY_PATH = 'strategy/contracts.json'
# Every option that git configuration could change in a patch is pinned here, so
# patch_sha256 is the same on any machine with git >= 2.40. Attributes are read
# from the head commit, not from the working tree or the user's configuration.
DIFF_CONFIG = ('-c', 'core.quotepath=true', '-c', 'core.attributesFile=/dev/null',
               '-c', 'diff.suppressBlankEmpty=false', '-c', 'diff.noprefix=false',
               '-c', 'diff.mnemonicPrefix=false', '-c', 'diff.relative=false')
DIFF_OPTIONS = ('diff', '--binary', '--full-index', '--no-color', '--no-ext-diff', '--no-textconv',
                '--no-renames', '--diff-algorithm=myers', '--indent-heuristic', '-U3',
                '--inter-hunk-context=0', '--src-prefix=a/', '--dst-prefix=b/', '--no-relative',
                '--submodule=short', '-O/dev/null')
MIN_GIT = (2, 40)
RECEIPT_KEYS = ('schema_version', 'kind', 'artifact_sha256', 'source_commit_oid', 'code_tree_oid',
                'policy_sha256', 'issued_at')
APPROVAL_KEYS = ('schema_version', 'kind', 'policy', 'object_format', 'base_commit', 'result_tree',
                 'patch_sha256', 'paths', 'scope', 'review_ref', 'author', 'issued_at')


class DocumentError(ValueError):
    """The document or the repository state does not support the statement."""


_TRUSTED: set[str] = set()


@contextlib.contextmanager
def trusting(repo: Path):
    """Let git read ``repo`` although another account owns it (``ante sign`` under its own account).

    Only for the checkout whose code is already running; every call stays read-only.
    """
    path = str(Path(repo).resolve())
    _TRUSTED.add(path)
    try:
        yield
    finally:
        _TRUSTED.discard(path)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Read-only git with pathspec magic off and no fsmonitor hook from an untrusted repository."""
    command = ['git', '--literal-pathspecs', '-c', 'core.fsmonitor=false']
    path = str(Path(repo).resolve())
    if path in _TRUSTED:
        command += ['-c', f'safe.directory={path}']
    result = subprocess.run([*command, '-C', path, *args], capture_output=True)
    if check and result.returncode != 0:
        raise DocumentError(f'git {args[0] if args else ""} failed (exit {result.returncode})')
    return result


def _git_version() -> tuple[int, int]:
    out = subprocess.run(['git', 'version'], capture_output=True).stdout.decode('ascii', 'replace')
    try:
        major, minor = out.split()[2].split('.')[:2]
        return int(major), int(minor)
    except (IndexError, ValueError):
        return (0, 0)


def object_format(repo: Path) -> str:
    fmt = _git(repo, 'rev-parse', '--show-object-format').stdout.decode().strip()
    if fmt not in OBJECT_FORMATS:
        raise DocumentError('unsupported git object format')
    return fmt


def resolve(repo: Path, spec: str) -> str | None:
    result = _git(repo, 'rev-parse', '--verify', '--quiet', '--end-of-options', spec, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.decode().strip() or None


def _require(repo: Path, spec: str) -> str:
    oid = resolve(repo, spec)
    if oid is None:
        raise DocumentError(f'{spec} does not exist in {repo}')
    return oid


def dirty(repo: Path, paths: list[str]) -> list[str]:
    out = _git(repo, 'status', '--porcelain', '--untracked-files=all', '--', *paths).stdout
    return [line for line in out.decode('utf-8', 'replace').splitlines() if line.strip()]


def committed(repo: Path, rev: str, path: str) -> bytes | None:
    """The bytes of ``path`` as committed at ``rev``, or ``None`` when absent."""
    result = _git(repo, 'show', f'{rev}:{path}', check=False)
    return result.stdout if result.returncode == 0 else None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc(at: str) -> str:
    """``--at`` as ``YYYY-MM-DDTHH:MM:SSZ``; sub-second precision is not signed."""
    return ante_time.parse(at, 'at').strftime('%Y-%m-%dT%H:%M:%SZ')


def _oid(value: object, fmt: str, where: str) -> None:
    if not isinstance(value, str) or len(value) != OBJECT_FORMATS[fmt] or any(c not in '0123456789abcdef' for c in value):
        raise DocumentError(f'{where}: not a {fmt} object id')


def _hex64(value: object, where: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise DocumentError(f'{where}: not a lowercase SHA-256 hex digest')


def _text(value: object, where: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise DocumentError(f'{where}: non-empty text required')


def _git_ref(value: object, where: str) -> str:
    if not isinstance(value, dict) or set(value) != {'object_format', 'oid'}:
        raise DocumentError(f'{where}: expected {{object_format, oid}}')
    fmt = value['object_format']
    if not isinstance(fmt, str) or fmt not in OBJECT_FORMATS:
        raise DocumentError(f'{where}.object_format must be sha1 or sha256')
    _oid(value['oid'], fmt, f'{where}.oid')
    return fmt


def validate(document: object) -> str:
    """Check the unsigned document against its schema and return its kind."""
    if not isinstance(document, dict):
        raise DocumentError('a signed document is a JSON object')
    jcs.check(document)
    kind = document.get('kind')
    if document.get('schema_version') != 1 or kind not in KINDS:
        raise DocumentError(f'expected schema_version 1 and kind in {", ".join(KINDS)}')
    expected = RECEIPT_KEYS if kind == RECEIPT else APPROVAL_KEYS
    if set(document) != set(expected):
        extra, missing = len(set(document) - set(expected)), sorted(set(expected) - set(document))
        raise DocumentError(f'{kind}: {extra} unexpected field(s), missing {", ".join(missing) or "none"}')
    if not isinstance(document['issued_at'], str) or utc(document['issued_at']) != document['issued_at']:
        raise DocumentError('issued_at must be YYYY-MM-DDTHH:MM:SSZ')
    if kind == RECEIPT:
        _hex64(document['artifact_sha256'], 'artifact_sha256')
        _hex64(document['policy_sha256'], 'policy_sha256')
        if _git_ref(document['source_commit_oid'], 'source_commit_oid') != \
                _git_ref(document['code_tree_oid'], 'code_tree_oid'):
            raise DocumentError('source_commit_oid and code_tree_oid use different object formats')
        return kind
    fmt = document['object_format']
    if not isinstance(fmt, str) or fmt not in OBJECT_FORMATS:
        raise DocumentError('object_format must be sha1 or sha256')
    if document['policy'] != 'D-020':
        raise DocumentError('policy must be D-020')
    _oid(document['base_commit'], fmt, 'base_commit')
    _oid(document['result_tree'], fmt, 'result_tree')
    _hex64(document['patch_sha256'], 'patch_sha256')
    paths = document['paths']
    if not isinstance(paths, list) or not paths:
        raise DocumentError('paths must list every changed path')
    names = []
    for index, entry in enumerate(paths):
        if not isinstance(entry, dict) or set(entry) != {'path', 'base_blob', 'result_blob'}:
            raise DocumentError(f'paths[{index}]: expected {{path, base_blob, result_blob}}')
        _text(entry['path'], f'paths[{index}].path')
        for side in ('base_blob', 'result_blob'):
            if entry[side] is not None:
                _oid(entry[side], fmt, f'paths[{index}].{side}')
        if entry['base_blob'] is None and entry['result_blob'] is None:
            raise DocumentError(f'paths[{index}]: a path cannot be absent on both sides')
        names.append(entry['path'])
    if names != sorted(set(names)):
        raise DocumentError('paths must be sorted and unique')
    scope = document['scope']
    if (not isinstance(scope, list) or not scope or not all(isinstance(s, str) and s in SCOPES for s in scope)
            or scope != sorted(set(scope))):
        raise DocumentError(f'scope must be a sorted, non-empty subset of {", ".join(SCOPES)}')
    _text(document['review_ref'], 'review_ref')
    _text(document['author'], 'author')
    return kind


def receipt(artefact_path: Path | str, at: str, repo: Path = ROOT) -> dict:
    """An unsigned execution receipt for a sealed artefact at the checkout's HEAD."""
    try:
        art = artifact.load_parent(artefact_path)
    except artifact.LineageError as exc:
        raise DocumentError(f'artefact: {exc}') from None
    changed = dirty(repo, [CODE_PATH, POLICY_PATH])
    if changed:
        raise DocumentError(f'{CODE_PATH}/ or {POLICY_PATH} has uncommitted changes ({len(changed)}); '
                            'a receipt names committed code only')
    fmt = object_format(repo)
    commit = _require(repo, 'HEAD^{commit}')
    document = {
        'schema_version': 1,
        'kind': RECEIPT,
        'artifact_sha256': art['artifact_sha256'],
        'source_commit_oid': {'object_format': fmt, 'oid': commit},
        'code_tree_oid': {'object_format': fmt, 'oid': _require(repo, f'{commit}:{CODE_PATH}')},
        'policy_sha256': _sha256(_git(repo, 'show', f'{commit}:{POLICY_PATH}').stdout),
        'issued_at': utc(at),
    }
    validate(document)
    return document


def _changed(repo: Path, base: str, head: str) -> list[str]:
    out = _git(repo, 'diff', '--name-only', '--no-renames', '-z', base, head).stdout
    return sorted(name.decode('utf-8', 'replace') for name in out.split(b'\0') if name)


def _patch(repo: Path, base: str, head: str, paths: list[str]) -> bytes:
    if _git_version() < MIN_GIT:
        raise DocumentError('patch hashes need git 2.40 or later (--attr-source)')
    return _git(repo, *DIFF_CONFIG, f'--attr-source={head}', *DIFF_OPTIONS, base, head, '--', *paths).stdout


BINDING_KEYS = ('object_format', 'base_commit', 'result_tree', 'patch_sha256', 'paths')


def bindings(base: str, head: str, repo: Path = ROOT) -> dict:
    """What an approval of the change from ``base`` to ``head`` binds, read from git."""
    fmt = object_format(repo)
    base_commit = _require(repo, f'{base}^{{commit}}')
    head_commit = _require(repo, f'{head}^{{commit}}')
    names = _changed(repo, base_commit, head_commit)
    if not names:
        raise DocumentError('base and head do not differ; there is nothing to approve')
    return {
        'object_format': fmt,
        'base_commit': base_commit,
        'result_tree': _require(repo, f'{head_commit}^{{tree}}'),
        'patch_sha256': _sha256(_patch(repo, base_commit, head_commit, names)),
        'paths': [{'path': name, 'base_blob': resolve(repo, f'{base_commit}:{name}'),
                   'result_blob': resolve(repo, f'{head_commit}:{name}')} for name in names],
    }


def approval(base: str, head: str, scope: list[str], review_ref: str, author: str, at: str,
             repo: Path = ROOT) -> dict:
    """An unsigned D-020 approval of the change from ``base`` to ``head``."""
    document = {'schema_version': 1, 'kind': APPROVAL, 'policy': 'D-020', **bindings(base, head, repo),
                'scope': sorted(set(scope)), 'review_ref': review_ref, 'author': author, 'issued_at': utc(at)}
    try:
        validate(document)
    except jcs.CanonicalError as exc:
        raise DocumentError(f'cannot be signed: {exc}') from None
    return document


def check_receipt(document: dict, repo: Path, artefact_path: str | None) -> dict:
    """Compare a receipt with the repository and, optionally, the artefact file."""
    checks: dict = {}
    fmt = document['source_commit_oid']['object_format']
    checks['object_format'] = object_format(repo) == fmt
    commit = document['source_commit_oid']['oid']
    checks['commit_present'] = resolve(repo, f'{commit}^{{commit}}') == commit
    if checks['commit_present']:
        checks['code_tree'] = resolve(repo, f'{commit}:{CODE_PATH}') == document['code_tree_oid']['oid']
        policy = _git(repo, 'show', f'{commit}:{POLICY_PATH}', check=False)
        checks['policy'] = policy.returncode == 0 and _sha256(policy.stdout) == document['policy_sha256']
    if artefact_path is not None:
        try:
            art = artifact.load_parent(artefact_path)
            checks['artefact'] = art['artifact_sha256'] == document['artifact_sha256']
        except artifact.LineageError:
            checks['artefact'] = False
    return checks


def check_approval(document: dict, repo: Path, head: str | None) -> dict:
    """Compare an approval with the repository and, optionally, a candidate head."""
    checks: dict = {}
    checks['object_format'] = object_format(repo) == document['object_format']
    base = document['base_commit']
    checks['base_present'] = resolve(repo, f'{base}^{{commit}}') == base
    if head is not None and checks['base_present']:
        head_commit = resolve(repo, f'{head}^{{commit}}')
        if head_commit is None:
            checks['head_present'] = False
            return checks
        checks['result_tree'] = resolve(repo, f'{head_commit}^{{tree}}') == document['result_tree']
        names = _changed(repo, base, head_commit)
        checks['paths'] = names == [entry['path'] for entry in document['paths']]
        checks['blobs'] = checks['paths'] and all(
            resolve(repo, f'{base}:{entry["path"]}') == entry['base_blob']
            and resolve(repo, f'{head_commit}:{entry["path"]}') == entry['result_blob']
            for entry in document['paths'])
        checks['patch'] = _sha256(_patch(repo, base, head_commit, names)) == document['patch_sha256']
    return checks
