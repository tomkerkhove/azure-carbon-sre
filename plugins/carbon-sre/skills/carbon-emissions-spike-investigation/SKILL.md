---
name: carbon-emissions-spike-investigation
description: Investigate a Carbon Optimization emissions increase by extending a completed subscription-scoped carbon assessment with category and resource drilldowns.
---

# Carbon emissions spike investigation

Use this skill after `carbon-emissions-assessment` establishes a `CarbonAssessment` with `evidenceStatus: ready`.

## Preconditions

- If the assessment record is missing or incomplete, run the assessment first.
- Do not infer a subscription scope from earlier conversations; reuse only the explicit IDs recorded in `CarbonAssessment`.
- Treat reported emissions movement as a signal, not proof of a deployment, configuration, or usage cause.

## Investigation workflow

1. Confirm the month or range with the unexpected change and define the comparison period.
2. Query `TopItemsMonthlySummaryReport` by `ResourceType` for the trend window.
3. Query `TopItemsSummaryReport` for the affected month by `ResourceType`, `ResourceGroup`, or `Location`.
4. Query `ItemDetailsReport` for the affected month and category. Follow pagination until `skipToken` is empty.
5. Rank contributors by absolute kgCO2e change and contribution to the selected period, not percentage alone.
6. Identify candidates for corroboration with cost, utilization, deployment, or service telemetry. Do not label a root cause until an independent source supports it.

## Output

Extend the assessment record with:

```text
Investigation
- targetMonthOrRange: <date range>
- primaryContributors: <resource types, resources, locations>
- absoluteChangesKgCO2e: <ranked values>
- corroborationNeeded: <cost, utilization, deployment, or telemetry signals>
- conclusion: <observed contributor pattern, not an unsupported root cause>
```
