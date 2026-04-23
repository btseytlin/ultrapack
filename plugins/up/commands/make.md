---
description: Orchestrate the full SA ultrapack workflow — slug, task file, scope analysis, coverage plan, FR writing, curl validation, review. Size-aware, resume-ready. Prefix args with `handsoff` for fewer prompts.
---

# /up:make

Drives an FR documentation task through the full SA workflow: one task file at `docs/tasks/<slug>.md`, evolving through Analyze → Plan → Document → Validate → Conclude. Each stage is a separate skill. You orchestrate; the skills do the work.

## Arguments

The user's description of the task follows the command — a scenario code, a feature name, or a full sentence. Use it as the seed for the slug and the initial framing for `up:udesign`.

Hands-off activation: if the first whitespace-delimited token is the literal string `handsoff`, enable hands-off mode. Strip that token before deriving the slug.

## Flow

### 1. Slug

Derive a kebab-case slug from the description, 3 words max (e.g. `p-01-bonus-balance`, `a-01-auth-login`). Confirm with user.

### 2. Resume check

Check if `docs/tasks/<slug>.md` already exists.

- Exists: read `**Status:**`. Resume from next stage:
  - `design` → continue analysis
  - `planning` → run `up:uplan`
  - `executing` → run `up:uexecute`
  - `reviewing` → run `up:ureview`
  - `done` → ask user what they want (follow-up FR, re-open, view conclusion)
- Multiple in-flight tasks: list all with Status ≠ `done`, ask which to work on.
- Doesn't exist: proceed to step 3.

### 3. Create task file

Create `docs/tasks/<slug>.md`. Status = `design`. No git branch by default (doc-only tasks rarely need one). Mode = `hands-off` if keyword was present.

Template:

```markdown
# <Task Title>

**Status:** design
**Branch:** main
**Worktree:** none
**Mode:** <interactive|hands-off>

## Design
<empty — filled by up:udesign>

### Invariants
<empty — IV1, IV2, … : hard constraints that must hold>

### Assumptions
<empty — AS1, AS2, … : unverified premises; conclusion must report whether each held>

### Unknowns
<empty — UK1, UK2, … : gaps and open questions; conclusion must report outcome>

## Plan
<empty — filled by up:uplan>

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>

### Hands-off decisions
<empty — populated only when Mode is hands-off>

### Deferred (needs user input)
<empty — populated when a choice has no safe conservative default>
```

### 4. Size classification

- **Trivial** — single well-known endpoint, all fields confirmed, no gaps. Skip Analyze and Plan. Go straight to Document. Task file still created.
- **Small** — single endpoint with minor unknowns. Skip Analyze. Plan runs.
- **Medium / Large** — multiple endpoints, migration scenario, or gaps present. Full flow.

Interactive: confirm classification before skipping. When unsure, ask.
Hands-off: default to Medium (full flow). Only auto-pick Trivial when the endpoint is a single fully-known route with no open questions.

### 5. Analyze stage — `up:udesign`

Populates `## Design`, `### Invariants` (IV), `### Assumptions` (AS), `### Unknowns` (UK). Outputs endpoint map and gap list. Status → `planning`.

### 6. Branch decision (optional)

For doc-heavy tasks with many FR files (5+): suggest a dedicated branch. For single-FR tasks: working on `main` is fine. Always confirm in interactive mode.

Hands-off: default to `main` for doc-only tasks. Only create a branch if the task explicitly involves many files.

### 7. Plan stage — `up:uplan`

Populates `## Plan` with coverage plan: FR document codes, endpoints per doc, planned curl commands per doc. Status → `executing`.

### 8. Document stage — `up:uexecute`

Writes FR documents phase by phase. Dispatches `up:explorer` per endpoint as needed. Commits each FR document after writing.

### 9. Validate loop — `up:uverify`

Runs real curl against real endpoints. Records actual responses. Updates FR on mismatch. Writes `## Verify`. On failure or mismatch: loop back to `up:uexecute` with correction notes. On partial-block: continue to review with blocked items listed.

**This step is never skipped.** If infra is genuinely unavailable, blocked items are logged explicitly — they do not become passes.

### 10. Review stage — `up:ureview`

Status → `reviewing`. Dispatches `up:reviewer`. Processes findings. Fills `## Conclusion`. Updates `context.md`. Status → `done`.

### 11. Finish

Hands-off mode: print `### Hands-off decisions` and `### Deferred` to user, ask: "Here's what I did to make it hands-off. Want to change anything?" Wait for response before continuing.

Both modes — present options:
- Push FR document to Confluence (user executes manually — provide exact file path)
- Start next FR in the coverage plan (if plan has multiple phases)
- Archive task, move on

Never auto-push to Confluence. User decides.

## After task is done — docs refresh

Run once after Review concludes the task as `done`. Scan:
- `context.md` section 5 — FR status table updated?
- `context.md` section 7 — any resolved open questions to remove?
- `docs/FR/DECOMPOSITION.md` — any scenario now fully covered?

If nothing needs updating: say so in one line. If updates needed: make them directly, summarize in 1-2 lines.

## Stop conditions

Stop and ask when:
- Scenario is out of scope per `context.md` section 4 (don't analyze, don't document)
- UK item has no safe conservative default in hands-off mode
- Endpoint not found in `routes.php` and user needs to decide how to proceed

## Rules

- Never skip validate (`up:uverify`) — not for any reason
- Never claim FR is complete without curl results (pass or explicit block)
- Never document out-of-scope scenarios
- Never auto-push to Confluence
- Keep task file as single source of truth — each stage reads and writes it
- External specs (`OpenApi/*.json`, WRITING_GUIDE.md) are read-only — if wrong, surface to user
- Don't assume prior session memory — fresh context agent reads only the task file

## Hands-off mode

Full contract in `up:handsoff`. Stage-specific: validate runs unchanged; blocked curls go to `### Deferred (needs user input)` with exact environment needed; never fabricate pass on blocked.

## Terminal state

Task file Status = `done`. Conclusion filled. `context.md` updated. User has chosen a finish action.
