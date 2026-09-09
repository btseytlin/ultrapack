---
name: uplan
description: Use after design to turn a validated spec into a lean implementation plan. Outputs the `## Plan` section of the task file — files, line numbers, class/method names, invariants, test strategy, order. Ends with a scope-creep / simpler-way check.
---

# Plan

Convert the approved design into an implementation contract for [uexecute](../uexecute/SKILL.md). Fill `## Plan` in the existing `docs/tasks/<slug>.md`. Do not create a separate plan file.

Read the [brevity rules](../_brevity.md) and [global principles](../_principles.md) before planning. Preserve required content and omit optional sections with no useful content. Deviations, deferrals, failures, and risks retain evidence and reasons.

## Scope

Design decides the outcome and scope. Planning names the concrete changes needed to reach it. If a new finding requires splitting the task, changing the design, or expanding scope, stop and ask the user. Do not silently rewrite the goal.

## Process

1. Read context, design, invariants, principles, assumptions, and unknowns in the task file.
2. Identify files, symbols, and interfaces to change. Include only defects within the approved scope in the plan. Report unrelated findings under `## Code smells` without adding their fixes.
3. Divide the work into coherent phases with at least one commit per phase.
4. Write concrete file changes, interfaces, verification behavior, and dependencies. Follow the design's test-driven-development decision.
5. Map compatibility risks to phases and mitigation steps. If a new break was not covered by the design, stop and ask the user. For greenfield work, state that this check does not apply.
6. Review the plan for coverage, correctness, and simplicity using the checks below.
7. Present the plan. In interactive mode, wait for approval before invoking [uexecute](../uexecute/SKILL.md). In hands-off mode, follow the contract below.

## Required contents

Always include:

- Approach and why it fits the design.
- Each changed or new file as `path:lineA-lineB`, with affected symbols and concrete changes. For example, name `Parser.tokenize()` rather than just "modify parser".
- New or changed signatures without implementation bodies.
- Ordered phases and intended commits.
- References to the design constraints each phase preserves or relies on.

Include when relevant:

- Test strategy: behaviors to cover, with failing tests first when `TDD: yes`.
- Dependencies, open questions, risks, and rollback.
- Cross-phase interfaces when two or more phases share a signature, anchor, or other contract.
- An interface graph for multi-phase plans. Omit it for a single phase.
- A snippet only when prose cannot express the most critical detail in a phase. Do not write full implementations in the plan.

## ID conventions

- `PH1`, `PH2`, and so on identify phases. Each phase heading is `### PH<N> — <name>`.
- `RK1`, `RK2`, and so on identify risks, each defined in one sentence.
- `IF1`, `IF2`, and so on identify cross-phase interfaces.
- Reference existing design entities by their IDs rather than repeating definitions.

## Format

```markdown
## Plan

Approach: <strategy and reason>

### PH1 — <name>
- 1.1 `path/to/file.ext:lineA-lineB` (create|modify)
  - `Class.method(arg: Type) -> Ret` — <concrete change>
  - Respects: IV2, AS1
- Commit: <message>

### Test strategy
- <behavior and affected file or phase>

### Order & dependencies
- <what blocks what>

### Risks / rollback
- RK1 — <risk and mitigation>

### Interfaces
- IF1 — <signature and contract>
- IF2 [blocks] — <signature, contract, and why the consumer must wait>

### Interface graph
- PH1 -> IF1, IF2 @ src/producer.py
- PH2 IF1 -> @ src/consumer.py
- PH3 IF2 -> @ src/generated_consumer.py
```

Repeat phase entries as needed. The graph above illustrates dependencies for three phases, whose concrete change bullets must also be written. Omit irrelevant optional sections.

## When to declare interfaces

An interface is a contract shared by phases: a function signature, class shape, file format, or skill section anchor. The consume arrow names an interface the phase uses. A phase that only reads an earlier phase's plan text does not consume its output.

For each graph line, declare consumed interfaces, produced interfaces, and owned paths after `@`. An empty consume side is a source. An empty produce side is a sink.

Only `[blocks]` interfaces create wave boundaries. Non-blocking consumers can be implemented against the declared signature while the producer runs. Do not hand-declare waves. The executor derives them and checks that concurrent phases own disjoint paths.

## Blocking interfaces

Use `[blocks]` when a consumer needs actual producer output, such as a generated file or applied migration, or when a large or critical producer must be completed and verified first. State the reason in the interface contract.

Leave ordinary signature dependencies non-blocking when their declarations provide enough context. The executor's wiring check reconciles drift after the final wave.

## Self-review

1. Every invariant, principle, assumption, and unknown maps to a plan bullet or an explicit deferral to execution or verification.
2. File paths and symbols are concrete and consistent. Remove placeholders such as "handle edge cases" or "similar to phase 1".
3. Every phase follows the global principles. A deviation names the principle and the reason.
4. The test strategy and compatibility mitigations match the design.
5. If a graph is present, every phase declares owned paths, every consumed interface is defined, every defined interface has exactly one producer, and every blocking annotation has a reason. Paths within a derived wave must be disjoint.
6. Keep the plan proportional to the work. Fix these issues inline without a review subagent.

## Final check — scope creep, elegance, simpler way

- Does each phase serve the approved design, without unrelated refactors, extra validation layers, or speculative abstractions?
- Can phases or duplicate paths be combined without losing clear ownership?
- Would a simpler approach meet the goal with less work? Present a material alternative to the user rather than changing scope silently.

Revise a bloated plan before handoff. For example, remove a generalization phase whose only justification is a second caller that does not exist.

## Hands-off mode

Read [handsoff](../handsoff/SKILL.md). Present the completed plan, log `uplan: plan auto-approved` under `### Hands-off decisions`, and invoke [uexecute](../uexecute/SKILL.md) without waiting for routine approval. Keep all self-review and compatibility checks.

Record ambiguities requiring user input under `### Deferred (needs user input)` and stop. Do not invent a choice to complete the plan.

## Terminal state

The plan is written, self-reviewed, scope-checked, and approved explicitly or through hands-off mode before execution begins.
