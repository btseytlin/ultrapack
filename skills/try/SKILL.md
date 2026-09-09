---
name: try
description: Manually test the latest change with one realistic positive case and one adversarial negative case, capturing evidence before any further fix. Use when the user asks for a quick confidence check or wants to test a recent implementation.
---

# Fast manual test

Use this as the Codex and Pi equivalent of `/up:try`.

1. Identify the latest relevant change from the conversation and `git status`.
2. Design exactly two fast probes: one realistic happy path and one likely misuse or edge case that should fail or be rejected.
3. Run both and capture their actual output. Do not fix unexpected failures before reporting them.
4. Report exactly:

```
Pos: [PASS/FAIL] — <what happened>
Neg: [PASS/FAIL] — <what happened>
```
