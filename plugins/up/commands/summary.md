---
description: Produce a summary so another session can continue with zero context beyond CLAUDE.md, the codebase, and the summary itself. Asks whether to append to the current task file or create a new summary task file.
---

# /up:summary

Prepare a summary so another agent session can continue this work without needing the current conversation.

## Process

### 1. Gather concrete state first

- `git status` and `git diff` for uncommitted work
- Check for active remote sessions (tmux, running processes) if applicable
- Review the conversation for decisions made, approaches tried, and blockers hit
- Check `tmp/` for useful logs or intermediate files

### 2. Draft the summary

Write with the sections below. Omit any section only if genuinely not applicable.

- Goal: one or two sentences — the top-level objective, not the latest sub-task
- Problem: what's broken or missing, why it matters, concrete example if available. Explain well enough that the next agent could diagnose independently.
- Infrastructure / Environment: SSH commands, pod IPs, tmux sessions, required env vars and where they live, exports/source commands, tools/binaries needed. Omit for purely local work.
- Current state: what's been done — files modified (with paths), pipeline stages completed, data/artifacts produced, what is working and verified
- Active blocker: the specific problem preventing progress — what it is, what was tried, partial fixes applied (with file:line), diagnostic output. If none, say "no blockers".
- Key files: only files the next session will need to touch or reference
- What to do next: numbered, actionable steps in order. Include commands where possible. Most important section after Goal.
- Gotchas: non-obvious things that waste time — env quirks, sync commands, versioning traps, flaky behavior

### 3. Ask the user where to put it

<required>
Show the drafted summary, then ask:

1. Append to the current task file's `## Conclusion` as a `### Summary — YYYY-MM-DD` subsection (provide the detected `docs/tasks/<slug>.md` path)
2. Create a new file at `docs/tasks/summary-<new-slug>.md` (propose a slug based on the current work)

Pick the destination based on the user's answer. Do not write anywhere without confirmation.
</required>

If no active task file can be detected, option 1 is unavailable — only offer option 2.

## Rules

- Concrete: exact commands, exact paths, exact error messages. No "run the appropriate command."
- Terse: bullets over prose. No filler.
- Include only info that can't be derived from code or git history. Don't restate CLAUDE.md.
- Copy-pasteable commands over descriptions.
- If unsure about something (e.g. whether a remote process is still running), say so explicitly rather than assuming.
