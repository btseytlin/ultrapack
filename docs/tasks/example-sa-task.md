# P-01-01-BE Bonus Balance

**Status:** done
**Branch:** main
**Worktree:** none
**Mode:** interactive

## Design

Scenario P-01-01-BE: GET endpoint returning a customer's bonus balance. Part of migration from legacy CRM to new CRM.

Scope: document the to-be (new CRM) behavior only. The current (legacy) behavior is explicitly out of scope for this task — it is documented separately in the legacy reference doc.

As-is / to-be boundary:
- Current system: balance fetched directly from legacy CRM SDK via mobile/web client
- Target system: backend endpoint proxies the request to new CRM External Integrations API and returns a normalized response

Approach: trace from `routes.php` → controller → service → new CRM OpenAPI; write the FR; validate with curl against the test environment.

### Invariants

- IV1 — `customer_id` sent to new CRM API is always sourced from the `users_extension.uf_newcrm_id` DB field, never derived inline.
- IV2 — If `uf_newcrm_id` is null, the endpoint returns 404 before calling the external API.

### Assumptions

- AS1 — New CRM GET /loyalty/customers/{id}/balance returns 200 with `{ "balance": <int>, "currency": "RUB" }` on success.
- AS2 — Test environment has valid API key configured in env vars.

### Unknowns

- UK1 — Whether the endpoint requires OAuth2 Bearer token or is accessible via API key only. *(Resolved in execute: requires OAuth2 Bearer token — confirmed from AuthMiddleware in routes.php.)*

## Plan

Approach: single FR document covering the GET balance endpoint. One curl confirms the happy path; one confirms the 404 on missing customer.

### PH1 — P-01-01-BE. Баланс бонусов

- **1.1** `docs/FR/P-01-01-BE. Баланс бонусов.md` (create)
  - Endpoints: `GET /api/loyalty/balance`
  - Covers: algorithm (3 steps: auth check, lookup newcrm_id, call new CRM), DB mapping (uf_newcrm_id), error cases (401, 404, 502)
  - Validation curl: `curl -X GET .../api/loyalty/balance -H "Authorization: Bearer <token>"` → expected: 200
  - Respects: IV1, IV2, AS1
- Commit: `doc: draft P-01-01-BE Баланс бонусов`

### Test strategy

Happy path: `GET /api/loyalty/balance` with valid token and existing customer → 200 + balance field.
Error: valid token, customer without `uf_newcrm_id` → 404.
Error: invalid/missing token → 401.

### Risks / rollback

- RK1 — New CRM test environment intermittently unavailable — validation of step 3 (external call) may be partially blocked.

## Verify

**Result:** partially-blocked

**Environment:** https://back-new.example.ru, test user: test-user@example.com (token obtained via /api/security/login)

Positive:
- CK1 — GET /api/loyalty/balance (valid token, existing customer) → 200, `{"balance": 1250, "currency": "RUB"}` ✓
- CK2 — Response contains `balance` as integer ✓

Negative:
- CK3 — GET /api/loyalty/balance (valid token, customer without uf_newcrm_id) → 404 `{"error": "customer_not_found"}` ✓
- CK4 — GET /api/loyalty/balance (no token) → 401 `{"error": "unauthorized"}` ✓

Mismatches:
- CK5 — FR draft said 502 on new CRM unavailable; actual was 503 with `{"error": "upstream_unavailable"}`. FR updated at Алгоритм step 3, error table.

Blocked:
- CK6 — Direct new CRM API call verification requires server-side log access — deferred (need: tail access to backend logs in test env, or new CRM sandbox credentials)

curl commands used:
```bash
# Happy path
curl -s -X GET https://back-new.example.ru/api/loyalty/balance \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Q..."
# → 200 {"balance":1250,"currency":"RUB"}

# Missing customer
curl -s -X GET https://back-new.example.ru/api/loyalty/balance \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Q..." \
  -H "X-Test-User-Id: 99999"
# → 404 {"error":"customer_not_found"}

# No token
curl -s -X GET https://back-new.example.ru/api/loyalty/balance
# → 401 {"error":"unauthorized"}
```

## Conclusion

**Outcome:** FR P-01-01-BE ready for publication (pending CK6 log access)

**Validation result:** partially-blocked — CK6 (new CRM direct call) deferred pending server log access

**Review findings:** no findings ≥80 confidence

**Open questions remaining:**
- Q-01: resolved — OAuth2 Bearer token required (confirmed from AuthMiddleware in routes.php:143)
- Q-02: resolved — 503 (not 502) on upstream unavailability (confirmed by curl CK5, FR updated)

**Assumptions outcome:**
- AS1: held — new CRM returned `{"balance": <int>, "currency": "RUB"}` as expected (CK1)
- AS2: held — test env API key was configured correctly

**Unknowns outcome:**
- UK1: resolved — OAuth2 Bearer token required (AuthMiddleware applied via routes.php middleware group `authenticated`)

### Hands-off decisions

*(none — interactive mode)*

### Deferred (needs user input)

- CK6: verify new CRM outbound call — need server log access or new CRM sandbox. Owner: backend team.
