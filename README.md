# Carbon SRE

Carbon SRE is an Azure SRE Agent plugin for safe, repeatable Carbon Optimization operations. It packages skills that help operators discover available emissions data, query reports, validate subscription access, and explain month-over-month results.

The repository is a standalone plugin: `plugin.json` identifies the package and `skills/` contains the skills imported by Azure SRE Agent. Templates, validation, and contributor guidance live outside the production skill path so they are not imported as active skills.

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
3. Grant the calling user, service principal, or managed identity the **Carbon Optimization Reader** role on each target subscription. Subscription scope is recommended when querying all subscription resources.
4. Use lowercase subscription IDs and first-of-month dates in report requests.
5. Query the available data range before selecting report dates.
6. For a Live Report, configure a read-only Carbon connector; installing this plugin alone does not create a data connector.

Do not add client secrets, bearer tokens, customer exports, or unredacted incident data to this repository.

## Install and use

Install this repository as a standalone plugin from the Azure SRE Agent Plugins page, then select the imported skills from the Skill builder. See the [plugin installation guide](https://learn.microsoft.com/en-us/azure/sre-agent/tutorials/connectors/install-plugin-from-url) for the supported installation flow.

## Carbon Optimization references

- [Export Carbon Optimization emissions data](https://learn.microsoft.com/en-us/azure/carbon-optimization/api-export-data)
- [Query carbon emission data available date range API](https://learn.microsoft.com/en-us/rest/api/carbon/carbon-service/query-carbon-emission-data-available-date-range?view=rest-carbon-2025-04-01)
- [Query carbon emission reports API](https://learn.microsoft.com/en-us/rest/api/carbon/carbon-service/query-carbon-emission-reports?view=rest-carbon-2025-04-01)

## Live Report setup

The plugin includes an exported [Carbon emissions overview setup](templates/live-reports/carbon-emissions-overview.md). It defines the connector contract, subscription-selection rule, dashboard layout, and authoring prompt. Configure the connector first, then use `carbon-emissions-live-report` to create the saved Live Report.

## Repository layout

```text
.
├── plugin.json                         # Standalone plugin manifest
├── skills/                             # Production skills imported by the plugin
│   ├── carbon-optimization-reports/
│   ├── carbon-emissions-assessment/
│   ├── carbon-emissions-spike-investigation/
│   ├── carbon-emissions-optimization/
│   └── carbon-emissions-live-report/
├── templates/skill/SKILL.md            # Starter template; not imported
├── templates/live-reports/             # Connector-aware Live Report blueprints
├── scripts/validate_plugin.py          # Manifest and strict YAML validation
├── requirements-dev.txt                # Pinned validation dependency
├── .github/PULL_REQUEST_TEMPLATE.md    # Pull-request checklist
└── CONTRIBUTING.md                     # Skill authoring and safety rules
```

## Develop

Create skills in `skills/<kebab-case-name>/SKILL.md`. Each skill must include frontmatter with a matching `name` and a specific `description` that explains when it should activate.

Validate the repository locally before opening a pull request:

```bash
python -m pip install --requirement requirements-dev.txt
python scripts/validate_plugin.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for authoring, safety, and review requirements.
