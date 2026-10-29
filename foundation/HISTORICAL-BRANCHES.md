# Historical branch reconciliation — 29 October 2026

Base inspected: `b719f5789b20288d8fa519f747ed4dac1d560674` (Netrunner Foundation `main`, after #22).

The 16 historical tips retained by the consolidation are now accounted for.
**Thirteen were integrated by squash with identical complete Git trees; two
contain merge-only history that introduces no current content delta; one is a
test-only alternative superseded by the approved P3 fix. No additional content
merge is required by this audit.**

This is stronger than matching commit subjects or individual patch IDs. For
all 13 squashes, `git rev-parse TIP^{tree}` equals
`git rev-parse INTEGRATION^{tree}`, including paths, file modes and blob objects,
and the named integration commit is an ancestor of the inspected main. It
proves their incorporation at that point in history. Main legitimately contains
later changes; this is not a claim that an old branch tip equals today's main.

| Historical reference | Integration or disposition |
|---|---|
| `arch/registry-driven-tools-ci-hardening` | `142c6c1` — identical full tree |
| `docs/sync-operating-metadata` | `8a2fff8` — identical full tree |
| `doctrine/complete-termination-contracts` | `413d3b9` — identical full tree |
| `feat/challenger-veto` | Merge-only history; merge probe leaves main tree unchanged |
| `feat/doctrine-alignment` | `776b5ea` — identical full tree |
| `feat/mispriced-cmo-hardening` | `e696689` — identical full tree |
| `feat/solana-program-engineer` | `1b2492d` — identical full tree |
| `fix/functional-installation` | `6a506f1` — identical full tree |
| `fix/nexus-review-artifact-selection` | `087b87a` / P3 supersedes the test-only alternative |
| `fix/relay-audit` | `99323a6` — identical full tree |
| `fix/review-provenance-and-ci` | `2976cdb` — identical full tree |
| `overdrive/planner-agent` | Merge-only history; merge probe leaves main tree unchanged |
| `perf/benchmark-canonical-agent-loading` | `c4db504` — identical full tree |
| `perf/reduce-conversion-overhead` | `709fdfa` — identical full tree |
| `security/privilege-provenance-hardening` | `35829a2` — identical full tree |
| `strategic-overhaul-v2` | `c19d9f7` — identical full tree |

The test-only branch chooses an artifact through `index.json`; P3 chooses the
first sorted Markdown artifact excluding `REVIEWER.md`. The existing regression
fixture is already fixed by P3. The audit does not assert universal equivalence
of these two selection algorithms and does not replace the approved test.

Exact tips, integration commits, tree object IDs and assertions are retained in
[evidence/historical-branch-reconciliation.json](evidence/historical-branch-reconciliation.json).
The earlier 87-tip inventory remains unchanged as a dated source snapshot.
No branch has been deleted, reset or force-pushed. Development continues from
current `main`; historical refs are retained for provenance. In particular,
blindly merging the old tips would create conflicts with later protected CI,
installer, registry and doctrine changes despite their earlier integration.

## Reproduce the evidence

For each squash row, use the full SHAs from the JSON:

```bash
git rev-parse ORIGINAL_TIP^{tree}
git rev-parse INTEGRATION_COMMIT^{tree}
git diff --exit-code ORIGINAL_TIP^{tree} INTEGRATION_COMMIT^{tree}
git merge-base --is-ancestor INTEGRATION_COMMIT INSPECTED_MAIN
```

For the two merge-only tips, `git rev-list --no-merges TIP --not INSPECTED_MAIN`
is empty, and `git merge-tree --write-tree INSPECTED_MAIN TIP` exits zero with
the inspected main tree as its first output line. The probe writes Git objects;
it does not merge into a branch, modify the index, or touch working files.
