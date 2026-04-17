# Skill output brevity

**Status:** done
**Branch:** main
**Worktree:** none
**Mode:** hands-off

## Design
Skipped (Small task; design agreed in conversation — see Principles + Hands-off decisions below).

The problem: skill-driven outputs (task-file `## Plan`, `## Verify`, `## Conclusion`) carry boilerplate sections and restate-the-diff prose that add no information beyond what the commit, git log, or lived-through checks already show. Example: previous task's Conclusion was ~60 lines for a rename whose essence is "renamed X to Y, commit SHA".

Fix: one shared brevity principle loaded by every output-producing skill, plus terser template examples.

### Invariants
- Skill outputs stay truthful — brevity never means dropping a finding, a deviation, or a failed check.
- Every SKILL.md remains self-sufficient for a fresh agent: referencing `_brevity.md` via an explicit `<required>` read, not an implicit assumption.
- Existing workflow unchanged — no new stages, no new status values, no runtime behavior.
- `_brevity.md` sits at `plugins/up/skills/_brevity.md` and is not a skill itself (no SKILL.md inside, no registration).

### Principles
- **Omit don't fill.** A section with default content ("none", "n/a", "single phase, no deps") is deleted, not written.
- **Evidence only on surprise.** Passed checks are one line. Failures, deferrals, and anomalies carry evidence.
- **Don't re-narrate what the artifact already shows.** Commit message + diff + git log are authoritative. Prose in the task file should add context only they can't express.
- Soft caps, not hard word limits.

### Hands-off decisions
- Slug: `skill-output-brevity`
- Size: Small — skip Design; Plan runs
- Branch: main, no worktree
- Shared file at `plugins/up/skills/_brevity.md` (flat, alongside skill dirs — inert because no SKILL.md)
- Applied to 4 output-producing process skills: `uplan`, `uverify`, `ureview`, `uexecute`
- Not applied to `udesign`, `udebug`, `udocument`, `handsoff`, `git-worktrees`, `test-driven-development` — they don't produce task-file output sections that suffered the bloat
- Edit templates + good-examples now (retroactive); don't leave stale verbose examples contradicting the new rule
- Soft caps only — phrasing like "lean toward ≤1 screen" not "≤200 words"

## Plan

Approach: One commit. Create `plugins/up/skills/_brevity.md` with the 5 generalized principles (omit/evidence/no-re-narrate/one-sentence/soft-caps), then edit the 4 output-producing SKILL.md files to (a) reference the shared file via a short `## Brevity` block near the top and (b) mark optional template subsections accordingly + rewrite good-examples to the terse form. All changes live in one logical commit.

### Phase 1 — Shared principle + skill references

- **1.1** `plugins/up/skills/_brevity.md` (create, ~35 lines)
  - Sections: `# Brevity principles for task-file output`, `## Principles` (5 numbered), `## Checklist before saving`, `## Exception`
  - Principles enumerated: Omit-don't-fill · Evidence-only-on-surprise · Don't-re-narrate · One-sentence-not-paragraph · Soft-caps
  - Exception: failures/deviations/deferrals always carry evidence + why
  - Invariant: truthfulness preserved (explicit exception clause)

- **1.2** `plugins/up/skills/uplan/SKILL.md` (modify)
  - Insert `## Brevity` section after `## Output` (around line 33): points to `_brevity.md`, one-sentence directive
  - `## Format` block (lines 64-90): mark `### Test strategy`, `### Order & dependencies`, `### Open questions / risks / rollback` with `(optional — include only if non-trivial)`
  - `## Required contents` list (lines 49-62): split into `Required always` and `Required when relevant` per the optional-section rule
  - Invariant: skill remains self-sufficient (explicit `<required>` to read `_brevity.md`, not an implicit assumption)

- **1.3** `plugins/up/skills/uverify/SKILL.md` (modify)
  - Insert `## Brevity` section after `# Verify` intro (around line 9)
  - `## Phase 4` template (lines 69-86): change `<check> → <pass/fail + 1-line evidence>` to `<check> — evidence only on fail/surprise`; mark `Smoke:` and `Notes:` as `(omit if nothing to report)`
  - `<good-example>` in Phase 4 area: add a terse variant showing collapsed pass-only Verify section
  - Invariant: failed checks still require evidence (explicit in Exception clause of `_brevity.md` and retained in Phase 5)

