# ante decide — lab-consortium

| Field | Value |
|---|---|
| Decision time | 2026-10-28T14:00:00Z |
| Verdict | PROCEED_WITH_CONDITIONS |
| Independence | — |
| Input SHA-256 | `c1384be4b69530ebbd21b54ac45eee3244177e5e7d156766be6b58b7ce09e01c` |
| Artefact SHA-256 | `84e768f60970669a60938a5d8d2661ab511a4c269e9d7d0313d234bb719012f6` |

## Lineage

- cause `dbcd3f8552ac57d0fb012db9327e95752f3f253ba3b28829fd6e2bce64dd3b86`
- close `b96ede0f4457d88a2b5c557fc20d2292657e063f355fc35db50e8e8d13f8e938`
- cohere `93ba12abee0dc78db233b62828312a00b44c7743042bab03b01af15845aef94b`
- frame `d6e55f031b0bbfb954dccf850690412029f568e3a1ccdd8b962aed6cff9d2574`
- nodal `2e378e26ca7347eee525a6d761b7a2ed717c164d2d4962e581b55e36085e9dac`
- pathology `5dac54f0cbf3c0f24b4588a3f98e19563d62539fc61e6d21701821af70306960`

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
        "artifact_sha256": "dbcd3f8552ac57d0fb012db9327e95752f3f253ba3b28829fd6e2bce64dd3b86"
      },
      {
        "command": "close",
        "artifact_sha256": "b96ede0f4457d88a2b5c557fc20d2292657e063f355fc35db50e8e8d13f8e938"
      },
      {
        "command": "cohere",
        "artifact_sha256": "93ba12abee0dc78db233b62828312a00b44c7743042bab03b01af15845aef94b"
      },
      {
        "command": "frame",
        "artifact_sha256": "d6e55f031b0bbfb954dccf850690412029f568e3a1ccdd8b962aed6cff9d2574"
      },
      {
        "command": "nodal",
        "artifact_sha256": "2e378e26ca7347eee525a6d761b7a2ed717c164d2d4962e581b55e36085e9dac"
      },
      {
        "command": "pathology",
        "artifact_sha256": "5dac54f0cbf3c0f24b4588a3f98e19563d62539fc61e6d21701821af70306960"
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
    "snapshot_sha256": "66348e309f31857ae21ccb70d144e192b58e8ffcff99a1dd15834e6af3f28f9a"
  }
}
```

## Next decision

Satisfy each condition before the gated commitment; preparatory work only.
