---
name: uplan
description: Use after design to turn a validated spec into a lean implementation plan. Outputs the `## Plan` section of the task file — files, line numbers, class/method names, invariants, test strategy, order. Ends with a scope-creep / simpler-way check.
---

# Plan

Convert the approved Design into a lean, concrete implementation plan. Output fills the `## Plan` section of `docs/tasks/<slug>.md`. The plan is the contract that `up:uexecute` will follow.

## What a plan is

A plan is the minimum information an engineer needs to implement the Design without re-doing the thinking. That means:

- Concrete locations: exact file paths, line number ranges, class/method/interface names. "Modify `parser.py`" is not enough — `parser.py:120-160, Parser.tokenize()` is.
- Per-file change bullets: what changes in each file, by name. Not prose.
- Interface signatures: new or changed function/method signatures. No bodies.
- Phases with commits: ordered phases, one commit per phase minimum.
- Test strategy: the behaviors to cover, not test code.
- Snippets only where words fail: one regex, one tricky algorithm, one non-obvious API call. Never full implementations.

If an engineer could read your plan and implement the wrong thing, the plan is incomplete. If they need to re-derive the Design to understand the plan, the plan is bloated.

## Scope is decided in design, not here

By the time you plan, the task's scope is fixed. If you discover a subsystem-split issue now, it means design missed it — stop planning, go back to the user, and decide whether to re-open design or keep the current scope.

Do **not** silently split the task here. Do not silently expand it either.

## Output

Fill `## Plan` in `docs/tasks/<slug>.md`. Do not create a separate plan file.

## Process

<required>
1. Read the task file's `## Design`, `### Invariants`, `### Principles`. Know what you're planning for.
2. Sketch the file structure — which files change, which are new, which classes/methods.
3. Break into phases. Each phase is a coherent commit.
4. Write phase-by-phase plan entries. Concrete locations, per-file bullets, interfaces.
5. Write test strategy (per task's TDD decision).
6. Write order + dependencies, open questions, risks, rollback.
7. Add snippets only for the single most critical component per phase.
8. Backwards-compat check — restate Design's compat risks in concrete plan terms.
9. Self-review inline (placeholders, consistency, invariants, spec coverage).
10. Scope-creep / simpler-way check — see below. This is the final step before handoff.
11. Present the plan to the user. On approval, invoke `up:uexecute`.
</required>

## Required contents

Every plan has:
- Approach: 2-3 sentences on the strategy and why it fits the Design
- File structure: for each file, `path/to/file.ext:lineA-lineB` (create|modify) + affected class/method names
- Per-file bullets: what changes, by name. As many bullets as needed, no filler.
- New/changed interfaces: signatures only
- Invariants referenced: which Design invariants each phase preserves
- Test strategy: behaviors to cover. If `TDD: yes`, list the failing tests to write first.
- Order + dependencies: phases, what blocks what
- Open questions / risks / rollback: what could go wrong, how to back out

Optional:
- Code snippets: only for the most critical component per phase. If tempted to include full code, you're over-planning.

## Format

```markdown
## Plan

Approach: <2-3 sentences>

### Phase 1 — <name>

- **1.1** `path/to/file.ext:lineA-lineB` (create|modify)
  - `ClassName.method_name(arg: Type) -> Ret` — <what changes, by name>
  - Invariant: <which Design invariant this respects>
- **1.2** ...
- Commit: `<message>`

### Phase 2 — <name>
...

### Test strategy
<behavior list, per file or per phase>

### Order & dependencies
<what blocks what, parallelizable phases>

### Open questions / risks / rollback
- <item>
```

## Self-review (inline, no subagent)

<required>
1. Spec coverage — every Design / Invariant / Principle item maps to at least one plan bullet.
2. Placeholder scan — no "TBD", "handle edge cases", "add validation", "similar to task N", "write tests for the above".
3. Consistency — method/class names match across bullets; later phases' interfaces reference what earlier phases define.
4. Leanness — plan size should fit the task. If it exceeds ~1 screen per day of expected work, trim.
5. Invariants — each invariant has a referencing bullet somewhere.
</required>

Fix issues inline. No re-review loop.

## Backwards-compat check — restate the design's risks in plan terms

<required>
Design should already have surfaced backwards-compat risks. In the plan, restate each one with its concrete phase and the mitigation step. If you discover a new break the Design missed (schema rename in phase 2, config key no longer read, output format drift), stop planning and go back to the user — don't smuggle it in.
</required>

<good-example>
"Phase 3 renames `log_level` → `logging.level`. Per Design decision, Phase 3 also adds a one-release compat read of the old key with a deprecation warning. Removal is out of scope for this task."
</good-example>

<bad-example>
Plan includes a schema migration with no mention of the compat strategy. Execute runs the migration; the old service version in prod breaks on the next deploy.
</bad-example>

If the task is greenfield, skip this check explicitly in one line.

## Final check — scope creep, elegance, simpler way

<required>
Before handing off to the user, ask yourself honestly:

1. Scope creep: is every phase directly serving the Design, or have I snuck in "while I'm here" refactors, extra validation layers, speculative generality?
2. Elegance: can any pair of phases merge? Are there accidental duplicate data paths? Does the plan introduce abstractions that aren't pulling their weight?
3. Simpler way: is there a one-paragraph alternative plan that gets 90% of the value with 30% of the work? If yes, propose it to the user as an option.
</required>

<good-example>
"Plan says 7 phases. The honest version is 3 phases — phases 4-7 are a generalization layer for a second caller that doesn't exist. Cut to 3, flag the generalization as future work."
</good-example>

<bad-example>
"Plan is 12 phases. I'll just hand it off — the user can decide what to cut." No. That's the agent's job here, not the user's.
</bad-example>

If this check surfaces real simplifications, rewrite the plan. Don't stack warnings on top of a bloated plan.

## Terminal state

Plan written, self-reviewed, scope-checked → present the highlights to the user and ask for approval. On approval, invoke `up:uexecute`.
