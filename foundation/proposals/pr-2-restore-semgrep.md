# PR #2: exact reversal of the vulnerable Semgrep update

Proposed patch: `pr-2-restore-semgrep.patch`.

The only remaining open PR upgrades Semgrep, Zizmor and Hypothesis. Its hosted
OSV job fails because the Semgrep lock change downgrades `mcp` from 1.30.0 to
1.29.0, which has four reported vulnerabilities (one high, three medium).

The proposed correction reverses only the two Semgrep file diffs. It retains
Semgrep 1.179.0 and MCP 1.30.0 with the existing locked hashes. Zizmor 1.31.1
and Hypothesis 6.170.5 remain in the PR. It introduces no security exception.

## Exact validation

The PR diff was reproduced in an isolated temporary Git index. Its two changed
blob ids matched the PR's index lines. Applying the inverse patch passed
`git apply --check` and restored the original blobs exactly:

| File | Restored Git blob |
|---|---|
| `.github/requirements/semgrep.in` | `afb8d7d760ca5e86d2df98640f9adc810fe8269f` |
| `.github/requirements/semgrep.txt` | `bb6d2a98c424affc00bcc1cc7c4194f176f3ce9d` |

This proposal has not been applied to the PR or any protected checkout path.
Hosted CI must rerun after application; a green result is not assumed.

## Owner decision

The supplied mandate's section 11 says to stop and ask before any protected-path
change that is not a mechanical extraction. These two `.github/**` dependency
files are protected, and this operation is a dependency rollback. Authorize this
specific exception, or have a human apply the attached exact reversal. Existing
authorization to merge PRs does not itself amend that source-change restriction.

## Foundation CI follow-up

The already merged PR #11 now shows all 13 checks passed on head `275ab22`.
That verifies the existing hosted checks; the new Foundation-specific CI wiring
remains a separate protected proposal under D-017/D-020.
