# ante pathology — lab-consortium

| Field | Value |
|---|---|
| Decision time | 2026-10-28T13:15:00Z |
| Verdict | — |
| Independence | SEPARATED_CONTEXT |
| Input SHA-256 | `47c3ed00a869e9522e287a6784496a0e00dd474af579f01545060ccd31951262` |
| Artefact SHA-256 | `5dac54f0cbf3c0f24b4588a3f98e19563d62539fc61e6d21701821af70306960` |

## Lineage

- frame `d6e55f031b0bbfb954dccf850690412029f568e3a1ccdd8b962aed6cff9d2574`
- map `a4e9a714ee77a69296f58be4412b2b58df8703d46d4b011d8ded18526afac0d1`

## Content

```json
{
  "pathologies": {
    "level_inversion": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "nominal_objective": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "imaginary_centre": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "concept_confusion": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "dispersion": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "frictionless_plan": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "disoriented_speed": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "denied_culmination": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "reflex_symmetry": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "illegitimate_victory": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "intent_attribution": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "metric_substitution": {
      "status": "DETECTED",
      "evidence": [
        "a-inflates"
      ],
      "false_positive_check": "urgency labels could rise for real deadlines; the watch threshold checks for new deadline letters",
      "note": "the urgency label can be gamed to win hours"
    },
    "escalation_of_commitment": {
      "status": "NOT_DETECTED",
      "evidence": [],
      "false_positive_check": "not applicable when not detected",
      "note": "examined against the frame, options and watch artefacts; no mechanism present"
    },
    "chronic_personalization": {
      "status": "NOT_ASSESSED",
      "evidence": [],
      "false_positive_check": "n/a",
      "note": "requires observing how exceptions are granted over more than one cycle"
    }
  },
  "detected": [
    {
      "id": "metric_substitution",
      "mechanism": "Incentives change the record or the conduct to improve the number.",
      "correction": "Review the relation between measure, mechanism and result."
    }
  ],
  "not_assessed": [
    "chronic_personalization"
  ],
  "doctrine_sha256": "ac92df4ffe92ddf666e84fafd1fb4648a85ca103f4bea2e9b91fa15df921b3be"
}
```

## Next decision

Address metric_substitution in the decision conditions (ante decide).
