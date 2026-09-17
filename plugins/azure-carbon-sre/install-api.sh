#!/usr/bin/env bash
# Install the Azure Carbon SRE plugin and one static-snapshot task per explicit subscription.
# Requires: az (logged in), curl, and python3. This script never grants Azure roles or deletes tasks.
#
# Usage:
#   AGENT_RESOURCE_ID=/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.App/agents/<agent> \
#   CARBON_SUBSCRIPTIONS=<lowercase-subscription-id>[,<lowercase-subscription-id>] \
#   ./install-api.sh
set -euo pipefail
umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"

AGENT_RESOURCE_ID="${AGENT_RESOURCE_ID:-}"
ENDPOINT="${ENDPOINT:-}"
TOKEN_RESOURCE="${TOKEN_RESOURCE:-https://azuresre.dev}"
MARKETPLACE_NAME="${MARKETPLACE_NAME:-azure-carbon-sre-plugins}"
PLUGIN_NAME="${PLUGIN_NAME:-azure-carbon-sre}"
REPO_SLUG="${REPO_SLUG:-tomkerkhove/azure-carbon-sre}"
SOURCE_FORMAT="${SOURCE_FORMAT:-copilot}"
GITHUB_PAT="${GITHUB_PAT:-}"
TASK_AGENT_NAME="${TASK_AGENT_NAME:-}"
CARBON_SUBSCRIPTIONS="${CARBON_SUBSCRIPTIONS:-}"
CARBON_TASK_CRON="${CARBON_TASK_CRON:-0 15 * * 1}"
CARBON_MODEL_TIER="${CARBON_MODEL_TIER:-ReasoningHeavy}"
TASK_RENDERER="$SCRIPT_DIR/scheduled-tasks/render_tasks.py"

say() { printf '\n==> %s\n' "$*"; }
ok() { printf '  OK %s\n' "$*"; }
warn() { printf '  WARN %s\n' "$*"; }
die() { printf '  ERROR %s\n' "$*" >&2; exit 1; }

say "Preflight"
for command in az curl python3 mktemp; do
  command -v "$command" >/dev/null 2>&1 || die "$command is required."
done
az account show >/dev/null 2>&1 || die "Not logged in to Azure. Run az login first."
[ -n "$AGENT_RESOURCE_ID" ] || die "AGENT_RESOURCE_ID is required."
[ -n "$CARBON_SUBSCRIPTIONS" ] || die "CARBON_SUBSCRIPTIONS is required; the installer will not infer a subscription."
[ -f "$TASK_RENDERER" ] || die "Scheduled-task renderer not found: $TASK_RENDERER"
python3 "$TASK_RENDERER" check || die "Scheduled-task references drifted from their canonical prompt."

