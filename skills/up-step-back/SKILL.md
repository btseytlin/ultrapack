---
name: up-step-back
description: Break a failed implementation loop by tracing attempts, identifying the real blocker, and proposing a materially different direction before further changes. Use when repeated fixes or investigations are not converging.
---

# Circuit breaker

Stop the current approach. Do not make another fix until the user confirms a new direction.

1. State the user-facing goal in one sentence.
2. List the last three to five attempts and what failed in each.
3. Name the common root issue in one sentence: an invalid assumption, unsupported capability, architectural constraint, or needless complexity.
4. Propose a genuinely different approach, why it avoids the blocker, and its risks or trade-offs.
