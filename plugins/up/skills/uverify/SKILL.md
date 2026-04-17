---
name: uverify
description: Use after execute to confirm the change actually works end-to-end. Builds a positive + negative + invariant checklist, runs each check freshly, does a manual smoke test, writes a short summary to the task file's Verify section, loops back to execute on any failure.
---

# Verify

Confirm the change actually works — not "looks right", not "tests probably pass", but *verified by running the thing in this message*. Verify's verdict either advances the workflow to `up:ureview` or bounces it back to `up:uexecute` with remediation notes. A short summary is persisted to the task file's `## Verify` section so review (and later readers) see what was checked.

## Brevity

<required>
Before writing the Verify section, read `plugins/up/skills/_brevity.md`. Apply its five principles (omit / evidence-on-surprise / don't-re-narrate / one-sentence / soft-caps). Passed checks are one line; evidence citations attach to failures, deferrals, or genuinely surprising passes. Omit `Smoke:` and `Notes:` when there's nothing to report. The Exception clause still holds: failures always carry evidence and a clear "how it should have worked" note.
</required>

## Phase 1 — Build the checklist (positive, negative, invariant)

The checklist enumerates every behavior you'll actually run. Built from the Plan, Invariants, and Design, not imagined.

- Positive checks: "POST /items returns 201 for a valid payload." "`Dataset.load()` reads the file and returns the expected schema." Specific inputs → specific expected outputs.
- Negative checks: "POST /items returns 400 for missing fields." "`Dataset.load()` raises on a missing file." Things that must still fail correctly.
- Invariant checks: one check per Design invariant. "`Dataset` does not import from `training/`" → a grep that must return nothing.

The checklist lives in-session. It is not written to the task file.

<good-example>
```
Positive:
- POST /items {valid} → 201, body contains new id
- Dataset.load("good.csv") → DataFrame with 3 columns

Negative:
- POST /items {missing name} → 400, "name is required"
- Dataset.load("nope.csv") → FileNotFoundError

Invariants:
- grep "from training" src/dataset/ → empty
- all DB writes go through transaction() helper → manual trace
```
</good-example>

<bad-example>
"I'll test the happy path." Too vague. No negatives, no invariants, no specific inputs or expected outputs.
</bad-example>

## Phase 2 — Run each check freshly, in this message

Evidence before claims. If you haven't run it in this message, you cannot claim it passes.

- Use `/up:try`-style minimal verification — the direct command, no harness
- One-off scripts go in project-local `tmp/` (gitignored); clean up after
- Capture *actual* output. "Looks right" is not evidence.
- Decide pass/fail on what you saw, not what you expected

If a check passed in an earlier session or an earlier message — re-run it now. State does drift.

## Phase 3 — Manual smoke test end-to-end

Run the shortest full path that exercises the change in its real shape:

- CLI change → invoke the command with representative input
- API change → `curl` against a running server
- UI change → open in a browser, click through the feature
- ML change → run a tiny training step or inference call

If you can't run the smoke test (e.g. infra unavailable), say so explicitly. Do not fabricate success. Do not substitute a unit test for the smoke test.

## Phase 4 — Write the Verify summary to the task file

<required>
Append (or replace) the `## Verify` section of `docs/tasks/<slug>.md`. Keep it short — this is not a transcript, it's an audit trail.

Format:

```markdown
## Verify

**Result:** passed | failed

Positive:
- <check>                         (evidence only on fail or surprise)
- <check> → <evidence>            (failure: required)

Negative:
- <check>

Invariants:
- <invariant>

Smoke: `<command>` → <one-line result>   (omit if no smoke test run or nothing to report)

Notes: <anomalies, re-runs, deferrals>   (omit if none)
```

Write this whether verify passed or failed. On failure, the Notes section names what failed and points to where execute should pick up.
</required>

<good-example>
Fully-passing terse form:
```markdown
## Verify

**Result:** passed

Positive:
- POST /items {valid} → 201 with new id
- Dataset.load("good.csv") → 3-column DataFrame

Negative:
- POST /items {missing name} → 400
- Dataset.load("nope.csv") → FileNotFoundError

Invariants:
- `Dataset` does not import from `training/`
- all DB writes go through `transaction()`

Smoke: `curl -X POST /items ... → 201` — end-to-end OK
```
No `Notes:` (nothing anomalous), no evidence padding on passes.
</good-example>

## Phase 5 — Consolidate: pass loops to review, fail loops to execute

- All checks passed → declare verify passed. Invoke `up:ureview`.
- Any check failed → for each failure, describe how it *should have* worked conceptually (not "add the missing line" — the behavior it was supposed to exhibit). Loop back to `up:uexecute` with these notes. Do not move forward.

<good-example>
Failure note: "POST /items returned 500 instead of 400 for a missing `name`. The validation layer should reject the payload with a 400 and a 'name is required' message before the handler runs."
</good-example>

<bad-example>
Failure note: "Test failed, fix it." Tells execute nothing about what the behavior should be.
</bad-example>

## Future Work vs. incomplete work — the slacking-loophole rule

When a check fails or surfaces ambiguity, do not move it to `## Conclusion → Future Work` unless you have justification.

<required>
- In-scope = do it. If the plan mandated it, it's not future work. Complete it, or explicitly rescope with user consent.
- Justification required. Future Work needs a pointer to (a) a Design-scope line that excludes it, or (b) a new fact discovered mid-execution that changes scope. Hand-waving doesn't count.
- Out-of-scope but related? Fine — add to Future Work with justification, keep verifying the rest.
</required>

## Red flags — STOP, do not claim pass

<system-reminder>
These phrases mean verify did not actually happen:
- "Just this once"
- "I'm confident it works"
- "Linter passed" (linter is not runtime)
- "Unit tests pass" (unit tests are not smoke tests)
- "Agent said done" (you haven't verified the diff yourself)
- "Should work", "probably works", "looks correct"
</system-reminder>

If you used any of those as the basis of a pass verdict: back to Phase 1.

## Never

- Claim pass without running the check in this message
- Declare pass when any check failed
- Skip verify to get to review faster
- Trust a prior session's verdict — re-run

## Hands-off mode

See `up:handsoff` for the full contract. Stage-specific delta: verify's behavior is unchanged — the pass → review / fail → execute loop already runs without user confirmation. Infeasible smoke tests (infra unavailable, etc.) are logged under `### Deferred (needs user input)` so the user knows what wasn't verified end-to-end. Never fabricate success to skip a deferred entry.

## Terminal state

Verify summary written to task file. Pass → invoke `up:ureview`. Fail → invoke `up:uexecute` with failure notes describing intended behavior.
