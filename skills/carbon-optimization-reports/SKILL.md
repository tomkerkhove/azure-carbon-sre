---
name: carbon-optimization-reports
description: Query Azure Carbon Optimization availability and emissions reports, validate subscription access, and interpret month-over-month results.
---

# Carbon Optimization reports

Use this skill for requests to retrieve or interpret Azure Carbon Optimization emissions data.

## Safety and access

- Treat report queries as read-only.
- Use an Azure Resource Manager token for `https://management.azure.com`.
- Confirm the calling service principal or managed identity has the `Carbon Optimization Reader` role on every target subscription.
- Never expose bearer tokens, client secrets, or raw customer export data beyond the requested scope.

## Workflow

1. Query the available data range before choosing dates:
   `POST /providers/Microsoft.Carbon/queryCarbonEmissionDataAvailableDateRange?api-version=2025-04-01`.
2. Use lowercase subscription IDs in `subscriptionList` and first-of-month dates in `dateRange`.
3. Select the smallest report type that answers the request:
   - `OverallSummaryReport` for totals across a range.
   - `MonthlySummaryReport` for month-by-month totals.
   - `TopItemsSummaryReport` or `TopItemsMonthlySummaryReport` for the highest-emitting categories.
   - `ItemDetailsReport` for one month of granular resource, group, type, location, or subscription data.
4. Send `POST /providers/Microsoft.Carbon/carbonEmissionReports?api-version=2025-04-01` with `subscriptionList`, `carbonScopeList`, `dateRange`, and the selected `reportType`.
5. Check `subscriptionAccessDecisionList` before interpreting `value`. Report denied subscriptions separately from zero-emission results.
6. Follow `skipToken` until it is absent when the response is paginated.

## Interpretation

- Emissions values are expressed in kgCO2e.
- `latestMonthEmissions` represents the requested range; `previousMonthEmissions` is the comparable prior range.
- `monthOverMonthEmissionsChangeRatio` is a ratio, not a percentage. Multiply by 100 only when presenting it as a percentage.
- State the subscription scope, date range, included scopes, report type, and any denied subscriptions with every summary.

## References

- `references/api.md` contains the public export guide and REST API links.
