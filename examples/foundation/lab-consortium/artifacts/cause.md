# ante cause — lab-consortium

| Field | Value |
|---|---|
| Decision time | 2026-10-28T10:00:00Z |
| Verdict | — |
| Independence | — |
| Input SHA-256 | `7891f77ff0020031feaf02546a5d2a66e317eb3484d97c4bf1c827a2f5884ec7` |
| Artefact SHA-256 | `dbcd3f8552ac57d0fb012db9327e95752f3f253ba3b28829fd6e2bce64dd3b86` |

## Lineage

- frame `d6e55f031b0bbfb954dccf850690412029f568e3a1ccdd8b962aed6cff9d2574`
- map `a4e9a714ee77a69296f58be4412b2b58df8703d46d4b011d8ded18526afac0d1`

## Claims

| Id | Status | Claim | Source | Date | Limit |
|---|---|---|---|---|---|
| slack-20 | ASSUMPTION | 20 hours can move to the following weeks, where slack is confirmed. | booking forecast for weeks 45-46 | 2026-10-27 | Synthetic didactic data (Marco, Appendix E); not an observation of any real institution. |

## Content

```json
{
  "chain": {
    "if": "we adopt shared priority criteria applied by each university and coordinate only the conflicts",
    "then": "conflicting bookings fall and priority projects get their hours",
    "because": "members stop over-reserving defensively once the criteria are predictable and appealable",
    "provided_that": [
      "essential demand stays within 90 ordinary hours",
      "deferred hours fit the confirmed slack"
    ],
    "immediate_effect": "fewer conflicting reservations per week",
    "final_result": "priority projects completed on time and members still value the consortium"
  },
  "rivals": [
    {
      "id": "structural-scarcity",
      "explanation": "Demand that cannot be deferred exceeds capacity, so no rule removes the conflict.",
      "discriminating_evidence": "essential demand above 90 hours in consecutive cycles despite applied criteria"
    },
    {
      "id": "bad-records",
      "explanation": "Duplicate or stale reservations inflate the apparent demand.",
      "discriminating_evidence": "reconciliation of active requests against projects shows duplicates"
    }
  ],
  "refutations": [
    {
      "observation": "conflicts do not fall after two cycles of applied criteria",
      "horizon": "end of cycle 2",
      "observed_by": "technical staff booking report"
    }
  ],
  "basis": [
    "demand-110",
    "slack-20"
  ]
}
```

## Next decision

Locate the decisive dependency and the main effort (ante focus).
