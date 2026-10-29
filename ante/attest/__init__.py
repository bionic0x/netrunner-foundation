"""Local signatures for sealed artefacts and protected-maintenance approvals (G1a).

A signature binds a document to a key. It does not make the document true, it
grants no permission and it does not turn a system record into independent
evidence. ``foundation/ATTEST.md`` states the contract and the threat model.

    jcs        strict JSON parsing and the canonical form of the signed subset
    multibase  base58-btc and the Ed25519 multicodec prefixes
    eddsa      the W3C ``eddsa-jcs-2022`` Data Integrity proof
    trust      the pinned keys a verifier accepts
    documents  execution receipts and D-020 approvals: schemas and git references
    commands   ``ante sign``, ``ante verify`` and ``ante attest``

Nothing here opens the network. ``cryptography`` is needed only to sign or
verify; without it both fail closed.
"""
