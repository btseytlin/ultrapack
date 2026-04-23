# sa-ultrapack

Claude Code plugin for systems analysts. Fork of ultrapack, reoriented from code development to functional requirements documentation, endpoint validation, and migration coverage.

## What this is

A skill pack that helps a systems analyst:
- Map scenarios to real endpoints
- Write FR documents in the correct format
- Validate requirements against real curl responses
- Track gaps and open questions
- Confirm migration coverage (Mindbox → DreamCRM)

Core idea: **requirements are not complete until the real endpoint confirms them.** Like TDD for code, but for documentation — describe → validate → update → finalize.

## Repo layout

- `.claude-plugin/marketplace.json` — marketplace manifest
- `plugins/up/.claude-plugin/plugin.json` — plugin manifest (name: `up`)
- `plugins/up/skills/` — process skills
- `plugins/up/commands/` — orchestrator commands
- `plugins/up/agents/` — subagents (explorer, reviewer, researcher)
- `docs/tasks/*.md` — one task file per FR coverage task

## Skill index (`up:<name>`)

| Skill | Purpose |
|---|---|
| `udesign` | Scope analysis: map scenario → endpoints → gaps |
| `uplan` | Coverage planning: which FR documents, what order, what curls |
| `uexecute` | FR writing: write document per WRITING_GUIDE.md |
| `uverify` | Curl validation: real endpoint, real response, real verdict |
| `ureview` | FR review: format + sourcing + validation presence |
| `udocument` | Project docs: context.md updates, FR status tracking |
| `udebug` | Mismatch diagnosis: curl vs FR, OpenAPI vs code |
| `handsoff` | Hands-off mode contract |
| `git-worktrees` | Parallel doc work in worktrees |

## Command index (`/up:<name>`)

| Command | Purpose |
|---|---|
| `/up:make` | Full SA workflow: analyze → plan → document → validate → review |
| `/up:reflect` | Extract learnings from session into CLAUDE.md or memory |
| `/up:step-back` | Circuit breaker: stop, diagnose, propose new direction |
| `/up:try` | Quick positive + negative check |
| `/up:summary` | Summarize current session state |

## Agent index

| Agent | Model | Purpose |
|---|---|---|
| `explorer` | Haiku | Traces endpoint → routes.php → controller → service → OpenAPI |
| `reviewer` | Sonnet | Reviews FR document for format + sourcing + validation |
| `researcher` | Sonnet | External lookup: API docs, spec questions |

## SA workflow

```
/up:make <scenario or FR code>
   ↓
up:udesign  →  scope analysis, endpoint map, gaps as UK entries
   ↓
up:uplan    →  coverage plan: FR documents + curl targets
   ↓
up:uexecute →  write FR per WRITING_GUIDE.md (dispatches up:explorer)
   ↓
up:uverify  →  MANDATORY curl validation, record actual responses
   ↓
up:ureview  →  FR format + sourcing review (dispatches up:reviewer)
   ↓
Conclusion  →  context.md updated, FR ready for Confluence
```

## Key principle: no completion without curl

`up:uverify` is never skipped. If the endpoint is unreachable, the check is **blocked** (not passed). A blocked check requires explicit logging with:
- The curl command that was intended
- The reason it couldn't run
- The environment needed to unblock

Only after curls are run (or explicitly blocked with reason) can the task reach `done`.

## Global SA principles

Defined in `plugins/up/skills/_principles.md`. Summary:

- **SAPC1** — verify-driven documentation (curl is mandatory)
- **SAPC2** — every claim has a source (OpenAPI, code, DB, curl)
- **SAPC3** — gaps are first-class artifacts (open question stubs, not guesses)
- **SAPC4** — as-is and to-be are always distinct
- **SAPC5** — single source of truth (context.md, WRITING_GUIDE.md, DECOMPOSITION.md)
- **SAPC6** — scope discipline (check context.md section 4 before any FR)
- **SAPC7** — stubs over speculation
- **SAPC8** — format is not optional

## Key project files (read before any FR task)

- `docs/context.md` — project state, open questions, scope
- `docs/FR/WRITING_GUIDE.md` — FR format (mandatory)
- `docs/FR/DECOMPOSITION.md` — full scenario decomposition with stakeholder comments
- `OpenApi/CRM-EXTERNAL-INTEGRATIONS-openapi.json` — DreamCRM API spec
- `OpenApi/ACCOUNTING-EXTERNAL-INTEGRATIONS-openapi.json` — Accounting API spec
- `source_code/back_site/.../local/config/routes.php` — all backend routes
- `docs/DB_description.md` — DB schema (verify field names before writing)

## Install

Symlink `plugins/up/` into `~/.claude/plugins/up` (or use the plugin marketplace). Reload plugins with `/reload-plugins`.

## Versioning

Bump patch version in `plugins/up/.claude-plugin/plugin.json` when merging changes to main.
