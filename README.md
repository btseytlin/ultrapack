# ultrapack

Opinionated Claude Code skill pack for spec-driven, git-centered development.

## TL;DR

One command:

```
/up:make fix the flaky login test
```

Claude drives it through design → plan → execute → verify → review, writing every stage into `docs/tasks/<slug>.md`. The task file is the source of truth — any fresh agent can read it and resume from wherever the last one stopped.

Core ideas:
- **One task, one file.** `docs/tasks/<slug>.md` evolves through Design → Plan → Verify → Conclusion.
- **Invariants-first.** Discovered in design, obeyed in plan, verified during review.
- **Subagent independence.** Reviewers run in fresh contexts, never see change rationale.
- **Per-phase implementation.** Each plan phase dispatched to a fresh `up:implementer`.
- **Manual testing mandatory.** Agent must run what it built before claiming done.
- **Review is never skipped**, regardless of task size.
- **Fail fast, fail loud.** No silent fallbacks.

## Install

Add the repo as a marketplace and install the plugin:

```
/plugin marketplace add btseytlin/ultrapack
/plugin install up@ultrapack
```

Then `/reload-plugins`. Verify with `/up:make` or by listing skills.

## Design

Ultrapack is opinionated scaffolding for how Claude Code should handle non-trivial work. It merges the load-bearing parts of [obra/superpowers](https://github.com/obra/superpowers) and Anthropic's [feature-dev](https://github.com/anthropics/claude-code/tree/main/plugins/feature-dev), drops the rest, freezes the behavior. The result is a small set of skills, commands, and agents that implement one workflow — not a menu of options.

Every task produces exactly one markdown file at `docs/tasks/<slug>.md` with sections Design, Plan, Verify, Conclusion. Each stage is a skill; `/up:make` orchestrates them. If `/up:make` is invoked on a slug whose file already exists, it reads the `Status` header and resumes from the next stage — so a session can crash, be replaced, or be handed off without losing state.

Execution is per-phase subagent dispatch. `up:implementer` gets one phase of the plan, writes code + tests + commit, then returns. `up:uexecute` runs a plan-diff check and consistency sweep between phases. Verification builds a positive + negative + invariant checklist and loops back to execute on any failure. Review is never skipped: `up:reviewer` runs fresh, without session history or change rationale, so its verdict stays independent. The `up:` prefix on everything (`/up:make`, `up:udesign`, `up:reviewer`) keeps the whole surface discoverable at a glance.

## Details

### Skills

Process skills (u-prefixed to dodge Claude Code built-ins):
- `up:udesign` — Brainstorm requirements, populate Design + Invariants + Principles. Record TDD yes/no with reason.
- `up:uplan` — Concrete plan: files, line numbers, class/method names, invariants, test strategy, order. Ends with a scope/simpler-way check.
- `up:uexecute` — Dispatch `up:implementer` per phase, incremental commits, plan-diff + consistency sweep between phases.
- `up:uverify` — Positive + negative + invariant checklist, manual smoke test, writes summary to task file, loops back to execute on failure.
- `up:ureview` — Dispatch `up:reviewer`, process findings fairly, fill Conclusion.
- `up:udebug` — Four-phase root-cause investigation; no fixes without reproduction.
- `up:udocument` — Guidance for docs, CLAUDE.md, READMEs, in-code comments.

Discipline skills:
- `up:test-driven-development` — RED → GREEN → REFACTOR, only when the task qualifies.
- `up:git-worktrees` — Smart directory selection, safety verification.
- `up:handsoff` — Shared contract for hands-off mode (activated via `/up:make handsoff <description>`): safety principles, decision log, no-default rule, end-of-task summary. Referenced by `/up:make` and every process skill.

Removed in this release: `up:data-engineering`, `up:ml-experiments` — moved to user-level skills (they weren't spec-driven-dev scoped).

### Commands

- `/up:make <description>` — Orchestrate the full flow: slug → task file → design → branch → plan → execute → verify → review.
- `/up:try` — Design one positive and one negative test case, run both, report.
- `/up:step-back` — Circuit breaker: stop, diagnose why approaches failed, propose new direction.
- `/up:summary` — Produce a summary so another session can continue with zero context.
- `/up:reflect` — Reflect on the dialogue, extract learnings into CLAUDE.md / memory / docs.

### Agents

- `up:explorer` (Haiku 4.5) — Codebase tracing, file:line refs, 3–5 essential files.
- `up:implementer` (Sonnet 4.6) — One phase: code + tests + commit + self-review. Fresh context per phase.
- `up:reviewer` (Sonnet 4.6) — Independent review against Plan + Invariants. Confidence-filtered (≥80), severity-tiered.
- `up:researcher` (Sonnet 4.6) — General-purpose investigation: decompose + systematically answer.

## License

MIT
