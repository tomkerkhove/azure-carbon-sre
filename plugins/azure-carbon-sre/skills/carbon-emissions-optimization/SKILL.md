---
name: carbon-emissions-optimization
description: Produce evidence-based, non-destructive Carbon Optimization recommendations only after reusable assessment and investigation skills establish the emissions state.
---

# Carbon emissions optimization

Use this skill to prioritize optimization opportunities. It does not make Azure changes.

## Required evidence gate

Before proposing an action, require a `CarbonAssessment` from `carbon-emissions-assessment` with `evidenceStatus: ready`.

- If the user asks for optimization directly, assess the state first instead of producing generic recommendations.
- If a material increase or concentrated contributor exists, use `carbon-emissions-spike-investigation` before suggesting a cause-specific action.
- Reuse the explicit subscription scope, available-through date, access results, and evidence gaps from the assessment. Do not expand scope without asking the user.

## Recommendation workflow

1. Identify the highest absolute contributors and persistent trends from the assessment/investigation.
2. Separate emissions observations from operational causes. Require cost, utilization, configuration, or deployment evidence before proposing a specific change.
3. Rank candidates by expected emissions relevance, confidence, customer impact, cost impact, reversibility, and validation signal.
4. Offer read-only verification first. For any future mutating action, provide the exact target, impact, rollback, and approval step.
5. State uncertainty explicitly when corroborating evidence is absent.

## Output format

```text
OptimizationCandidate
- target: <resource or category>
- observation: <measured emissions pattern>
- corroboratingEvidence: <present | missing, with source>
- recommendation: <specific next verification or change proposal>
- confidence: <high | medium | low>
- impactAndRollback: <required for any change>
```

Never claim an emissions reduction estimate unless it is backed by a documented model or measured before-and-after evidence.
