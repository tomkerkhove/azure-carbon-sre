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

## Presentation dependency

Load `carbon-response-presentation` and follow its current SKILL.md before writing any user-facing output.

Return concise, decision-ready Markdown in this order:

1. `## Carbon emissions assessment` with a one-line takeaway that distinguishes the selected-period trend from the latest available month.
2. `### Scope and freshness` with the explicit subscriptions, carbon scopes, available-through date, and reporting period.
3. A three-column scorecard table for selected-period total, latest available month, and latest month-over-month change, all in kgCO2e.
4. `### Monthly trend` with a chart when the monthly series is available, followed by one plain-language takeaway. Use a compact table only when chart rendering is unavailable.
5. `### Data quality` with allowed and denied subscriptions, missing months, pagination state, freshness limits, and any comparison-baseline revision. Never describe a denial, gap, or empty optional response as zero emissions.
6. `### Evidence status` with **Ready** or **Incomplete**, followed by the exact reason and the next read-only verification when incomplete.

Keep the explicit scope, range, access outcome, baseline, trend, data-quality limitations, and evidence status in the visible response so downstream Carbon skills can reuse them. Do not emit a `CarbonAssessment` object, a code-block schema, or an internal field-name inventory.

## Completion rule

Set **Evidence status: Ready** only when the subscription scope is explicit, access outcomes are known, and the selected period is within the returned available range. Do not diagnose causes or recommend changes in this skill.
