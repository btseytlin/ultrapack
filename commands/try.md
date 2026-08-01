---
description: Manually test the latest change with one positive and one negative case. Goal is speed — shortest path to confidence.
---

Manually test the latest change. Goal is speed — shortest path to confidence.

Steps:
1. Identify the change: check recent conversation context, `git status`. 
2. Design exactly two test cases:
   - **Positive**: happy path, realistic minimal input
   - **Negative**: should fail/be rejected — most likely misuse or edge case
3. Run both tests. Capture output as evidence.
4. If either fails unexpectedly, stop and report before attempting fixes.

Report format:
```
Pos: [PASS/FAIL] — <what happened>
Neg: [PASS/FAIL] — <what happened>
```

Rules:
- Pick the fastest ways to test. 
- Designing the test aim to break. Don't go easy on it.
- If both pass, the change is verified.
