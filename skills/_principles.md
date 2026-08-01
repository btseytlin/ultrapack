# Global Principles

GPC1–GPC8. Apply to every task unless clearly irrelevant. Deviations name the GPC and the reason in one line.

- **GPC1 — Explicit interfaces, no defaults, no hidden config.** Caller passes every argument. Each constant / config / magic value is defined in exactly one place and threaded explicitly to its use site. No reading config behind the caller's back.
- **GPC2 — One concern per unit.** One responsibility per function, class, file. Functions >~10 lines are a smell — split unless justified. Error handling is its own concern. Short files/classes follow from short functions; goal is fewer concerns per unit, not fewer symbols. Code reads top-to-bottom like prose.
- **GPC3 — Query/command separation.** A function either does something or returns something, never both.
- **GPC4 — Single source of truth + boundaries.** If a value is used across train + eval + inference, it lives in the model config — saved on train, loaded on eval, never redefined in a second code path. Layering is explicit: declare what can import what (e.g. `Dataset` must not import `training/`). Cross-boundary leaks are a design bug, not a style nit.
- **GPC5 — Idempotent, atomic, observable writes.** Anything that writes to disk, DB, or a checkpoint must be re-runnable without corruption: write-to-temp-then-rename, transactional or retriable. Log inputs/outputs at seams (entry/exit of each unit), not inside hot loops — seams are what you grep when things break.
- **GPC6 — Fail fast, fewest moving parts.** Crash loud on unexpected state — no silent fallbacks, no defaulted-to-zero metrics. Parkinson's law: whatever can break will. Prefer the plan with fewer components, fewer code paths, fewer places a future bug can hide. Prefer reversible changes over clever ones.
- **GPC7 — Plan for debugging.** Assume every new piece of functionality will need to be debugged. Design it so future-you can diagnose without a rewrite: structured logs at seams, meaningful IDs threaded through (request id, run id, sample id), state-transition logging for long-running processes, deterministic-where-possible execution, and a way to reproduce a single failing case in isolation. "We'll add logging when it breaks" means you'll add logging in production at 2am.
- **GPC8 — DRY, reuse first.** Before writing new code, search for existing helpers, utilities, or patterns that already solve it — extend or call them rather than parallel-implementing. Duplicated logic across two call sites is a smell; three is a bug. Reuse wins over re-creation; the exception is when reuse would force a premature abstraction that mixes concerns (then prefer explicit over DRY per GPC2).

## Incidental code smells

While exploring code for a task you'll pass smells unrelated to the change — a 200-line function, a duplicated helper, a leaked layer boundary. Two outcomes, no third:

- In task scope, or a genuinely easy and low-risk win → fix it (Boy-Scout rule, GPC2/GPC8). The fix lands in the diff; nothing to record.
- Out of scope and non-trivial — a wide rename, a risky refactor, a new test surface → don't balloon the task. Record it, one line, in the task file's `## Code smells` section:

  `- <file:line> — <smell, one sentence> (<GPC it offends, if one fits>)`

A pointer plus a sentence; the next reader opens the line. Recorded smells are `Future work` candidates decided at review — recording one does not authorize fixing it now.

## How to use

- `up:udesign` — surface GPC tradeoffs (layering, SSOT, fail-fast, debuggability) as Design decisions; reference by ID. Task-specific PCs only when deviating from a GPC or adding a rule the GPCs don't cover.
- `up:uplan` — every phase consistent with GPCs; deviating bullets cite the GPC and why.
- `up:udebug` — anti-whack-a-mole: name the pattern behind a bug and grep for the same shape before closing (not a GPC, same family).
- Incidental code smells — `up:udesign` / `up:uplan` fold an in-scope or easy fix into the design/plan, else record to `## Code smells`; `up:uexecute` fixes in-scope/easy ones, records the rest; `up:explorer` / `up:implementer` report passed smells in their output for the dispatcher to act on.
