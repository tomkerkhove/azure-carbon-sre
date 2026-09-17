---
name: carbon-emissions-assessment
description: Establish a subscription-scoped, reusable Carbon Optimization assessment before investigating changes or recommending optimization actions.
---

# Carbon emissions assessment

Use this skill as the first step for Carbon Optimization analysis. It produces a compact assessment record that `carbon-emissions-spike-investigation` and `carbon-emissions-optimization` consume.

## Subscription scope is mandatory

1. Check whether the user explicitly supplied subscription IDs.
2. If none were supplied, ask a pointed question naming the available subscription candidates. Do not silently use the agent's subscription or a previous query scope.
3. Confirm the selected IDs are lowercase and in the user's intended ownership boundary.

## Read-only assessment workflow

1. Query the available data range and use it as the freshness boundary.
2. Query `MonthlySummaryReport` for the requested period and all requested carbon scopes.
3. Query `OverallSummaryReport` for the same period.
4. Check `subscriptionAccessDecisionList` and separate denied subscriptions from zero-emission results.
5. Record any `skipToken`, missing months, or comparison values that would make interpretation incomplete.

## Assessment record

Return this structure in the response so downstream skills can reuse it:

```text
CarbonAssessment
- subscriptions: <explicit selected IDs>
- scopes: <Scope1/Scope2/Scope3 selection>
- availableThrough: <date from availability API>
- period: <start and end month>
- access: <allowed and denied subscriptions>
- baseline: <overall and monthly totals, units kgCO2e>
- trend: <month-over-month movement>
- dataGaps: <freshness, pagination, missing months, or access limitations>
- evidenceStatus: <ready | incomplete>
```

## Completion rule

Set `evidenceStatus` to `ready` only when the subscription scope is explicit, access outcomes are known, and the selected period is within the returned available range. Do not diagnose causes or recommend changes in this skill.
