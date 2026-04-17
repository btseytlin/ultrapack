---
name: udesign
description: Use before any creative work — features, components, behavior changes. Turns an idea into a validated spec with explicit tradeoffs and unknowns, and splits scope into multiple tasks if it's too large. Output is the `## Design` section of the task file.
---

# Design

Turn an idea into a validated spec through collaborative dialogue. Output lives in `docs/tasks/<slug>.md` — `## Design`, `### Invariants`, `### Principles` — with a TDD decision recorded. Nothing is planned or written until the user approves.

## When to invoke

Before any creative work: new features, component builds, behavior changes, architectural moves. Even "simple" tasks — five minutes of design prevents hours of rework. Skip only when the task is trivial (typo, one-line fix) and the user has confirmed the skip.

## Process

<required>
Follow these steps in order. Do not combine or skip.

1. Explore project context — files, recent commits, existing patterns. No exceptions.
2. Scope check — split into multiple tasks now if the ask is too large.
3. Ask clarifying questions, one at a time. Prefer multiple choice.
4. Propose 2–3 approaches. Each with explicit tradeoffs and unknowns.
5. Backwards-compat check — flag anything that could break already-running or already-used systems. Ask the user how to resolve before proceeding.
6. Present the design in sections. Get per-section approval.
7. Identify invariants (hard constraints) and principles (soft guidance).
8. Decide TDD — yes or no, with reason. Use `up:test-driven-development`'s applicability rule.
9. Write to task file — `## Design`, `### Invariants`, `### Principles`.
10. Self-review for placeholders, contradictions, scope, ambiguity. Fix inline.
11. Wait for user approval before invoking `up:uplan`.
</required>

## Scope check — split before planning

If the ask spans multiple independent subsystems, stop and propose a split. Each piece gets its own task file. We work on one in this dialogue; the rest wait.

<good-example>
User: "Add auth, billing, and admin dashboard."

Agent: "That's three independent tasks. I'd split into:
- `docs/tasks/add-auth.md`
- `docs/tasks/add-billing.md`
- `docs/tasks/add-admin-dashboard.md`

Each is a separate task file, designed and built in its own session. Which one should we start with?"
</good-example>

<bad-example>
Agent designs all three at once in a single task file. Later agents can't resume a coherent piece of work; plans become gigantic and unreviewable.
</bad-example>

A good test: **can a plan for this piece produce working, testable software on its own?** If no, it's too big.

## Proposing approaches — tradeoffs and unknowns, always

For every option, state:
- What it is: 1-2 sentences
- Tradeoffs: what you gain, what you give up (cost, complexity, flexibility, reversibility)
- Unknowns: what you can't answer without more info or experiment

End with a recommendation and why. Don't hedge on the recommendation — if the tradeoffs don't settle it cleanly, say *that* explicitly and ask the user to weigh in.

<good-example>
"Option A: Redis-backed rate limiter.
- Tradeoff: fast, durable across restarts. Adds Redis as a required dep in prod.
- Unknown: our existing Redis cluster's latency from the edge nodes — need to measure before committing.

Option B: In-memory token bucket per pod.
- Tradeoff: zero new infra, simpler code. Loses limits on pod restart; uneven limits across horizontally-scaled pods.
- Unknown: how often pods cycle — if it's every 10 minutes, users see limit resets.

Option C: Postgres-backed counter with short TTL.
- Tradeoff: uses existing DB; no new infra. DB write per request is expensive at our RPS.
- Unknown: whether our DB can absorb the extra write load — need a napkin calc.

Recommendation: B for now, revisit when we outgrow it. The redis latency unknown (A) and write-load unknown (C) both need measurement work before committing, and B is cheap to replace."
</good-example>

## Backwards compatibility — flag breaks loudly

<required>
Before presenting the design, enumerate anything in the chosen approach that could break a system already in use: API shape changes, schema migrations, renamed config keys, removed commands, on-disk format changes, changes to outputs that other code/tools consume, behavioral changes to stable endpoints. Surface each one with its blast radius and ask the user how to resolve: deprecate with shim, hard break with migration, version the new behavior, or revise the approach.
</required>

<good-example>
"Backwards-compat risks:
- `GET /api/v1/users` response shape changes — field `name` splits into `first_name`/`last_name`. Any existing client expecting `name` breaks. Options: (a) return both until v2, (b) hard-break with a migration note, (c) ship as `/api/v2/users` and leave v1 alone. Which?
- Config key `log_level` renamed to `logging.level`. Running deployments on old configs will silently fall through to the default. Options: (a) read both for one release, warn on old, (b) fail loud on old key. Which?"
</good-example>

<bad-example>
Agent designs a schema change without flagging it. Execute runs the migration. Production service that still reads the old column 500s. Root cause: design never surfaced the break.
</bad-example>

If the task is greenfield (no existing consumers), say so in one line and move on. Don't invent risks.

## Identifying invariants and principles

<invariants>
Specific things that must hold. Concrete enough to check against the code.
- "The `Dataset` class must not import from `training/`."
- "All DB writes go through the `transaction()` helper."
</invariants>

<principles>
Softer abstract guidance. Still concrete enough to audit.
- "Fail fast, no silent fallbacks."
- "Prefer composition over inheritance."
</principles>

**Not principles:** "prefer composition" (too vague without "over inheritance"). "Be consistent." "Write clean code."

## TDD decision

Invoke the applicability rule from `up:test-driven-development`. Record in Design:

```
TDD: yes
```
or
```
TDD: no (reason: one-off migration script; no reusable logic)
```

## Task-file output shape

```markdown
## Design
<purpose, scope, chosen approach, key decisions, tradeoffs that settled it, unknowns that remain>
<TDD: yes|no (reason)>

### Invariants
- <specific thing that must hold>
- <...>

### Principles
- <softer guidance — concrete enough to check>
- <...>
```

## Rules

- One question per message. No batching.
- YAGNI ruthlessly. Cut anything not needed for the stated goal.
- Follow existing patterns. Targeted improvements only if they serve this task.
- Isolation. Units with one clear purpose; interfaces understandable without reading internals.
- No code yet. Design's output is words, not code.

## Terminal state

User has approved the Design section → invoke `up:uplan`. Do not write code. Do not invoke any other skill.
