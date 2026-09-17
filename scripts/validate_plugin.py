#!/usr/bin/env python3
"""Validate the Azure Carbon SRE marketplace and installable plugin package with PyYAML."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "azure-carbon-sre"
PLUGIN_ROOT = ROOT / "plugins" / PLUGIN_NAME
MARKETPLACE_PATH = ROOT / ".github" / "plugin" / "marketplace.json"
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


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

    for path in skill_paths:
        metadata = parse_frontmatter(path)
        expected_name = path.parent.name
        if metadata.get("name") != expected_name:
            fail(
                f"{path.relative_to(ROOT)} frontmatter name must match directory "
                f"'{expected_name}'"
            )
        if not NAME_PATTERN.fullmatch(metadata["name"]):
            fail(f"{path.relative_to(ROOT)} name must be lowercase kebab-case")


def main() -> None:
    validate_marketplace()
    validate_manifest()
    validate_skills()
    print("Marketplace and plugin validation passed.")


if __name__ == "__main__":
    main()
