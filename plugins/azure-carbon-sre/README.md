# azure-carbon-sre

`azure-carbon-sre` is an Azure SRE Agent plugin for safe, repeatable Azure Carbon Optimization operations.

## Included capabilities

- `carbon-optimization-reports` runs read-only, explicitly subscription-scoped Carbon Optimization report queries.
- `carbon-emissions-assessment` establishes the shared scope, freshness, access, and trend record required by downstream workflows.
- `carbon-emissions-spike-investigation` identifies category and resource contributors without asserting unsupported root causes.
- `carbon-emissions-optimization` requires a completed assessment before proposing a verified, non-destructive optimization path.
- `carbon-emissions-live-report` exports the connector-aware setup required to create a recurring Carbon dashboard.

## Install

Install the parent repository as a marketplace, then select the `azure-carbon-sre` plugin. For direct repository installation, use `plugins/azure-carbon-sre` as the package path.

## Prerequisites

See the parent [Azure Carbon SRE prerequisites](../../README.md#prerequisites) before running a Carbon Optimization skill. In particular, the calling identity needs the **Carbon Optimization Reader** role on every target subscription.

A saved Live Report also requires a read-only Carbon connector. Installing this plugin alone does not provision a connector.

## Managed identity authentication

A hosted agent should use its own managed identity to request an Azure Resource Manager token, then send that token in the `Authorization` header on every Carbon API request. Never copy a bearer token into a prompt, source file, log, or issue.

For Azure CLI callers, sign in with the intended identity and obtain a token for the Azure Resource Manager audience:

```bash
# System-assigned managed identity
az login --identity

# User-assigned managed identity; use its client ID
az login --identity --client-id <managed-identity-client-id>

access_token="$(az account get-access-token \
  --resource https://management.azure.com \
  --query accessToken --output tsv)"
```

Pass the value only in memory as `Authorization: Bearer ${access_token}`. SDK callers can use `DefaultAzureCredential` to obtain the same `https://management.azure.com/.default` token scope. See [sign in with a managed identity using Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-managed-identity) for the supported identity selectors.

An authorized administrator can grant the needed role at subscription scope with:

```bash
az role assignment create \
  --assignee-object-id <managed-identity-principal-id> \
  --assignee-principal-type ServicePrincipal \
  --role "Carbon Optimization Reader" \
  --scope "/subscriptions/<lowercase-subscription-id>"
```

If `carbonEmissionReports` returns HTTP `502` with `BearerFallbackDisabled`, verify the exact managed identity has this role on every requested subscription. The availability API may succeed with the same token even when the reports API is not authorized, so it is not proof of report access. Capture the tracking ID and UTC timestamp for escalation after confirming the token audience, identity, role assignment, and subscription scope.

## Contribute

See the repository [contribution guide](../../CONTRIBUTING.md) for skill and plugin authoring requirements.