TEMP_ROOT="${TMPDIR:-/tmp}"
TEMP_ROOT="$(cd "$TEMP_ROOT" 2>/dev/null && pwd -P)" || die "Temporary directory is unavailable."
case "$TEMP_ROOT" in
  "$REPO_ROOT"|"$REPO_ROOT"/*) TEMP_ROOT="$(cd /tmp && pwd -P)";;
esac
INSTALL_WORK_DIR="$(mktemp -d "$TEMP_ROOT/carbon-install.XXXXXXXX")" || die "Could not create installer work directory."
chmod 700 "$INSTALL_WORK_DIR"
trap 'rm -rf -- "$INSTALL_WORK_DIR"' EXIT

say "Discovering agent endpoint and user-assigned identity"
ARM_AGENT_JSON="$(az resource show --ids "$AGENT_RESOURCE_ID" -o json)" || die "Could not read agent ARM resource."
DISCOVERY_JSON="$(printf '%s' "$ARM_AGENT_JSON" | python3 -c '
import json
import re
import sys

doc = json.load(sys.stdin)
properties = doc.get("properties")
if not isinstance(properties, dict):
    raise SystemExit("Agent resource is missing properties.")
endpoint = properties.get("agentEndpoint")
if not isinstance(endpoint, str) or not endpoint.strip():
    raise SystemExit("Agent resource properties.agentEndpoint is empty.")
name = doc.get("name")
if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", name):
    raise SystemExit("Agent resource name is missing or invalid.")
identity = doc.get("identity")
uamis = identity.get("userAssignedIdentities") if isinstance(identity, dict) else None
if not isinstance(uamis, dict) or len(uamis) != 1:
    raise SystemExit("Agent resource must have exactly one user-assigned identity.")
uami_resource_id = next(iter(uamis))
if not isinstance(uami_resource_id, str) or not uami_resource_id.strip():
    raise SystemExit("Agent user-assigned identity resource ID is empty.")
json.dump({"endpoint": endpoint.strip().rstrip("/"), "agentName": name, "uamiResourceId": uami_resource_id.strip()}, sys.stdout)
')" || die "Agent endpoint and identity discovery failed."

ARM_ENDPOINT="$(printf '%s' "$DISCOVERY_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["endpoint"])')"
DISCOVERED_AGENT_NAME="$(printf '%s' "$DISCOVERY_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["agentName"])')"
UAMI_RESOURCE_ID="$(printf '%s' "$DISCOVERY_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["uamiResourceId"])')"
if [ -n "$ENDPOINT" ] && [ "${ENDPOINT%/}" != "$ARM_ENDPOINT" ]; then
  die "ENDPOINT does not match properties.agentEndpoint on AGENT_RESOURCE_ID."
fi
ENDPOINT="$ARM_ENDPOINT"
if [ -z "$TASK_AGENT_NAME" ]; then
  TASK_AGENT_NAME="$DISCOVERED_AGENT_NAME"
fi
case "$TASK_AGENT_NAME" in *[!A-Za-z0-9._-]*|'') die "TASK_AGENT_NAME contains unsupported characters.";; esac
CARBON_IDENTITY_CLIENT_ID="$(az identity show --ids "$UAMI_RESOURCE_ID" --query clientId -o tsv)" || die "Could not resolve the agent UAMI client ID."
case "$CARBON_IDENTITY_CLIENT_ID" in *[!A-Za-z0-9._-]*|'') die "Agent UAMI client ID contains unsupported characters.";; esac
export CARBON_SUBSCRIPTIONS CARBON_TASK_CRON CARBON_MODEL_TIER CARBON_IDENTITY_CLIENT_ID TASK_AGENT_NAME
python3 "$TASK_RENDERER" api >/dev/null || die "Invalid Carbon task configuration."
ok "Target task agent: $TASK_AGENT_NAME"
ok "Configured snapshot subscriptions validated"

say "Acquiring agent management token"
TOKEN="$(az account get-access-token --resource "$TOKEN_RESOURCE" --query accessToken -o tsv)" || die "Failed to mint agent management token."
[ -n "$TOKEN" ] || die "Agent management token is empty."

HTTP_CODE=""
RESP_BODY=""
api() {
  local method="$1" path="$2" body="${3:-}"
  local args=(-s -w '\n%{http_code}' -X "$method" -H "Authorization: Bearer $TOKEN")
  if [ -n "$body" ]; then args+=(-H "Content-Type: application/json" --data-binary @"$body"); fi
  local output
  output="$(curl "${args[@]}" "$ENDPOINT$path")" || return
  HTTP_CODE="${output##*$'\n'}"
  RESP_BODY="${output%$'\n'*}"
}

say "Registering marketplace $MARKETPLACE_NAME"
MARKETPLACE_BODY="$INSTALL_WORK_DIR/marketplace.json"
MARKETPLACE_NAME="$MARKETPLACE_NAME" REPO_SLUG="$REPO_SLUG" SOURCE_FORMAT="$SOURCE_FORMAT" GITHUB_PAT="$GITHUB_PAT" python3 - "$MARKETPLACE_BODY" <<'PY'
import json
import os
import sys

spec = {
    "sourceType": "github",
    "sourceUrl": os.environ["REPO_SLUG"],
    "owner": {"name": os.environ["REPO_SLUG"].split("/", 1)[0]},
    "description": "Azure Carbon SRE plugin",
    "sourceFormat": os.environ["SOURCE_FORMAT"],
}
if os.environ.get("GITHUB_PAT"):
    spec["credentials"] = {"authMethod": "pat", "pat": os.environ["GITHUB_PAT"]}
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    json.dump({"metadata": {"name": os.environ["MARKETPLACE_NAME"]}, "spec": spec}, handle)
PY
api POST /api/v2/plugins/marketplaces "$MARKETPLACE_BODY" || die "Marketplace registration failed before a response."
rm -f -- "$MARKETPLACE_BODY"
case "$HTTP_CODE" in
  200|201|202) ok "Marketplace upserted";;
  *) die "Marketplace registration failed (HTTP $HTTP_CODE): $RESP_BODY";;
esac

say "Waiting for marketplace clone"
for attempt in $(seq 1 30); do
  api GET "/api/v2/plugins/marketplaces/${MARKETPLACE_NAME}" || die "Marketplace status request failed."
  status="$(printf '%s' "$RESP_BODY" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("spec",{}).get("cloneStatus",""))' 2>/dev/null || true)"
  case "$status" in
    Ready) ok "Marketplace clone is ready"; break;;
    Failed) die "Marketplace clone failed: $RESP_BODY";;
    *) [ "$attempt" -lt 30 ] || die "Timed out waiting for marketplace clone."; sleep 2;;
  esac
done

say "Installing plugin $PLUGIN_NAME"
api POST "/api/v2/plugins/marketplaces/${MARKETPLACE_NAME}/plugins/${PLUGIN_NAME}/install" || die "Plugin installation request failed before a response."
case "$HTTP_CODE" in
  200|201|202) ok "Plugin installation requested";;
  *) die "Plugin installation failed (HTTP $HTTP_CODE): $RESP_BODY";;
esac

say "Waiting for Carbon skills"
for attempt in $(seq 1 60); do
  api GET /api/v2/plugins/installations || die "Plugin installation status request failed."
  if printf '%s' "$RESP_BODY" | MARKETPLACE_NAME="$MARKETPLACE_NAME" PLUGIN_NAME="$PLUGIN_NAME" python3 -c '
import json
import os
import sys
expected = {
    "carbon-optimization-reports",
    "carbon-emissions-assessment",
    "carbon-emissions-spike-investigation",
    "carbon-emissions-optimization",
    "carbon-emissions-live-report",
}
data = json.load(sys.stdin)
for item in data if isinstance(data, list) else data.get("value", []):
    spec = item.get("spec", {})
    if spec.get("marketplaceName") == os.environ["MARKETPLACE_NAME"] and spec.get("pluginName") == os.environ["PLUGIN_NAME"]:
        imported = {skill.get("skillName") for skill in spec.get("importedSkills", [])}
        raise SystemExit(0 if expected <= imported else 1)
raise SystemExit(1)
'; then
    ok "All Carbon skills are ready"
    break
  fi
  [ "$attempt" -lt 60 ] || die "Timed out waiting for Carbon skills."
  sleep 2
done

say "Loading existing scheduled tasks"
api GET /api/v1/scheduledtasks || die "Could not list scheduled tasks."
case "$HTTP_CODE" in
  200) printf '%s' "$RESP_BODY" > "$INSTALL_WORK_DIR/tasks-before.json";;
  *) die "Could not list scheduled tasks (HTTP $HTTP_CODE): $RESP_BODY";;
esac
python3 "$TASK_RENDERER" install-plan --existing "$INSTALL_WORK_DIR/tasks-before.json" --output-dir "$INSTALL_WORK_DIR" || die "Could not prepare Carbon task install plan."

while IFS=$'\x1f' read -r body_name name payload_agent task_id current_agent; do
  [ -n "$body_name" ] || continue
  [ "$payload_agent" = "$TASK_AGENT_NAME" ] || die "Rendered task targets an unexpected agent: $name"
  body="$INSTALL_WORK_DIR/$body_name"
  say "Upserting scheduled task $name"
  if [ -n "$task_id" ]; then
    [ "$current_agent" = "$TASK_AGENT_NAME" ] || die "Existing task $name targets $current_agent; refusing to replace it. Retarget it manually, then rerun the installer."
    api PUT "/api/v1/scheduledtasks/${task_id}" "$body" || die "Task update failed before a response."
    case "$HTTP_CODE" in
      200|201|204) ok "Scheduled task updated";;
      *) die "Task update failed (HTTP $HTTP_CODE): $RESP_BODY";;
    esac
  else
    api POST /api/v1/scheduledtasks "$body" || die "Task creation failed before a response."
    case "$HTTP_CODE" in
      200|201) ok "Scheduled task created";;
      *) die "Task creation failed (HTTP $HTTP_CODE): $RESP_BODY";;
    esac
  fi
done < "$INSTALL_WORK_DIR/task-plan.tsv"

say "Verifying scheduled tasks"
api GET /api/v1/scheduledtasks || die "Task verification request failed."
case "$HTTP_CODE" in
  200) printf '%s' "$RESP_BODY" > "$INSTALL_WORK_DIR/tasks-after.json";;
  *) die "Could not verify scheduled tasks (HTTP $HTTP_CODE): $RESP_BODY";;
esac
python3 "$TASK_RENDERER" verify-install --existing "$INSTALL_WORK_DIR/tasks-after.json" --expected "$INSTALL_WORK_DIR/expected-tasks.json" || die "Carbon task verification failed."
ok "All requested Carbon static-snapshot tasks are present exactly once"

say "Done"
printf '  Plugin: %s\n' "$PLUGIN_NAME"
printf '  Task agent: %s\n' "$TASK_AGENT_NAME"
printf '  Scope: %s\n' "$CARBON_SUBSCRIPTIONS"
printf '  Cadence: %s\n' "$CARBON_TASK_CRON"
printf '  Rollback: pause or cancel only the exact Carbon: Emissions Snapshot task(s) created for these subscriptions.\n'
