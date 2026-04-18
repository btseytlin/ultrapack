---
description: Orchestrate the full ultrapack workflow — slug, task file, design, plan, execute, verify, review. Size-aware, resume-ready. Prefix args with `handsoff` for hands-off mode (fewer prompts, conservative defaults, decision log).
---

# /up:make

Drives a task through the full ultrapack workflow: one task file at `docs/tasks/<slug>.md`, evolving through Design → Plan → Conclusion. Each stage is a separate skill. You orchestrate; the skills do the work.

## Arguments

The user's description of the task follows the command. May be a one-liner ("fix the flaky login test") or a paragraph. Use it as the seed for the slug and the initial framing for `up:udesign`.

Hands-off activation: if the first whitespace-delimited token of the arguments is the literal string `handsoff`, enable hands-off mode. Strip that token before deriving the slug or framing for design. Any other spelling (`hands-off`, `handsOff`, `--handsoff`) is treated as part of the description — only the bare token `handsoff` activates. See `## Hands-off mode` below for behavior.

## Flow

### 1. Slug

Derive a kebab-case slug from the description, 3 words max (e.g. "flaky-login-test"), and proceed.

### 2. Resume check

Before creating a new task file, check if `docs/tasks/<slug>.md` already exists.

- Exists: read `**Status:**` from the header. Resume from the next stage:
  - `design` → continue design
  - `planning` → run `up:uplan`
  - `executing` → run `up:uexecute`
  - `reviewing` → run `up:ureview`
  - `done` → ask the user what they want to do (start a follow-up, re-open, view conclusion)
- Doesn't exist: proceed to step 3.
- Multiple in-flight tasks: if more than one `docs/tasks/*.md` has Status ≠ `done`, list them and ask which one the user means (or whether this is a new task).

### 3. Create task file

Create `docs/tasks/<slug>.md` from the template. Status = `design`. Branch = `main` (placeholder until step 5). No worktree. Mode = `hands-off` if the keyword was present, else `interactive`.

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

### Principles
<empty — PC1, PC2, … : softer guidance>

### Assumptions
<empty — AS1, AS2, … : unverified premises the design rests on; conclusion must report whether each held>

### Unknowns
<empty — UK1, UK2, … : open questions left to plan / execute; conclusion must report whether each resolved>

## Plan
<empty — filled by up:uplan>

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>

### Hands-off decisions
<empty — populated only when Mode is hands-off>

### Deferred (needs user input)
<empty — populated only when Mode is hands-off and a choice had no conservative default>
```

### 4. Size classification

Based on the task description, classify size:

- Trivial — one-line change, typo, rename. Skip Design and Plan. Go straight to Execute. Status file still created.
- Small — single file or single concept change. Skip Design. Plan runs.
- Medium / Large — full flow.

Interactive mode: confirm the classification with the user before skipping any stage. When unsure, ask.

Hands-off mode: do not confirm. Default to Medium (full flow) unless the scope is unambiguously Trivial (true one-liner in one file). Never auto-pick Small or auto-skip Design — Design is the one interactive stage preserved in hands-off. Append the choice to `## Conclusion → ### Hands-off decisions` as `- size: <classification> — <rationale>`.

### 5. Design stage (unless skipped)

Invoke `up:udesign`. It populates `## Design`, `### Invariants` (IV), `### Principles` (PC), `### Assumptions` (AS), `### Unknowns` (UK), and records `TDD: yes / no (reason)`. Status → `planning`.

### 6. Branch & worktree decision

After Design (or immediately for trivial/small tasks), decide:

- Complex / long-running / touches many files → suggest a dedicated branch + worktree. Use `up:git-worktrees`.
- Easy fix / small scope → suggest working on current branch (usually `main`).

Interactive mode: always confirm with the user.

Hands-off mode: default to the safest reversible option — always a dedicated branch + worktree via `up:git-worktrees`, never direct edits to `main`/`master`. Log the branch name and worktree path under `## Conclusion → ### Hands-off decisions`. The only exception: if `up:git-worktrees` itself fails (e.g. no gitignored worktree path available), log the failure under `### Deferred (needs user input)` and stop — do not silently fall back to working on `main`.

