"""What the develop loop may and may not touch, read from the base revision.

``strategy/overdrive-protected.json`` is the shared protected-path manifest for
schema 2 policies. ``foundation/develop-policy.json`` keeps editable scopes and
loop limits, and names that exact manifest without carrying a second list.
Historical schema 1 revisions retain their extra protected list when loaded.
Frozen reviewer fingerprints remain in ``ante/constructs/frozen.json``.

Every input is read **at the base revision**: a proposal is judged by the rules
that existed before it, so it cannot loosen them.
"""
from __future__ import annotations

import fnmatch
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ante.constructs import frozen as frozen_mod

POLICY_PATH = 'foundation/develop-policy.json'
OVERDRIVE_PATH = 'strategy/overdrive-protected.json'


class PolicyError(ValueError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise PolicyError(f'git {" ".join(args[:2])} failed: {proc.stderr.strip()[:300]}')
    return proc.stdout


@dataclass(frozen=True)
class Policy:
    max_open_proposals: int
    campaign_spend_usd: float
    consecutive_regressions_to_stop: int
    editable_scopes: tuple[str, ...]
    protected: tuple[str, ...]
    overdrive: tuple[str, ...]
    frozen: tuple[str, ...] = ()
    finding_min_sample: int = 30

    def classify(self, path: str) -> str | None:
        """Why ``path`` may not be changed, or None if it may."""
        if path in self.frozen:
            return 'frozen reviewer (ante/constructs/frozen.json)'
        for pattern in self.overdrive:
            if fnmatch.fnmatchcase(path, pattern):
                return f'protected by strategy/overdrive-protected.json ({pattern})'
        for pattern in self.protected:
            if fnmatch.fnmatchcase(path, pattern):
                return f'protected by {POLICY_PATH} ({pattern})'
        if not any(fnmatch.fnmatchcase(path, pattern) for pattern in self.editable_scopes):
            return 'outside every editable scope of the develop loop'
        return None


def at_ref(repo: Path, ref: str) -> Policy:
    try:
        policy = json.loads(git(repo, 'show', f'{ref}:{POLICY_PATH}'))
        overdrive = json.loads(git(repo, 'show', f'{ref}:{OVERDRIVE_PATH}'))
    except json.JSONDecodeError as exc:
        raise PolicyError(f'policy at {ref} is not valid JSON: {exc}') from None
    version = policy.get('schema_version')
    if type(version) is not int:
        raise PolicyError('develop policy schema_version must be an integer')
    if version == 1:
        legacy_protected = tuple(policy['protected'])
    elif version == 2:
        if policy.get('protected_manifest') != OVERDRIVE_PATH or 'protected' in policy:
            raise PolicyError('schema 2 requires the shared protected manifest and no shadow list')
        legacy_protected = ()
    else:
        raise PolicyError(f'unsupported develop policy schema_version: {version}')
    return Policy(
        max_open_proposals=int(policy['max_open_proposals']),
        campaign_spend_usd=float(policy['campaign_spend_usd']),
        consecutive_regressions_to_stop=int(policy['consecutive_regressions_to_stop']),
        editable_scopes=tuple(policy['editable_scopes']),
        protected=legacy_protected,
        overdrive=tuple(overdrive['protected']),
        frozen=frozen_mod.paths(repo, ref),
        finding_min_sample=int(policy.get('finding_min_sample', 30)),
    )


def patch_paths(repo: Path, patch: Path) -> list[str]:
    """Paths a unified diff touches (both sides of a rename), without applying it."""
    out = git(repo, 'apply', '--numstat', '-z', str(patch))
    paths = []
    for record in out.split('\0'):
        if not record:
            continue
        parts = record.split('\t')
        if len(parts) == 3 and parts[2]:
            paths.append(parts[2])
    # -z with renames emits "added\tdeleted\t\0old\0new"; collect those too.
    tokens = [t for t in out.split('\0') if t and '\t' not in t]
    return sorted(set(paths) | set(tokens))
