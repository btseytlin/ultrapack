---
name: make
description: "Orchestrate the full Ultrapack workflow in Codex: create or resume a task file, design, plan, execute, verify, review, and validate the observable goal. Use when the user asks to build, fix, or deliver a non-trivial change with the complete workflow."
---

# Ultrapack workflow

Use this as Codex's equivalent of Claude Code's `/up:make`. Treat the user's remaining message as the task description. A `handsoff` first token enables hands-off mode and is otherwise removed before making the slug.

1. Derive a kebab-case slug of at most three words. If `docs/tasks/<slug>.md` exists, read its status and resume at the next incomplete stage. If several tasks are in flight, ask which one to resume.
2. For a new task, create `docs/tasks/<slug>.md` from this template. Set Status to `design`, Branch to `main`, Worktree to `none`, Mode from the argument, and make Goal a draft observable outcome from the request.

```markdown
# <Task Title>

**Status:** design
**Branch:** main
**Worktree:** none
**Goal:** <observable end state>
**Mode:** <interactive|hands-off>

## Design
### Invariants
### Principles
### Assumptions
### Unknowns
## Plan
## Verify
## Code smells
## Conclusion
### Hands-off decisions
### Deferred (needs user input)
```
3. Classify the task. In interactive mode, confirm before skipping Design or Plan. In hands-off mode, default to Medium unless the task is unmistakably a one-line change.
4. Run `udesign` unless skipped, then set Status to `planning`. Decide on a branch/worktree: ask in interactive mode; in hands-off mode use `git-worktrees` and stop rather than edit the main branch if it cannot provision isolation.
5. Run `uplan` unless skipped, then set Status to `executing`. In hands-off mode, record that the plan was auto-approved.
6. Run `uexecute`, then `uverify`. Send demonstrated failures back to execution until the verification attacks pass. Set Status to `reviewing` and run `ureview`.
7. Set Status to `validating`. Mark `done` only when the task file's Goal has direct end-to-end evidence or the user confirms an outcome that Codex cannot observe. Do not equate a clean diff, passing tests, or review with a confirmed Goal.
8. Once done, scan `CLAUDE.md`, `README.md`, and non-task project documentation for material updates. Present branch merge/PR, worktree cleanup, or defer options; never push or merge without the user's choice.

Use `handsoff` for the shared safety contract. Record every automatic decision in `### Hands-off decisions`; never invent a value without a conservative, explicit basis. Ask the user only when there is no safe default or a blocker prevents the next stage.

## Harness adaptation

Use the existing skills by name (`udesign`, `uplan`, `uexecute`, `uverify`, `ureview`, and `git-worktrees`). Codex has no Claude slash-command syntax, so tell users to invoke this skill as `$make` or say “use make.”
