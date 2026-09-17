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

## Recommendation and presentation workflow

1. Identify the highest absolute contributors and persistent trends from the assessment or investigation.
2. Separate emissions observations from operational causes. Require cost, utilization, configuration, or deployment evidence before proposing a specific change.
3. Rank candidates by expected emissions relevance, confidence, customer impact, cost impact, reversibility, and validation signal.
4. Present the outcome for decisions rather than as a raw data dump:
   - Lead with one clear takeaway that distinguishes overall trend from the latest-month movement.
   - Show three scorecards: selected-period total, latest available month, and latest month-over-month change.
   - State the available-through date prominently and label historical anomalies separately from current opportunities.
   - Keep the current-priority action table to the highest-value items, normally no more than five.
5. Offer read-only verification first. For any future mutating action, provide the exact target, impact, rollback, and approval step.
6. State uncertainty explicitly. If utilization, cost, configuration, or deployment evidence is missing, say `No change recommended yet` and name the next verification needed.

## Output format

Write a concise, decision-ready Markdown result in this order:

1. `## Carbon optimization snapshot` with the one-line takeaway.
2. A three-column scorecard table for selected-period total, latest available month, and latest month-over-month change.
3. A visible data-freshness note that includes the `availableThrough` date and material data gaps.
4. `### What changed` with a prioritized table: priority, target, measured signal, and next read-only validation.
5. `### Historical items to close` only when a historical spike needs ownership or lifecycle validation. Do not present it as a current optimization opportunity.
6. `### Evidence and decision` that lists corroborating evidence, gaps, and either a safe next action or `No change recommended yet`.
7. One `OptimizationCandidate` block for each item in the action table when structured detail is useful.

Use kgCO2e units consistently. Use tables for comparisons, not nested bullets. Do not claim that a contributor is a root cause or that a change will reduce emissions without independent evidence.

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
