---
name: carbon-response-presentation
description: Shared response-presentation contract for Azure Carbon SRE workflows. Load before producing user-facing Carbon analysis, investigation, optimization, report, or dashboard output.
---

# Carbon response presentation

Load this skill before writing any user-facing output for another Azure Carbon SRE skill. It centralizes presentation only; the calling skill remains responsible for evidence collection, scope, safety, and domain-specific decisions.

## User-facing presentation

Every response must use sentence-cased headings and human-facing labels. Do not expose raw field names, camelCase keys, or schema-shaped labels to the user.

Lead with the decision-relevant takeaway. Present explicit scope, time range, freshness, units, access outcomes, and material limitations before recommendations or conclusions. Use kgCO2e consistently for emissions.

## Decision-ready structure

Use the smallest structure that answers the request while preserving these elements when available:

1. A one-line takeaway that distinguishes the selected-period trend from the latest available month.
2. Scope and freshness: explicit subscriptions, carbon scopes, reporting period, and available-through date.
3. A compact comparison table or scorecards for material values.
4. A monthly trend chart and contributor chart when the underlying series supports them; pair every chart with a one-sentence plain-language takeaway. Use a compact table only when chart rendering is unavailable.
5. Data quality: access denials, missing months, pagination state, incomplete optional queries, empty results, and baseline revisions. Never treat a gap or denial as zero emissions.
6. A clear decision, evidence status, or next read-only verification.

## Presentation rules

- Use readable labels such as **Latest available month**, **Available through**, **Primary contributors**, and **Evidence status**.
- Use tables for comparisons; do not bury comparable values in nested bullets or dense prose.
- Keep raw API payloads, internal object names, response schemas, and transport-specific terminology out of user-facing output.
- State unavailable evidence plainly. Do not turn uncertainty into a causal claim, an optimization recommendation, or an emissions-reduction estimate.
- Preserve security boundaries: never display tokens, secrets, raw customer exports, or identifiers beyond the authorized scope.
- A dashboard or static report must apply the same rules to visible labels, tooltips, tables, warnings, and chart takeaways.
