---
name: summary
description: Produce a compact, zero-context handoff for the current Codex or Pi work and save it to the requested destination, active task conclusion, or a new task summary file. Use when the user asks to preserve progress for a later session.
---

# Handoff summary

Use this as the Codex and Pi equivalent of `/up:summary`. Work from the current conversation, task file, git state, and repository; do not assume a Claude JSONL transcript exists.

1. Find the most recently modified in-flight file in `docs/tasks/*.md`, if one exists.
2. Draft a concise handoff with: Goal, Problem, Current state, Active blocker, Key files, What to do next, and Gotchas. Include only facts not obvious from the code or git history.
3. Use the requested destination, otherwise append under `## Conclusion` in the active task file. If there is no active task, create `docs/tasks/summary-<slug>.md`. Ask only when the destination is ambiguous.
4. Save the handoff and report its path. Keep paths, commands, evidence, and unresolved decisions concrete.
