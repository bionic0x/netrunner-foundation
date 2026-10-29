# Local signatures: receipts and D-020 approvals (G0 + G1a)

`ante sign` and `ante verify` add one capability: a document can be bound to a
pinned Ed25519 key, offline, in the W3C `eddsa-jcs-2022` format, and anyone with
the repository can check the binding. The code is `ante/attest/`, the tests are
`tests/foundation/test_attest.py`, the trust store is
`foundation/attest/trusted-keys.json`.

## What a signature proves

A verified signature proves one thing: the holder of a pinned key signed these
exact bytes. Four boundaries follow from that and are enforced, not only stated.

| Boundary | Rule | Where it holds |
|---|---|---|
| Epistemic | A signature never moves a claim from `HYPOTHESIS` or `ATTRIBUTED_INTENT` to `EVIDENCE`. It shows integrity of a record, not truth about the world. | No module under `ante/strategy`, `learn`, `constructs`, `ice`, `develop`, `turing`, `core` or `doctrine` imports `ante.attest` (`test_no_strategy_learning_or_construct_module_reads_a_signature`). |
| Authorisation | A valid signature or proof never replaces the owner's mandate or the host's control. | `ante verify` reports `authorizes_action: false` for every document; a receipt has no field that could carry a permission (`test_receipt_carries_no_authority`). |
| Self-development | A change to the verifier, its tests or the trust store cannot be approved or signed by the loop that benefits from it. | `ante/attest/**` and `foundation/attest/**` are protected in both manifests; the tests under `tests/**` are protected in `foundation/develop-policy.json` (`test_the_verifier_and_the_trust_store_are_protected_from_self_development`). The manifests bind proposals, not the checkout a verifier runs from, which is why the default store is read from HEAD and a modified verifier fails. |
| Independence | A record signed with the system's or the owner's own key is still an internal record. A signature does not make it independent corroboration. | A verified receipt reports `evidence_origin: SYSTEM`, a verified approval `PINNED_HUMAN_KEY`, anything else `UNVERIFIED`; nothing reads that report back into a claim. |

A bare key signature also does not prove that a person was present. `ante sign`
makes an unattended signature hard (below); it cannot make it impossible.

## Documents

Two kinds, both closed schemas: an unknown field is refused, not ignored.

**Execution receipt** (`ante.execution.receipt`) — a statement about a finished
event. No mandate, scope, expiry, nonce or permission: presenting it again
triggers nothing.

| Field | Content |
|---|---|
| `artifact_sha256` | the artefact's own sealed digest; the seal is checked before a receipt is built |
| `source_commit_oid` | `{object_format, oid}` of the commit described |
| `code_tree_oid` | `{object_format, oid}` of the `ante/` tree object in that commit |
| `policy_sha256` | SHA-256 of `strategy/contracts.json` as committed there |
| `issued_at` | the signer's statement of time; not a time witness |

Git object ids are named as such. A SHA-1 tree id is never called a SHA-256.
`ante attest receipt` refuses when `ante/` or `strategy/contracts.json` has
uncommitted or untracked changes: a receipt names committed code only (files
that git ignores, such as `__pycache__`, are not considered). The receipt states that the artefact belongs to that code and policy; the tool
checks the seal and the commit, not that this code produced this artefact.

**D-020 approval** (`ante.d020.approval`) — the owner's approval of one exact
maintenance change. It is not a receipt, and verifying it does not admit the
change: the host still applies D-020.

| Field | Content |
|---|---|
| `base_commit` | the reviewed base |
| `result_tree` | the root tree after the change — the binding that does not depend on diff rendering |
| `patch_sha256` | SHA-256 of the diff the reviewer saw. Every git option that configuration could change is pinned, pathspecs are literal and attributes come from the head commit (git 2.40 or later), so the hash does not depend on the machine |
| `paths` | every changed path with its base and result blob ids (`null` when absent on one side); verification checks each blob |
| `scope` | subset of `apply`, `merge` |
| `review_ref`, `author` | where it was reviewed; who prepared it, recorded apart from the signer |

The approver is the signer; the author is a field; the host that applies the
change is a third role, recorded by the application step (outside G1a). A
different base, a different result tree or a different path list needs a new
approval (`test_approval_binds_base_result_tree_paths_and_patch`,
`test_an_approval_never_covers_a_different_base`, `test_blob_ids_are_checked`,
`test_a_file_name_cannot_hide_the_patch`,
`test_the_patch_hash_ignores_local_git_configuration_and_attributes`).

The **mandate** — principal, scope, validity, revocation — is a separate object
held by the host. G1a neither stores nor checks it; no signed document carries
it.

## Cryptographic profile

