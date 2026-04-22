---
name: udebug
description: Use on any bug, test failure, or unexpected behavior before proposing a fix. Enforces four-phase root-cause investigation — reproduce, pattern-match, hypothesize, fix — with a hard rule against symptom patches.
---

# Debug

**Iron law:** no fixes without root-cause investigation first. Symptom patches are failure.

## When to invoke

Any technical issue: test failure, production bug, unexpected behavior, performance regression, build break, integration failure. Especially when:
- Under time pressure (makes guessing tempting)
- You already tried 1+ fixes
- The problem "seems simple" (simple-looking bugs still have root causes)

## Phase 1 — Reproduce the problem and trace the data

You cannot fix what you cannot observe. Start by making the bug happen on demand, then follow the bad value back to where it came from.

<required>
1. Read the error completely — stack trace, file, line, error codes. No skimming.
2. Reproduce it — exact steps. Every time? Sometimes? If you can't reproduce: gather more data, don't guess.
3. Check recent changes — `git diff`, recent commits, new deps, config drift, env differences.
4. Instrument component boundaries (multi-component systems) — log what enters and exits each boundary, run once to see *where* it breaks before deciding *what* to fix.
5. Trace data flow backward — where does the bad value originate? What called this with the bad value? Keep tracing up until you find the source. Fix at source, not symptom.
</required>

## Phase 2 — Pattern analysis against a working example

Bugs rarely occur in isolation. Find similar code that works, understand *why* it works, then enumerate every difference.

<required>
1. Find working examples in the same codebase. What works that's similar?
2. Read reference implementations completely — don't skim, don't adapt something you didn't fully understand.
3. List every difference between working and broken. Don't assume "that can't matter."
4. Enumerate dependencies and assumptions — configs, env vars, adjacent components.
</required>

## Phase 3 — Single hypothesis, minimal test

One cause at a time. Stacked guesses turn fixes into guesses about guesses.

<required>
1. Form a single hypothesis. Write it: "I think X is the root cause because Y."
2. Test minimally — smallest possible change. One variable at a time.
3. Verify or discard. Confirmed → Phase 4. Not confirmed → new hypothesis.
4. If you don't know, say so. Research, ask. Don't pretend.
</required>

## Phase 4 — Implement one fix, verify, stop at three failed attempts

Now and only now do you change production code.

<required>
1. Create a failing reproduction — automated test if possible; one-off script in `tmp/` otherwise. Must fail *now*.
2. Implement one fix — root cause only. No "while I'm here" refactors.
3. Verify — reproduction passes; nothing else broke.
4. If three fixes have failed, stop. This is an architecture problem, not a hypothesis problem. Discuss with the user before a fourth attempt.
</required>

## Condition-based waiting — never use `sleep(N)` for timing bugs

A sleep that "seems long enough" is a bomb on a fuse. Poll for the actual condition with a bounded timeout:

```python
deadline = time.time() + timeout
while time.time() < deadline:
    if condition():
        break
    time.sleep(0.1)
else:
    raise TimeoutError(f"condition not met in {timeout}s")
```

## Defense in depth — validate one or two layers past the fix

Once the root cause is fixed, add validation at the next layer so the same class of bug can't re-enter silently:

- Validate inputs at component boundaries
- Crash loudly on contract violations
- Log state transitions in long-running processes

Don't scatter defensive code everywhere. One or two layers past the fix is enough.

## Anti-whack-a-mole — find the pattern before closing

One bug is rarely alone. Before marking the fix done, name the pattern behind it in one sentence and grep the rest of the code for the same shape. Report matches: fix the trivial ones in the same commit, file follow-ups for the rest. Closing without this check is how the same bug ships three more times in three more places.

## Red flags — STOP, return to Phase 1

<system-reminder>
These thoughts mean you're about to patch a symptom:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that"
- "Pattern says X but I'll adapt it differently"
- Proposing solutions before tracing data flow
- "One more attempt" when 2+ have already failed
</system-reminder>

## When root cause really is environmental

After systematic investigation, if the issue is timing, external, or truly non-deterministic:
- Document what you investigated
- Implement appropriate handling (retry, timeout with condition polling, loud error)
- Add logging / monitoring for future occurrences

But 95% of "no root cause" verdicts are incomplete investigations. Double-check before settling for this.

## Terminal state

Fix verified with reproduction → return to `up:uverify` if in a task workflow, or commit and move on.
