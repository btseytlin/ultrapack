---
name: udebug
description: Use when a curl response contradicts an FR claim, when an OpenAPI spec conflicts with running code, or on any technical discrepancy that needs root-cause investigation before the FR can be corrected.
---

# Debug

**Iron law:** no FR corrections without root-cause investigation first. Patching the symptom (changing a status code in the FR without understanding why it differs) is failure — the next endpoint will produce the same class of mismatch.

## Primary SA trigger

Curl from `up:uverify` returns something different from what the FR says. Before correcting the FR:

1. Determine whether the FR was wrong, the system is wrong, or the test data was wrong.
2. Trace back to the real source: OpenAPI spec, source code, DB schema.
3. Update the FR to reflect the confirmed truth — not the assumption.

## When to invoke

- Curl response (status code, body, field name) differs from FR claim
- OpenAPI spec entry contradicts actual endpoint behavior
- DB field mapping in FR doesn't match what the code actually reads/writes
- An open question (UK) is unexpectedly complex to resolve — needs systematic investigation

## Phase 1 — Reproduce the mismatch

You cannot fix what you cannot observe precisely.

<required>
1. State the mismatch in one sentence: "FR says POST /api/X returns 422 for missing email. Curl returns 400."
2. Confirm it's reproducible: run the curl again. Is it consistent? Different test data? Environment-specific?
3. Check recent changes — `git log` on the controller/service, recent OpenAPI spec changes.
4. Instrument the boundary: if the mismatch is in a DreamCRM call you can't observe directly, check logs or test the same DreamCRM endpoint directly.
</required>

## Phase 2 — Locate the authoritative source

Three possible causes, check in order:

1. **FR was written incorrectly** — claim doesn't match OpenAPI or code. Read the actual controller/service; correct the FR.
2. **Code doesn't match OpenAPI** — the spec says one thing, the implementation does another. This is a system bug, not an FR bug. Document both behaviors; flag the discrepancy as an open question.
3. **Test data or environment issue** — the curl hit a different state (wrong user, wrong env, rate-limited). Fix the test setup; re-run before concluding.

<required>
For each mismatch, trace to the actual code path:
- Find the controller method handling the endpoint
- Find the exact return statement or error throw for the observed status
- Find which DB field or external API response drove that return
</required>

## Phase 3 — Single hypothesis, minimal re-test

<required>
1. Write one hypothesis: "The controller returns 400 (not 422) because the validation layer uses a generic bad-request handler, not a field-specific validator."
2. Verify with a targeted curl or code read — one change in test data or one read of the specific code path.
3. Confirmed → Phase 4. Not confirmed → new hypothesis.
</required>

## Phase 4 — Correct the right artifact

Now and only now do you change something.

<required>
- If the FR was wrong: correct the FR. Cite the code path or OpenAPI entry that proves the correction.
- If the code doesn't match the OpenAPI spec: add an open question to the FR. Don't guess which is authoritative — escalate.
- If test data was wrong: re-run `up:uverify` with corrected data. Do not mark the original check as passed.
</required>

## Anti-whack-a-mole — find the pattern before closing

One mismatch is rarely alone. Before closing:
- Name the pattern in one sentence: "field validation returns 400, not 422, across all endpoints in this controller."
- Grep the FR documents for the same status code claim. Correct all instances in one pass.

## Red flags — STOP, return to Phase 1

<system-reminder>
- "The OpenAPI spec says so, the FR is correct" (OpenAPI ≠ running system)
- "I'll just change the status code in the FR" (without finding the code path)
- "It's probably an environment issue" (without a second curl to confirm)
- "The behavior is obvious from context" (obvious behavior has a traceable source)
</system-reminder>

## Terminal state

Mismatch traced to root cause. Correct artifact updated (FR, or open question logged). Return to `up:uverify` to re-run the affected checks.
