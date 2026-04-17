# Brevity principles for task-file output

Every skill that writes to `docs/tasks/<slug>.md` (`uplan`, `uverify`, `ureview`, `uexecute`) applies these rules to the section it owns. The goal is an audit trail, not a retelling.

## Principles

1. **Omit, don't fill.** A subsection with default content ("none", "n/a", "single phase, no deps", "no open questions") is deleted, not written. The absence of the header *is* the signal that nothing needed saying.

2. **Evidence only on surprise.** Passed checks are a one-line bullet. Attach evidence — command output, a grep that confirmed emptiness, a file:line reference — only to failures, deferrals, or genuinely surprising passes.

3. **Don't re-narrate.** The commit, the diff, and `git log` are authoritative. Task-file prose only adds context the artifacts can't express: why a choice was made, what was explicitly deferred, what would bite a future reader. Never summarize the diff in prose — a SHA and a short name is enough.

4. **One sentence, not a paragraph.** Outcomes, rationales, and deferrals fit in one sentence unless there's a concrete reason they can't. If you're writing a second sentence, check whether the first was padding.

5. **Soft caps, hard judgment.** No word limits. Lean toward ≤1 screen for a Small task's full task file; ≤3 screens for Medium. Over? Cut.

## Checklist before saving

- Can any subsection be removed entirely because its content is "none" or the default?
- Does any bullet re-state what the diff or commit message already shows? Drop it.
- Any evidence citation on a check that just passed? Drop it.
- Any second sentence that adds no new information? Cut it.

## Exception — never abbreviate these

Failures, deviations from plan, deferrals, and known risks ALWAYS carry their evidence and their "why". Brevity means not padding the trivially-fine cases; it never means losing a finding.