- `eddsa-jcs-2022` (W3C *Data Integrity EdDSA Cryptosuites v1.0*): sign
  `SHA-256(JCS(proof options)) || SHA-256(JCS(document))` with pure Ed25519;
  `proofValue` is multibase base58-btc. One proof per document; proof sets,
  chains and options beyond `type`, `cryptosuite`, `created`,
  `verificationMethod`, `proofPurpose` and `@context` are refused.
- **Signed subset.** Only JSON whose canonical form is the same under RFC 8785
  and under Python's sorted compact encoding is signed: printable ASCII strings
  and keys, integers within ±(2^53−1), `true`, `false`, `null`, arrays and
  objects; no floats, no duplicate keys, no byte-order mark. Outside that subset
  the two encodings really differ (key order by UTF-16 code units, number
  formatting), so it is refused instead of repaired. A cross-check against Trail
  of Bits' `rfc8785` over 2,000 generated documents runs in the tests; production
  code does not import `rfc8785`.
- **Conformance.** The W3C Annex B.3 vector (`tests/foundation/vectors/`, pinned
  to upstream commit `13e7070`) verifies, and signing its unsigned credential
  with its key reproduces the published `proofValue` byte for byte, along with
  each intermediate hash. That is evidence of interoperability for this vector
  and this subset; no claim is made beyond them.
- `ante/core/canon.py` and its four historical profiles are untouched; no
  lineage hash changes.
- `cryptography` is needed to sign or verify. Without it both fail closed
  (`CRYPTO_UNAVAILABLE`); nothing else in `ante` imports it.

## Keys and trust

The verifier accepts only keys pinned in `foundation/attest/trusted-keys.json`,
each for listed proof purposes and document kinds. A key is never taken from the
document, the proof or a DID resolver. A `did:key` method must encode the pinned
key. An approval verifies only with a `human` key; a future automated signer
needs its own key and its own entry. The store ships **empty**: until the owner
pins a key through D-020, nothing verifies.

`ante sign` signs only from a **separate signing account**. Each condition is
tested and checked on one open file descriptor:

- `ante sign` runs as an account that is not the owner of the checkout, so the
  account an agent works under in the repository cannot sign;
- the key file belongs to that signing account, is a regular file with mode
  `600` or stricter and lies outside the checkout;
- it is an encrypted PKCS#8 Ed25519 key — unencrypted keys are refused;
- the passphrase is typed at the terminal; arguments, environment variables
  and pipes are not accepted, and a process without a terminal is refused.

Two controls remain the owner's and cannot be proven here: the passphrase is
never given to an agent or stored where one can read it, and no agent runs with
the right to become the signing account (root, or `sudo` to it without a
password). A hardware token can replace the file key in a later stage.

Owner setup, once (macOS or Linux; `ante-signer` is any dedicated account):

```sh
sudo -u ante-signer sh -c 'umask 077; mkdir -p ~/.ante && openssl genpkey -algorithm ed25519 -aes-256-cbc -out ~/.ante/owner.pem'
sudo -u ante-signer openssl pkey -in ~ante-signer/.ante/owner.pem -pubout > owner.pub.pem
sudo -u ante-signer python3 -m pip install --user --require-hashes --no-deps -r .github/requirements/attest.txt
python3 scripts/ante attest key owner.pub.pem --principal owner:bionic0x --principal-type human
# add the printed entry to foundation/attest/trusted-keys.json in a D-020 change
```

Approving a protected change:

```sh
python3 scripts/ante attest approval --base <base> --head <head> --scope apply \
  --review-ref <PR> --author <who prepared it> --at <now> --out approval.json
git diff <base> <head>                       # read what you are about to approve
sudo -u ante-signer python3 scripts/ante sign approval.json --key ~ante-signer/.ante/owner.pem \
  --method <did:key...> --at <now> > approval.signed.json
python3 scripts/ante verify approval.signed.json --repo . --head <head>
```

The signing account needs read access to the checkout and to `approval.json`;
the signed document goes to standard output, written by the calling account.

`ante sign` first checks the document against the checkout — for an approval
it re-derives base, result tree, patch and paths from `--head` and refuses any
difference — then shows what it is about to sign, and only then asks for the
passphrase. An agent-prepared `approval.json` that names another tree is
refused before the owner types anything.

What `ante verify` reports, and under which conditions:

- **Trust store.** By default the store is read from the commit the checkout
  is on (`HEAD:foundation/attest/trusted-keys.json`), never from the working
  tree, and any uncommitted change under `ante/attest/` or `foundation/attest/`
  fails the verification (`VERIFIER_MODIFIED`). Verification means something
  only from a clean checkout of a trusted commit. Another store can be named
  with `--trust`; the report then says so in `trust_store` and a verified
  approval reports `evidence_origin: CALLER_TRUST_STORE`, never
  `PINNED_HUMAN_KEY`.
