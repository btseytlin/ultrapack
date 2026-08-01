---
description: Circuit breaker — stop, diagnose why attempts are failing, propose a fundamentally new direction before trying again.
---

Circuit breaker. Stop all current attempts — do not try another fix.

Follow these steps in order:

1. **State the real goal** — go back to what was originally asked for. Not "make this error go away" — the actual user-facing goal. One sentence.

2. **Trace the path** — list the last 3-5 things tried, briefly. For each, note what went wrong. Look for a pattern:
   - Are all failures related to the same root cause?
   - Are you fighting a library/framework not designed for this?
   - Did an early assumption turn out wrong?
   - Is the approach fundamentally incompatible with the codebase?

3. **Identify the core issue** — name the real blocker in one sentence. Common patterns:
   - "I assumed X but actually Y" (wrong mental model)
   - "This library doesn't support Z" (wrong tool)
   - "The architecture makes this hard because..." (need to change approach)
   - "I'm overcomplicating this — the simple solution is..." (overthinking)

4. **Propose a new direction** — fundamentally different, not a variation of what failed:
   - What the new approach is (one paragraph max)
   - Why it avoids the problems that blocked previous attempts
   - Any trade-offs or risks

Do NOT proceed until the user confirms the new direction. The whole point is to break the cycle.
