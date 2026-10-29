# ante street — lab-consortium

| Field | Value |
|---|---|
| Decision time | 2026-10-28T11:45:00Z |
| Verdict | — |
| Independence | — |
| Input SHA-256 | `0122006c62d142985d372c5ca01d41b3bac716f442a658f2b0d787142701d65e` |
| Artefact SHA-256 | `bf0945a98aa4c002aaaee44368258185a9ff89555b3b463eabdffc43f7530549` |

## Lineage

- frame `d6e55f031b0bbfb954dccf850690412029f568e3a1ccdd8b962aed6cff9d2574`
- map `a4e9a714ee77a69296f58be4412b2b58df8703d46d4b011d8ded18526afac0d1`

## Content

```json
{
  "misuse_analysis": [
    {
      "id": "urgent-share",
      "kind": "metric",
      "statement": "share of hours declared urgent",
      "purpose": "protect hours with a real external deadline",
      "misuse": [
        {
          "actor": "uni-a",
          "variant": "adversarial",
          "reuse": "relabel ordinary requests as urgent so they jump the queue",
          "effect_on_purpose": "urgent hours crowd out the requests the label was meant to protect",
          "indicator": "urgent requests without a deadline document attached",
          "countermeasure": "an urgency label counts only with the funder's deadline letter"
        },
        {
          "actor": "council",
          "variant": "adversarial",
          "reuse": "push the share down by refusing urgent labels to show the metric improving",
          "effect_on_purpose": "real deadlines are missed while the indicator looks healthy",
          "indicator": "missed external deadlines on requests that were refused the urgent label",
          "countermeasure": "report missed deadlines beside the share every cycle"
        },
        {
          "actor": "council",
          "variant": "regressional",
          "reuse": "rank cycles by the urgent share and copy the settings of the best one",
          "effect_on_purpose": "the best-looking cycle was partly luck in how requests were labelled, so the copied settings protect nothing",
          "indicator": "deadline hits per cycle, compared across the cycles ranked best and worst by urgent share",
          "countermeasure": "judge settings over several cycles against deadline hits, never on one cycle's share"
        }
      ],
      "goodhart_variants": [
        "regressional",
        "adversarial"
      ]
    },
    {
      "id": "essential-demand",
      "kind": "metric",
      "statement": "essential demand per cycle",
      "purpose": "trigger a capacity decision before coordination stops helping",
      "misuse": [
        {
          "actor": "research-teams",
          "variant": "adversarial",
          "reuse": "split one essential booking into several smaller ones to look less dominant",
          "effect_on_purpose": "the capacity trigger fires late because demand looks fragmented",
          "indicator": "bookings by one team within the same week whose sum exceeds its declared need",
          "countermeasure": "aggregate essential demand by project, not by booking"
        },
        {
          "actor": "research-teams",
          "variant": "extremal",
          "reuse": "stop booking hours that will not be served once the laboratory is full",
          "effect_on_purpose": "near saturation recorded demand understates need, so the capacity trigger never fires",
          "indicator": "requests withdrawn or never filed that teams report in the cycle review",
          "countermeasure": "collect declared need per project each cycle, independent of bookings"
        }
      ],
      "goodhart_variants": [
        "extremal",
        "adversarial"
      ]
    },
    {
      "id": "deadline-document-rule",
      "kind": "rule",
      "statement": "urgency labels require a deadline document",
      "purpose": "remove the incentive to inflate urgency",
      "misuse": [
        {
          "actor": "uni-a",
          "variant": "adversarial",
          "reuse": "obtain generic deadline letters that cover every request",
          "effect_on_purpose": "the document becomes a formality and inflation resumes",
          "indicator": "deadline letters reused across unrelated projects",
          "countermeasure": "letters name the project and the date; the coordinator samples them each cycle"
        }
      ],
      "goodhart_variants": [
        "adversarial"
      ]
    }
  ],
  "covered_metrics": [
    "essential demand per cycle",
    "share of hours declared urgent"
  ],
  "unconsidered_variants": {
    "urgent-share": [
      "extremal",
      "causal"
    ],
    "essential-demand": [
      "regressional",
      "causal"
    ]
  }
}
```

## Findings

- **WARN** `GOODHART_VARIANTS_UNCONSIDERED` instruments[0].misuse: no scenario for: extremal, causal
- **WARN** `GOODHART_VARIANTS_UNCONSIDERED` instruments[1].misuse: no scenario for: regressional, causal

## Next decision

Carry each manipulation indicator into watch; cohere checks coverage.
