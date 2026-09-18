#!/usr/bin/env python3
"""Validate the Azure Carbon SRE marketplace and installable plugin package with PyYAML."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "azure-carbon-sre"
PLUGIN_ROOT = ROOT / "plugins" / PLUGIN_NAME
MARKETPLACE_PATH = ROOT / ".github" / "plugin" / "marketplace.json"
CORE_PRESENTATION_SKILL = "carbon-response-presentation"
CORE_PRESENTATION_LOAD_DIRECTIVE = (
    "Load `carbon-response-presentation` and follow its current SKILL.md before "
    "writing any user-facing output."
)
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
PRESENTATION_CONTRACT = (
    "Every response must use sentence-cased headings and human-facing labels. "
    "Do not expose raw field names, camelCase keys, or schema-shaped labels to the user."
)
PRESENTATION_SECTION_PATTERN = re.compile(
    r"^## User-facing presentation\s*$\n(?P<section>.*?)(?=^#{1,2}(?:\s|$)|\Z)",
    re.MULTILINE | re.DOTALL,
)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"{label} is required at {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def parse_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        fail(f"{path.relative_to(ROOT)} must start with YAML frontmatter")

    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"{path.relative_to(ROOT)} has unclosed YAML frontmatter")

    try:
        metadata = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        fail(f"{path.relative_to(ROOT)} has invalid YAML frontmatter: {exc}")

    if not isinstance(metadata, dict):
        fail(f"{path.relative_to(ROOT)} frontmatter must be a YAML mapping")
    for key in ("name", "description"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            fail(f"{path.relative_to(ROOT)} requires a non-empty string '{key}'")
    return metadata


def validate_marketplace() -> None:
    marketplace = load_json(MARKETPLACE_PATH, "marketplace.json")
    if marketplace.get("name") != "azure-carbon-sre-plugins":
        fail("marketplace name must be azure-carbon-sre-plugins")

    owner = marketplace.get("owner")
    metadata = marketplace.get("metadata")
    plugins = marketplace.get("plugins")
    if not isinstance(owner, dict) or not isinstance(owner.get("name"), str):
        fail("marketplace owner.name must be a non-empty string")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("description"), str):
        fail("marketplace metadata.description must be a non-empty string")
    if not isinstance(metadata.get("version"), str) or not SEMVER_PATTERN.fullmatch(metadata["version"]):
        fail("marketplace metadata.version must use semantic versioning")
    if not isinstance(plugins, list):
        fail("marketplace plugins must be an array")

    expected_source = f"./plugins/{PLUGIN_NAME}"
    matched = [
        plugin
        for plugin in plugins
        if isinstance(plugin, dict)
        and plugin.get("name") == PLUGIN_NAME
        and plugin.get("source") == expected_source
    ]
    if len(matched) != 1:
        fail(f"marketplace must contain one {PLUGIN_NAME} plugin at {expected_source}")


def validate_manifest() -> None:
    manifest_path = PLUGIN_ROOT / "plugin.json"
    manifest = load_json(manifest_path, "plugin.json")

    for key in ("name", "version", "description", "license"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            fail(f"{manifest_path.relative_to(ROOT)} requires a non-empty string '{key}'")

    if manifest["name"] != PLUGIN_NAME or not NAME_PATTERN.fullmatch(manifest["name"]):
        fail(f"{manifest_path.relative_to(ROOT)} name must be {PLUGIN_NAME}")
    if not SEMVER_PATTERN.fullmatch(manifest["version"]):
        fail(f"{manifest_path.relative_to(ROOT)} version must use semantic versioning")
    if manifest.get("skills") != ["skills/"]:
        fail(f"{manifest_path.relative_to(ROOT)} must declare skills as [\"skills/\"]")


def validate_skills() -> None:
    skill_paths = sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md"))
    if not skill_paths:
        fail("at least one plugins/azure-carbon-sre/skills/<name>/SKILL.md file is required")

    skill_names = set()
    for path in skill_paths:
        metadata = parse_frontmatter(path)
        expected_name = path.parent.name
        skill_names.add(expected_name)
        if metadata.get("name") != expected_name:
            fail(
                f"{path.relative_to(ROOT)} frontmatter name must match directory "
                f"'{expected_name}'"
            )
        if not NAME_PATTERN.fullmatch(metadata["name"]):
            fail(f"{path.relative_to(ROOT)} name must be lowercase kebab-case")

        content = path.read_text(encoding="utf-8")
        if expected_name == CORE_PRESENTATION_SKILL:
            presentation_sections = list(PRESENTATION_SECTION_PATTERN.finditer(content))
            if len(presentation_sections) != 1 or PRESENTATION_CONTRACT not in presentation_sections[0].group("section"):
                fail(
                    f"{path.relative_to(ROOT)} must include exactly one user-facing "
                    "presentation section containing the shared presentation contract"
                )
        elif CORE_PRESENTATION_LOAD_DIRECTIVE not in content:
            fail(
                f"{path.relative_to(ROOT)} must load {CORE_PRESENTATION_SKILL} "
                "before writing user-facing output"
            )

    if CORE_PRESENTATION_SKILL not in skill_names:
        fail(f"Missing required shared skill: {CORE_PRESENTATION_SKILL}")


def validate_scheduled_task_assets() -> None:
    task_root = PLUGIN_ROOT / "scheduled-tasks"
    required = (
        PLUGIN_ROOT / "install-api.sh",
        task_root / "task-manifest.json",
        task_root / "render_tasks.py",
        task_root / "prompts" / "carbon-static-snapshot.txt",
        task_root / "carbon-static-snapshot-weekly.yaml",
    )
    for path in required:
        if not path.is_file():
            fail(f"Required scheduled-task asset is missing: {path.relative_to(ROOT)}")

    result = subprocess.run(
        [sys.executable, str(task_root / "render_tasks.py"), "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        fail(
            "Scheduled-task validation failed: "
            + (result.stderr.strip() or result.stdout.strip() or "unknown error")
        )


def main() -> None:
    validate_marketplace()
    validate_manifest()
    validate_skills()
    validate_scheduled_task_assets()
    print("Marketplace and plugin validation passed.")


if __name__ == "__main__":
    main()
