# ultrapack

Ultrapack or `/up:` is an opinionated Claude Code skill pack for developers: plan-driven, git-centered, minimalistic. Built around frequently clearing context and using one conversation for one feature. 

## TL;DR

```
/up:make fix the flaky login test
```

Will take you through the process: design → plan → execute → verify → review → update docs.

Each stage populates `docs/tasks/<slug>.md`. The task file is the source of truth — any fresh agent can read it and resume from wherever the last one stopped.


```
/up:make handsoff fix the flaky login test
```

Same, but ask you as few questions as possible. 

While you are not looking, the agent will pick the safest and most conservative choices: don't delete things (copy and rename instead), work in a git branch, don't introduce silent defaults and fallbacks, fix only critical and important issues. 

Core ideas:
- One file per task. `docs/tasks/<slug>.md` evolves through Design → Plan → Verify → Conclusion.
- Invariants-, principles-, and assumptions-first. Discovered in design, obeyed in plan, checked at review. Short IDs (IV, PC, AS, UK, PH, RK, CK) let later sections reference them without re-quoting.
- Per-phase subagent implementation. Each plan phase dispatched to a fresh `up:implementer`. Plan declares interfaces (`### Interfaces`) and an execution graph (`### Interface graph`); the executor topo-sorts it into waves and dispatches independent phases in parallel.
- Mandatory manual testing. Agent must run what it built before claiming done.
- As short as I could make it, doesn't waste tokens.

## Install

Add the repo as a marketplace and install the plugin:

```
/plugin marketplace add btseytlin/ultrapack
/plugin install up@ultrapack
```

Then `/reload-plugins`. Verify with `/up:make` or by listing skills.

## Design

Ultrapack is a small set of skills, commands, and agents to help Claude Code handle non-trivial work. 

Inspired by [feature-dev](https://github.com/anthropics/claude-code/tree/main/plugins/feature-dev) and [obra/superpowers](https://github.com/obra/superpowers). [feature-dev](https://github.com/anthropics/claude-code/tree/main/plugins/feature-dev) is too barebones. [obra/superpowers](https://github.com/obra/superpowers) is great, but creates huge plans with a lot of work duplication, changes too frequently and is geared to a specific type of dev work. Also it's a chore to type "superpowers" every time.

Ultrapack is the best of both, shortened and simplified. The whole workflow is built around updating one markdown file per task `docs/tasks/<slug>.md` with sections Design, Plan, Verify, Conclusion. It's also git centered: use worktrees by default for easier parallel work, incremental commits for easier rollback and review.

Each stage of task planning and execution is a skill. `/up:make` is a helper command that orchestrates the whole flow. 

`up:udesign` is the first stage: discuss trade-offs with the user, discover invariants (specific things that must hold, e.g. "class Player must not access internals of class Enemy"), principles (softer guidance, like "prefer composition over inheritance"), assumptions (unverified premises the design rests on — the Conclusion reports whether each held), and unknowns (open questions to resolve during plan/execute). Prepare initial spec in the task file.

`up:uplan` populate the task file with a specific plan. Define what files to change, what classes and methods to update or create, what interfaces they will have, what is the test strategy, break down into phases, define order of execution. No code blocks here unless they are especially tricky. 

`up:uexecute` create git branch and worktree, dispatch independent `up:implementer` agents per plan phase, make incremental commits, check against plan and design between phases. When the plan declares `### Interface graph`, the executor topo-sorts the graph into waves; phases in the same wave are dispatched in parallel (implementers stage changes, dispatcher commits serially in phase order). After each phase's commit: Boundary check (diff ⊆ declared `@` paths). After the final wave: Wiring check (per-IF caller/anchor match). Uses TDD for tasks where it's helpful.

`up:uverify` performs manual smoke testing, defining a checklist of fast positive (what should work) and negative (what should not work) checks based on invariants. Writes summary to task file. Loops back to execute on failure. 

`up:ureview` dispatches an independent `up:reviewer` subagent that knows the design, plan, and changes. It doesn't know the implementer's rationale. In the end it's an independent review: check that all invariants from design and plan still hold and find bugs. 

Finally, the conclusion section of the task markdown file is populated. Then all documentation of the project is updated.

## Details

### Skills

Process skills (u-prefixed to dodge Claude Code built-ins):
- `up:udesign` — Brainstorm requirements, populate Design + Invariants + Principles + Assumptions + Unknowns, decide whether to use TDD.
- `up:uplan` — Plan: what files to change, what class/methods and with what interfaces, test strategy, order. Only non-trivial code blocks.
- `up:uexecute` — Dispatch `up:implementer` per phase (parallel waves derived from `### Interface graph`), incremental commits, Boundary + plan-diff + consistency sweep per phase, Wiring check after the final wave.
- `up:uverify` — Positive + negative + invariant checklist, manual smoke test, writes summary to task file, loops back to execute on failure.
- `up:ureview` — Dispatch `up:reviewer` subagent: independent review, check that all invariants from design and plan still hold.
- `up:udebug` — Four-phase root-cause investigation.
- `up:udocument` — Guidance for updating docs, CLAUDE.md, READMEs, in-code comments.

Discipline skills:
- `up:test-driven-development` — write failing test → make change → test passes.
- `up:git-worktrees` — guidance for using git worktrees.
- `up:handsoff` — Shared contract for hands-off mode (activated via `/up:make handsoff <description>`): safety principles, decision log, no-default rule, end-of-task summary. Referenced by `/up:make` and every process skill.

### Commands

- `/up:make [handsoff] <description>` — Orchestrate the full flow: task file → design → branch → plan → execute → verify → review → update docs.
- `/up:try` — Design one positive and one negative test case, run both, report.
- `/up:step-back` — Circuit breaker: stop, diagnose why approaches failed, propose new direction.
- `/up:summary` — Produce a summary so another session can continue with zero context.
- `/up:reflect` — Reflect on the dialogue, extract learnings into CLAUDE.md / memory / docs.

### Agents

- `up:explorer` (Haiku 4.5) — Codebase tracing, file:line refs, 3–5 essential files.
- `up:implementer` (Sonnet 4.6) — One phase: code + tests + commit + self-review. Receives `Owns` / `Implements` / `Consumes` from the plan's interface graph. `commit: self|defer` mode; defer stages only and the dispatcher commits (used in parallel waves). Fresh context per dispatch.
- `up:reviewer` (Sonnet 4.6) — Independent review against Plan + Invariants + Assumptions. Confidence-filtered (≥80), severity-tiered.
- `up:researcher` (Sonnet 4.6) — General-purpose investigation: decompose + systematically answer.
- `up:summarizer` (Sonnet 4.6) — Drafts the handoff prose for `/up:summary`; gathers repo state, never writes to disk.

## License

WTFPL — see [license.txt](license.txt).
