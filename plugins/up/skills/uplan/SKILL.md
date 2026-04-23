---
name: uplan
description: Use after scope analysis to plan FR coverage — which documents to write, in what order, which endpoints each covers, what curl validation each needs.
---

# Coverage Plan

Convert the approved Design into a concrete FR coverage plan. Output fills `## Plan` in `docs/tasks/<slug>.md`. The plan is the contract that `up:uexecute` will follow document by document.

## What a coverage plan is

A plan that specifies: which FR documents to write, in what order, what each must cover, and how each will be validated. That means:

- Concrete FR document names with codes (following `WRITING_GUIDE.md` naming: `SECTION-NN-MM-ROLE`)
- Per-document scope: which endpoint(s), which algorithm sections, which DB fields
- Endpoint per document: HTTP method + exact path from `routes.php`
- Validation target per document: the curl command that will confirm the behavior
- Dependencies: auth FRs before feature FRs, GEN documents before module-specific ones

## Process

<required>
1. Read the task file's `## Design`, `### Invariants` (IV), `### Assumptions` (AS), `### Unknowns` (UK).
2. List all FR documents needed. Each document covers one endpoint or one coherent set of related endpoints.
3. Order by dependency: auth before features; GEN-01-XX before module-specific; as-is before to-be when documenting migration.
4. For each document: list endpoints covered, key sections needed (algorithm, DB mapping, error cases), planned curl validation.
5. Identify which UK items block which documents. A blocked document can proceed to stub only — validation is blocked until the UK is resolved.
6. Self-review: is every in-scope endpoint from Design covered by at least one FR document?
7. Present to user. Wait for approval, then invoke `up:uexecute`.
</required>

## Format

```markdown
## Plan

Approach: <1-2 sentences on coverage strategy>

### PH1 — <FR document code and name>
- **1.1** `docs/FR/<code>. <name>.md` (create)
  - Endpoints: `POST /api/path`, `GET /api/other`
  - Covers: algorithm, DB mapping table, error cases (list codes)
  - Validation curl: `curl -X POST <url> -H "..." -d '{...}'` → expected: <HTTP status>
  - Blocked on: UK1 (if applicable — skip validation until resolved)
  - Respects: IV1, AS2
- Commit: `doc: draft <code> <name>`

### PH2 — <next FR document>
...

### Test strategy
<which curl commands cover which documents; what responses to record>

### Order & dependencies
<what blocks what; e.g. "PH2 requires PH1 to define the auth token format">

### Risks / rollback
- RK1 — DreamCRM API key not available in test env — validation of DreamCRM-dependent steps will be blocked
- RK2 — <...>
```

## Rules

- Every in-scope endpoint from Design must appear in at least one plan phase.
- UK-blocked documents get a stub note, not a skip — the document is started, the validation is deferred.
- Curl commands are planned here and run in `up:uverify`. Do not run them in this stage.
- Scope is fixed in `up:udesign`. If new scope issues appear here, go back to the user — do not silently expand or shrink.
- No TDD decision needed — this is doc-only work.

## Self-review

<required>
1. Coverage: every endpoint from Design maps to at least one document.
2. Dependency order: no document precedes its dependency.
3. Validation: every document has a planned curl command, or a UK explaining why it's blocked.
4. Format: document names follow `WRITING_GUIDE.md` naming convention.
</required>

## Hands-off mode

Skip the approval wait — present plan highlights, log `- uplan: plan auto-approved (hands-off)` to `### Hands-off decisions`, invoke `up:uexecute` directly.

## Terminal state

Plan written, self-reviewed. Interactive: present highlights, wait for approval, invoke `up:uexecute`. Hands-off: present highlights, log auto-approval, invoke `up:uexecute`.
