---
name: test-driven-development
description: Use when implementing deterministic, reusable code where regressions would warrant a CI red light. Enforces RED-GREEN-REFACTOR. Applicability rule and skip conditions inside.
---

# Test-Driven Development

Write the test first. Watch it fail. Write minimal code to pass. Refactor. Repeat.

**Core principle:** if you didn't watch the test fail, you don't know whether it tests the right thing.

## Applicability — invoke only when all three hold

<applies-when>
1. The code produces specific outputs for specific inputs (deterministic I/O contract)
2. It is called from more than one place (library code, API method, utility, validator)
3. A regression here would warrant a CI red light
</applies-when>

## Skip conditions — do not invoke when any holds

<skip-when>
- Training a model, hyperparameter tuning, anything stochastic with no "correct" output
- Exploratory data analysis (you're figuring out what's in the data)
- One-off scripts or throwaway prototypes
- Research / experiment code
- UI changes where the real test is "does it look right"
</skip-when>

The decision is recorded during `up:udesign` as `TDD: yes` or `TDD: no (reason)`.

## Iron law when applicable — no production code without a failing test first

Wrote code before the test? Delete it. Start over from the test. Don't "adapt" what you wrote — the test will be shaped by the code instead of shaping it.

## Phase 1 — RED: write a failing test

- One behavior per test
- Clear name describing the behavior
- Real code path where possible; mocks only when genuinely unavoidable

```python
def test_retry_succeeds_after_two_failures():
    attempts = 0
    def op():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("fail")
        return "success"
    assert retry(op, max_attempts=3) == "success"
    assert attempts == 3
```

## Phase 2 — Verify RED: run it, confirm it fails for the right reason

<required>
- It fails (not an import/syntax error)
- The failure reason is "feature missing", not a typo
- The error message matches what you expected
</required>

Test passed immediately? You're testing behavior that already exists. Fix the test.

## Phase 3 — GREEN: minimal code to pass

```python
def retry(op, max_attempts):
    for i in range(max_attempts):
        try:
            return op()
        except Exception:
            if i == max_attempts - 1:
                raise
    raise RuntimeError("unreachable")
```

Don't add features, options, or "while I'm here" changes. Just pass the test.

## Phase 4 — Verify GREEN: run it, confirm it passes, nothing else broke

Run the new test and the existing suite. If either fails: back to GREEN (not RED — don't change the test).

## Phase 5 — REFACTOR: clean up with tests green

Names, duplication, helpers. Keep tests green. Don't add behavior in this step. Then loop back to RED for the next test.

## Good tests

<good-test>
- Minimal — one behavior per test. If "and" appears in the name, split.
- Clear — name describes what it checks.
- Real — exercises actual code, not mocks pretending to be code.
</good-test>

## Red flags — stop and start over

<system-reminder>
- You wrote code before the test
- A test passes immediately on first run
- You can't explain why a test failed the way it did
- You're keeping old code "as reference" while writing tests — delete it
- You're "adapting" existing code while writing tests — that's tests-after, not TDD
</system-reminder>

## Why order matters

Tests-after answer: *what does this do?*
Tests-first answer: *what should this do?*

They are not the same. Tests-after are biased by the implementation you already wrote. Tests-first force edge-case discovery before you commit to a design.

## When stuck

- Don't know how to test: write the wished-for API in the test first; let it drive the implementation shape
- Test is too complicated: the interface is too complicated; simplify it
- Must mock everything: the code is too coupled; use dependency injection
- Huge setup: extract helpers; if it stays huge, the design is wrong

## For bug fixes

Write a failing test that reproduces the bug. Then RED-GREEN-REFACTOR. The test proves the fix and prevents regression.

## Final rule

```
Production code → a test exists and was written first and failed first
Otherwise → not TDD
```
