---
name: carbon-optimization-reports
description: Query Azure Carbon Optimization availability and emissions reports, validate subscription access, and interpret month-over-month results.
---

# Carbon Optimization reports

Use this skill for requests to retrieve or interpret Azure Carbon Optimization emissions data.

## Subscription selection is mandatory

1. Check whether the user explicitly supplied subscription IDs.
2. If none were supplied, ask which subscriptions to query before sending a report request. When concrete candidates are available, present them as choices.
3. Do not default to the agent subscription, a prior conversation scope, or every accessible subscription.
4. Confirm selected IDs are lowercase and repeat the final scope in the result.

## Safety and access

- Treat report queries as read-only.
- Use an Azure Resource Manager token for `https://management.azure.com` and send it as `Authorization: Bearer <token>` on every Carbon API request.
- For a hosted agent, obtain the token through its managed identity: use `az login --identity` for a system-assigned identity, or `az login --identity --client-id <client-id>` for a user-assigned identity, then request the `https://management.azure.com` resource token. SDK callers should use `DefaultAzureCredential` with the `https://management.azure.com/.default` scope.
- Confirm the calling service principal or managed identity has `Carbon Optimization Reader` on every target subscription; this role is required for Carbon report queries.
- The general Azure RBAC `Reader` role is additionally recommended when the identity needs Azure resource discovery. It does not replace `Carbon Optimization Reader`.
- Never expose bearer tokens, client secrets, or raw customer export data beyond the requested scope.

### Managed identity failure diagnosis

If `carbonEmissionReports` returns HTTP `502` with `BearerFallbackDisabled`:

1. Confirm the request used the hosted agent's managed identity, an Azure Resource Manager token, and the `Authorization` header; do not fall back to a copied user token.
2. Verify `Carbon Optimization Reader` is assigned to that exact identity at each requested subscription scope. An availability request succeeding with the same token does not prove that report access is authorized.
3. Capture the tracking ID, UTC timestamp, API version, and requested subscription IDs for escalation if the role assignment is present and the failure persists.

See [managed identity authentication](../../README.md#managed-identity-authentication) for the Azure CLI role-assignment and token-acquisition examples.

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
- Latest-month emissions represent the requested range; previous-month emissions are the comparable prior range.
- The month-over-month emissions-change ratio is a ratio, not a percentage. Multiply by 100 only when presenting it as a percentage.
- State the subscription scope, date range, included scopes, report type, and any denied subscriptions with every summary.

## User-facing presentation

Every response must use sentence-cased headings and human-facing labels. Do not expose raw field names, camelCase keys, or schema-shaped labels to the user.

Lead with a one-line takeaway, then show scope and freshness, a compact kgCO2e comparison table, and data-quality limitations. Use a monthly trend chart with a one-sentence takeaway when the series is available; otherwise use a compact table. Label access denials, missing months, incomplete pagination, and unavailable comparison values explicitly instead of returning raw API payloads or treating gaps as zero.

## References

- `references/api.md` contains the public export guide and REST API links.
