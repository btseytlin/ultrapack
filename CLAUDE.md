# ultrapack

Claude Code and Codex plugin for spec-driven, git-centered development. The repository root is one shared, Git-cloneable `up` plugin and a GitHub-native marketplace for both harnesses.

## Repo layout

- `.claude-plugin/{marketplace.json,plugin.json}` — Claude Code marketplace and plugin manifests
- `.agents/plugins/marketplace.json` — Codex marketplace manifest
- `.codex-plugin/plugin.json` — Codex plugin manifest; both manifests have the same version
- `skills/` — shared Claude Code + Codex skills; `up-*` skills are Codex equivalents of Claude slash commands
- `commands/`, `agents/`, `hooks/` — Claude Code-only components
- `scripts/validate_pack.py`, `.github/workflows/validate-pack.yml` — dependency-free packaging validation
- `docs/tasks/*.md` — task files (design + plan + conclusion per task)
- `README.md`, `CLAUDE.md` — repo docs

The repository root is the plugin. Codex loads `skills/`; Claude Code also loads `commands/` and `agents/`. `docs/`, README, and CLAUDE.md are repository-only, while manifests, marketplace metadata, and validation scripts support distribution.

## Naming

Internal plugin name: `up`. Claude Code slash/skill invocations use the `up:` prefix: `/up:make`, `up:udesign`, `up:reviewer`. Codex command skills use the same names as Claude commands, without Claude's namespace: `$make`, `$try`. Process skills are `u`-prefixed (`udesign`, `uplan`, `uexecute`, `uverify`, `ureview`, `udebug`, `udocument`) to dodge collisions.

## Design principles

- **Minimal** — only skills we actually use; no speculative additions
- **Doc-only** — no application runtime code or unit-test suite; packaging gets a dependency-free static validator plus install-and-invoke smoke tests

## Versioning

Plugin version lives in `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. Keep them identical and always bump the patch digit (`x.y.Z`) when merging, finalizing, or otherwise landing changes on `main`. Default to patch; ask before bumping minor (`x.Y.z`) or major (`X.y.z`).
