---
name: uverify
description: Use after execute to attack the change and demonstrate how it's broken. Default stance — the change is broken; prove and demonstrate it. Builds an attack checklist (happy-path / negative / invariant / interface hypotheses), runs each freshly, smokes the end-to-end, writes a short summary to the task file's Verify section, loops back to execute on any demonstrated break.
---

# Verify

Verify is the adversary. Default stance: the change is broken — prove and demonstrate it with running evidence in this message. Each check is a hypothesis about how the change bites; verify tries to make the bite land. Pass = honest attack produced no demonstrated break. Fail = break demonstrated, here's the evidence.

Verify's verdict either advances the workflow to `up:ureview` or bounces it back to `up:uexecute` with remediation notes. A short summary is persisted to the task file's `## Verify` section so review (and later readers) see what was attacked.

Steelman the critique: don't fish for cases that pass — fish for the case that would bite a future reader, on-call, or downstream user. If you didn't try to break it, you didn't verify it.

## Brevity

<required>
Before writing the Verify section, read `plugins/up/skills/_brevity.md`. Apply its five principles (omit / evidence-on-surprise / don't-re-narrate / one-sentence / soft-caps). Passed checks are one line; evidence citations attach to failures, deferrals, or genuinely surprising passes. Omit `Smoke:`, `Goal:`, and `Notes:` when there's nothing to report (`Goal:` only when a proxy stood in for the real run). The Exception clause still holds: failures always carry evidence and a clear "how it should have worked" note.
</required>

## Phase 1 — Build the attack list (happy-path, negative, invariant, interface)

Each CK is a hypothesis: a specific way the change might bite. Built from the Plan, IV / PC / AS from Design, plus your own adversarial reading — not imagined confirmations.

Checks are numbered CK1..CKN within the task file. Each one targets exactly one bite.

- Happy-path attack (CK): hypothesize the claimed happy path falls over for some input shape, env condition, ordering, or hidden state the author didn't consider. "POST /items: find a valid payload the handler mishandles (unicode name, max-length, concurrent submit, retried request)." Not "show it returns 201" — find the valid case where it doesn't.
- Negative attack (CK): hypothesize bad input slips past validation, gets silently coerced, or surfaces the wrong error. "POST /items: find a missing-field shape that bypasses validation (null, empty string, whitespace, type confusion, deeply nested)." Not "show it returns 400" — find the bad input that doesn't get rejected.
- Invariant attack (CK): hypothesize the IV is already violated, or trivially bypassable. Reference IV<n>. "IV1: hunt for `from training` in `src/dataset/`, and re-exports / dynamic imports that smuggle it in."
- Interface attack (CK): hypothesize the declared contract doesn't match real callers or real returns. Reference IF<n>. "IF1: find a caller passing the wrong type, or a return path that violates the declared signature (None on error, str instead of bytes)."

The attack list lives in-session. It is not written to the task file.

<good-example>
```
Happy-path:
- CK1 — POST /items: try unicode name, 10KB body, double-submit — find one that doesn't 201
- CK2 — Dataset.load("good.csv"): try LF vs CRLF, BOM, trailing newline — find a "good" file it mishandles

Negative:
- CK3 — POST /items: try {name: ""}, {name: null}, {name: "  "}, missing field entirely — find one that doesn't 400
- CK4 — Dataset.load: try missing file, directory, symlink to /dev/null, file with no read perms — find one that doesn't raise cleanly

Invariants / assumptions:
- CK5 (IV1) — grep "from training" src/dataset/ and re-export chains — try to find a smuggled import
- CK6 (IV2) — find a DB write that bypasses transaction() (raw cursor, ORM escape hatch)
- CK7 (AS1) — sample upstream /users — find a non-UTF-8 `email` in the wild

Interfaces:
- CK8 (IF1) — grep `Parser.parse` callers — find one passing non-str
- CK9 (IF2) — invoke Formatter.render with malformed AST — find a return that violates `-> str`
```
</good-example>

<bad-example>
"I'll test the happy path." Confirmation, not attack. No hypothesis of how it breaks.
</bad-example>

## Phase 2 — Run each attack freshly, in this message

Evidence before claims. If you haven't run the attack in this message, you cannot claim "no break demonstrated."

- Use `/up:try`-style minimal probes — the direct command, no harness
- One-off scripts go in project-local `tmp/` (gitignored); clean up after
- Capture *actual* output. "Looks right" is not evidence; a stack trace is.
- Decide on what you saw, not what you expected. A passed attack (you tried hard and couldn't break it) is a real outcome; so is a landed attack (you broke it — record the repro).

If an attack failed to land in an earlier session — re-run it. State drifts; what couldn't be broken yesterday may break today.

## Phase 3 — Smoke the end-to-end (lowest-bar attack)

The smoke is the most basic attack hypothesis: the change is broken enough that it doesn't even run end-to-end in its real shape.

Run the shortest full path:

- CLI change → invoke the command with representative input
- API change → `curl` against a running server
- UI change → open in a browser, click through the feature
- ML change → run a tiny training step or inference call

If smoke fails, that's a demonstrated break — record it. If smoke passes, the change clears the lowest bar; the per-attack hypotheses still need to land or fail to land on their own.

If you can't run the smoke (infra unavailable), say so explicitly. Do not fabricate success. Do not substitute a unit test for the smoke.

If the smoke only exercises a proxy for the Goal — a small or local stand-in for a full-scale or real-world run (converting 10 files when the Goal is 700GB on a pod) — say so: name what the proxy covered and what real-world validation still stands between here and the Goal. That gap is what `/up:make` step 11 hands to the user.

## Phase 4 — Write the Verify summary to the task file

<required>
Append (or replace) the `## Verify` section of `docs/tasks/<slug>.md`. Keep it short — this is not a transcript, it's an audit trail of what was attacked.

Per-CK verdict vocabulary:
- `held` — attack ran, no break demonstrated.
- `broke` — attack landed; evidence required (one line, real output).
- `deferred` — attack couldn't be run (infra, scope); name what blocks it.

Overall `Result:` is `passed` only if every CK is `held` (or justifiably `deferred` with user-visible deferral). Any `broke` → `failed`.

Format:

```markdown
## Verify

**Result:** passed | failed

Happy-path:
- CK1 — <attack hypothesis> — held
- CK2 — <attack hypothesis> — broke: <evidence>

Negative:
- CK3 — <attack hypothesis> — held

Invariants / assumptions:
- CK4 (IV1) — <attack hypothesis> — held: <how attacked>
- CK5 (AS1) — <attack hypothesis> — deferred: <what blocks>

Interfaces:
- CK6 (IF1) — <attack hypothesis> — held
- CK7 (IF2) — <attack hypothesis> — broke: <evidence>

Smoke: `<command>` → <one-line result>   (omit if not run; never substitute a non-smoke)

Goal: proxy only — <what the smoke covered, what real-world validation remains>   (omit when the smoke exercised the full Goal)

Notes: <break repros, deferrals, re-runs>   (omit if none)
```

Write this whether verify passed or failed. On failure, Notes names the demonstrated break(s) and points to where execute should pick up.
</required>

<good-example>
Fully-passing terse form (every attack held):
```markdown
## Verify

**Result:** passed

Happy-path:
- CK1 — unicode/long/double-submit POST /items — held
- CK2 — LF/CRLF/BOM variants of good.csv — held

Negative:
- CK3 — null/empty/whitespace/missing name on POST /items — held (all 400)
- CK4 — missing/dir/symlink-to-null inputs to Dataset.load — held (all raise)

Invariants / assumptions:
- CK5 (IV1) — grep + re-export sweep for `from training` in `src/dataset/` — held
- CK6 (IV2) — manual trace of write paths — held, all go through `transaction()`

Interfaces:
- CK7 (IF1) — caller-type sweep for `Dataset.load` — held
- CK8 (IF2) — malformed AST to Formatter.render — held (raises ValueError, doesn't violate `-> str`)

Smoke: `curl -X POST /items ... → 201` — end-to-end OK
```
</good-example>

<good-example>
Failing form (a break landed):
```markdown
## Verify

**Result:** failed

Negative:
- CK3 — null name on POST /items — broke: `{"name": null}` → 500 (TypeError in handler), not 400

Notes: validation layer doesn't reject `null` before the handler; should reject with 400 "name is required". Loop back to execute.
```
</good-example>

## Phase 5 — Consolidate: held loops to review, broke loops to execute

- Every attack held (or justifiably deferred) → declare verify passed. Invoke `up:ureview`.
- Any attack broke → for each, describe how it *should have* worked conceptually (not "add the missing line" — the behavior it was supposed to exhibit under the attack). Loop back to `up:uexecute` with these notes. Do not move forward.

<good-example>
Break note: "POST /items returned 500 instead of 400 when `name` was `null`. The validation layer should reject the payload with a 400 and a 'name is required' message before the handler runs, for null/empty/whitespace equally."
</good-example>

<bad-example>
Break note: "Attack landed, fix it." Tells execute nothing about what the behavior should be.
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
These phrases mean verify did not actually attack:
- "Just this once"
- "I'm confident it works"
- "Linter passed" (linter is not runtime)
- "Unit tests pass" (unit tests are not adversarial)
- "Agent said done" (you haven't tried to break it yourself)
- "Should work", "probably works", "looks correct"
- "Couldn't think of a way to break it" — without naming the angles you tried (input shapes, ordering, partial failure, stale state, hidden coupling)
</system-reminder>

If any of these was the basis of a pass verdict: back to Phase 1.

## Never

- Claim a CK held without running the attack in this message
- Declare pass when any attack broke
- Build the attack list as restatements of the happy path (no adversarial angle = not an attack)
- Skip verify to get to review faster
- Trust a prior session's verdict — re-run

## Hands-off mode

See `up:handsoff` for the full contract. Stage-specific delta: verify's behavior is unchanged — the pass → review / fail → execute loop already runs without user confirmation. Infeasible smoke tests (infra unavailable, etc.) are logged under `### Deferred (needs user input)` so the user knows what wasn't verified end-to-end. Never fabricate success to skip a deferred entry.

## Terminal state

Verify summary written to task file. Pass → invoke `up:ureview`. Fail → invoke `up:uexecute` with failure notes describing intended behavior.
