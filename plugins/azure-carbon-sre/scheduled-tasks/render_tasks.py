#!/usr/bin/env python3
"""Render and validate Carbon static-snapshot scheduled-task payloads."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import textwrap


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "task-manifest.json"
SUBSCRIPTION_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
PLAIN_VALUE_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
TEMPLATE_TOKEN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
OWNERSHIP_MARKER_PREFIX = "azure-carbon-sre:carbon-static-snapshot:"


def fail(message: str) -> None:
    raise ValueError(message)


def load_task() -> dict[str, object]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = data.get("task")
    if data.get("schemaVersion") != 1 or not isinstance(task, dict):
        fail("Unsupported or malformed task manifest")

    required_strings = (
        "id",
        "yaml",
        "defaultCron",
        "defaultModelTier",
        "description",
        "prompt",
    )
    for key in required_strings:
        if not isinstance(task.get(key), str) or not task[key].strip():
            fail(f"Task manifest requires non-empty string {key}")
    if task["id"] != "carbon-static-snapshot":
        fail("Task manifest must define carbon-static-snapshot")
    if not isinstance(task.get("tags"), list) or not all(
        isinstance(item, str) and item for item in task["tags"]
    ):
        fail("Task manifest requires non-empty string tags")
    if not (ROOT / task["prompt"]).is_file():
        fail(f"Missing prompt asset: {task['prompt']}")
    return task


def plain_value(name: str, value: object) -> str:
    value = str(value)
    if not value or any(ord(char) < 32 for char in value):
        fail(f"{name} must be non-empty and contain no control characters")
    return value


def identifier(name: str, value: object) -> str:
    value = plain_value(name, value)
    if not PLAIN_VALUE_PATTERN.fullmatch(value):
        fail(f"{name} contains unsupported characters")
    return value


def parse_subscriptions(value: str | None = None) -> list[str]:
    raw = os.environ.get("CARBON_SUBSCRIPTIONS", "") if value is None else value
    candidates = [item.strip() for item in raw.split(",") if item.strip()]
    if not candidates:
        fail("CARBON_SUBSCRIPTIONS is required as comma-separated lowercase subscription IDs")

    result: list[str] = []
    seen: set[str] = set()
    for subscription in candidates:
        if not SUBSCRIPTION_PATTERN.fullmatch(subscription):
            fail(
                "CARBON_SUBSCRIPTIONS must contain comma-separated lowercase GUID subscription IDs"
            )
        if subscription not in seen:
            seen.add(subscription)
            result.append(subscription)
    return result


def template_substitute(source: str, values: dict[str, str]) -> str:
    tokens = set(TEMPLATE_TOKEN.findall(source))
    remainder = TEMPLATE_TOKEN.sub("", source)
    if "{{" in remainder or "}}" in remainder:
        fail("Malformed source prompt placeholder")
    unknown = tokens - values.keys()
    if unknown:
        fail("Unresolved prompt variables: " + ", ".join(sorted(unknown)))
    for key in tokens:
        source = source.replace("{{" + key + "}}", values[key])
    return source.strip()


def task_name(subscription: str) -> str:
    return f"Carbon: Emissions Snapshot ({subscription})"


def ownership_marker(subscription: str) -> str:
    return OWNERSHIP_MARKER_PREFIX + subscription


def task_description(task: dict[str, object], subscription: str, reference: bool) -> str:
    marker = "__AZURE_CARBON_SRE_OWNERSHIP_MARKER__" if reference else ownership_marker(subscription)
    return f"{task['description']} [{marker}]"


def task_values(subscription: str, reference: bool = False) -> dict[str, str]:
    if reference:
        subscription_value = "__CARBON_SUBSCRIPTION__"
        report_name = "Carbon: Emissions Snapshot (__CARBON_SUBSCRIPTION_SHORT__)"
        agent = "__AGENT_NAME__"
        identity = "__CARBON_IDENTITY_CLIENT_ID__"
    else:
        subscription_value = subscription
        report_name = task_name(subscription)
        agent = identifier("TASK_AGENT_NAME", os.environ["TASK_AGENT_NAME"])
        identity = identifier(
            "CARBON_IDENTITY_CLIENT_ID", os.environ["CARBON_IDENTITY_CLIENT_ID"]
        )
    return {
        "CARBON_SUBSCRIPTION": subscription_value,
        "CARBON_REPORT_NAME": report_name,
        "CARBON_IDENTITY_CLIENT_ID": identity,
        "TASK_AGENT_NAME": agent,
    }


def render_task(subscription: str, reference: bool = False) -> dict[str, object]:
    task = load_task()
    values = task_values(subscription, reference)
    prompt = template_substitute(
        (ROOT / task["prompt"]).read_text(encoding="utf-8"), values
    )
    if reference:
        name = "Carbon: Emissions Snapshot (__CARBON_SUBSCRIPTION_SHORT__)"
        cron = "__CARBON_TASK_CRON__"
        model = str(task["defaultModelTier"])
    else:
        name = task_name(subscription)
        cron = plain_value(
            "CARBON_TASK_CRON",
            os.environ.get("CARBON_TASK_CRON", str(task["defaultCron"])),
        )
        model = identifier(
            "CARBON_MODEL_TIER",
            os.environ.get("CARBON_MODEL_TIER", str(task["defaultModelTier"])),
        )
    return {
        "id": str(task["id"]),
        "yaml": str(task["yaml"]),
        "name": name,
        "description": task_description(task, subscription, reference),
        "cronExpression": cron,
        "agentPrompt": prompt,
        "agent": values["TASK_AGENT_NAME"],
        "agentMode": "review",
        "modelTier": model,
        "tags": task["tags"],
    }


def api_payloads() -> list[dict[str, object]]:
    return [
        {
            key: value
            for key, value in render_task(subscription).items()
            if key not in {"id", "yaml", "tags"}
        }
        for subscription in parse_subscriptions()
    ]


def task_list(data: object) -> list[dict[str, object]]:
    items = data if isinstance(data, list) else data.get("value", []) if isinstance(data, dict) else None
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        fail("Scheduled-task list response must contain task objects")
    return items


def api_id(value: object) -> str:
    value = "" if value is None else plain_value("scheduled task id", value)
    if value and not PLAIN_VALUE_PATTERN.fullmatch(value):
        fail("Scheduled task id contains unsupported characters")
    return value


def write_install_plan(existing_path: Path, output_dir: Path) -> None:
    existing = task_list(json.loads(existing_path.read_text(encoding="utf-8")))
    payloads = api_payloads()
    names = [str(payload["name"]) for payload in payloads]
    if len(names) != len(set(names)):
        fail("Configured subscriptions produce duplicate snapshot task names")

    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    expected: list[dict[str, str]] = []
    for index, payload in enumerate(payloads, start=1):
        name = str(payload["name"])
        matches = [item for item in existing if item.get("name") == name]
        if len(matches) > 1:
            fail(f"Multiple scheduled tasks have canonical name: {name}")
        current = matches[0] if matches else {}
        current_id = api_id(current.get("id"))
        current_agent = "" if not current else plain_value(
            "scheduled task agent", current.get("agent", "")
        )
        if current and not current_agent:
            fail(f"Existing scheduled task has no agent: {name}")
        if current and current.get("description") != payload["description"]:
            fail(
                "Existing scheduled task is not owned by this installer or has a different "
                f"scope marker: {name}"
            )

        body_name = f"task-{index}.json"
        (output_dir / body_name).write_text(
            json.dumps(payload, separators=(",", ":")), encoding="utf-8"
        )
        rows.append(
            "\x1f".join(
                (body_name, name, str(payload["agent"]), current_id, current_agent)
            )
        )
        expected.append(
            {
                "name": name,
                "agent": str(payload["agent"]),
                "description": str(payload["description"]),
            }
        )

    (output_dir / "task-plan.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (output_dir / "expected-tasks.json").write_text(
        json.dumps({"tasks": expected}, separators=(",", ":")), encoding="utf-8"
    )


def verify_install(existing_path: Path, expected_path: Path) -> int:
    existing = task_list(json.loads(existing_path.read_text(encoding="utf-8")))
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    tasks = expected.get("tasks") if isinstance(expected, dict) else None
    if not isinstance(tasks, list):
        fail("Expected-task file is malformed")
    failures = []
    for item in tasks:
        matches = [
            task
            for task in existing
            if task.get("name") == item.get("name")
            and task.get("agent") == item.get("agent")
            and task.get("description") == item.get("description")
        ]
        if len(matches) != 1:
            failures.append(
                f"expected exactly one owned task on {item.get('agent')}: {item.get('name')}"
            )
    if failures:
        print("Scheduled-task verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


def quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_yaml() -> str:
    task = load_task()
    item = render_task("00000000-0000-0000-0000-000000000000", reference=True)
    description = textwrap.wrap(str(item["description"]), width=88)
    prompt_lines = str(item["agentPrompt"]).splitlines()
    lines = [
        "# Generated by render_tasks.py from task-manifest.json and prompts/.",
        "# Do not edit this file directly; run: python3 render_tasks.py write",
        "apiVersion: azuresre.ai/v1",
        "kind: ScheduledTask",
        "metadata:",
        f"  name: {quoted(str(item['name']))}",
        "  tags:",
        *(f"    - {tag}" for tag in item["tags"]),
        "spec:",
        f"  name: {quoted(str(item['name']))}",
        "  description: >-",
        *(f"    {line}" for line in description),
        f"  agent: {quoted(str(item['agent']))}",
        f"  cron: {quoted(str(item['cronExpression']))}",
        f"  modelTier: {quoted(str(item['modelTier']))}",
        "  agentMode: review",
        "  agentPrompt: |",
        *(f"    {line}" if line else "" for line in prompt_lines),
    ]
    return "\n".join(lines) + "\n"


def write_or_check(check: bool) -> int:
    task = load_task()
    target = ROOT / str(task["yaml"])
    expected = render_yaml()
    if check:
        if not target.is_file() or target.read_text(encoding="utf-8") != expected:
            print(f"Generated scheduled-task YAML drift: {target.name}", file=sys.stderr)
            return 1
        return 0
    target.write_text(expected, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("api", "write", "check", "install-plan", "verify-install"))
    parser.add_argument("--existing", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--expected", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "write":
            return write_or_check(False)
        if args.command == "check":
            return write_or_check(True)
        if args.command == "api":
            json.dump(api_payloads(), sys.stdout, indent=2)
            print()
            return 0
        if args.command == "install-plan":
            if args.existing is None or args.output_dir is None:
                parser.error("install-plan requires --existing and --output-dir")
            write_install_plan(args.existing, args.output_dir)
            return 0
        if args.existing is None or args.expected is None:
            parser.error("verify-install requires --existing and --expected")
        return verify_install(args.existing, args.expected)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
