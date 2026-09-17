# Carbon SRE

Carbon SRE is an Azure SRE Agent plugin marketplace for safe, repeatable Carbon Optimization operations. The installable `carbon-sre` package includes skills for report queries, assessment, spike investigation, optimization recommendations, and Live Report setup.

## Install

End users install this repository as a marketplace, then choose the `carbon-sre` plugin from the marketplace catalog. For direct URL installation, use `plugins/carbon-sre` as the path in the repository.

The importable package declares its skills explicitly in `plugins/carbon-sre/plugin.json`, matching the official Azure SRE Agent marketplace layout.

## Included capabilities

- `carbon-optimization-reports` provides a read-only workflow for explicit subscription-scoped Carbon Optimization report queries.
- `carbon-emissions-assessment` creates the shared scope, freshness, access, and trend record used by downstream skills.
- `carbon-emissions-spike-investigation` drills into category and resource contributors without asserting unsupported root causes.
- `carbon-emissions-optimization` requires the completed assessment before it can propose a verified, non-destructive optimization path.
- `carbon-emissions-live-report` exports the connector-aware setup needed to author a recurring Carbon dashboard.

## Prerequisites

Before using a Carbon Optimization skill:

1. Target an Azure subscription with Carbon Optimization data available.
2. Authenticate to Azure Resource Manager (`https://management.azure.com`).
3. Grant the calling user, service principal, or managed identity the **Carbon Optimization Reader** role on each target subscription.
4. Use lowercase subscription IDs and first-of-month dates in report requests.
5. Query the available data range before selecting report dates.
6. For a Live Report, configure a read-only Carbon connector; installing this plugin alone does not create a data connector.

Do not add client secrets, bearer tokens, customer exports, or unredacted incident data to this repository.

## Carbon Optimization references

- [Export Carbon Optimization emissions data](https://learn.microsoft.com/en-us/azure/carbon-optimization/api-export-data)
- [Query carbon emission data available date range API](https://learn.microsoft.com/en-us/rest/api/carbon/carbon-service/query-carbon-emission-data-available-date-range?view=rest-carbon-2025-04-01)
- [Query carbon emission reports API](https://learn.microsoft.com/en-us/rest/api/carbon/carbon-service/query-carbon-emission-reports?view=rest-carbon-2025-04-01)

## Live Report setup

The plugin includes an exported [Carbon emissions overview setup](plugins/carbon-sre/templates/live-reports/carbon-emissions-overview.md). It defines the connector contract, subscription-selection rule, dashboard layout, and authoring prompt. Configure the connector first, then use `carbon-emissions-live-report` to create the saved Live Report.

## Repository layout

```text
.
├── .github/plugin/marketplace.json      # Marketplace manifest
├── plugins/carbon-sre/                   # Installable plugin package
│   ├── plugin.json                       # Plugin manifest with skills/ declaration
│   ├── skills/                           # Production skills imported by the plugin
│   └── templates/                        # Supporting templates; not imported as skills
├── scripts/validate_plugin.py            # Marketplace and package validation
├── requirements-dev.txt                  # Pinned validation dependency
└── CONTRIBUTING.md                       # Skill authoring and safety rules
```

## Develop

Create skills in `plugins/carbon-sre/skills/<kebab-case-name>/SKILL.md`. Each skill must include frontmatter with a matching `name` and a specific `description` that explains when it should activate.

Validate the marketplace and plugin before opening a pull request:

```bash
python -m pip install --requirement requirements-dev.txt
python scripts/validate_plugin.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for authoring, safety, and review requirements.