- **Purpose.** Only `assertionMethod` proofs verify.
- **Candidate.** An approval verifies only against a candidate, with `--repo`
  and `--head`; otherwise the report says `CANDIDATE_REQUIRED` with
  `signature_valid: true` and `verified: false`.
- **No echo.** Fields copied from the document (`verification_method`,
  `proof_purpose`, `created`, `principal`) appear only once the signature
  verified; error messages name the defect, not the input.

Exit status: `0` verified or document written; `2` usage error, invalid input
to `ante attest` or a refused signature; `4` not verified, which includes any
unreadable or invalid document given to `ante verify`. Every failure carries a
reason: `MALFORMED`, `SCHEMA_INVALID`, `UNSUPPORTED_PROOF`, `CONTEXT_MISMATCH`,
`TRUST_STORE_INVALID`, `VERIFIER_MODIFIED`, `UNTRUSTED_KEY`, `BAD_SIGNATURE`,
`CRYPTO_UNAVAILABLE`, `CANDIDATE_REQUIRED`, `REPOSITORY_MISMATCH`,
`REPOSITORY_UNAVAILABLE`.

## Threat model

| ID | Threat | Control | Status |
|---|---|---|---|
| T01 | An agent reads or uses the approver's key | Separate signing account that does not own the checkout; key owned by it, mode 600, encrypted, outside the checkout; passphrase typed at a terminal | Tested (`SigningGuards`), and run end to end with a real second account. Passphrase secrecy and denying agents the right to become the signing account are owner controls |
| T02 | The owner signs an approval an agent prepared without reading it | `ante sign` re-derives the approval from the checkout and `--head`, refuses any difference, and shows base, tree, patch and paths before the passphrase | Tested (`test_signing_rederives_the_approval_from_the_checkout`); reading the diff remains a human control |
| T03 | Key substitution | Pinned store read from HEAD; `did:key` must encode the key; no resolution; a caller-chosen store is named in the report | Tested (`test_key_substitution_fails`, `test_a_did_key_must_encode_the_pinned_key`, `test_unknown_method_fails`, `test_an_uncommitted_verifier_or_store_fails_every_verification`, `test_the_default_store_is_read_from_head_and_claims_a_pinned_key`) |
| T04 | JSON ambiguity | Strict, size-bounded parsing; signed subset; RFC 8785 cross-check | Tested (`SignedSubset`, including `test_hostile_input_is_refused_with_a_reason_not_a_crash`; `test_duplicate_keys_in_a_signed_file_are_malformed`) |
| T05 | Replaying a receipt triggers an action | Verification is read-only; `authorizes_action: false` | Tested (`test_verification_is_read_only_and_repeatable`) |
| T06 | Receipt names code or policy that did not run | Commit, `ante/` tree and policy re-checked from git; dirty state refused | Tested (`test_uncommitted_code_or_policy_is_refused`, `test_receipt_for_other_code_or_policy_or_artefact_fails`) |
| T07 | The system attests its own observation | `evidence_origin: SYSTEM`; no judging module reads signatures | Tested (`test_no_strategy_learning_or_construct_module_reads_a_signature`) |
| T08 | An agent alters the verifier or the trust store | Protected in both manifests; changes only through D-020 | Tested (`test_the_verifier_and_the_trust_store_are_protected_from_self_development`) |
| T09 | Private content leaks through signed metadata or reports | Closed schemas of hashes, object ids, paths and references; errors and unverified reports echo nothing from the input | Tested (`test_errors_do_not_echo_the_input`, `test_unverified_reports_do_not_echo_the_document`, `test_receipt_carries_no_authority`, schema tests) |
| T10 | False signing time | `created` and `issued_at` are the signer's statement | Documented; a time witness is outside G1a |
| T11 | A key is compromised after signing | Removing the key from the store invalidates all its signatures; no historical trust | Rotation and dated revocation are G1b |
| T12 | An approval is taken as standing authority | Bound to base, result tree, paths with blob ids and patch; verifies only against a candidate; never authorises by itself | Tested (`test_approval_binds_base_result_tree_paths_and_patch`, `test_an_approval_never_covers_a_different_base`, `test_an_approval_verifies_only_against_a_candidate`) |

## Not in G1a

No blockchain, ZK proof, credential issuance, DID resolution, key rotation,
revocation, external timestamp, review interface, application receipt, host
admission gate or network access. G1b adds rotation and local revocation. G2–G4
(zkVM, ZKML, external anchoring) need a named external verifier and a separate
owner decision.

## Dependencies

`.github/requirements/attest.txt`, hash-pinned with pip-compile:
`cryptography`, its `cffi` and `pycparser`, and `rfc8785` (tests only). The
Foundation CI job installs them and sets `ANTE_REQUIRE_ATTEST=1`, which turns a
missing dependency into a test failure instead of a skip.
