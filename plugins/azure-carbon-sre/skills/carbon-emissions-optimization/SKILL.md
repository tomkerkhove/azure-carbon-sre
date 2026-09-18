---
name: carbon-emissions-optimization
description: Produce evidence-based, non-destructive Carbon Optimization recommendations only after reusable assessment and investigation skills establish the emissions state.
---

# Carbon emissions optimization

Use this skill to prioritize optimization opportunities. It does not make Azure changes.

## Required evidence gate

Before proposing an action, require a completed assessment from `carbon-emissions-assessment` with **Evidence status: Ready**.

- If the user asks for optimization directly, assess the state first instead of producing generic recommendations.
- If a material increase or concentrated contributor exists, use `carbon-emissions-spike-investigation` before suggesting a cause-specific action.
- Reuse the explicit subscription scope, available-through date, access results, and evidence gaps from the assessment. Do not expand scope without asking the user.

## Recommendation and presentation workflow

1. Identify the highest absolute contributors and persistent trends from the assessment or investigation.
2. Separate emissions observations from operational causes. Require cost, utilization, configuration, or deployment evidence before proposing a specific change.
3. Rank candidates by expected emissions relevance, confidence, customer impact, cost impact, reversibility, and validation signal.
4. Establish resource proof for each resource-level candidate when Reader access is available: resource ID, type, location, provisioning state, and current SKU or capacity. If a read is denied or unavailable, label the proof gap instead of implying the resource configuration.
5. Present the outcome for decisions rather than as a raw data dump:
   - Lead with one clear takeaway that distinguishes overall trend from the latest-month movement.
   - Show three scorecards: selected-period total, latest available month, and latest month-over-month change.
   - State the available-through date prominently and label historical anomalies separately from current opportunities.
   - Keep the current-priority action table to the highest-value items, normally no more than five.
   - Render a monthly emissions trend chart and a contributor bar chart when the underlying series is available. State the chart takeaway in plain language; use a compact table only when chart rendering is unavailable.
6. Evaluate capacity actions with configuration and recent utilization evidence:
   - Recommend a horizontal scale-in only when capacity is above the minimum, utilization and queue/error signals show sustained headroom, and the exact instance reduction and validation signal are known.
   - If capacity is already one, state that horizontal scale-in is unavailable. Assess a SKU scale-down separately and only after confirming application runtime, networking, availability, and feature compatibility.
7. When Azure API Management (`Microsoft.ApiManagement/service`) appears as a contributor, check for a multi-region deployment before proposing a capacity change: look for `additionalLocations` in the resource definition, or a `Capacity` metric split across more than one value of the `Location` dimension. If either signal is present, recommend evaluating APIM's built-in sustainability capabilities:
   - **Traffic shaping**: policies that read the current region's carbon-intensity context and throttle, delay, or reroute non-critical calls when intensity is high.
   - **Traffic shifting**: the built-in backend load balancer across `additionalLocations`, weighted to prefer lower-carbon-intensity regions while preserving failover.
   - State that this is a Premium-tier, multi-region-only capability, and confirm the SKU and `additionalLocations` count as resource proof before recommending it. Treat it as a policy/configuration change, not a capacity or SKU change, and still require a rollback and validation step.
8. Offer read-only verification first. For any future mutating action, provide the exact target, impact, rollback, and approval step.
9. State uncertainty explicitly. If utilization, cost, configuration, or deployment evidence is missing, say `No change recommended yet` and name the next verification needed.

## Presentation dependency

Load `carbon-response-presentation` and follow its current SKILL.md before writing any user-facing output.

Write a concise, decision-ready Markdown result in this order:

1. `## Carbon optimization snapshot` with the one-line takeaway.
2. A three-column scorecard table for selected-period total, latest available month, and latest month-over-month change.
3. A visible data-freshness note that includes the available-through date and material data gaps.
4. `### Charts` with a monthly emissions trend and contributor bar chart when data is available, followed by one sentence explaining what each chart shows.
5. `### What changed` with a prioritized table: priority, target, measured signal, and next read-only validation.
6. `### Resource proof` with resource ID, type, location, state, and current SKU or capacity for the leading resource-level candidates. State unavailable proof explicitly.
7. `### Capacity decision` for compute candidates: distinguish horizontal scale-in, SKU scale-down, and no action; state the observed metric evidence and compatibility gaps.
8. `### Multi-region sustainability` for Azure API Management candidates with `additionalLocations` or a multi-location `Capacity` metric: recommend evaluating policy-based traffic shaping and load-balanced traffic shifting, and state the SKU and region evidence.
9. `### Historical items to close` only when a historical spike needs ownership or lifecycle validation. Do not present it as a current optimization opportunity.
10. `### Evidence and decision` that lists corroborating evidence, gaps, and either a safe next action or `No change recommended yet`.
11. One plain-language candidate section for each item in the action table when more detail is useful.

Use kgCO2e units consistently. Use tables for comparisons, not nested bullets. Do not claim that a contributor is a root cause or that a change will reduce emissions without independent evidence.

```text
### Candidate
**Target:** <resource or category>
**Observed pattern:** <measured emissions pattern>
**Supporting evidence:** <present or missing, with source>
**Recommended next step:** <specific verification or change proposal>
**Confidence:** <high, medium, or low>
**Impact and rollback:** <required for any proposed change>
```

Never claim an emissions reduction estimate unless it is backed by a documented model or measured before-and-after evidence.
