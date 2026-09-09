# ultrapack

Claude Code, Codex, and Pi package for spec-driven, git-centered development. The repository root is one shared, Git-cloneable `up` plugin. All three harnesses use the same `main` branch.

## Repo layout

- `.claude-plugin/{marketplace.json,plugin.json}` — Claude Code marketplace and plugin manifests
- `.agents/plugins/marketplace.json` — Codex marketplace manifest
- `.codex-plugin/plugin.json` — Codex plugin manifest; both manifests have the same version
- `skills/` — shared Claude Code, Codex, and Pi skills; command-named skills adapt Claude slash commands for Codex and Pi
- `commands/`, `agents/`, `hooks/` — Claude Code-only components
- `scripts/validate_pack.py`, `.github/workflows/validate-pack.yml` — dependency-free packaging validation
- `docs/tasks/*.md` — task files (design + plan + conclusion per task)
- `README.md`, `CLAUDE.md` — repo docs

The repository root is the plugin. Codex loads `skills/`. Claude Code also loads `commands/` and `agents/`. Pi loads only `skills/` through `package.json` and exposes workflows through native `/skill:<name>` commands. `docs/`, README, and CLAUDE.md are repository-only, while manifests, marketplace metadata, and validation scripts support distribution.

## Naming

Internal plugin name: `up`. Claude Code slash and skill invocations use the `up:` prefix: `/up:make`, `up:udesign`, `up:reviewer`. Codex command skills use `$make` and `$try`. Pi uses `/skill:make` and `/skill:qplan`. Process skills are `u`-prefixed (`udesign`, `uplan`, `uexecute`, `uverify`, `ureview`, `udebug`, `udocument`) to dodge collisions.

## Design principles

- **Minimal** — only skills we actually use; no speculative additions
- **Doc-only** — no application runtime code or unit-test suite; packaging gets a dependency-free static validator plus install-and-invoke smoke tests

## Versioning

Package version lives in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `package.json`. Keep them identical and always bump the patch digit (`x.y.Z`) when merging, finalizing, or otherwise landing changes on `main`. Default to patch; ask before bumping minor (`x.Y.z`) or major (`X.y.z`).
