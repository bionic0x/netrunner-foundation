# ante nodal — lab-consortium

| Field | Value |
|---|---|
| Decision time | 2026-10-28T13:30:00Z |
| Verdict | — |
| Independence | — |
| Input SHA-256 | `9ab10f0f885c9c17b9bb160e685330f8e0891ef8f13bba2ae0d86091e62bb844` |
| Artefact SHA-256 | `e2803a1bb15434ea655a31ad83a8357c26d54ce7846bccb8a05c360edef71401` |

## Lineage

- ach `1d7c2f4c72c18fbb313b4063282b8179bbac5d0d90286d0fb4213cb896ab908f`
- cause `dbcd3f8552ac57d0fb012db9327e95752f3f253ba3b28829fd6e2bce64dd3b86`
- close `b96ede0f4457d88a2b5c557fc20d2292657e063f355fc35db50e8e8d13f8e938`
- cohere `3dc4bdb4aca789ee4696dfe11778f9377e6ffe79a2544584402cb03f0036c3ef`
- focus `250120fe71f32059e8abcbba6f1c98c52e4aee2af834ff62abded113cf54eba1`
- frame `d6e55f031b0bbfb954dccf850690412029f568e3a1ccdd8b962aed6cff9d2574`
- map `a4e9a714ee77a69296f58be4412b2b58df8703d46d4b011d8ded18526afac0d1`
- options `fc02126b99d0bc538a5b573cd2e9d3508c95f6e18c6eb1fb1eaff0e114b429fb`
- pathology `5dac54f0cbf3c0f24b4588a3f98e19563d62539fc61e6d21701821af70306960`
- react `a7b5dfd8bd228c2938256e87360c298d07ffa2d7a135f9b3eacb220ac11bebb9`
- street `9b779a6783be2bf0c8bf27261f468b6ccd17c599aa9c08171a272f6c5706b9a4`
- watch `c2543a226b69a7d737c502f7f729f898fee3e86fc02f4d0d1f34278d6bf05229`

## Content

```json
{
  "irreversibility": "medium",
  "weight": 1.5,
  "thresholds": {
    "corroborate": 4.0,
    "check": 2.0
  },
  "artefacts_examined": [
    "ach:1d7c2f4c72c1",
    "cause:dbcd3f8552ac",
    "close:b96ede0f4457",
    "cohere:3dc4bdb4aca7",
    "focus:250120fe71f3",
    "frame:d6e55f031b0b",
    "map:a4e9a714ee77",
    "options:fc02126b99d0",
    "pathology:5dac54f0cbf3",
    "react:a7b5dfd8bd22",
    "street:9b779a6783be",
    "watch:c2543a226b69"
  ],
  "load_bearing_claims": [
    {
      "id": "demand-110",
      "status": "EVIDENCE",
      "origin": "external",
      "stated_in": "frame",
      "load": 5,
      "score": 7.5,
      "required_verification": "corroborate",
      "cited_by": [
        "map:actors[3].basis",
        "cause:basis",
        "ach:evidence[0].claim",
        "options:options[0].assumptions",
        "cohere:tests.legitimacy.evidence"
      ],
      "blocking": false
    },
    {
      "id": "cap-100",
      "status": "EVIDENCE",
      "origin": "external",
      "stated_in": "frame",
      "load": 4,
      "score": 6.0,
      "required_verification": "corroborate",
      "cited_by": [
        "map:actors[2].basis",
        "options:options[1].assumptions",
        "cohere:tests.conversion.evidence",
        "cohere:tests.exit.evidence"
      ],
      "blocking": false
    },
    {
      "id": "a-inflates",
      "status": "ATTRIBUTED_INTENT",
      "origin": "external",
      "stated_in": "map",
      "load": 3,
      "score": 4.5,
      "required_verification": "corroborate",
      "cited_by": [
        "cohere:tests.epistemic.evidence",
        "cohere:tests.interactive.evidence",
        "pathology:pathologies.metric_substitution.evidence"
      ],
      "blocking": true
    },
    {
      "id": "slack-20",
      "status": "ASSUMPTION",
      "origin": "owner",
      "stated_in": "cause",
      "load": 3,
      "score": 4.5,
      "required_verification": "corroborate",
      "cited_by": [
        "options:options[2].assumptions",
        "cohere:tests.causal.evidence",
        "cohere:tests.epistemic.evidence"
      ],
      "blocking": true
    },
    {
      "id": "priority-50",
      "status": "EVIDENCE",
      "origin": "external",
      "stated_in": "frame",
      "load": 2,
      "score": 3.0,
      "required_verification": "check",
      "cited_by": [
        "cohere:tests.conversion.evidence",
        "cohere:tests.purpose.evidence"
      ],
      "blocking": false
    }
  ],
  "routine_claims": [
    "cohesion-hypothesis",
    "dup-check",
    "model-summary",
    "tech-report",
    "tech-report-echo"
  ],
  "blocking": [
    "a-inflates",
    "slack-20"
  ]
}
```

## Findings

- **WARN** `LOAD_BEARING_UNVERIFIED` a-inflates: carries the plan unverified: corroborate it or accept it as a named risk in decide
- **WARN** `LOAD_BEARING_UNVERIFIED` slack-20: carries the plan unverified: corroborate it or accept it as a named risk in decide

## Next decision

Corroborate a-inflates, slack-20 and re-run nodal, or accept them as named risks in decide; PROCEED is refused until then.
