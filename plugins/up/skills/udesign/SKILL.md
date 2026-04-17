---
name: udesign
description: Use before any creative work — features, components, behavior changes. Turns an idea into a validated spec with explicit tradeoffs and unknowns, and splits scope into multiple tasks if it's too large. Output is the `## Design` section of the task file.
---

# Design

Turn an idea into a validated spec through collaborative dialogue. Output lives in `docs/tasks/<slug>.md` — `## Design`, `### Invariants` (IV), `### Principles` (PC), `### Assumptions` (AS), `### Unknowns` (UK) — with a TDD decision recorded. Nothing is planned or written until the user approves.

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
7. Identify invariants (IV), principles (PC), assumptions (AS), and unknowns (UK).
8. Decide TDD — yes or no, with reason. Use `up:test-driven-development`'s applicability rule.
9. Write to task file — `## Design`, `### Invariants`, `### Principles`, `### Assumptions`, `### Unknowns`.
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

## ID conventions — define once, reference by ID

Entities in the task file are assigned short IDs so later sections (Plan, Verify, Conclusion) can reference them without re-quoting full sentences.

Design owns four entity types:

- IV1, IV2, … — Invariants
- PC1, PC2, … — Principles
- AS1, AS2, … — Assumptions
- UK1, UK2, … — Unknowns

Rules:
- Defined once with a full sentence at first appearance; later mentions are ID-only.
- Max one sentence per definition.
- Numbering is scoped to the task file. The same ID can recur across tasks with different meanings.
- IDs are for persisted artifacts (task file, commit messages, agent-to-agent prompts). When talking to the user in chat, expand the ID — write out the invariant, principle, or assumption in plain English. "IV3 was violated" is fine in the task file; to the user say "the invariant that Dataset must not import from training/ was violated". Mentioning the ID alongside is OK; replacing the content with just the ID is not.

Plan owns PH (phases) and RK (risks). Verify owns CK (checks). Those are introduced in their stage's skill.

## Identifying invariants, principles, assumptions, unknowns

<invariants>
IV — specific things that must hold. Concrete enough to check against the code.
- IV1 — The `Dataset` class must not import from `training/`.
- IV2 — All DB writes go through the `transaction()` helper.
</invariants>

<principles>
PC — softer abstract guidance. Still concrete enough to audit.
- PC1 — Fail fast, no silent fallbacks.
- PC2 — Prefer composition over inheritance.
</principles>

<assumptions>
AS — unverified premises the design rests on. Conclusion must report whether each held.
- AS1 — The upstream `users` service returns `email` as UTF-8 in every response.
- AS2 — Nightly batch volume stays under 10M rows for the next quarter.
</assumptions>

<unknowns>
UK — open questions the design cannot answer alone. Resolved during plan, execute, or explicitly deferred. Conclusion must report outcome.
- UK1 — Whether the existing Redis cluster has spare capacity for this workload.
- UK2 — Exact failure mode when the upstream API rate-limits mid-batch.
</unknowns>

**Not principles:** "prefer composition" (too vague without "over inheritance"). "Be consistent." "Write clean code."

**Assumptions vs invariants:** an IV is something the code guarantees. An AS is something the world is assumed to give you. If the code can enforce it, it's an IV; if it depends on something outside your control, it's an AS.

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
<purpose, scope, chosen approach, key decisions, tradeoffs that settled it>
<TDD: yes|no (reason)>

### Invariants
- IV1 — <specific thing that must hold>
- IV2 — <...>

### Principles
- PC1 — <softer guidance — concrete enough to check>
- PC2 — <...>

### Assumptions
- AS1 — <unverified premise the design rests on>
- AS2 — <...>

### Unknowns
- UK1 — <open question left to plan / execute>
- UK2 — <...>
```

## Rules

- One question per message. No batching. (Hands-off: ask only when genuinely blocking; prefer conservative defaults logged in the task file.)
- YAGNI ruthlessly. Cut anything not needed for the stated goal.
- Follow existing patterns. Targeted improvements only if they serve this task.
- Isolation. Units with one clear purpose; interfaces understandable without reading internals.
- No code yet. Design's output is words, not code.
- Omit empty subsections. `### Invariants`, `### Principles`, `### Assumptions`, `### Unknowns` are pre-seeded by the `/up:make` template. Delete any that end up with no entries — never leave a placeholder like `<empty>`, "none", or "n/a". See `_brevity.md` principle 1.

## Hands-off mode

See `up:handsoff` for the full contract. Stage-specific delta: Design is still the one interactive stage — run the full process. The only relaxation is "one question per message" → "ask only when genuinely blocking; prefer a conservative default". Log each defaulted answer as `- udesign: <what> — <rationale>` in `### Hands-off decisions`; log no-default gaps under `### Deferred (needs user input)`.

## Terminal state

User has approved the Design section (interactive) or the Design has been written and self-reviewed (hands-off) → invoke `up:uplan`. Do not write code. Do not invoke any other skill.
