---
name: reflect
description: Extract durable, non-obvious lessons from the current dialogue and route them to project guidance, memory, documentation, or the active task conclusion. Use when the user asks to reflect on a session or preserve learnings.
---

# Reflect

Use this as Codex's equivalent of `/up:reflect`.

1. Identify non-obvious user corrections, discovered conventions, external-system details, and decisions the code does not explain. Discard one-off debugging facts and anything already documented.
2. Route each remaining lesson to the right home: `CLAUDE.md` for durable repository guidance, memory for cross-session personal context, project docs for domain knowledge, or the task conclusion for task-specific discoveries.
3. Write concise actionable entries: what the rule is, why it matters when non-obvious, and when it applies. Do not duplicate a learning across destinations.
4. Show the user a proposed diff before committing changes to `CLAUDE.md`. Re-read every entry as a fresh agent would and tighten anything that still needs unstated context.
