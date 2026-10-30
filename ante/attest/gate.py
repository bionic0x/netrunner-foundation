"""The D-020 admission gate: does a change to protected paths carry a verified human approval?

    ante attest gate --base REV --head REV --pr N [--repo DIR]

The answer is PROCEED or HOLD. Any doubt is HOLD. The gate is informational: it
reports, it never merges, blocks or authorises (``authorizes_action`` is false);
the host that merges decides what to do with the report.

A signed approval binds the exact head it approves, so it cannot live inside
that head. It is stored in the repository as ``foundation/approvals/PR-N.json``
in one last commit that adds nothing else. The gate then treats the parent of
that commit as the candidate and verifies the approval against it. Anything else
(a later merge, a second file) leaves the approval unbound and the answer HOLD.

Which paths are protected is read at ``--base``, the target branch, so the change
cannot loosen its own rules; the trust store is read there too, so it cannot pin
a key for its own approval.
"""
from __future__ import annotations

import fnmatch
import re
import tempfile
from pathlib import Path

from ante.attest import commands, documents
from ante.develop import policy as policy_mod

APPROVALS_DIR = 'foundation/approvals'
PROCEED, HOLD = 'PROCEED', 'HOLD'


def approval_path(pr: int) -> str:
    return f'{APPROVALS_DIR}/PR-{pr}.json'


def protected_paths(rules: policy_mod.Policy, names: list[str]) -> list[str]:
    """Paths the shared manifest, the legacy list or the frozen reviewers protect."""
    def hit(name: str) -> bool:
        return name in rules.frozen or any(fnmatch.fnmatchcase(name, pattern)
                                           for pattern in (*rules.overdrive, *rules.protected))
    return [name for name in names if hit(name)]


def decide(repo: Path, base: str, head: str, pr: int) -> dict:
    report = {'decision': HOLD, 'reason': 'UNDETERMINED', 'detail': '', 'authorizes_action': False,
              'pr': pr, 'base': None, 'target_base': None, 'candidate': None, 'protected_paths': [], 'approval': None}
    if not isinstance(pr, int) or isinstance(pr, bool) or pr < 1:
        report['reason'], report['detail'] = 'USAGE', 'the pull request number must be a positive integer'
        return report
    try:
        base_commit = documents.resolve(repo, f'{base}^{{commit}}')
        head_commit = documents.resolve(repo, f'{head}^{{commit}}')
        if base_commit is None or head_commit is None:
            report['reason'], report['detail'] = 'REVISION_UNKNOWN', 'base or head is not a commit of this repository'
            return report
        report['target_base'] = base_commit
        merge_base = documents._git(repo, 'merge-base', base_commit, head_commit, check=False).stdout.decode().strip()
        if not merge_base:
            report['reason'], report['detail'] = 'NO_MERGE_BASE', 'base and head share no history'
            return report
        path = approval_path(pr)
        parents = documents._git(repo, 'rev-list', '--parents', '-n1', head_commit).stdout.split()[1:]
        parent = parents[0].decode() if len(parents) == 1 else None
        # The approval commit adds or replaces exactly the approval file.
        candidate = head_commit
        if parent is not None and documents._changed(repo, parent, head_commit) == [path]:
            candidate = parent
        report['base'], report['candidate'] = merge_base, candidate
        rules = policy_mod.at_ref(repo, base_commit)
        names = documents._changed(repo, merge_base, candidate)
        protected = protected_paths(rules, names)
        # A target-only update need not move the merge base. Compare entries,
        # including modes, for every input of a protected patch. Unrelated
        # target changes can leave all those reviewed inputs intact.
        stale_inputs = bool(protected) and any(
            documents._git(repo, 'ls-tree', '-z', merge_base, '--', name).stdout !=
            documents._git(repo, 'ls-tree', '-z', base_commit, '--', name).stdout
            for name in names)
    except (documents.DocumentError, policy_mod.PolicyError, OSError, KeyError, ValueError) as exc:
        report['reason'], report['detail'] = 'UNDETERMINED', f'{type(exc).__name__}: {exc}'[:300]
        return report
    report['protected_paths'] = protected
    if not names:
        report.update(decision=PROCEED, reason='NO_CHANGES', detail='the candidate does not differ from the base')
        return report
    if not protected:
        report.update(decision=PROCEED, reason='NO_PROTECTED_PATHS',
                      detail=f'{len(names)} changed path(s), none protected at the base revision')
        return report
    if stale_inputs:
        report['reason'] = 'STALE_BASE'
        report['detail'] = 'the target branch changed an input or mode of the reviewed patch; renew its approval'
        return report
    blob = documents.committed(repo, head_commit, path)
    if blob is None:
        report['reason'] = 'APPROVAL_MISSING'
        report['detail'] = f'{len(protected)} protected path(s) changed and {path} is not in the head'
        return report
    with tempfile.TemporaryDirectory() as directory:
        file = Path(directory) / 'approval.json'
        file.write_bytes(blob)
        verified = commands.verify_file(str(file), None, str(repo), None, candidate, root=repo, trust_ref=base_commit)
        document = commands._load(str(file)) if verified['verified'] else None
    report['approval'] = {key: verified.get(key) for key in (
        'verified', 'signature_valid', 'reason', 'detail', 'principal', 'verification_method', 'created',
        'evidence_origin', 'trust_store')}
    if not verified['verified']:
        report['reason'], report['detail'] = 'APPROVAL_NOT_VERIFIED', f'{verified["reason"]}: {verified["detail"]}'[:300]
        return report
    if verified['evidence_origin'] != 'PINNED_HUMAN_KEY':
        report['reason'], report['detail'] = 'NOT_A_PINNED_HUMAN_KEY', f'evidence origin is {verified["evidence_origin"]}'
        return report
    if document['base_commit'] != merge_base:
        report['reason'] = 'STALE_BASE'
        report['detail'] = 'the approval was made against another base than the merge base; renew it'
        return report
    if 'merge' not in document['scope']:
        report['reason'], report['detail'] = 'SCOPE_LACKS_MERGE', f'approval scope is {", ".join(document["scope"])}'
        return report
    if not re.search(rf'(?:#|/pull/){pr}(?!\d)', document['review_ref']):
        report['reason'] = 'REVIEW_REF_MISMATCH'
        report['detail'] = f'review_ref {document["review_ref"]!r} does not name pull request {pr}'
        return report
    report.update(decision=PROCEED, reason='APPROVED',
                  detail=f'{len(protected)} protected path(s) covered by a verified approval of a pinned human key')
    return report
