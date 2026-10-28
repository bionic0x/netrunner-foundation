# ante decide — lab-consortium

| Field | Value |
|---|---|
| Decision time | 2026-10-28T14:00:00Z |
| Verdict | PROCEED_WITH_CONDITIONS |
| Independence | — |
| Input SHA-256 | `c1384be4b69530ebbd21b54ac45eee3244177e5e7d156766be6b58b7ce09e01c` |
| Artefact SHA-256 | `4a66bd00a6fa03b346a901639af48a6d8a1dcd17a59719c0ff843366f651e33d` |

## Lineage

- cause `2456016bc2caa97e0e59231577425b55f42c6179fa30b1bd2760e18cd339e927`
- close `b5437d8d4c3692706913991c729d868c65a977e90bd6898cb8ae673e52489b8f`
- cohere `aa8d7bb24c5bf41c687c8025b2fa15e1c1982368c481b3530468559abf18e6e1`
- frame `f3f11099665d17b689e605f8d9cf131a04e864ece52a0137d9187b5df392b28b`
- nodal `971dc5cc9f29cf2180f6afec287c3d663d128bd887021fad311fa242b21b159a`
- pathology `acbf0725bc64103f4b83a067549d680bc713543d507925b27c826ce77ceddbbb`

## Content

```json
{
  "case": {
    "id": "lab-consortium",
    "title": "Shared laboratory access across universities A, B and C"
  },
  "decision_owner": "Consortium council (synthetic)",
  "verdict": "PROCEED_WITH_CONDITIONS",
  "rationale": "Shared criteria protect priority work, keep the reserve and remain reversible; the causal risk is bounded by the trial.",
  "conditions": [
    "An independent operator reviews the coherence record before cycle 2",
    "Urgency labels require a deadline document (metric substitution detected)",
    "slack-20: each principal investigator confirms in writing that the deferred hours keep their deadline before the 20 hours move"
  ],
  "admissible_verdicts": [
    "PROCEED_WITH_CONDITIONS",
    "HOLD",
    "REDESIGN",
    "REJECT"
  ],
  "review_independence": "SEPARATED_CONTEXT",
  "detected_pathologies": [
    "metric_substitution"
  ],
  "termination_contract": {
    "accountable": "The consortium council answers for the rule; the laboratory director runs it with ordinary staff.",
    "achieved": "Priority hours are protected each week and deferrals land in confirmed later slots under a rule all three members adopted.",
    "conservation_resources": "Half a day of coordinator time per week and the booking system's existing audit log.",
    "on_breach": "A member that books outside the rule loses priority for that slot; repeated breaches go to the council, which may suspend the trial.",
    "outstanding": "The external-capacity option remains unverified and is kept as a contingency with an owner and a trigger.",
    "revision_conditions": "Review after three cycles, or earlier if essential demand exceeds 90 hours twice in a row.",
    "type": "conservation"
  },
  "dissent": [
    {
      "by": "University A research office",
      "objection": "The rule places most deferrals on A.",
      "evidence": [
        "demand-110"
      ],
      "response": "Deferrals follow deferrability, not the requester; the appeal path is available after cycle 1."
    }
  ],
  "dissent_solicited_from": [
    "universities A, B and C",
    "technical staff"
  ],
  "residual_risk": {
    "statement": "Essential demand may exceed ordinary capacity before the trial ends.",
    "accepted_by": "Consortium council (synthetic)"
  },
  "expires": "2027-01-31T00:00:00Z",
  "expectations": [
    {
      "id": "conflicts-fall",
      "what_should_change": "conflicting bookings per week",
      "in_whom": "teams of A, B and C",
      "horizon": "2026-12-15T00:00:00Z",
      "refuted_by": "conflicts at or above the current level after two cycles",
      "probability": {
        "verbal": "likely",
        "interval": [
          0.55,
          0.8
        ]
      }
    },
    {
      "id": "priority-delivered",
      "what_should_change": "priority projects meeting their deadline",
      "in_whom": "funded research teams",
      "horizon": "2027-01-15T00:00:00Z",
      "refuted_by": "any deadline-bound project missing its slot for capacity reasons",
      "probability": {
        "verbal": "very likely",
        "interval": [
          0.75,
          0.95
        ]
      }
    }
  ],
  "authority": "This record does not itself grant production, legal, financial, security or other real-world execution authority.",
  "load_bearing_claims": {
    "blocking": [
      "a-inflates",
      "slack-20"
    ],
    "accepted_risks": [
      {
        "claim": "a-inflates",
        "accepted_by": "Consortium council (synthetic)",
        "statement": "University A's inflation of urgent requests stays an attributed intention; the deadline-document rule removes the incentive whether or not it is true, so the plan does not depend on proving it."
      }
    ]
  },
  "snapshot": {
    "frozen_at": "2026-10-28T14:00:00Z",
    "parents": [
      {
        "command": "cause",
        "artifact_sha256": "2456016bc2caa97e0e59231577425b55f42c6179fa30b1bd2760e18cd339e927"
      },
      {
        "command": "close",
        "artifact_sha256": "b5437d8d4c3692706913991c729d868c65a977e90bd6898cb8ae673e52489b8f"
      },
      {
        "command": "cohere",
        "artifact_sha256": "aa8d7bb24c5bf41c687c8025b2fa15e1c1982368c481b3530468559abf18e6e1"
      },
      {
        "command": "frame",
        "artifact_sha256": "f3f11099665d17b689e605f8d9cf131a04e864ece52a0137d9187b5df392b28b"
      },
      {
        "command": "nodal",
        "artifact_sha256": "971dc5cc9f29cf2180f6afec287c3d663d128bd887021fad311fa242b21b159a"
      },
      {
        "command": "pathology",
        "artifact_sha256": "acbf0725bc64103f4b83a067549d680bc713543d507925b27c826ce77ceddbbb"
      }
    ],
    "claims_known": [
      {
        "id": "slack-20",
        "status": "ASSUMPTION",
        "origin": "owner",
        "from": "cause"
      },
      {
        "id": "cap-100",
        "status": "EVIDENCE",
        "origin": "external",
        "from": "frame"
      },
      {
        "id": "demand-110",
        "status": "EVIDENCE",
        "origin": "external",
        "from": "frame"
      },
      {
        "id": "priority-50",
        "status": "EVIDENCE",
        "origin": "external",
        "from": "frame"
      }
    ],
    "expectations": [
      {
        "id": "conflicts-fall",
        "what_should_change": "conflicting bookings per week",
        "in_whom": "teams of A, B and C",
        "horizon": "2026-12-15T00:00:00Z",
        "refuted_by": "conflicts at or above the current level after two cycles",
        "probability": {
          "verbal": "likely",
          "interval": [
            0.55,
            0.8
          ]
        }
      },
      {
        "id": "priority-delivered",
        "what_should_change": "priority projects meeting their deadline",
        "in_whom": "funded research teams",
        "horizon": "2027-01-15T00:00:00Z",
        "refuted_by": "any deadline-bound project missing its slot for capacity reasons",
        "probability": {
          "verbal": "very likely",
          "interval": [
            0.75,
            0.95
          ]
        }
      }
    ],
    "verdict": "PROCEED_WITH_CONDITIONS",
    "snapshot_sha256": "7b3bf56e1c139ba7e98c5fd771c58e88d9f41996480f13ae2cba3a178d9d9eed"
  }
}
```

## Next decision

Satisfy each condition before the gated commitment; preparatory work only.
