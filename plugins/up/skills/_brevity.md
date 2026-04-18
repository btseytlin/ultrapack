# Brevity principles for long-lived artifacts

Applies to anything that outlives the conversation: code, comments, docstrings, frontmatter descriptions, task files (`docs/tasks/<slug>.md`), READMEs, commit messages. Every skill that writes to such artifacts applies these rules to the section it owns. The goal is an audit trail, not a retelling.

## Principles

1. **Omit, don't fill.** A subsection with default content ("none", "n/a", "single phase, no deps", "no open questions") is deleted, not written. The absence of the header *is* the signal that nothing needed saying.

2. **Evidence only on surprise.** Passed checks are a one-line bullet. Attach evidence — command output, a grep that confirmed emptiness, a file:line reference — only to failures, deferrals, or genuinely surprising passes.

3. **Don't re-narrate.** The commit, the diff, and `git log` are authoritative. Task-file prose only adds context the artifacts can't express: why a choice was made, what was explicitly deferred, what would bite a future reader. Never summarize the diff in prose — a SHA and a short name is enough.

4. **One sentence, not a paragraph.** Outcomes, rationales, and deferrals fit in one sentence unless there's a concrete reason they can't. If you're writing a second sentence, check whether the first was padding.

5. **Soft caps, hard judgment.** No word limits. Lean toward ≤1 screen for a Small task's full task file; ≤3 screens for Medium. Over? Cut.

6. **No orphan text (a.k.a. conversation bleed).** Cut anything that doesn't help the reader understand the artifact now. Usual cause: scaffolding Claude used while writing — framing, rejected alternatives, references to the task or the user's last critique. Scaffolding stays in the chat. Conversation bleed is the visible symptom; orphaning is the rule. Test: does the line earn its place by informing?

   - Negative: `// do X (NOT Y)` — `Y` was the user's last critique, already removed from the code; the comment now refers to nothing.
   - Negative: agent description "…Fresh context, never sees session history or later phases. Sonnet 4.6." — session semantics and an inlined model string are bleed; the description should say what the agent *does*.
   - Not bleed: agent description "…Dispatched per-phase from `up:uexecute`." — naming the dispatching skill is wiring, not bleed. Claude Code reads the description to decide when to dispatch the agent; the referent is another long-lived file in the same repo, renamed atomically if it moves. Test: if the referent is a file a stranger can `grep` for, it's wiring; if the referent is a dialogue, a critique, or a transient decision, it's bleed.
   - Negative: task file narrating the dialogue to a reader:

     <bad>
     (Both resolved in design dialogue; kept here as record.)
     - UK1 — Pre-seed `### Assumptions` and `### Unknowns` in the `/up:make` template. Resolved: yes.
     - UK2 — Conclusion gets dedicated `### Assumptions check` and `### Unknowns outcome` subsections. Resolved: yes, dedicated.
     </bad>

     <good>
     - UK1 — Pre-seed `### Assumptions` and `### Unknowns` in the `/up:make` template. Resolved: yes.
     - UK2 — Conclusion gets dedicated `### Assumptions check` and `### Unknowns outcome` subsections. Resolved: yes, dedicated.
     </good>

     Why it's bleed: the parenthetical addresses a reader ("kept here as record") and references "the design dialogue" — a conversation that, from the file's point of view, never happened. The file is the record; it doesn't need to explain why it's the record. A stranger reading six months later sees the two resolved items and understands them on their own; the parenthetical only makes sense if you were in the chat where they were being debated.
   - Positive: `// integer overflow here caused the 2026-02 billing incident` — timeless reason, useful in six months.
   - Positive: agent description "Implement one phase of an approved plan — code, tests, commit." — stands alone, describes purpose.

## Checklist before saving

- Can any subsection be removed entirely because its content is "none" or the default?
- Does any bullet re-state what the diff or commit message already shows? Drop it.
- Any evidence citation on a check that just passed? Drop it.
- Any second sentence that adds no new information? Cut it.
- Any text that references this conversation — the current task, my last critique, session semantics, an inlined model string? Cut it. (Exception: naming another long-lived skill/command/agent file — e.g. "Dispatched from `up:ureview`" — is wiring, not bleed. Keep.)

## Exception — never abbreviate these

Failures, deviations from plan, deferrals, and known risks ALWAYS carry their evidence and their "why". Brevity means not padding the trivially-fine cases; it never means losing a finding.
