# ante react — lab-consortium

| Field | Value |
|---|---|
| Decision time | 2026-10-28T11:30:00Z |
| Verdict | — |
| Independence | — |
| Input SHA-256 | `b93c068f911c0ae1c3c5a13defd622a1206f65a8a9b8092b9f146a803164f3d6` |
| Artefact SHA-256 | `a7b5dfd8bd228c2938256e87360c298d07ffa2d7a135f9b3eacb220ac11bebb9` |

## Lineage

- map `a4e9a714ee77a69296f58be4412b2b58df8703d46d4b011d8ded18526afac0d1`
- options `fc02126b99d0bc538a5b573cd2e9d3508c95f6e18c6eb1fb1eaff0e114b429fb`

## Content

```json
{
  "reactions": [
    {
      "id": "a-overbooks",
      "actor": "uni-a",
      "kind": "opposition",
      "against_option": "shared-criteria",
      "description": "A classifies more requests as urgent to keep its hours.",
      "incentive": "A bears most deferrals under the rule",
      "information_revealed": "urgent share rising without new external deadlines",
      "capacity_required": "evidence check of deadlines by the coordinator",
      "activation_signal": "urgent hours rise without new deadline letters",
      "contingent_decision": "adjust",
      "changes_choice": false
    },
    {
      "id": "b-swaps",
      "actor": "research-teams",
      "kind": "cooperation",
      "against_option": "shared-criteria",
      "description": "Teams of B and C swap slots directly, making most coordination unnecessary.",
      "incentive": "faster access than waiting for coordination",
      "information_revealed": "conflicts resolved before they reach the coordinator",
      "capacity_required": "a swap log the council can audit",
      "activation_signal": "coordinator receives fewer than two conflicts a week",
      "contingent_decision": "adjust",
      "changes_choice": true
    },
    {
      "id": "funder-deadline",
      "actor": "council",
      "kind": "third_party_shift",
      "against_option": "shared-criteria",
      "description": "A funder advances a deadline, raising essential demand above 90 hours.",
      "incentive": "external reporting calendar",
      "information_revealed": "essential demand exceeding ordinary capacity",
      "capacity_required": "activate the external-capacity evaluation",
      "activation_signal": "essential demand above 90 hours for one cycle",
      "contingent_decision": "pause",
      "changes_choice": true
    }
  ]
}
```

## Next decision

Tie each indicator to a response before acting (ante watch).
