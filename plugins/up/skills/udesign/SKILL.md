---
name: udesign
description: Use before writing any FR — new scenario, migration coverage, gap analysis. Maps scope to real endpoints, reads context.md and DECOMPOSITION.md, identifies knowns vs unknowns. Output is the `## Design` section of the task file.
---

# Analyze

Map a scenario to the real system: endpoints, contracts, code paths, and gaps. Nothing is documented until the real shape is known. Output lives in `docs/tasks/<slug>.md` — `## Design`, `### Invariants` (IV), `### Assumptions` (AS), `### Unknowns` (UK).

## When to invoke

Before writing any FR: new scenario coverage, migration documentation, gap analysis, or any case where the system behavior isn't fully known.

## Process

<required>
Follow in order. Do not skip.

1. Read `docs/context.md` — scope, architecture, and open questions (section 7).
2. Read `docs/FR/DECOMPOSITION.md` — find the relevant scenario(s) and stakeholder comments.
3. Check `context.md` section 4 — if the scenario is explicitly out of scope, stop and tell the user. Do not analyze out-of-scope items.
4. Identify the endpoints: read `source_code/back_site/.../local/config/routes.php` for each relevant route.
5. For each endpoint: find the controller (`local/src/Controllers/`), the service (`local/src/Services/`), and the OpenAPI entry (if present) in `OpenApi/*.json`.
6. Map to DreamCRM / Accounting API: find the OpenAPI spec entries in `OpenApi/CRM-EXTERNAL-INTEGRATIONS-openapi.json` or `OpenApi/ACCOUNTING-EXTERNAL-INTEGRATIONS-openapi.json`.
7. List what is known vs unknown. Unknowns become UK entries.
8. Write to task file: `## Design` (scope + approach + as-is/to-be boundary), `### Invariants`, `### Assumptions`, `### Unknowns`.
9. Self-review: are there any guesses? Convert them to UK or AS entries. No guesses in IV.
10. Wait for user approval before invoking `up:uplan`.
</required>

## Scope check

Verify the scenario is listed in `DECOMPOSITION.md` and in scope per `context.md` section 4. If unclear, ask the user. If out of scope, stop — do not produce any output.

## Endpoint mapping

For each scenario, produce a concrete mapping:

```
Route (routes.php) → Controller → Service → external API call (if any)
```

- If route is missing from `routes.php`: record as UK, flag explicitly.
- If no OpenAPI entry exists for an external call: record as UK.
- If controller/service doesn't exist yet (to-be only): label clearly as "to-be, not yet implemented".
- Distinguish as-is (Mindbox) from to-be (DreamCRM) at every step.

## ID conventions

- IV1, IV2, … — Invariants: specific things that must hold. Example: "IV1 — `user.cardNumber` maps to `b_user.PERSONAL_PAGER`, not `PERSONAL_PHONE`."
- AS1, AS2, … — Assumptions: unverified premises. Example: "AS1 — DreamCRM returns 201 Created on successful customer-actions call."
- UK1, UK2, … — Unknowns / Gaps: open questions to resolve in execute or verify stage.

UK entries are not failures — they are the honest map of what needs verification.

## Task-file output shape

```markdown
## Design
<scenario, scope, as-is vs to-be boundary, approach, key decisions>

### Invariants
- IV1 — <specific thing that must hold, cites source>
- IV2 — <...>

### Assumptions
- AS1 — <unverified premise the design rests on>
- AS2 — <...>

### Unknowns
- UK1 — <open question to resolve during execute or validate stage>
- UK2 — <...>
```

## Rules

- No FR writing in this stage. Output is words only.
- Distinguish as-is from to-be explicitly in every section.
- Unknowns are never guessed away — they stay as UK until verified.
- Every IV and AS cites its source (code file, OpenAPI entry, DB field) per SAPC2.
- Omit empty subsections — delete `### Invariants`, `### Assumptions`, or `### Unknowns` if they have no entries.

## Hands-off mode

Ask only when genuinely blocking; prefer conservative defaults. Log each defaulted answer as `- udesign: <what> — <rationale>` in `### Hands-off decisions`. Log no-default gaps under `### Deferred (needs user input)`.

## Terminal state

User approves Design section → invoke `up:uplan`. Do not write FR content. Do not invoke any other skill.
