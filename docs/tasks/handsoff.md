# handsoff

**Status:** executing
**Branch:** main
**Worktree:** none
**Mode:** hands-off

## Design

Two bundled changes. They share a PR because they're small, related (both reshape what the pack ships and how it runs), and the user bundled them.

### Piece 1 — Move `data-engineering` and `ml-experiments` out of the pack

**Why:** These skills are user-global (Boris's data/ML workflow), not part of an opinionated plugin for spec-driven dev. They don't belong in `plugins/up/skills/`.

**What:**
- Copy `plugins/up/skills/data-engineering/` → `~/.claude/skills/data-engineering/` and `~/.claude-work/skills/data-engineering/` (overwrite).
- Copy `plugins/up/skills/ml-experiments/` → same two user dirs (overwrite).
- Delete `~/.claude/skills/dataset-engineering/` (superseded by `data-engineering` — user flagged as outdated).
- Remove `plugins/up/skills/data-engineering/` and `plugins/up/skills/ml-experiments/` from the pack.

**Conservative choices (hands-off, documented for review):**
- Copy to BOTH `~/.claude` and `~/.claude-work` because user said "both" — no dedup assumption.
- Overwrite without a backup: user said "overwrite". If they wanted a backup they would've said so.
- Delete old `dataset-engineering` since pack's `data-engineering` supersedes it by name and content.

### Piece 2 — Hands-off mode in `/up:make` and child skills

**Activation:** the literal word `handsoff` (matching user's spelling) as the first token of `/up:make` arguments. Anything else: normal interactive mode, unchanged. No env var, no config flag — keyword arg is simplest and discoverable.

**Propagation:** hands-off is written into the task-file header as `**Mode:** hands-off`. Every child skill reads the header and branches. No parameter passing through the Skill tool — the task file is already the source of truth per existing convention.

**Per-skill behavior in hands-off:**
- `/up:make`: after design, skip user confirmation for size classification, branch/worktree, TDD. Pick conservative defaults: branch = `main`, worktree = none, size auto-classified from scope with no skip of Design/Plan/Review (Review is never skippable anyway). Every auto-choice appended to task file's `## Conclusion → ### Hands-off decisions`. After Review concludes `done`, present that list to the user: "here's what I did to make it hands-off — want to change anything?"
- `up:udesign`: mostly unchanged — design is the one stage where user interaction is valuable. Still ask clarifying questions if genuinely needed, but prefer conservative defaults and document them. Record TDD decision as usual.
- `up:uplan`: skip the "present plan for approval" step — auto-proceed to execute. Log "plan auto-approved (hands-off)" in `### Hands-off decisions`.
- `up:uexecute`: unchanged. The existing "stop and ask" list (ambiguous plan, missing dep, would-invent-fallback) already represents "genuinely impossible without user input" — exactly the exception the user allowed. Don't invent silent fallbacks. Same fail-fast principle.
- `up:uverify`: unchanged. Already auto-loops to execute on failure without asking. Fits hands-off natively.
- `up:ureview`: in hands-off, high-confidence actionable findings from `up:ureviewer` are **fixed directly** instead of asked ("should I fix this? → just fix"). Each fix recorded in `### Hands-off decisions`. Low-confidence / ambiguous findings are documented as deviations/future-work in conclusion, not fixed.

**Conservative rule (applies to all stages):** if a choice has no obvious conservative default and the user didn't specify, DO NOT guess — skip the work and record it under `## Conclusion → ### Deferred (needs user input)`. Matches user's "no default, user-provided" directive.

**End-of-task summary:** after Review sets status=`done` and docs-refresh runs, surface the `### Hands-off decisions` list to the user with: "Here's what I did to make it hands-off. Want to change anything?" That's the only required interaction after design.

### Backwards-compat

- `/up:make` currently says "always confirms branch/worktree" — hands-off changes this only when the `handsoff` keyword is present. Default invocation (`/up:make <description>`) unchanged. No break for existing users.
- Pack loses `data-engineering` and `ml-experiments` skills. Any other user of the published plugin who was relying on them as auto-triggering skills loses them on pack update. Blast radius: small (plugin is barely distributed; internal). Mitigation: mention in README under a "Removed in this release" line. Don't build a migration shim — overkill.

### Scope check

Both pieces are small. Bundling is justified (shared PR scope, both shape pack shipping/runtime). No split.

### TDD

TDD: no (doc-only plugin per CLAUDE.md; verification is install-and-invoke manual testing)

### Invariants
- `plugins/up/skills/` must not contain `data-engineering` or `ml-experiments` after this task.
- `/up:make` without the `handsoff` keyword behaves exactly as before (no regression for interactive users).
- The task file's `**Mode:**` header is the single source of truth for hands-off state. Every child skill reads it; no out-of-band signaling.
- Hands-off never invents defaults for ambiguous args. Missing → deferred under `### Deferred (needs user input)`, not silently filled.
- `### Hands-off decisions` subsection must exist in every hands-off task's Conclusion and be surfaced to the user at end-of-task.

### Principles
- Fail fast over silent fallbacks (unchanged from project baseline; hands-off does not loosen this).
- Conservative over clever: when two paths both work, pick the one with fewer assumptions.
- Document every auto-choice so the user can reverse it with one prompt.
- Keyword activation over config flags: discoverable, per-invocation, no persistent state.

## Plan

Approach: three phases. Phase 1 is a mechanical file move (skills out of pack). Phase 2 adds the hands-off keyword + defaults + end-of-task summary to `/up:make` and introduces the `**Mode:**` header on the task template. Phase 3 teaches each child skill to branch on that header. Phases 2 and 3 are tightly coupled but separable — phase 2 stands alone (child skills just ignore an unknown header); phase 3 depends on the header existing.

### Phase 1 — Relocate `data-engineering` and `ml-experiments` out of the pack

- **1.1** copy `plugins/up/skills/data-engineering/SKILL.md` → `~/.claude/skills/data-engineering/SKILL.md` (overwrite) and → `~/.claude-work/skills/data-engineering/SKILL.md` (create)
- **1.2** copy `plugins/up/skills/ml-experiments/SKILL.md` → `~/.claude/skills/ml-experiments/SKILL.md` (create) and → `~/.claude-work/skills/ml-experiments/SKILL.md` (create)
- **1.3** delete `~/.claude/skills/dataset-engineering/` (superseded by `data-engineering`)
- **1.4** delete `plugins/up/skills/data-engineering/` and `plugins/up/skills/ml-experiments/` (pack side)
- **1.5** `README.md:56-61` (modify) — remove the two bullets `up:data-engineering` and `up:ml-experiments` from the "Discipline skills" list. Leave `up:test-driven-development` and `up:git-worktrees`. Add one-line note at top of that section: "Removed in this release: `up:data-engineering`, `up:ml-experiments` — moved to user-level skills."
- Invariant: `plugins/up/skills/` must not contain `data-engineering` or `ml-experiments` after this phase.
- Commit: `move data-engineering and ml-experiments out of the pack`

### Phase 2 — Add hands-off mode to `/up:make`

- **2.1** `plugins/up/commands/make.md:1-3` (modify) — update frontmatter `description` to mention hands-off activation via `handsoff` keyword.
- **2.2** `plugins/up/commands/make.md:9-11` (modify) — extend `## Arguments` section: if the first whitespace-delimited token of the arguments is the literal string `handsoff`, set mode=hands-off, strip that token, and use the rest as the task description. The slug is derived from the user's description as usual. Otherwise mode=interactive (current default).
- **2.3** `plugins/up/commands/make.md:32-62` (modify) — update the task-file template under step 3 to include a `**Mode:** hands-off | interactive` header and a `### Hands-off decisions` subsection placeholder inside `## Conclusion`:
  ```markdown
  **Status:** design
  **Branch:** main
  **Worktree:** none
  **Mode:** <interactive|hands-off>
  ```
  and the Conclusion placeholder:
  ```markdown
  ## Conclusion
  <empty — filled by up:ureview>

  ### Hands-off decisions
  <empty — populated if Mode is hands-off>
  ```
- **2.4** `plugins/up/commands/make.md:64-87` (modify) — add a "Hands-off override" paragraph after steps 4 (size classification) and 6 (branch/worktree decision): in hands-off, auto-classify size from scope (default: Medium unless trivially one file) and auto-pick branch=`main` + worktree=`none`. Do not confirm. Append each choice to `## Conclusion → ### Hands-off decisions` as `- <stage>: <choice> — <rationale>`.
- **2.5** `plugins/up/commands/make.md:89-91` (modify) — step 7 (Plan stage): in hands-off, after `up:uplan` returns, invoke `up:uexecute` without presenting the plan for approval. Log `- uplan: auto-approved (hands-off)` to decisions.
- **2.6** `plugins/up/commands/make.md:109-116` (modify) — step 11 (Finish): in hands-off, before presenting merge/PR/cleanup options, first print the `### Hands-off decisions` list to the user with the exact prompt: "Here's what I did to make it hands-off. Want to change anything?" Wait for user response. Only after that proceed to the merge/PR/cleanup options.
- **2.7** `plugins/up/commands/make.md:139-146` (modify) — update `## Stop conditions` and `## Rules`: in hands-off, "Never create a worktree without confirming" and "Always confirm the classification" are overridden by the hands-off defaults. Document exactly which confirmation rules are overridden and add one new rule: "In hands-off, never invent a default for an ambiguous argument — record it under `### Deferred (needs user input)` in Conclusion and skip that work."
- **2.8** `plugins/up/commands/make.md` (modify, append new section before `## Terminal state`) — new section `## Hands-off mode` summarizing:
  - activation (first token = `handsoff`)
  - propagation (task-file `**Mode:**` header is the source of truth)
  - what's suppressed (confirmations for size/branch/worktree/TDD; plan-approval gate; review fix-me-yes/no prompts)
  - what's preserved (design dialogue, execute's fail-fast and stop-and-ask list, verify loop, review's existence)
  - decision log (`### Hands-off decisions`) and deferred log (`### Deferred (needs user input)`)
  - end-of-task summary (the "want to change anything?" prompt)
- Invariants: `/up:make` without the `handsoff` keyword behaves exactly as before. The `**Mode:**` header is the single source of truth. No silent fallbacks.
- Commit: `make: add hands-off mode (keyword-activated, conservative defaults, decision log)`

### Phase 3 — Teach child skills to honor hands-off

Each child skill gets a `## Hands-off mode` section near the end (before `## Terminal state`), plus targeted edits where behavior branches. Reading the task file's `**Mode:**` header is already implicit ("Read the task file") — make it explicit in the relevant steps.

- **3.1** `plugins/up/skills/udesign/SKILL.md` (modify, append new section)
  - Add `## Hands-off mode`: in hands-off, still run the full process (explore, scope, propose, backwards-compat check, write design). Relax only rule "One question per message" to "Prefer conservative defaults; ask only if genuinely blocking." Record each conservative-default choice under `## Conclusion → ### Hands-off decisions` when the user would normally be asked.
  - Keep the TDD decision step; keep the rest of the rules.

- **3.2** `plugins/up/skills/uplan/SKILL.md` (modify)
  - Line 46: change step 11 from "Present the plan to the user. On approval, invoke `up:uexecute`" to "Present the plan highlights. In hands-off, invoke `up:uexecute` directly and log `- uplan: plan auto-approved (hands-off)` under `### Hands-off decisions`. In interactive, wait for approval."
  - Line 142 (Terminal state): same adjustment — hands-off skips the wait.
  - Append `## Hands-off mode` section: one paragraph restating the above.

- **3.3** `plugins/up/skills/uexecute/SKILL.md` (modify)
  - No behavioral change. The existing "stop and ask" list (line 178) and "no silent fallbacks" rule (line 119) already implement the "genuinely impossible without user input" exception the hands-off directive allows.
  - Append `## Hands-off mode` section: explicitly document that execute's behavior is unchanged in hands-off, and that its existing stop-and-ask + no-fallback rules are the correct handling of "genuinely impossible" cases. Each such stop is logged under `### Deferred (needs user input)` in Conclusion.

- **3.4** `plugins/up/skills/uverify/SKILL.md` (modify)
  - No behavioral change. Append `## Hands-off mode` section: one paragraph stating verify's loop (fail → execute, pass → review) already fits hands-off; no confirmations to suppress.

- **3.5** `plugins/up/skills/ureview/SKILL.md` (modify)
  - Line 68-88 (step 4, "Announce the plan before editing"): in hands-off, announce and apply together — no pause for user interjection. Still require the restate/verify/evaluate/decide process from step 3. Each fix recorded under `### Hands-off decisions` as `- ureview: fixed <finding summary> — <what changed>`.
  - Low-confidence or ambiguous findings that would have been deferred to the user in interactive mode: in hands-off, log them under `### Deferred (needs user input)` in Conclusion, do not apply the fix.
  - Append `## Hands-off mode` section summarizing: high-confidence actionable findings are fixed directly (no "should I fix?"), low-confidence/ambiguous findings are deferred under `### Deferred (needs user input)`, everything logged in decisions.
- Invariants: hands-off never invents defaults. Task-file `**Mode:**` header is the single source of truth across all skills. `### Hands-off decisions` exists and is surfaced to the user at end-of-task.
- Commit: `child skills: honor **Mode:** hands-off header (uplan auto-approves, ureview auto-fixes high-confidence findings, log decisions)`

### Test strategy (TDD: no — doc-only plugin)

Verification is install-and-invoke manual testing, per CLAUDE.md. Behaviors to verify in `up:uverify`:

Positive:
- `/up:make <description>` (interactive): prompts for size, branch, worktree, TDD, plan approval. Behaves exactly as before.
- `/up:make handsoff <description>`: creates task file with `**Mode:** hands-off`. Does not prompt for size/branch/worktree/TDD. Runs through design, auto-approves plan, executes, verifies, reviews. Final step presents `### Hands-off decisions` with "Want to change anything?"
- Task file for a hands-off run contains `### Hands-off decisions` with each auto-choice logged.
- Pack's `plugins/up/skills/data-engineering/` and `plugins/up/skills/ml-experiments/` are absent after Phase 1.
- `~/.claude/skills/data-engineering/` and `~/.claude-work/skills/data-engineering/` exist with the content from the old pack skill.
- `~/.claude/skills/dataset-engineering/` is absent.

Negative:
- `/up:make something` (no `handsoff`): `**Mode:** interactive` written to task file. Normal prompts happen.
- Hands-off run where a required argument has no conservative default: it is logged under `### Deferred (needs user input)` and not silently filled.
- Review finding that is low-confidence / ambiguous: not auto-fixed; logged under `### Deferred (needs user input)`.

Invariants:
- `grep -r "data-engineering\|ml-experiments" plugins/up/skills/` → empty after Phase 1.
- `/up:make` without `handsoff` keyword unchanged: diff of make.md interactive-path behavior shows no regression.
- `**Mode:**` header is the only place hands-off state lives (no env var, no plugin config).

### Order & dependencies

Phases are sequential. Phase 1 is independent of phases 2-3. Phase 2 introduces the `**Mode:**` header that phase 3 relies on, so phase 3 must come after phase 2. Each phase is one commit.

### Backwards-compat (restated)

- Phase 1: pack users lose two skills on update. Mitigation: README "Removed in this release" note. No shim — user explicitly said overwrite; the pack is barely distributed.
- Phase 2: interactive default unchanged. Only the new `handsoff` keyword branches behavior. No break for current `/up:make` users.
- Phase 3: child skills only branch when `**Mode:** hands-off` is in the header. Existing task files (no header) → interactive path. No break.

### Open questions / risks / rollback

- Risk: users may misspell `hands-off` vs `handsoff`. Conservative choice: accept only the literal `handsoff` (user's spelling). Misspellings fall through to interactive mode. Document this explicitly in make.md so the behavior is discoverable. Logged under `### Hands-off decisions` in *this* task's conclusion.
- Risk: the `**Mode:**` header is not present in existing task files (e.g. `docs/tasks/ultrapack-v1.md`). Child skills must treat missing-header as interactive (the default). Phase 3 edits must say this explicitly.
- Rollback: phases are single commits; `git revert <sha>` per phase cleanly backs out.

### Scope-creep / simpler-way check

- Scope creep: none. Every phase maps to the Design. No "while I'm here" refactors.
- Simpler way considered: could fold phases 2 and 3 into one commit. Rejected — they touch different concerns (command entrypoint vs child skills) and the bigger diff hurts reviewability. Keeping separate.
- Any phase mergeable? 2+3 could merge. Not worth it for the reasons above.

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>

### Hands-off decisions
- slug: `handsoff` — literal user wording, no canonicalization to `hands-off-mode`
- scope: bundled (piece 1 skill-move + piece 2 hands-off mode) into one task — user wrote them as one
- truncated point 3 in args: treated as empty, flagged here as deviation from input completeness
- size: Medium — two related pieces, full Design→Plan→Execute→Verify→Review flow
- branch: `main` — conservative default per CLAUDE.md ("Often users want to work directly on main")
- worktree: none — no parallel work, simple scope
- TDD: no — doc-only plugin per repo CLAUDE.md
- uplan: plan auto-approved (hands-off)
- keyword spelling: accept only literal `handsoff` (user's exact word); misspellings fall through to interactive

### Deferred (needs user input)
<empty — populated if any genuinely-impossible-without-user decisions were hit>
