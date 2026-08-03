---
name: summary
description: Produce a compact, zero-context handoff for the current Codex work and, after user confirmation, save it to the active task conclusion or a new task summary file. Use when the user asks to preserve progress for a later session.
---

# Handoff summary

Use this as Codex's equivalent of `/up:summary`. Work from the current conversation, task file, git state, and repository; do not assume a Claude JSONL transcript exists.

1. Find the most recently modified in-flight file in `docs/tasks/*.md`, if one exists.
2. Draft a concise handoff with: Goal, Problem, Current state, Active blocker, Key files, What to do next, and Gotchas. Include only facts not obvious from the code or git history.
3. Show the draft verbatim and ask the user whether to append it under `## Conclusion` in the active task file or create `docs/tasks/summary-<slug>.md`. If there is no active task, offer only the new-file destination.
4. Write only after the user chooses. Keep paths, commands, evidence, and unresolved decisions concrete.
