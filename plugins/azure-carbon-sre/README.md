# azure-carbon-sre

`azure-carbon-sre` is an Azure SRE Agent plugin for safe, repeatable Azure Carbon Optimization operations.

## Included capabilities

- `carbon-optimization-reports` runs read-only, explicitly subscription-scoped Carbon Optimization report queries.
- `carbon-emissions-assessment` establishes the shared scope, freshness, access, and trend record required by downstream workflows.
- `carbon-emissions-spike-investigation` identifies category and resource contributors without asserting unsupported root causes.
- `carbon-emissions-optimization` requires a completed assessment before proposing a verified, non-destructive optimization path.
- `carbon-emissions-live-report` creates either a connector-backed dashboard or, on explicit request and with the required capabilities, a scheduled static snapshot.

## Install

Install this repository as a marketplace, then select the `azure-carbon-sre` plugin. For direct repository installation, use `plugins/azure-carbon-sre` as the package path.

## Prerequisites

Before using a Carbon Optimization skill:

1. Target an Azure subscription with Carbon Optimization data available.
2. Authenticate to Azure Resource Manager at `https://management.azure.com`.
3. Grant the calling user, service principal, or managed identity the **Carbon Optimization Reader** role on every target subscription. This role is required for Carbon report queries.
4. Additionally assign the general Azure RBAC **Reader** role when the identity needs to discover Azure resource metadata. It is recommended, but it does not replace **Carbon Optimization Reader**.
5. Use lowercase subscription IDs and first-of-month dates in report requests.
6. Query the available data range before selecting report dates.
7. Configure a read-only Carbon connector for a dashboard that refreshes when viewed. Without a connector, use the scheduled static-snapshot fallback only when the user explicitly requests recurring saved output and scheduled tasks, report saving, managed-identity Carbon queries, and local HTML rendering are available.

Do not add client secrets, bearer tokens, customer exports, or unredacted incident data to the plugin package.

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

An authorized administrator must grant **Carbon Optimization Reader** at subscription scope for Carbon report queries. Assign the general Azure RBAC **Reader** role additionally when the identity needs resource discovery; it is recommended but does not replace the required Carbon role.

```bash
# Required for Carbon reports
az role assignment create \
  --assignee-object-id <managed-identity-principal-id> \
  --assignee-principal-type ServicePrincipal \
  --role "Carbon Optimization Reader" \
  --scope "/subscriptions/<lowercase-subscription-id>"

# Recommended for general Azure resource discovery
az role assignment create \
  --assignee-object-id <managed-identity-principal-id> \
  --assignee-principal-type ServicePrincipal \
  --role "Reader" \
  --scope "/subscriptions/<lowercase-subscription-id>"
```

If `carbonEmissionReports` returns HTTP `502` with `BearerFallbackDisabled`, verify the exact managed identity has the required **Carbon Optimization Reader** role on every requested subscription. The availability API may succeed with the same token even when the reports API is not authorized, so it is not proof of report access. Capture the tracking ID and UTC timestamp for escalation after confirming the token audience, identity, role assignment, and subscription scope.

## Contribute

To add a skill to this package:

1. Create `skills/<skill-name>/SKILL.md` using lowercase kebab-case for `<skill-name>`.
2. Add YAML frontmatter with a `name` that matches the directory and a specific `description` that states when the skill should activate.
3. Write an evidence-driven procedure that starts with read-only discovery and requires explicit confirmation, impact assessment, and rollback guidance for mutations.
4. Keep skill-specific references beside the skill and use `templates/` only for material that is not installed as a production skill.
5. From the marketplace repository checkout, run `python3 scripts/validate_plugin.py` before opening a pull request.
