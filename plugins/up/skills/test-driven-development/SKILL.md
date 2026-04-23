---
name: validation-driven-documentation
description: Use when writing FR documents to enforce the describe → validate → update → finalize cycle. The SA equivalent of TDD — documentation is not done until the real endpoint confirms it. Auto-triggers alongside up:uexecute and up:uverify.
---

# Validation-Driven Documentation

Write the requirement. Run the curl. If they disagree, update the requirement. Repeat until they agree. Only then is the FR done.

**Core principle:** if you didn't run the curl, you don't know whether the FR describes the right thing.

This is the SA equivalent of Test-Driven Development:

| TDD (code) | VDD (documentation) |
|---|---|
| Write failing test | Write FR claiming endpoint behavior |
| Watch it fail | Run curl, see actual response |
| Write code to pass | Update FR to match reality |
| Refactor | Clarify and finalize FR |
| Test suite green | Curl confirms FR |

## Applicability — always on for FR writing

VDD applies to every FR document in `up:uexecute` + `up:uverify`. There are no skip conditions. If an endpoint cannot be reached, the validation is **blocked** (not skipped) and logged explicitly.

The only relaxation: read-only reference documents (context.md, DECOMPOSITION.md updates) don't need curl validation — they describe intent, not endpoint behavior.

## Phase 1 — DESCRIBE: write the FR claim

Write what the endpoint is supposed to do, sourced from:
- Source code (controller + service)
- OpenAPI spec
- DECOMPOSITION.md stakeholder comments

Do not write claims you can't source. Unknown behavior → open question stub.

## Phase 2 — VALIDATE: run curl, capture actual response

<required>
Run the exact curl in this session. Capture HTTP status + body. Do not infer from prior sessions or OpenAPI alone.
</required>

```bash
curl -s -X POST https://<base>/api/<path> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"field": "value"}'
# Record: HTTP status + full body
```

If infra unavailable: mark as BLOCKED with the environment needed. Never write "PASSED" for a blocked check.

## Phase 3 — UPDATE: reconcile FR with actual behavior

Three outcomes:

- **Match** — FR was correct. One-line confirmation note.
- **Mismatch** — FR claim ≠ curl response. Update FR immediately to reflect actual behavior. Invoke `up:udebug` to understand *why* before correcting, if the mismatch is unexpected.
- **Blocked** — curl not runnable. Log explicit reason. FR stays in draft status.

## Phase 4 — FINALIZE: FR is done when curl confirms it

An FR is finalized only when:
- All positive checks passed (happy path confirmed)
- All negative checks passed (error cases confirmed)
- All mismatches resolved (FR updated to match reality)
- Blocked items explicitly logged with owner and environment needed

"FR looks complete" is not finalized. "All curls ran and confirmed" is finalized.

## Red flags — FR is not done

<system-reminder>
- "The OpenAPI spec confirms the behavior" — OpenAPI is a spec, not evidence
- "This endpoint clearly returns 200" — prove it with a curl
- "The FR matches the code" — code and running system can diverge
- "We can validate later" — later is blocked, not validated
</system-reminder>

## Cycle record in task file

Each iteration of the VDD cycle is visible in `## Verify`:

```
CK1 — POST /api/auth/login → expected 200, got 200 ✓
CK2 — missing email → expected 422, got 400 ✗ → FR updated at step 3 → re-verified ✓
CK3 — DreamCRM call → BLOCKED (need: test env with DreamCRM access)
```

## Terminal state

All checks confirmed (pass or explicitly blocked with reason). FR finalized. Invoke `up:ureview`.
