#!/usr/bin/env python3
"""Validate the portable Carbon SRE plugin structure with PyYAML."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


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


def validate_manifest() -> None:
    manifest_path = ROOT / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("plugin.json is required at repository root")
    except json.JSONDecodeError as exc:
        fail(f"plugin.json is not valid JSON: {exc}")

    for key in ("name", "version", "description"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            fail(f"plugin.json requires a non-empty string '{key}'")

    if not NAME_PATTERN.fullmatch(manifest["name"]):
        fail("plugin.json name must be lowercase kebab-case")
    if not SEMVER_PATTERN.fullmatch(manifest["version"]):
        fail("plugin.json version must be semantic versioning")


def validate_skills() -> None:
    skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skill_paths:
        fail("at least one production skills/<name>/SKILL.md file is required")

    for path in skill_paths:
        metadata = parse_frontmatter(path)
        expected_name = path.parent.name
        if metadata.get("name") != expected_name:
            fail(
                f"{path.relative_to(ROOT)} frontmatter name must match directory "
                f"'{expected_name}'"
            )
        if not metadata.get("description"):
            fail(f"{path.relative_to(ROOT)} requires a non-empty description")
        if not NAME_PATTERN.fullmatch(metadata["name"]):
            fail(f"{path.relative_to(ROOT)} name must be lowercase kebab-case")


def main() -> None:
    validate_manifest()
    validate_skills()
    print("Plugin validation passed.")


if __name__ == "__main__":
    main()
