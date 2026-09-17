---
name: carbon-emissions-live-report
description: Configure a connector-backed Live Report for Carbon Optimization emissions, freshness, trends, and contributor drilldowns.
---

# Carbon emissions Live Report

Use this skill when the user wants a recurring Carbon Optimization dashboard.

## Preconditions

- A Live Report can retrieve Carbon data only through a configured connector.
- Confirm a read-only Carbon connector exists before attempting to save a report. The connector identity must have `Carbon Optimization Reader` on the selected subscriptions; this role is required for Carbon report queries.
- The general Azure RBAC `Reader` role is additionally recommended when the connector needs Azure resource discovery. It does not replace `Carbon Optimization Reader`.
- If no connector exists, use `templates/live-reports/carbon-emissions-overview.md` as the exported setup blueprint. Do not create a static report and call it live.

## Required connector operations

The connector should expose read-only operations equivalent to:

1. `get_available_date_range`
2. `get_emissions_report` for `OverallSummaryReport`, `MonthlySummaryReport`, `TopItemsSummaryReport`, `TopItemsMonthlySummaryReport`, and `ItemDetailsReport`

Validate subscription IDs, first-of-month dates, report type, category type, page size, and pagination token at the connector boundary.

## Report authoring workflow

1. Ask the user which subscriptions the report should query; do not default to the agent subscription.
2. Discover the connector and probe each read-only tool before authoring.
3. Build the dashboard described in the exported blueprint.
4. Display available-through date, access denials, and empty-data states prominently.
5. Use only read-only operations. Do not include remediation buttons in the first report version.
