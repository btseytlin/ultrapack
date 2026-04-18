---
description: Produce a summary so another session can continue with zero context beyond CLAUDE.md, the codebase, and the summary itself. Asks whether to append to the current task file or create a new summary task file.
---

# /up:summary

Prepare a handoff summary so another agent session can continue this work without the current conversation. Drafting is delegated to the `up:summarizer` subagent (pinned to Sonnet) so the expensive main-session model doesn't write the long structured prose. The subagent reads the live session JSONL directly — that's how it sees what happened.

## Process

### 1. Locate the current session JSONL

The live transcript is on disk. Find it by encoding the cwd and picking the newest `.jsonl` across both possible projects dirs (`~/.claude/projects/` and `~/.claude-work/projects/` — some users run a work instance):

```bash
CWD_ENC="$(pwd | sed 's|^/|-|; s|/|-|g')"
ls -t ~/.claude/projects/"$CWD_ENC"/*.jsonl ~/.claude-work/projects/"$CWD_ENC"/*.jsonl 2>/dev/null | head -1
```

Store the absolute path. If nothing returns, stop and tell the user — the command can't run without it.

### 2. Detect the active task file

```bash
ls -t docs/tasks/*.md 2>/dev/null | head
```

The active task file is the most-recently-modified entry whose `**Status:**` header is not `done`. If none qualify, pass `null`.

### 3. Dispatch the `up:summarizer` subagent

<required>
Drafting runs in the subagent, not in the main session. Dispatching is not optional — drafting in the main session puts long structured output on the expensive model this command exists to avoid.
</required>

Dispatch via the Task tool with `subagent_type: up:summarizer` and a prompt containing:
- Working directory (absolute).
- Session JSONL path (absolute) from step 1.
- Active task file path, or `null`.

The subagent reads the JSONL itself to reconstruct session context. Do not paste the transcript into the prompt.

### 4. Receive the draft

The subagent returns prose beginning with `Draft summary below — main session decides destination.` followed by the eight-section summary (Goal / Problem / Infrastructure / Current state / Active blocker / Key files / What to do next / Gotchas).

Quote the draft verbatim back to the user. Do not rewrite — if something is missing, ask the subagent to revise rather than silently patching on the main model.

### 5. Ask the user where to put it

<required>
After showing the draft, ask:

1. Append to the current task file's `## Conclusion` as a `### Summary — YYYY-MM-DD` subsection (provide the detected `docs/tasks/<slug>.md` path).
2. Create a new file at `docs/tasks/summary-<new-slug>.md` (propose a slug based on the current work).

Pick the destination based on the user's answer. Do not write anywhere without confirmation.
</required>

If no active task file was detected in step 2, option 1 is unavailable — only offer option 2.

### 6. Write

Perform the write in the main session using Edit (append) or Write (new file). The subagent has no write tools.

## Rules

- Subagent drafts; main session locates the JSONL, asks, and writes.
- Concrete: exact commands, exact paths, exact error messages.
- Terse: bullets over prose. No filler.
- Include only info that can't be derived from code or git history. Don't restate `CLAUDE.md`.
- Never write without confirmation.
