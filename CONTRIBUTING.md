# Contributing

## Add a plugin

1. Create a self-contained package in `plugins/<plugin-name>/` with its own `plugin.json`, `skills/`, and optional `templates/` directory.
2. Give `plugin.json` a unique lowercase kebab-case `name`, an accurate description, and an explicit production skill declaration such as `"skills": ["skills/"]`.
3. Add a package README covering capabilities, installation, prerequisites, and any connector requirements.
4. Register the package in [`.github/plugin/marketplace.json`](.github/plugin/marketplace.json), then add it to the root [Included plugin](README.md#included-plugin) catalog.
5. Keep package skills and templates isolated; do not mix an additional package's files into `plugins/azure-carbon-sre/`.
6. Run `python3 scripts/validate_plugin.py` before opening a pull request.

## Add a skill

1. Create `plugins/azure-carbon-sre/skills/<skill-name>/SKILL.md`, using lowercase kebab-case for `<skill-name>`.
2. Add YAML frontmatter with a `name` matching the directory and a specific `description` that tells the agent when to load the skill.
3. Write an evidence-driven procedure. Prefer read-only discovery first; require explicit confirmation, impact assessment, and rollback guidance before mutating actions.
4. Keep service-specific references, queries, and supporting material beside the skill in its directory.
5. Run `python3 scripts/validate_plugin.py` before opening a pull request.

Use [plugins/azure-carbon-sre/templates/skill/SKILL.md](plugins/azure-carbon-sre/templates/skill/SKILL.md) as a starting point. Files under `plugins/azure-carbon-sre/templates/` are not installed as production skills.

## Quality requirements

- Do not commit credentials, access tokens, connection strings, customer data, or unredacted incident output.
- State data sources, scoping keys, expected signals, and limitations for operational procedures.
- Treat prior incident findings as hypotheses; validate them with current evidence.
- Keep the marketplace manifest, plugin manifest, and README accurate when skills or prerequisites change.
- Use pull requests; do not push directly to `main`.
