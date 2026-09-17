# Contributing

## Add a skill

1. Create `plugins/carbon-sre/skills/<skill-name>/SKILL.md`, using lowercase kebab-case for `<skill-name>`.
2. Add YAML frontmatter with a `name` matching the directory and a specific `description` that tells the agent when to load the skill.
3. Write an evidence-driven procedure. Prefer read-only discovery first; require explicit confirmation, impact assessment, and rollback guidance before mutating actions.
4. Keep service-specific references, queries, and supporting material beside the skill in its directory.
5. Run `python scripts/validate_plugin.py` before opening a pull request.

Use [plugins/carbon-sre/templates/skill/SKILL.md](plugins/carbon-sre/templates/skill/SKILL.md) as a starting point. Files under `plugins/carbon-sre/templates/` are not installed as production skills.

## Quality requirements

- Do not commit credentials, access tokens, connection strings, customer data, or unredacted incident output.
- State data sources, scoping keys, expected signals, and limitations for operational procedures.
- Treat prior incident findings as hypotheses; validate them with current evidence.
- Keep the marketplace manifest, plugin manifest, and README accurate when skills or prerequisites change.
- Use pull requests; do not push directly to `main`.
