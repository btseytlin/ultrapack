# Subagent prompt templates

**Status:** planning
**Branch:** main
**Worktree:** none
**Mode:** interactive

## Design

Add fill-in-the-blank prompt skeletons to each dispatching skill so dispatchers stop improvising prose preludes (e.g. "you are in a fresh subagent — nothing below was in your prior context") around the existing required-field lists. Five agents, five skeleton homes — all colocated with their dispatch call site:

- `up:implementer` → `plugins/up/skills/uexecute/SKILL.md` (augment existing §77-90 list)
- `up:explorer` → `plugins/up/skills/uexecute/SKILL.md` (augment existing §135 section)
- `up:researcher` → `plugins/up/skills/uexecute/SKILL.md` (new section alongside explorer)
- `up:reviewer` → `plugins/up/skills/ureview/SKILL.md` (augment existing §37-48)
- `up:summarizer` → `plugins/up/commands/summary.md` (augment existing §31-42)

Each skeleton is a short fenced code block with labeled fields and `<...>` placeholders, placed immediately next to the existing "Pass in the dispatch prompt" bullet list. Fields mirror the destination agent's "What you receive" section — no new fields, no rewriting of agent contracts.

Shape (illustrative, implementer):

```
Phase: <verbatim PHN text from ## Plan>
Invariants: <IV1, IV2, ...>
Principles: <PC1, PC2, ...>
Assumptions: <AS1, AS2, ...>
TDD: <yes | no (reason)>
Working directory: <absolute path>
Branch: <expected branch from task file header>
Commit mode: <self | defer>
```

Tradeoffs that settled it:

- Colocated-in-dispatching-skill over shared `_dispatch-template.md` — dispatchers read the skill end-to-end; a separate file adds a hop and risks drift from the skill's required-fields list.
- Labeled fenced block over Mad-Libs prose — fields are unambiguous, `<...>` markers discourage narrative wrapping, copy-paste-and-fill is fast.
- "Guidance" framing (no `<required>` tag) over strict schema — dispatchers may adapt for unusual cases without violating a rule.

Backwards-compat: greenfield. Internal plugin docs, no external consumers.

TDD: no (reason: doc-only plugin; verification is install-and-invoke, no reusable logic).

### Invariants
- IV1 — Each skeleton lives inside the dispatching skill's markdown, not in the agent definition file.
- IV2 — Every field listed in the skill's "Pass in the dispatch prompt" bullet list appears as a labeled line in the skeleton for that skill.
- IV3 — Skeletons use labeled `<...>` placeholders, not runnable code or rigid JSON schema.

### Principles
- PC1 — Skeletons are guidance, not mandate. Dispatchers may adapt; the skeleton shows what to pass, not how to narrate it.

### Assumptions
- AS1 — Dispatchers presented with a visible skeleton will follow it rather than improvise a prose wrapper. If this fails, escalate to strict-schema in a follow-up.

### Unknowns
- UK1 — Whether to standardize field order across all five skeletons or mirror each agent's own "What you receive" order. Leaning: mirror — less cognitive load when a dispatcher cross-checks agent file vs. skill.

## Plan

Approach: insert a labeled-field fenced code block (skeleton) immediately after each existing "Pass in the dispatch prompt" bullet list in the three dispatching skills. Fields mirror each agent's "What you receive" section. Three files changed, one phase per file.

### PH1 — uexecute: implementer, explorer, researcher skeletons

- **1.1** `plugins/up/skills/uexecute/SKILL.md` (modify)
  - After the "Do not pass:" block at §85-89, insert a `### Dispatch prompt skeleton` subsection containing a fenced block with labeled lines: `Phase`, `Invariants`, `Principles`, `Assumptions`, `TDD`, `Working directory`, `Branch`, `Commit mode`. `<...>` placeholders. (IV1, IV2, IV3)
  - Augment the existing `## When to dispatch up:explorer` section (~§135) with a `### Dispatch prompt skeleton` block: `Scope`, `Working directory`. (IV1, IV2, IV3)
  - Add a new `## When to dispatch up:researcher` section immediately after the explorer section, mirroring its shape: one short "when to use" paragraph + skeleton with `Question`, `Sub-questions` (optional), `Working directory`, `Scope hints`. (IV1, IV2, IV3)
  - No `<required>` tags on any skeleton — framing is guidance per PC1.
- Commit: `docs(uexecute): add dispatch prompt skeletons for implementer, explorer, researcher`

### PH2 — ureview: reviewer skeleton

- **2.1** `plugins/up/skills/ureview/SKILL.md` (modify)
  - After the `<system-reminder>` block at §52, insert `### Dispatch prompt skeleton` with fields: `Task file`, `BASE_SHA`, `HEAD_SHA`, `Working directory`. (IV1, IV2, IV3)
  - No `<required>` tag.
- Commit: `docs(ureview): add dispatch prompt skeleton for reviewer`

### PH3 — summary command: summarizer skeleton

- **3.1** `plugins/up/commands/summary.md` (modify)
  - After the "Dispatch via the Task tool..." bullet list at §37-40, insert `### Dispatch prompt skeleton` with fields: `Working directory`, `Distinctive phrases`, `Active task file`. (IV1, IV2, IV3)
  - No `<required>` tag.
- Commit: `docs(summary): add dispatch prompt skeleton for summarizer`

## Verify

**Result:** passed

Invariants / assumptions:
- CK1 (IV1) — `grep "Dispatch prompt skeleton" plugins/up/agents/*.md` → empty; skeletons live only in dispatching skills/commands
- CK2 (IV2) — every field in each skill's "Pass in the dispatch prompt" bullet list maps to a labeled line in its skeleton (implementer 8/8, reviewer 4/3, summarizer 3/3)
- CK3 (IV3) — all skeletons use `<...>` placeholders inside fenced blocks, no JSON schema

Positive:
- CK4 — five skeletons present: implementer (uexecute:92), explorer (uexecute:156), researcher (uexecute:170), reviewer (ureview:54), summary (summary.md:42)

Smoke: doc-only change, no runtime to exercise

## Conclusion
<empty — filled by up:ureview>

### Deviations from plan
- Skeleton heading style: used bold `**Dispatch prompt skeleton**` instead of plan's `### Dispatch prompt skeleton`. Reason: ureview and summary command use numbered `### N. Step name` subheadings; inserting a new `###` would break their numeric flow. Bold label fits all three files uniformly.
