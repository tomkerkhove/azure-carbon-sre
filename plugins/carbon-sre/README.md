# carbon-sre

`carbon-sre` is an Azure SRE Agent plugin for safe, repeatable Azure Carbon Optimization operations.

## Included capabilities

- `carbon-optimization-reports` runs read-only, explicitly subscription-scoped Carbon Optimization report queries.
- `carbon-emissions-assessment` establishes the shared scope, freshness, access, and trend record required by downstream workflows.
- `carbon-emissions-spike-investigation` identifies category and resource contributors without asserting unsupported root causes.
- `carbon-emissions-optimization` requires a completed assessment before proposing a verified, non-destructive optimization path.
- `carbon-emissions-live-report` exports the connector-aware setup required to create a recurring Carbon dashboard.

## Install

Install the parent repository as a marketplace, then select the `carbon-sre` plugin. For direct repository installation, use `plugins/carbon-sre` as the package path.

## Prerequisites

See the parent [Carbon SRE prerequisites](../../README.md#prerequisites) before running a Carbon Optimization skill. In particular, the calling identity needs the **Carbon Optimization Reader** role on every target subscription.

A saved Live Report also requires a read-only Carbon connector. Installing this plugin alone does not provision a connector.

## Contribute

See the repository [contribution guide](../../CONTRIBUTING.md) for skill and plugin authoring requirements.
