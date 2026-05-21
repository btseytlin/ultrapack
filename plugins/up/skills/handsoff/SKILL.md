---
name: handsoff
description: Contract for hands-off mode — the ultrapack workflow variant that minimizes user prompts after Design, takes the safest reversible path, and logs every auto-choice for one end-of-task review. Referenced by /up:make and the child skills (udesign, uplan, uexecute, uverify, ureview). Read when the task file's **Mode:** header is `hands-off`.
---

# Hands-off mode

The contract every ultrapack skill honors when the task file's `**Mode:**` header is `hands-off`. One home for the rules so child skills don't duplicate them.

## When this applies

The task file header names the mode:

```
**Mode:** hands-off
```

If absent or set to `interactive`, ignore this skill entirely — normal interactive flow.

## What hands-off is for

The user has said "run the full workflow and don't ask me each step." This is permission to proceed, not permission to guess. Hands-off **reduces prompts**; it does not **expand authority**. Two directives:

1. **Fewer questions after Design.** Don't gate progress on "should I fix this?" or "approve the plan?" — just do it.
2. **Safest reversible path, least assumptions.** When two routes both work, pick the one easier to undo. When a choice lacks an obvious conservative default, don't invent one — defer.

The user trades per-step approval for one end-of-task review against the decision log.

## Safety principles

<required>
In hands-off, every stage picks the **most reversible** path available. The user isn't there to catch a destructive move. Specifically:

- **Always work on a dedicated branch + worktree.** Never edit `main` / `master` directly in hands-off. If `up:git-worktrees` cannot provision one, log under `### Deferred (needs user input)` and stop — do not fall back to working on the main branch.
- **Prefer additive over subtractive edits.** Rename before deleting. Comment-out before removing. Add a new file before replacing the old one in place. The reviewer (`up:reviewer`) still catches unused cruft; better that than a deleted file the user wanted.
- **Never destructive git operations.** No `reset --hard`, no `branch -D`, no force-push, no `clean -f`, no overwriting of uncommitted work. If a clean state is needed, stash.
- **Never push to remote.** Pushing is always user-initiated, even in hands-off. The end-of-task step offers push/PR as an option; it does not execute it.
- **Never skip hooks or bypass signing** (`--no-verify`, `--no-gpg-sign`). If a hook fails, fix the underlying issue, not the hook-skip.
- **No mass deletes or rewrites.** If the plan calls for deleting many files, flag it and proceed one at a time with commits between. Keep the rollback surface.
- **External spec files are read-only.** Same rule as interactive.
</required>

Conservative ≠ inventive. When unsure whether an action is reversible, assume it isn't and defer.

## The decision log

Every auto-choice that would normally have prompted the user lands in the task file's Conclusion under:

```
### Hands-off decisions
- <stage>: <choice> — <rationale>
```

`<stage>` is the skill name (`make`, `udesign`, `uplan`, `uexecute`, `ureview`). Every entry is one line. The list is what the user reviews at end-of-task.

## The deferred log

When a choice has no conservative default — a required argument with no rigid fallback, a failing worktree provision, a smoke test that can't run, an ambiguous finding — do **not** guess. Append:

```
### Deferred (needs user input)
- <what was skipped> — <why> — <what the user needs to decide>
```

Then keep going on the rest, or stop and ask if the blocker is structural. The task can still finish with deferred items open; they're the agenda for the end-of-task prompt.

## No-default rule

If a value is required and neither the user nor the plan specified one:

- **Don't invent a "safe-looking" default.** `timeout=30` is not safe — it's invented. The user may have meant 5, or 300.
- **Don't pick a "common" value.** Commonness is not authorization.
- **Either:** the rigid path ("same as before", "as the user wrote it"), if one exists.
- **Or:** defer under `### Deferred (needs user input)`.

This rule is strictly stronger than the interactive-mode `uexecute` rule ("no silent fallbacks"). Hands-off keeps it loud.

## End-of-task summary

The final stage (`/up:make` step 11) presents the `### Hands-off decisions` list plus any `### Deferred (needs user input)` items to the user with the verbatim prompt:

> Here's what I did to make it hands-off. Want to change anything?

Only after the user responds does the workflow offer merge/PR/cleanup options. This is the single required interaction between Design and finish.

## Per-stage behavior (summary — see each SKILL.md for details)

- **make** — auto-classifies size (default Medium), auto-picks branch + worktree (default: new branch + worktree), logs the picks.
- **udesign** — runs as normal; relaxes "one question per message" to "ask only when genuinely blocking"; logs conservative defaults.
- **uplan** — skips the approval wait; logs `- uplan: plan auto-approved`.
- **uexecute** — behavior unchanged (the interactive rules already match hands-off's safety intent); stop-and-ask list now logs under Deferred.
- **uverify** — behavior unchanged; infeasible smoke tests log under Deferred.
- **ureview** — high-confidence actionable findings are announced-and-applied (no pause); low-confidence / ambiguous findings log under Deferred instead of being auto-fixed.

## Rules

- Reversibility over speed: a slower path that leaves rollback intact beats a faster path that doesn't.
- Log over guess: one line in the decision log always beats an inferred default.
- The task-file `**Mode:**` header is the single source of truth; no environment flags, no in-session memory.
- `### Hands-off decisions` must exist in every hands-off task's Conclusion and be surfaced at end-of-task.
- If the header is missing, behave as interactive. Do not assume hands-off from other signals.
