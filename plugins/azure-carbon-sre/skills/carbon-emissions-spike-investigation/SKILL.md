---
name: carbon-emissions-spike-investigation
description: Investigate a Carbon Optimization emissions increase by extending a completed subscription-scoped carbon assessment with category and resource drilldowns.
---

# Carbon emissions spike investigation

Use this skill after `carbon-emissions-assessment` returns a completed assessment with **Evidence status: Ready**.

## Preconditions

- If the assessment is missing or incomplete, run the assessment first.
- Do not infer a subscription scope from earlier conversations; reuse only the explicit IDs shown in the assessment's scope section.
- Treat reported emissions movement as a signal, not proof of a deployment, configuration, or usage cause.

## Investigation workflow

1. Confirm the month or range with the unexpected change and define the comparison period.
2. Query `TopItemsMonthlySummaryReport` by `ResourceType` for the trend window.
3. Query `TopItemsSummaryReport` for the affected month by `ResourceType`, `ResourceGroup`, or `Location`.
4. Query `ItemDetailsReport` for the affected month and category. Follow pagination until `skipToken` is empty.
5. Rank contributors by absolute kgCO2e change and contribution to the selected period, not percentage alone.
6. For leading resource-level contributors, use an ARM read when available to verify resource ID, type, location, provisioning state, and current SKU or capacity. If access is denied, state that the resource proof is unavailable.
7. Render a monthly trend chart and a contributor bar chart when the report data supports them. Pair each chart with a one-sentence observation; do not substitute a chart for the underlying evidence table.
8. Identify candidates for corroboration with cost, utilization, deployment, or service telemetry. Do not label a root cause until an independent source supports it.

## Presentation dependency

Load `carbon-response-presentation` and follow its current SKILL.md before writing any user-facing output.

Extend the assessment with concise, decision-ready Markdown. Use clear phrases and a table when comparing more than one contributor.

```text
### Investigation
**Investigated period:** <date range>
**Primary contributors:** <resource types, resources, locations>
**Largest absolute changes:** <ranked kgCO2e values>

### Resource proof
| Resource | ID | State | Current SKU or capacity |
| --- | --- | --- | --- |
| <resource name> | <resource ID> | <state or unavailable> | <SKU, capacity, or unavailable> |

### Charts
- <monthly trend chart and its one-sentence takeaway>
- <contributor bar chart and its one-sentence takeaway>

**Corroboration still needed:** <cost, utilization, deployment, or telemetry signals>
**Conclusion:** <observed contributor pattern, not an unsupported root cause>
```
