# Summary command on Sonnet

**Status:** executing
**Branch:** summary-sonnet
**Worktree:** .worktrees/summary-sonnet
**Mode:** hands-off

## Design

Goal: `/up:summary` drafts on Sonnet instead of whatever model the main session runs (typically Opus). Motivation: summary drafting is bulk reading + condensation — Sonnet is fast enough and cheap enough; Opus is overkill and slow.

Finding ("Maybe this requires a subagent, find out"): yes, it does. Commands execute in the main session and inherit the session model; a command cannot rewrite its own model. The existing pattern in the plugin for running work on a different model is an agent file with `model: sonnet` frontmatter (see `plugins/up/agents/implementer.md`, `reviewer.md`). So the fix is to introduce a summarizer agent and have `/up:summary` dispatch to it.

Shape:
- New agent `plugins/up/agents/summarizer.md` with `model: sonnet`. Tools: `Glob, Grep, Read, Bash`. Does steps 1 + 2 of the current command: gather concrete state (`git status`, `git diff`, task file scan, `tmp/` check) and draft the summary text against the shape already documented in `summary.md`.
- Rewrite `plugins/up/commands/summary.md` to be a thin orchestrator: dispatch the summarizer, receive the drafted text, then do step 3 (ask the user where to put it) and write. Asking + writing stays in the main session because it requires user interaction and a tool (Edit/Write) that may not be given to the subagent.

Boundaries:
- Subagent returns prose; never writes to disk. Main session writes. This keeps the "ask before writing" rule cleanly enforced in one place.
- Main session does not re-gather or re-read — it trusts the draft. (Re-drafting on Opus would defeat the purpose.)
- Conversation context is not forwarded to the subagent verbatim. The subagent has `Bash`/`Read`/`Grep` and rebuilds state from the repo. The one thing the main session passes is the active task file path (if any), since that's needed to offer option 1.

TDD: no (documentation-only change: a new agent markdown file and a rewritten command markdown file; no runtime logic to test).

### Invariants
- IV1 — Drafting (state gathering + prose writing) runs in a subagent whose frontmatter declares `model: sonnet`.
- IV2 — The destination prompt (append to current task file vs. new `summary-<slug>.md`) and the actual file write stay in the main session; the subagent never writes to disk.
- IV3 — The summary content shape (Goal / Problem / Infrastructure / Current state / Active blocker / Key files / What to do next / Gotchas) is preserved — only the execution model changes.

### Principles
- PC1 — Minimal: one new agent file, one rewritten command file. No speculative additions.
- PC2 — Follow the existing agent pattern (`implementer.md`, `reviewer.md`, `researcher.md`) for frontmatter, tool list, and report shape.

### Assumptions
- AS1 — An agent's `model: sonnet` frontmatter is honored by Claude Code regardless of the main session's model.
- AS2 — The summarizer can reconstruct the needed state from the repo (git + task files + tmp/) without conversation history; the main session only needs to pass the active task file path.

## Plan

Approach: add a `summarizer` agent pinned to Sonnet that does the gather+draft work, and rewrite `/up:summary` as a thin dispatcher that hands the drafted text to the main session for the user-interactive destination prompt and file write.

### PH1 — Add the `summarizer` agent

- **1.1** `plugins/up/agents/summarizer.md` (create)
  - Frontmatter: `name: summarizer`, one-line description, `tools: Glob, Grep, Read, Bash`, `model: sonnet`. Mirrors the shape of `researcher.md` / `reviewer.md`.
  - Body sections:
    - Purpose — one paragraph: draft a session-handoff summary so a fresh agent can continue with zero conversation context.
    - What you receive — task file path (optional; main session passes `null` if no active task) and working directory (absolute).
    - Process — 1. `pwd` matches the passed working dir; 2. gather concrete state (`git status`, `git diff`, `git log -n 5`, read the active task file if given, list `tmp/`); 3. draft the summary against IV3's eight-section shape; 4. return the prose. Do not write to disk.
    - Output shape — the eight-section template used by `/up:summary` today (Goal / Problem / Infrastructure / Current state / Active blocker / Key files / What to do next / Gotchas), introduced with a one-line "Draft summary below — main session decides destination" preface so the dispatcher can quote it cleanly.
    - Rules — Bash is readonly; no disk writes; no `Edit`/`Write` in the tool list; say when something is unknown rather than inventing.
  - Respects: IV1, IV2, IV3, PC2; relies on AS1, AS2.
- Commit: `feat(agents): add summarizer agent pinned to Sonnet`

### PH2 — Rewrite `/up:summary` as dispatcher

- **2.1** `plugins/up/commands/summary.md` (modify — near-total rewrite)
  - Keep the frontmatter `description` line (description is what makes the command discoverable).
  - Replace steps 1 + 2 ("Gather concrete state", "Draft the summary") with one step: dispatch the `summarizer` agent via the Task tool with `subagent_type: summarizer`, passing the active task file path (auto-detect via `ls docs/tasks/*.md` and the most recently modified non-`done` file, or `null` if none) and the working directory.
  - Keep step 3 as-is ("Ask the user where to put it") — quote the drafted summary back verbatim, then present options 1/2, then write to the chosen destination.
  - Rules section: tighten to reflect the new division of labor — "Subagent drafts; main session asks and writes; never write without confirmation."
  - Add a one-line note: dispatching the subagent is required, not optional — drafting in the main session defeats the performance motivation.
  - Respects: IV1, IV2, IV3, PC1.
- Commit: `refactor(summary): dispatch drafting to sonnet summarizer agent`

### Test strategy

None — this is a doc-only change (per Design: `TDD: no`). Verification is install-and-invoke: run `/up:summary` in a real session after merge and confirm the summarizer agent is dispatched (and its model reads as Sonnet in the transcript).

### Order & dependencies

PH1 before PH2 — PH2 references the agent by name. Otherwise linear, no parallelism.

### Risks / rollback

- RK1 — AS1 turns out false (Sonnet frontmatter not honored, falls back to session model). Mitigation: verify in the first smoke run; if violated, escalate in `## Conclusion` and consider an explicit model-check hook later. Rollback is a one-commit revert of PH2.
- RK2 — Summarizer's Bash-only state gathering misses something the conversation-aware Opus version would have caught (e.g. in-memory decisions never written to the task file). Mitigation: the user sees the draft before it's written (step 3 is unchanged), so any gap is caught at review time, not after-the-fact.


## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>

### Hands-off decisions
- size: Medium — default for hands-off; touches two plugin files across commands/agents boundary, more than trivial.
- udesign: TDD=no defaulted — documentation-only change.
- branch/worktree: `.worktrees/summary-sonnet` on branch `summary-sonnet`, resolved by the user choosing `.worktrees/` project-local. `.gitignore` updated in prereq commit on `main`.
- uplan: plan auto-approved (hands-off).
