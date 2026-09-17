---
name: carbon-emissions-live-report
description: Create a connector-backed Carbon Live Report or a scheduled static Carbon snapshot with freshness, trend, and contributor evidence.
---

# Carbon emissions Live Report

Use this skill when the user wants a recurring Carbon Optimization dashboard.

## Choose the dashboard mode

Ask the user which subscriptions the dashboard should query; do not default to the agent subscription or a prior scope. Use lowercase subscription IDs.

| Mode | When to use it | Freshness behavior |
| --- | --- | --- |
| Connector-backed Live Report | A read-only Carbon connector is configured and the user wants data to refresh whenever the report is opened. | The report calls approved connector tools at view time. |
| Scheduled static snapshot | No connector exists, but the agent can run scheduled tasks, query Carbon APIs with a managed identity, and save reports. | A task refreshes the HTML on its schedule; viewing makes no tool or Azure calls. |

Never describe a static snapshot as a connector-backed or view-time-live report. Label it **Static snapshot** and show its UTC refresh time.

## Shared preconditions

- Confirm each selected subscription has Carbon Optimization data available.
- The querying identity must have `Carbon Optimization Reader` on every selected subscription. The general Azure RBAC `Reader` role is recommended for resource discovery, but does not replace the Carbon role.
- Query the available data range before choosing dates. Use first-of-month values and report the exact range and returned month count; do not assume whether the API treats the end date as inclusive or exclusive.
- Use only read-only Carbon and Azure queries. Do not include remediation buttons in the first report version.
- Display the selected scope, included carbon scopes, available-through date, access denials, missing months, pagination state, and empty-data states prominently.

## Connector-backed Live Report

Use this mode only after confirming a read-only Carbon connector exists. Its identity must meet the shared RBAC preconditions.

### Required connector operations

The connector should expose read-only operations equivalent to:

1. `get_available_date_range`
2. `get_emissions_report` for `OverallSummaryReport`, `MonthlySummaryReport`, `TopItemsSummaryReport`, `TopItemsMonthlySummaryReport`, and `ItemDetailsReport`

Validate subscription IDs, first-of-month dates, report type, category type, page size, and pagination token at the connector boundary.

### Authoring workflow

1. Discover the connector and probe every intended read-only tool once before authoring.
2. Build the dashboard described in `templates/live-reports/carbon-emissions-overview.md`.
3. Use only the exact probed tool names in both `window.sreagent.callTool(...)` and `allowedTools`.
4. Render every data value with `textContent`, handle partial failures per section, and use the required report CSP.

## Scheduled static snapshot fallback

Use this mode when no Carbon connector is configured but the user explicitly wants a recurring saved report and the agent has scheduled-task, report-save, managed-identity, and local HTML-rendering capabilities.

### Schedule setup

1. Use this mode only after the user explicitly requests a recurring saved snapshot and confirms the subscription scope.
2. Choose an intentional cadence. Carbon data is monthly, so weekly or daily refreshes are normally sufficient; avoid high-frequency polling.
3. List existing scheduled tasks and reports first. Use a stable scope-specific name such as `Carbon: Emissions Snapshot (<subscription-short-id>)`; do not reuse a generic dashboard name.
4. During interactive setup, compare scope, cadence, purpose, and mode for each similar task or report. Ask the user to choose reuse, replacement, or a distinct name before altering an existing object.
5. Create one named task with an explicit subscription scope, safe read-only constraints, and a rollback path: pausing or cancelling that exact task.
6. State that the report will first exist after the task's first successful execution if there is no immediate-run capability.

### Per-run procedure

1. Call `ListReports`. Create the report when no exact scope-specific name exists. If exactly one candidate exists, call `GetReport` and reuse its `reportId` only when its HTML is visibly marked **Static snapshot** for the same subscription scope. If multiple matches exist, or the existing report is connector-backed, unmarked, or scoped differently, stop without `SaveReport` and report the conflict.
2. Acquire a fresh Azure Resource Manager token through the configured managed identity. Never expose the token in HTML, logs, prompts, or task output.
3. Query the available range, then request `OverallSummaryReport` and `MonthlySummaryReport` for the selected range. Request latest-month resource-type contributors and a resource drilldown when supported.
4. Inspect `subscriptionAccessDecisionList` and pagination before interpreting `value`. A denial, missing month, failed contributor query, or incomplete page is a visible data-quality warning, not zero emissions.
5. Render one self-contained HTML document. Escape all values; include a restrictive CSP with `connect-src 'self'`; do not include runtime calls, remote data fetches, or remediation actions. Include a decision-first headline, range total, comparable-period change, latest-month change, a monthly trend, primary contributors, and resource drilldown when available.
6. Call `SaveReport` with the generated HTML file, exact scope-specific report name, validated `reportId` when present, and `allowedTools: []`.
7. Verify the returned report ID and version. If data collection fails, save a clearly labelled failure snapshot without secrets only when doing so is safe; otherwise fail the run rather than publishing misleading values.

### Static snapshot content contract

Each saved snapshot must state:

- **Static snapshot** and the UTC refresh time.
- Subscription scope, carbon scopes, available-through date, and report range.
- Data-quality warnings, including access decisions and contributor/drilldown gaps.
- Emission values in kgCO2e with human-facing labels such as **Primary contributors:** rather than raw API field names.
- That viewing the report does not trigger Azure or connector calls.

## Report layout

1. Freshness and access banner.
2. KPI cards for selected-range total, comparable change, latest month, and latest-month movement.
3. Monthly emissions trend.
4. Latest-month resource-type contributor chart.
5. Top-resource drilldown table with current emissions, prior emissions, absolute and percentage changes, location, and resource group when available.
