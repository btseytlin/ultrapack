---
description: Reflect on the current dialogue, extract what's worth keeping, and route each learning to its right home — CLAUDE.md, memory, or project docs.
---

# /up:reflect

Capture learnings from the session that just happened so future sessions can replicate the outcome without re-discovery. This is a review of the dialogue, not of the code.

## Process

### 1. Scan the session for non-obvious content

Ask yourself:
- What was hard or surprising?
- What did the user correct me on?
- What patterns did we settle on after deliberation?
- What external systems, flags, or configs did we touch that aren't self-evident from the code?
- What decisions did we reach that the code doesn't explain?

Discard:
- Anything obvious from reading the current code
- One-off debugging details (the commit message holds them)
- Anything already captured in CLAUDE.md, existing docs, or memory

### 2. Route each learning

For each item worth keeping, decide where it belongs:

- **CLAUDE.md (project or global)** — project-wide or user-wide conventions, preferences, things to always or never do
- **Memory system** — references to external systems, user preferences, project context that applies across sessions
- **Project docs (`docs/`, README, inline comments)** — domain knowledge that belongs with the code
- **Task file's Conclusion** — deviations from plan, discoveries during execution, future work

When unclear, ask the user. Don't guess the destination.

### 3. Write concise, actionable entries

Each entry must state:
- **What** — the rule or fact, one line
- **Why** — the reason (only if non-obvious; skip if self-evident)
- **How to apply** — when this kicks in (only if non-obvious)

Style: terse, no filler, lists over paragraphs, exact commands and file paths over "the appropriate command".

### 4. Verify

Re-read each entry cold. Can a future fresh-context agent apply it without asking? If not, rewrite.

## Rules

- Don't document the obvious
- Don't duplicate across destinations — pick one home per learning
- Don't write aspirational content ("we should eventually...")
- Don't commit to CLAUDE.md without showing the user the proposed diff
- Memory edits can happen directly (per the auto-memory guidelines)

## Terminal state

Learnings routed to their homes. One-line summary to the user of what went where.
