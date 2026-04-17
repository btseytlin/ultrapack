# Shorthand IDs for task-file entities

**Status:** reviewing
**Branch:** main
**Worktree:** none
**Mode:** interactive

## Design

Replace full-text quoting of recurring task-file entities (invariants, principles, etc.) with short IDs defined once and referenced everywhere else. Solves verbosity in Verify/Conclusion, which today re-quotes entire invariant sentences.

Entity set (7 types, numbered within task only):

- IV — Invariants (hard constraints that must hold)
- PC — Principles (softer guidance)
- AS — Assumptions (unverified premises the design rests on)
- UK — Unknowns (open questions left to plan / execute)
- PH — Phases (plan phases)
- RK — Risks (plan risks)
- CK — Checks (verify checks: positive, negative, invariant)

Assumptions is the key new addition. Today we track what must hold (IV) and how to behave (PC), but not what we are assuming to be true. Conclusion must now explicitly report whether each AS held.

Definition rules:
- Defined once with full sentence at first appearance; every later mention is ID-only.
- Max one sentence per definition.
- Inline in the owning section (no separate legend block).

Ownership:
- Design owns IV, PC, AS, UK.
- Plan owns PH, RK.
- Verify owns CK. Verify references IV / PC / AS by ID.
- Conclusion references IV / PC / AS / UK / PH / RK / CK by ID. Adds an Assumptions-check subsection.

TDD: no (doc-only plugin changes; no runtime code).

### Invariants

- IV1 — Every task file uses the same 7 ID prefixes (IV, PC, AS, UK, PH, RK, CK).
- IV2 — IDs are defined once with a full sentence; later references are ID-only.
- IV3 — Numbering is scoped to the task file; the same ID may recur across tasks with different meanings.
- IV4 — Conclusion explicitly reports whether each AS held and each UK resolved.

### Principles

- PC1 — Minimal change: edit existing skills, don't add new ones.
- PC2 — Brevity: ID references replace quoted prose; no redundant restatement.
- PC3 — Doc-only: no runtime code, no tests.

### Assumptions

- AS1 — Existing completed task files (`ultrapack-v1.md`, `skill-output-brevity.md`) are not retrofitted; the new scheme applies to tasks created after this change.
- AS2 — Users reading a task file top-to-bottom can resolve IDs from context without tooling (no link syntax needed).
- AS3 — The 7-entity set covers the entities worth shortening; additions can happen later without breaking existing tasks.

## Plan

Approach: add a single shared "ID conventions" section to each affected skill via a short block, then update each skill's own output shape and examples to use IDs. One commit.

### PH1 — Template + udesign (owns IV/PC/AS/UK)

- **1.1** `plugins/up/commands/make.md` template block (~lines 40-71)
  - Add `### Assumptions` and `### Unknowns` subsections to the template after `### Principles`, before `## Plan`.
  - Covers IV1 (full ID set present), IV2 (defined once).
- **1.2** `plugins/up/skills/udesign/SKILL.md`
  - Add ID convention block near "Identifying invariants and principles" (~line 96) covering IV / PC / AS / UK: what each is, numbering scoped to task, define-once-reference-by-ID rule.
  - Expand `<invariants>` / `<principles>` blocks into IV / PC / AS / UK, each with a one-line example.
  - Update process step 7 (~line 25) from "Identify invariants and principles" to "Identify invariants (IV), principles (PC), assumptions (AS), and unknowns (UK)".
  - Update task-file output shape (~lines 126-138) to include `### Assumptions` and `### Unknowns`.
  - Covers IV1, IV3 (scoping), IV4 (AS-check will be in conclusion).

### PH2 — uplan (owns PH/RK), uverify (owns CK)

- **2.1** `plugins/up/skills/uplan/SKILL.md`
  - In Process step 1 (~line 42): read IV, PC, AS, UK (not just IV+PC).
  - Add ID block: phases are PH1..PHN, risks are RK1..RKN. References to design entities are by ID.
  - Update Format block (~line 74): phase headings become `### PH1 — <name>` (keeping the human name).
  - Update "Invariants referenced" bullet to "IV/PC/AS referenced by ID".
  - Update self-review step 5 ("each invariant has a referencing bullet") to cover IV / PC / AS.
- **2.2** `plugins/up/skills/uverify/SKILL.md`
  - Update Phase 1 (~line 17): checklist items are CK1..CKN. Good-example block rewritten to use CK IDs and reference IV by ID.
  - Update Phase 4 Format block (~line 76) so Verify section references IV/AS by ID instead of quoting prose.
  - Good-example (~line 98-119) rewritten with IDs.

### PH3 — ureview (Conclusion shape), reviewer agent, uexecute/implementer

- **3.1** `plugins/up/skills/ureview/SKILL.md`
  - Update Conclusion format (~lines 110-128) to add `### Assumptions check` (each AS: held | violated | unverifiable + one line) and `### Unknowns outcome` (each UK: resolved | still-open + one line).
  - `Invariants:` block continues to list IV + verification; references by ID.
  - Add the two new subsections to brevity omit-when-default list: omit if all AS held / all UK resolved and nothing noteworthy. Exception clause: violations always carry evidence.
- **3.2** `plugins/up/agents/reviewer.md`
  - Update "Read the task file's ## Design (especially ### Invariants)" (~line 15) → "(Invariants, Principles, Assumptions)".
  - Plan alignment step references IV/AS by ID.
- **3.3** `plugins/up/skills/uexecute/SKILL.md` + `plugins/up/agents/implementer.md`
  - uexecute "Dispatch per phase" (~line 64): pass AS (assumptions) alongside IV/PC to implementer.
  - implementer "What you receive" (~line 12): list Assumptions.
  - implementer self-review: add "Any assumption (AS) invalidated by what you found? If yes → flag in report."
  - implementer Report Format: add "Assumption status (if any invalidated)" line.

### PH4 — This task file itself

- **4.1** `docs/tasks/shorthand-ids.md` — this file already uses the new shape. Verify pass.

### Test strategy
Doc-only. Verify is an install-and-invoke sweep:
- Each edited SKILL.md parses (no broken frontmatter).
- The task-file template in make.md contains all 7 entity subsection headers (pre-seeded ones: IV / PC / AS / UK; PH / RK / CK are populated later, not pre-seeded).
- Cross-references between skills use IDs consistently (e.g. ureview references IV / AS / UK by the same IDs udesign defines).

### Order & dependencies
PH1 → PH2 → PH3 are sequential because later skills reference the convention introduced in earlier ones' docs. PH4 is a no-op verification.

Commit: one commit, `docs: add shorthand IDs (IV/PC/AS/UK/PH/RK/CK) to ultrapack task-file vocabulary`.

## Verify

**Result:** passed

Positive:
- CK1 — all 8 edited files have valid frontmatter (`head -5` sweep)
- CK2 — make.md template pre-seeds exactly 4 subsections (IV/PC/AS/UK)
- CK3 — uplan format uses `### PH<N>` headings; old "### Phase" gone
- CK4 — uverify good-examples use CK IDs; 19 `CK<digit>` references present
- CK5 — ureview Conclusion adds `### Assumptions check` and `### Unknowns outcome` (2 matches)

Invariants / assumptions:
- CK6 (IV1) — all 7 prefixes (IV/PC/AS/UK/PH/RK/CK) documented across udesign + uplan + uverify
- CK7 (IV4) — ureview Conclusion format lists AS and UK outcomes by ID
- CK8 (AS1) — no edits to old task files (`ultrapack-v1.md`, `skill-output-brevity.md`)

## Conclusion
<empty — filled by up:ureview>
