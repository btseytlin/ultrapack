# Brevity principles for long-lived artifacts

Applies to anything that outlives the conversation: code, comments, docstrings, frontmatter descriptions, task files (`docs/tasks/<slug>.md`), READMEs, commit messages. Every skill that writes to such artifacts applies these rules to the section it owns. The goal is an audit trail, not a retelling.

## Principles

1. **Omit, don't fill.** A subsection with default content ("none", "n/a", "single phase, no deps", "no open questions") is deleted, not written. The absence of the header *is* the signal that nothing needed saying.

2. **Evidence only on surprise.** Passed checks are a one-line bullet. Attach evidence — command output, a grep that confirmed emptiness, a file:line reference — only to failures, deferrals, or genuinely surprising passes.

3. **Don't re-narrate.** The commit, the diff, and `git log` are authoritative. Task-file prose only adds context the artifacts can't express: why a choice was made, what was explicitly deferred, what would bite a future reader. Never summarize the diff in prose — a SHA and a short name is enough.

4. **One sentence, not a paragraph.** Outcomes, rationales, and deferrals fit in one sentence unless there's a concrete reason they can't. If you're writing a second sentence, check whether the first was padding.

5. **Soft caps, hard judgment.** No word limits. Lean toward ≤1 screen for a Small task's full task file; ≤3 screens for Medium. Over? Cut.

6. **No conversation bleed.** Don't stamp the current task, dispatch path, just-removed alternative, model name, or the user's last critique into long-lived artifacts. The artifact must stand alone after the chat is gone. Test: delete the conversation — does this text still make sense to a stranger six months from now?

   - Negative: `// do X (NOT Y)` — `Y` was the user's last critique, already removed from the code; the comment now refers to nothing.
   - Negative: agent description "…Dispatched per-phase from up:uexecute. Fresh context, never sees session history or later phases. Sonnet 4.6." — dispatch mechanics, session semantics, and model are all bleed; the description should say what the agent *does*.
   - Positive: `// integer overflow here caused the 2026-02 billing incident` — timeless reason, useful in six months.
   - Positive: agent description "Implement one phase of an approved plan — code, tests, commit." — stands alone, describes purpose.

## Checklist before saving

- Can any subsection be removed entirely because its content is "none" or the default?
- Does any bullet re-state what the diff or commit message already shows? Drop it.
- Any evidence citation on a check that just passed? Drop it.
- Any second sentence that adds no new information? Cut it.
- Any text that references this conversation — the current task, my last critique, the dispatch path, the model? Cut it.

## Exception — never abbreviate these

Failures, deviations from plan, deferrals, and known risks ALWAYS carry their evidence and their "why". Brevity means not padding the trivially-fine cases; it never means losing a finding.