If a branch is created, update the task file's `**Branch:**` and `**Worktree:**` headers.

### 7. Plan stage (unless skipped)

Invoke `up:uplan`. It populates `## Plan`. Status → `executing`.

In hands-off, `up:uplan` auto-proceeds to `up:uexecute` without an approval prompt. It logs `- uplan: plan auto-approved (hands-off)` to `### Hands-off decisions`.

### 8. Execute stage

Invoke `up:uexecute`. Implements the plan, commits incrementally.

### 9. Verify loop

Invoke `up:uverify`. On failure: `up:uverify` describes how each failure *should* have worked, control returns to `up:uexecute`. Loop until verify passes.

### 10. Review stage

Status → `reviewing`. Invoke `up:ureview`. It dispatches `up:ureviewer`, processes findings, fills `## Conclusion`. Status → `done`.

Once the task is concluded as `done`, run the docs-refresh check (see below).

### 11. Finish

Hands-off mode — first: print the `## Conclusion → ### Hands-off decisions` list (and `### Deferred (needs user input)` if non-empty) to the user and ask verbatim: "Here's what I did to make it hands-off. Want to change anything?" Wait for the user's response before continuing.

Then (both modes) present options to the user:
- Merge / open PR (if on a branch)
- Clean up worktree
- Move on

Execute only after the user chooses.

## After task is done — docs refresh

Run this once, after Review concludes the task as `done` (not after every stage). Scan the project docs and update them if the work surfaced something they should reflect. Cheap, light-touch; not a full doc pass.

Files to scan:
- `CLAUDE.md` (project-wide agent guidance)
- `README.md`
- `docs/**/*.md` (project documentation, excluding the task file itself and archived tasks)

What to look for:
- New conventions, invariants, or principles that should be global → update `CLAUDE.md`
- New components, commands, or features the README should mention
- Stale content contradicted by the stage's work → delete or correct
- Pointers to the task file if future contributors would benefit

Rules:
- If nothing needs updating: say so in one line and move on. Do not invent edits.
- If updates are needed: make them directly, then summarize what changed in 1-3 lines (e.g. "README: fixed install instructions; CLAUDE.md: no change"). Do not prompt for approval first. Do not produce a detailed diff — the user will git-diff if they want.
- Follow `up:udocument`: lead with why, lists over tables, no aspirational content, kill stale content.
- Do not duplicate content across task file and project docs — pick one home per fact.

## Stop conditions

Stop and ask the user when:

- Size classification is genuinely unclear (interactive only; in hands-off, default to Medium)
- User has expressed a preference (branch, scope, TDD) that conflicts with the auto-inference
- Any stage's skill returns a blocker

## Rules

- Never skip Review (both modes)
- Never auto-merge or auto-push — the user chooses at step 11 (both modes)
- Never create a worktree without confirming in interactive mode
- Never edit `main` / `master` directly in hands-off (see `up:handsoff` safety principles)
- Keep the task file as the single source of truth — each stage reads it, each stage writes to it
- External spec / design docs (e.g. anything under `docs/specs/`) are read-only during execute. If a stage finds the spec is wrong, surface it to the user — don't mutate it silently
- Don't assume prior session memory — the next agent may be a fresh context reading only the task file
- In hands-off, never invent a default for an ambiguous argument — see `up:handsoff` no-default rule

## Hands-off mode

Activated by prefixing `/up:make` arguments with the literal token `handsoff`. The full contract — safety principles (worktree-first, reversible-first, no destructive ops, no push), decision log format, deferred log, no-default rule, end-of-task summary — lives in `up:handsoff`. Read that skill once when the task file's `**Mode:**` header is `hands-off`; the references in step 4, step 6, step 7, step 11 above are the stage-specific touches on top of it.

## Terminal state

Task file Status = `done`, Conclusion filled, user has chosen a finish action (merge, PR, cleanup, or defer). In hands-off, the user has also reviewed the `### Hands-off decisions` list.
