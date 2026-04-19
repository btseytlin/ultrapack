# ultrapack

Claude Code plugin for spec-driven, git-centered development. Distributed as a GitHub-native marketplace: the repo root is a marketplace (`.claude-plugin/marketplace.json`) that contains one plugin, `up`, under `plugins/up/`.

## Repo layout

- `.claude-plugin/marketplace.json` — marketplace manifest (lists `up`)
- `plugins/up/.claude-plugin/plugin.json` — plugin manifest
- `plugins/up/{skills,commands,agents,hooks}/` — plugin contents
- `docs/tasks/*.md` — task files (design + plan + conclusion per task)
- `README.md`, `CLAUDE.md` — repo docs

Everything under `plugins/up/` loads into Claude Code. Everything outside (`docs/`, README, CLAUDE.md) is repo-only.

## Naming

Internal plugin name: `up`. Slash/skill invocations use the `up:` prefix: `/up:make`, `up:udesign`, `up:reviewer`. Process skills are `u`-prefixed (`udesign`, `uplan`, `uexecute`, `uverify`, `ureview`, `udebug`, `udocument`) to dodge collisions with Claude Code built-ins.

## Design principles

- **Minimal** — only skills we actually use; no speculative additions
- **Doc-only** — no runtime code, no unit tests; verification is install-and-invoke

## Versioning

Plugin version lives in `plugins/up/.claude-plugin/plugin.json`. Default to bumping the patch digit (`x.y.Z`). Ask before bumping minor (`x.Y.z`) or major (`X.y.z`).
