---
name: uverify
description: Use after writing an FR to confirm it against the real system. Mandatory real curl requests — no curl, no pass. Records actual HTTP responses. Links requirement → endpoint → curl → response → verdict. Updates FR if behavior differs from what was written.
---

# Validate

Confirm the FR against the real system — not "looks right", not "OpenAPI says so", but *verified by running a real curl against the real endpoint in this message*.

This is the SA equivalent of TDD's test run. An FR cycle is not complete without it. OpenAPI is a spec, not evidence. A curl response is evidence.

## Brevity

<required>
Passed checks are one line. Evidence attaches to failures, mismatches, and blocked checks. Failures always carry: the exact curl command used, the actual response received, and what the FR claimed. Omit `Notes:` when nothing to report.
</required>

## Phase 1 — Build the validation checklist

From the FR document and the plan's validation targets:

- **Positive (CK):** `POST /api/auth/login` with valid credentials → 200 + access_token
- **Negative (CK):** `POST /api/auth/login` with wrong password → 401 invalid_credentials
- **Contract (CK):** Response body contains field `user.cardNumber` (mapped from `b_user.PERSONAL_PAGER`)
- **Error case (CK):** Blocked user → 423 account_blocked
- **Open question (CK):** UK2 — DreamCRM step behavior: BLOCKED until server-side log available

The checklist lives in-session. Do not write it to the task file.

## Phase 2 — Run each curl freshly, in this message

<required>
- Run the exact curl in this message. Do not rely on prior session results.
- Use real test environment credentials if available; document what was used.
- Capture the full response: HTTP status code + body.
- Pass/fail based on what was actually returned, not what was expected.
- If infra is unavailable (no test env, no credentials): log as BLOCKED — do not fabricate success.
</required>

Curl formats:

```bash
# Status-only check
curl -s -o /dev/null -w "%{http_code}" -X POST https://back-new.dreamisland.ru/api/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"secret123"}'

# Full response check
curl -s -X POST https://back-new.dreamisland.ru/api/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"secret123"}'
```

## Phase 3 — Reconcile with the FR

For each check result:

- **Match** — FR claim matches actual response → pass, one-line note
- **Mismatch** — FR claim differs from actual response → update the FR document directly to reflect actual behavior; flag for re-review
- **Blocked** — curl not runnable (no env, no credentials, requires server-side log) → log reason, mark as deferred

Mismatches update the FR first, then get logged in the Verify section. The FR must always reflect what the system actually does.

## Phase 4 — Write `## Verify` to the task file

<required>
```markdown
## Verify

**Result:** passed | failed | partially-blocked

**Environment:** <base URL used, test user or token if relevant>

Positive:
- CK1 — POST /api/auth/login → 200 ✓
- CK2 — POST /api/auth/login (wrong password) → 401 ✓

Negative:
- CK3 — Blocked user → 423 ✓

Contract:
- CK4 — `user.cardNumber` present in response body ✓

Mismatches:
- CK5 — FR said 422 for missing email, actual was 400. FR updated at step 3 of Алгоритм.

Blocked:
- CK6 — DreamCRM call verification requires server-side log access — deferred (need: log access to test env)

curl commands used:
```bash
curl -s -X POST https://back-new.dreamisland.ru/api/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"secret123"}'
# → 200 {"access_token":"eyJ...","token_type":"Bearer","expires_in":3600}
```
```
</required>

## Phase 5 — Verdict

- All CKs passed, no mismatches → passed → invoke `up:ureview`
- Mismatches found → FR updated → re-run verify once for updated checks → if all pass, invoke `up:ureview`
- Blocked items remain → partially-blocked → invoke `up:ureview` with blocked items explicitly listed

## Red flags — STOP, do not claim pass

<system-reminder>
These phrases mean verify did not happen:
- "The FR looks correct"
- "OpenAPI confirms this"
- "I'm confident it works"
- "Should return 200"
- "Probably works"
- "Curl not needed for documentation"
- "This is a to-be requirement, can't test yet"
</system-reminder>

"Can't test yet" is BLOCKED, not PASSED. Log it as blocked with the reason.

## Never

- Claim pass without running curl in this message
- Fabricate a curl response
- Skip verify because the endpoint "obviously works"
- Use OpenAPI as a substitute for running curl
- Leave mismatches unresolved in the FR

## Hands-off mode

Infeasible curls (no credentials, no test environment) go to `### Deferred (needs user input)` with the exact environment needed. Never claim pass on blocked checks.

## Terminal state

`## Verify` written to task file. Pass → invoke `up:ureview`. Fail → invoke `up:uexecute` with mismatch notes. Partially-blocked → invoke `up:ureview` with blocked items listed explicitly.
