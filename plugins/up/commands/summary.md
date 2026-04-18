---
description: Produce a summary so another session can continue with zero context beyond CLAUDE.md, the codebase, and the summary itself. Asks whether to append to the current task file or create a new summary task file.
---

# /up:summary

Prepare a handoff summary so another agent session can continue this work without the current conversation. Drafting is delegated to the `up:summarizer` subagent (pinned to Sonnet) so the expensive main-session model doesn't write the long structured prose. The subagent locates this session's JSONL transcript on disk using a distinctive phrase you pass to it, then reads it directly.

## Process

### 1. Pick a distinctive phrase from the current conversation

Choose a verbatim string that uniquely identifies this session — something unusual enough not to match any other session's JSONL:
- A recent user quote with unusual wording.
- An error message or stack-trace line.
- A commit hash or file path that's specific to this session.
- A made-up term, slug, or identifier coined this session.

Avoid generic phrases ("fix the bug", "run tests") — they'll match many sessions.

Pick 1–2 phrases. The subagent tries the first; if it matches 0 or >1 file, it falls back to the second.

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
- One or two distinctive phrases from step 1 — verbatim, exactly as they appear in the conversation.
- Active task file path, or `null`.

The subagent greps JSONL files under the encoded-cwd projects dirs to locate this session's transcript, then reads it. Do not paste the transcript into the prompt.

### 4. Receive the draft

The subagent returns prose beginning with `Draft summary below — main session decides destination.` followed by the eight-section summary (Goal / Problem / Infrastructure / Current state / Active blocker / Key files / What to do next / Gotchas).

Quote the draft verbatim back to the user. Do not rewrite — if something is missing, ask the subagent to revise rather than silently patching on the main model.

If the subagent reports it couldn't uniquely locate the JSONL (zero matches or multiple matches on both phrases), pick a different phrase and re-dispatch.

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

- Subagent locates the JSONL, drafts the summary; main session picks the phrase, asks, and writes.
- Concrete: exact commands, exact paths, exact error messages.
- Terse: bullets over prose. No filler.
- Include only info that can't be derived from code or git history. Don't restate `CLAUDE.md`.
- Never write without confirmation.
