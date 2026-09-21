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
   - Where the service supports autoscaling, prefer recommending it over a one-off scale-in when demand is variable, so capacity tracks load automatically instead of running a fixed, over-provisioned unit count. Link to the service's autoscale documentation when recommending it.

### API Management-specific guidance

7. For Azure API Management (`Microsoft.ApiManagement/service`) contributors, evaluate [sustainability capabilities](https://learn.microsoft.com/en-us/azure/api-management/sustainability) (preview) as recommendations in their own right, alongside the capacity evaluation above:
   - Before recommending either capability, verify that the subscription is enrolled in the limited preview and that each target region supports the preview. If either proof is unavailable, state `No change recommended yet` and name preview eligibility verification as the next step.
8. For eligible API Management contributors on the Developer, Basic, Standard, or Premium tier, evaluate [**traffic shaping**](https://learn.microsoft.com/en-us/azure/api-management/sustainability): policies that read the current region's carbon-intensity context and throttle, delay, or reroute non-critical calls when intensity is high. It does not depend on capacity, SKU, or region count.
9. For eligible Premium-tier API Management contributors, evaluate **traffic shifting**: the built-in [backend load balancer across `additionalLocations`](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-deploy-multi-region), weighted to prefer lower-carbon-intensity regions while preserving failover. Confirm a multi-region deployment with either `additionalLocations` in the resource definition or a [`Capacity` metric](https://learn.microsoft.com/en-us/azure/api-management/api-management-capacity) split across more than one `Location` value; state any unavailable resource proof separately.
10. For API Management capacity, apply the generic capacity-action evidence requirements from step 6 with these API Management-specific exceptions:
   - The [`Capacity` metric](https://learn.microsoft.com/en-us/azure/api-management/api-management-capacity) applies to every SKU except Consumption, which autoscales automatically.
   - For Developer, Basic, Standard, and Premium tiers, recommend scale-in when the evidence supports it.
   - Where supported, recommend [Azure Monitor autoscale](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-autoscale): it is available only on Basic, Standard, and Premium tiers and covers only the primary location in a multi-region deployment.
   - Do not skip this track when traffic shaping or traffic shifting is recommended.
11. Confirm the SKU for every API Management recommendation. Treat traffic shaping and traffic shifting as policy/configuration changes, not capacity or SKU changes, and require a rollback and validation step for each.
12. Offer read-only verification first. For any future mutating action, provide the exact target, impact, rollback, and approval step.
13. State uncertainty explicitly. If utilization, cost, configuration, or deployment evidence is missing, say `No change recommended yet` and name the next verification needed.

## Presentation dependency

Load `carbon-response-presentation` and follow its current SKILL.md before writing any user-facing output.

Write a concise, decision-ready Markdown result in this order:

1. `## Carbon optimization snapshot` with the one-line takeaway.
2. A three-column scorecard table for selected-period total, latest available month, and latest month-over-month change.
3. A visible data-freshness note that includes the available-through date and material data gaps.
4. `### Charts` with a monthly emissions trend and contributor bar chart when data is available, followed by one sentence explaining what each chart shows.
5. `### What changed` with a prioritized table: priority, target, measured signal, and next read-only validation.
6. `### Resource proof` with resource ID, type, location, state, and current SKU or capacity for the leading resource-level candidates. State unavailable proof explicitly.
7. `### Capacity decision` for compute candidates: distinguish horizontal scale-in, autoscale configuration, SKU scale-down, and no action; state the observed metric evidence and compatibility gaps.
8. `### API Management sustainability` for any Azure API Management candidate, presented as recommendations in their own right rather than only when a capacity change is proposed:
   - State the limited-preview enrollment and regional-availability evidence.
   - Recommend policy-based traffic shaping regardless of region count or capacity signal when preview eligibility is confirmed.
   - Recommend load-balanced traffic shifting when preview eligibility and either `additionalLocations` or a multi-location `Capacity` metric show a multi-region deployment.
   - Apply the capacity decision from the `Capacity decision` section as a complementary, independent track.
   - State the SKU and region evidence for each recommendation.
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