- **1.4** `plugins/up/skills/ureview/SKILL.md` (modify)
  - Insert `## Brevity` section after `## When to invoke` (around line 15)
  - `### 6. Write the ## Conclusion` template (lines 102-122): `Outcome:` tightened to `≤1 sentence + commit SHA, don't re-narrate the diff`; `Plan adherence:`, `Review findings:`, `Future work:`, `Verified by:` marked `(optional — include only if non-default)`
  - `Invariants:` stays required (explicit audit trail value)
  - Invariant: findings never hidden (explicit carve-out in Brevity section)

- **1.5** `plugins/up/skills/uexecute/SKILL.md` (modify)
  - Insert `## Brevity` section after `## Before starting` (around line 18)
  - `## Deviations from plan` (line 152-176): add explicit "omit the subsection entirely if no deviations" line to the `<required>` block
  - Hands-off decisions logging: add a line allowing collapse to one entry `"all stages auto-approved, no interventions"` when no stage chose against the grain
  - Invariant: deviations still logged when present (explicit)

- Commit: `skills: add _brevity.md shared principle; uplan/uverify/ureview/uexecute reference it and mark trivial-output subsections optional`

### Brevity block — canonical form for each skill

Identical copy-paste block appended where specified above:

```markdown
## Brevity

<required>
Before writing your section of the task file, read `plugins/up/skills/_brevity.md`. Apply its five principles (omit / evidence-on-surprise / don't-re-narrate / one-sentence / soft-caps). Treat every subsection in the Format block below as optional — include only when the content is non-default. Failures, deviations, deferrals, and known risks always include evidence.
</required>
```

### Test strategy

Doc-only, no runtime. Verification:
- `_brevity.md` exists and is well-formed
- Each of 4 SKILL.md files contains the `## Brevity` block pointing at the shared file
- Each of 4 SKILL.md template blocks marks optional subsections
- Grep: no stale "required" claims left on a subsection now marked optional

### Backwards-compat

No compat risk — existing in-flight tasks using older templates still produce valid task files (superset of optional subsections). Prior completed task files untouched.

## Verify

**Result:** passed

Positive:
- `plugins/up/skills/_brevity.md` exists, well-formed
- 4 target SKILL.md files reference `_brevity.md` (grep: 1 hit each, 2 in uexecute due to secondary mention in Deviations)
- Each of the 4 SKILL.md files preserves the Exception clause ("always carry evidence / truthfulness never abbreviated")

Negative:
- `_brevity.md` has no adjacent `SKILL.md` — not registered as a skill (top-level file, inert)
- Non-target SKILL.md files (udesign, udebug, udocument, handsoff, git-worktrees, test-driven-development) do not reference `_brevity.md`

Invariants:
- Skill outputs stay truthful — Exception clause retained in every Brevity block
- Each SKILL.md self-sufficient — explicit `<required>` read of `_brevity.md`, not implicit
- `_brevity.md` not a skill — top-level placement, no SKILL.md inside, no frontmatter

Smoke: deferred — end-to-end `/up:make` flow using the new templates requires a plugin reload outside this session.

## Conclusion

Outcome: shared `plugins/up/skills/_brevity.md` added; `uplan`/`uverify`/`ureview`/`uexecute` reference it and mark trivially-empty template subsections optional — commit `abf3ec4`.

Invariants:
- Skill outputs stay truthful — Exception clause present in `_brevity.md` and each Brevity block
- Each SKILL.md self-sufficient — explicit `<required>` pointer to `_brevity.md`
- `_brevity.md` not a skill — top-level flat file, no adjacent SKILL.md
- No new stages, status values, or runtime behavior

Verified by: reviewer APPROVE on `e391c55..abf3ec4` (3 nits, cosmetic). End-to-end smoke (new templates driving a fresh `/up:make` flow) is deferred to user — requires plugin reload.

### Hands-off decisions
- all stages auto-approved, no interventions
