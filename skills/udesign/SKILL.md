---
name: udesign
description: Use before any creative work — features, components, behavior changes. Turns an idea into a validated spec with explicit tradeoffs and unknowns, and splits scope into multiple tasks if it's too large. Output is the `## Context` and `## Design` sections of the task file.
---

# Design

Turn the goal into an approved specification. Write `## Context` and `## Design` in `docs/tasks/<slug>.md`, including constraints, assumptions, unknowns, and a test-driven-development decision. Design produces words, not implementation code.

Read the [brevity rules](../_brevity.md) and [global principles](../_principles.md) before responding or writing the task file.

## What design is

Describe how the system should work to meet the goal. Study existing behavior and patterns as evidence without letting today's implementation constrain the desired outcome. The plan will describe how to get there.

Invoke before features, components, behavior changes, and architectural work. Skip only for a trivial change when the user confirms the skip.

## Context

Record observations that motivate the design: current behavior, limits, and failures. Each bullet is a checkable fact from the repository or the user's stated experience. Cut facts that do not explain a design choice.

Example: "The importer holds a whole shard in memory and fails on shards larger than available memory."

Do not put solutions in context. Unconfirmed premises belong under assumptions or unknowns.

## The Goal — definition of done

Write one observable outcome in the task file's goal header and confirm it with the user during design approval. A passing diff, verification, or review does not establish the goal by itself.

Use an outcome such as "the importer completes on the full dataset within available memory", not an activity such as "rewrite the importer". If confirmation needs an expensive run, remote environment, or user observation, state that requirement. A local proxy does not prove the real outcome.

## Process

Follow these steps in order:

1. Read project context, existing patterns, recent commits, and previous attempts. Follow [global principles](../_principles.md#incidental-code-smells) for incidental defects: include in-scope or easy fixes in the design, and record other findings under `## Code smells`.
2. Check scope. If the request spans independent goals, propose separate task files and ask which to design first. Each task must be independently implementable and testable.
3. Ask clarifying questions one at a time, preferably with choices.
4. Propose two or three approaches with tradeoffs and unknowns. Recommend one and explain why. If the tradeoffs do not settle the choice, ask the user.
5. Identify compatibility risks and ask how to resolve them before proceeding.
6. Present the design in sections and get per-section approval.
7. Identify invariants, task-specific principles, assumptions, and unknowns.
8. Apply [test-driven-development](../test-driven-development/SKILL.md)'s applicability rule. Record `TDD: yes` or `TDD: no (reason)`.
9. Save the approved context and design, the goal header, and the constraint sections to the task file.
10. Check for placeholders, contradictions, scope drift, and ambiguity. Correct the text.
11. Wait for user approval before invoking [uplan](../uplan/SKILL.md).

Hands-off changes to these approval steps are defined below.

## Approaches

For each option state its mechanism, benefits, costs, reversibility, and unresolved questions.

Example: an in-memory rate limiter adds no infrastructure but loses counters on restart and cannot enforce a shared limit across replicas. A shared store can enforce that limit but adds latency and an operational dependency. Measure the unknown latency before relying on it.

## Backwards compatibility

List changes that could break existing consumers: signatures, schemas, configuration keys, commands, file formats, outputs, or endpoint behavior. State who is affected and ask the user to choose a migration, compatibility layer, versioned behavior, or revised design. Do not add compatibility machinery without that decision.

Example: splitting `name` into `first_name` and `last_name` breaks clients reading the old field. Ask whether to retain it temporarily or require migration.

For greenfield work with no consumers, say so briefly and do not invent risks.

## ID conventions

Define each entity once in a concrete sentence, with numbering scoped to the task file:

- `IV` — invariant: a property the implementation must guarantee.
- `PC` — principle: task-specific guidance or a justified deviation from a global principle.
- `AS` — assumption: an unverified premise outside the implementation's control.
- `UK` — unknown: an open question that needs an answer or explicit deferral.

Later task sections and child prompts reference these IDs rather than repeating definitions. In user-facing chat, explain the rule in plain words rather than using only an ID. Planning introduces `PH` for phases, `RK` for risks, and `IF` for interfaces. Verification introduces `CK` for checks.

## Invariants, principles, assumptions, and unknowns

- Invariants must be testable. Example: `IV1 — Every database write goes through transaction().`
- Principles must guide a concrete choice. Do not restate global principles. Example: `PC1 — Error messages must tell an operator how to resume an interrupted import.` A deviation from a global principle names it and explains why.
- Assumptions must be checked later. Example: `AS1 — The upstream users service returns email as UTF-8.` The conclusion reports whether each assumption held.
- Unknowns must be resolved during planning or execution, or explicitly deferred. Example: `UK1 — Whether the existing shared store has spare capacity.` The conclusion records each outcome.

If code can enforce a condition, make it an invariant. If the condition depends on the outside world, record an assumption. Avoid vague principles such as "write clean code".

## Task-file output shape

```markdown
## Context
- <observation motivating the design>

## Design
<purpose, scope, approach, decisions, and tradeoffs>
TDD: <yes | no (reason)>

### Invariants
- IV1 — <testable requirement>

### Principles
- PC1 — <task-specific guidance or justified global-principle deviation>

### Assumptions
- AS1 — <unverified premise>

### Unknowns
- UK1 — <question for planning or execution>
```

Also set the task file's goal header. Omit empty sections, including unused sections seeded by the workflow template. Do not leave placeholders or "none" entries.

## Rules

- Keep interactive questions one per message.
- Include only what serves the stated goal. Follow existing patterns where they fit.
- Keep units focused and interfaces understandable without reading internals.
- Do not implement code during design.

## Hands-off mode

Read [handsoff](../handsoff/SKILL.md). Run the full design process, asking only when genuinely blocking. Use conservative choices with a recorded reason instead of routine per-section approval prompts.

Log each choice under `### Hands-off decisions` as `udesign: choice — reason`. Record gaps with no safe default under `### Deferred (needs user input)`.

## Terminal state

Interactive: the user has approved context, design, and the goal. Hands-off: they are written and self-reviewed under its contract. Then invoke [uplan](../uplan/SKILL.md). Do not implement code or jump to another workflow stage.
