# Carbon emissions overview Live Report setup

This is an exported setup blueprint, not a saved Live Report. A configured read-only Carbon connector is required before it can be authored as a live dashboard.

## Connector contract

Provide exact connector tool names for these operations during report authoring:

- Available range: no report body; returns `startDate` and `endDate`.
- Summary report: accepts explicit `subscriptionList`, `carbonScopeList`, `dateRange`, and `reportType`.
- Detailed report: additionally accepts `categoryType`, ordering, page size, top-item count, and pagination token when relevant.

The connector identity must have `Carbon Optimization Reader` on every selected subscription; this role is required for Carbon report queries. The general Azure RBAC `Reader` role is additionally recommended when the connector needs resource discovery, but it does not replace `Carbon Optimization Reader`. The connector must never return bearer tokens or accept arbitrary ARM URLs.

## Required filters

- Subscriptions: explicit user selection; no implicit default.
- Carbon scopes: Scope1, Scope2, Scope3, or an explicit subset.
- Date range: first-of-month values constrained by the available range.
- Contributor grouping: ResourceType by default; Resource, ResourceGroup, Location, and Subscription for drilldown.

## Dashboard layout

1. **Freshness and access banner**
   - Available-through date
   - Selected subscriptions and scopes
   - Denied subscriptions, missing months, and pagination notices
2. **KPI cards**
   - Latest month emissions (kgCO2e)
   - Previous month emissions
   - Month-over-month change
   - Selected-range total
3. **Trend chart**
   - Monthly emissions across the selected range
4. **Contributor chart**
   - Top resource types for the latest month
5. **Drilldown table**
   - Top resources with current emissions, prior emissions, absolute change, percentage change, region, and resource group

## Authoring prompt

```text
Create a Live Report named "Carbon Emissions Overview" using the configured Carbon connector.
Ask me to choose subscriptions before querying. Use the available-date operation first,
then show Scope1/Scope2/Scope3 monthly emissions for the selected range, a latest-month
top-resource-type chart, and a sortable resource drilldown table. Show the available-through
date, access denials, missing data, and pagination state. Use read-only tools only.
```
