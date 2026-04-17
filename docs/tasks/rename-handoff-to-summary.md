# Rename /handoff command to /summary

**Status:** done
**Branch:** main
**Worktree:** none
**Mode:** hands-off

## Design
Skipped (Small task — single concept rename).

### Invariants
- `/up:handoff` invocation stops working; replaced by `/up:summary`
- Command semantics unchanged — only the name
- Historical task files (Status=done) keep their `handoff` references as historical record

### Principles
- Conservative rename: touch only live artifacts (command file, skills that reference it, README). Leave archived/done task files alone.

### Hands-off decisions
- Slug auto-picked: `rename-handoff-to-summary`
- Size: Small — skip Design per /up:make rules
- No Design, no worktree, TDD: no (doc-only)
- Historical refs in `docs/tasks/ultrapack-v1.md` (done task) left untouched

## Plan

Approach: Single-commit rename. Move `plugins/up/commands/handoff.md` → `summary.md` via `git mv`, update user-facing references inside the command file (heading, subsection name, sample paths), and update the README entry. Leave generic English "handoff" in `uplan/SKILL.md:45` and historical references in the done task `docs/tasks/ultrapack-v1.md` untouched.

### Phase 1 — Rename command file and update references

- **1.1** `plugins/up/commands/handoff.md` → `plugins/up/commands/summary.md` (rename via `git mv`)
  - Heading `# /up:handoff` → `# /up:summary`
  - Frontmatter `description:` — swap "handoff summary" / "handoff task file" / "handoff itself" to "summary" / "summary task file" / "summary itself"
  - Section `### 2. Draft the handoff` → `### 2. Draft the summary`
  - Body "Show the drafted handoff" → "Show the drafted summary"
  - Body "a `### Handoff — YYYY-MM-DD` subsection" → "a `### Summary — YYYY-MM-DD` subsection"
  - Path pattern `docs/tasks/handoff-<new-slug>.md` → `docs/tasks/summary-<new-slug>.md`
  - Keep prose verb "hand off work to another session" / "continue this work" — generic English, not command name
  - Invariant: command semantics unchanged — only name and its self-references

- **1.2** `README.md:68` (modify)
  - Line `- \`/up:handoff\` — Produce a handoff summary...` → `- \`/up:summary\` — Produce a summary so another session can continue with zero context.`
  - Invariant: README commands list matches actual command filenames

- **1.3** Out of scope (explicit non-changes):
  - `plugins/up/skills/uplan/SKILL.md:45` — "handoff" is generic English ("final step before handoff"), not a command ref. Leave.
  - `docs/tasks/ultrapack-v1.md` — Status=done historical task; documents the command as it was. Leave per task invariant.

- Commit: `rename /up:handoff command to /up:summary`

### Test strategy

Doc-only rename, no code. Verify:
- `plugins/up/commands/summary.md` exists; `handoff.md` does not
- `grep -rn "up:handoff"` on repo returns only historical task file (`docs/tasks/ultrapack-v1.md`)
- `grep -rn "up:summary"` returns new command file + README entry
- Plugin reload in Claude Code: `/up:summary` appears in command list, `/up:handoff` does not (manual check — deferred to verify stage)

### Order & dependencies

Single phase, single commit. No dependencies.

### Backwards-compat

`/up:handoff` invocation breaks. Per task invariant, this is expected. No alias/shim (plugin is pre-1.0, single user). Users running `/up:handoff` will get an unknown-command error and can read the README for the new name.

### Open questions / risks / rollback

- Risk: `git mv` preserves history; plain rename via Write + delete loses it. Use `git mv`.
- Rollback: `git mv summary.md handoff.md` and revert README line. Cheap.
- No open questions.

## Verify

**Result:** passed

Positive:
- `plugins/up/commands/summary.md` exists → pass (`ls` output; `git log --follow` shows renamed from `handoff.md`, history preserved)
- README line 68 reads `/up:summary — Produce a summary…` → pass (grep `/up:summary` hit)
- Command file content: heading `# /up:summary`, `### 2. Draft the summary`, `### Summary — YYYY-MM-DD`, path `docs/tasks/summary-<new-slug>.md` → pass (re-read full file)

Negative:
- `plugins/up/commands/handoff.md` does not exist → pass (`ls` confirms)
- No live `/up:handoff` references — grep hits only in this task file (self-documenting) and `docs/tasks/ultrapack-v1.md:306` (done historical task, intentionally preserved) → pass

Invariants:
- Command semantics unchanged → verified by diff: only renames in user-visible text, all bullets and rules intact
- `plugins/up/skills/uplan/SKILL.md:45` generic English "handoff" left untouched → pass (grep confirms)
- `docs/tasks/ultrapack-v1.md` historical refs preserved → pass (grep confirms)
- git history preserved → pass (`git log --follow summary.md` shows full chain through `ffaeb78`)

Smoke: `/up:summary` invocation end-to-end requires a Claude Code plugin reload (new session / marketplace reinstall). Plugin cache at `~/.claude-work/plugins/cache/ultrapack/up/0.1.0/commands/` still holds the pre-rename snapshot — normal cache behavior, refreshes on user's next install. **Deferred to user on next session.**

Notes: doc-only rename, no runtime code. All in-repo checks pass. Smoke test is a one-step manual action (reload plugin, type `/up:summary`) that cannot be executed from inside this session.

## Conclusion

Outcome: `/up:handoff` command renamed to `/up:summary`. Single commit (`b0091eb`) moves `plugins/up/commands/handoff.md` → `summary.md` via `git mv` (history preserved), updates all user-visible self-references inside the file (heading, description frontmatter, section 2 title, "drafted summary" body, `### Summary — YYYY-MM-DD` subsection, `docs/tasks/summary-<slug>.md` path pattern), and rewrites README.md:68. Command semantics unchanged.

Plan adherence: clean. Every Phase 1 bullet reflected in diff; no deviations.

Invariants (verified):
- Command semantics unchanged — reviewer confirmed process/rules untouched.
- Historical refs preserved — `docs/tasks/ultrapack-v1.md` and generic English in `plugins/up/skills/uplan/SKILL.md:45` untouched (grep confirmed).
- `/up:handoff` invocation stops working — file no longer exists under old name.
- git history preserved — `git log --follow summary.md` traces back through `ffaeb78`.

Review findings:
- Critical: none.
- Important: none.
- Nit: none. Reviewer verdict: APPROVE.

Future work:
- none.

Verified by: in-repo positive/negative/invariant checks in `## Verify`; up:reviewer subagent run on `d1aba5b..b0091eb`. End-to-end smoke (`/up:summary` in a live Claude Code session) is deferred to user — requires plugin reload outside this session's control.

### Hands-off decisions
- uplan: plan auto-approved (hands-off)
- uexecute: trivial phase executed inline (no implementer dispatch) — rename + 6 text edits across 2 files
- ureview: approved with no findings, no remediation needed
