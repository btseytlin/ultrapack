---
name: uexecute
description: Use to implement an approved plan. Dispatches the up:implementer agent per phase on Sonnet 4.6. Runs plan-diff check and consistency sweep after each phase. Forbids silent fallbacks and mutation of external spec/design docs. Dispatches the planner skill when deviations invalidate the plan.
---

# Execute

Implement the approved `## Plan` from `docs/tasks/<slug>.md`. You are the dispatcher — each phase is handed to a fresh `up:implementer` subagent. After each phase returns, you run the plan-diff check and consistency pass before moving on. The goal is a working change that honors Design and Plan.

## Before starting

<required>
1. Read the full task file — Design, Invariants, Principles, Plan. Plan is not optional reading.
2. Scan the plan for ambiguity, missing dependencies, or contradictory steps. Raise now, not after writing half the code.
3. Verify branch + worktree. Check `git rev-parse --show-toplevel` and `git branch --show-current` match the task file's `**Branch:**` and `**Worktree:**` headers. If mismatched: stop and ask.
4. Build the checklist — one todo per plan phase (or per task if phases are coarse). Use TodoWrite.
</required>

## Branch / worktree correctness

<system-reminder>
Editing the wrong repository is one of the most common bugs. Before any write, confirm:

- `pwd` matches the task file's `**Worktree:**` (or the main repo if `none`)
- `git branch --show-current` matches `**Branch:**`

When you dispatch a subagent (`up:explorer`, `up:researcher`), pass the intended working directory explicitly in the prompt. Subagents do not inherit your `cwd` reliably across harnesses.
</system-reminder>

## Per-phase loop

For each phase in the plan:

<required>
1. Mark the phase `in_progress` in TodoWrite.
2. Dispatch the `up:implementer` agent with the phase text + invariants + principles + working directory + TDD decision (see "Dispatch per phase" below).
3. On implementer return, handle status:
   - `DONE` → continue to step 4.
   - `DONE_WITH_CONCERNS` → read the concerns. Resolve or record them, then continue.
   - `NEEDS_CONTEXT` → supply missing context, re-dispatch.
   - `BLOCKED` → diagnose. If the plan is wrong, invoke `up:uplan`. If context-only, re-dispatch. Do not retry identically.
4. **Plan-diff check.** Read the phase's commit (`git show <sha>`). For every plan bullet in this phase: is it reflected in the diff? For every change in the diff: is it covered by a bullet, or by a deviation the implementer reported? Any unreported structural gap → record as a deviation, or re-dispatch with correction.
5. **Consistency pass.** If the implementer tightened a rule, renamed a symbol, or changed a pattern in one spot, grep the diff and the wider repo for the same pattern. Apply the same change everywhere. If the implementer already did this (their self-review requires it), confirm and move on. If they missed siblings, either re-dispatch or fix inline and amend.
6. Mark the phase `completed`.
</required>

Do not batch phases. One at a time. Commits give you a rollback surface and a legible history.

## Dispatch per phase

Each phase runs in a fresh `up:implementer` subagent (Sonnet 4.6). You (the dispatcher, on Opus) coordinate.

<required>
**Pass in the dispatch prompt:**
- Full verbatim text of the phase from `## Plan`
- `### Invariants` and `### Principles` from `## Design`
- TDD decision (from Design — `yes` or `no (reason)`)
- Absolute working directory (subagents do not inherit `cwd` reliably across harnesses)
- Expected git branch (from task file `**Branch:**` header)

**Do not pass:**
- Session history or prior-phase chatter
- The full task file (pass only the sections above)
- Later phases (keep the implementer scoped to one phase)
- Rationale behind design decisions — the plan is the contract
</required>

**When to skip dispatch and do it inline:**
- Trivial phase (typo, one-line import fix, changelog edit)
- Phase needs mid-work interactive user input
- A phase-N-and-N+1 fix follows from review findings, small enough to just edit

**Parallel dispatch:**
Phases are normally sequential (phase 2 imports what phase 1 created). Only dispatch two implementers in parallel when the phases touch disjoint files and have no import/data dependencies. When in doubt, sequential.

## TDD

If Design recorded `TDD: yes`, invoke `up:test-driven-development` for each unit under test:

- Write the failing test, watch it fail for the right reason
- Write the minimal implementation to pass
- Refactor with tests green
- Commit

If `TDD: no`, skip the test-first loop; verification happens in `up:uverify`.

## When to dispatch `up:explorer`

- The implementer reported `NEEDS_CONTEXT` and a code map would unblock them
- You need a call graph or execution path beyond what a quick Grep gives
- You need a ranked list of essential files for a feature

Dispatch with tight scope and pass the working directory explicitly. Don't over-use — inline Grep/Read beats a subagent for one-shot lookups.

## Consistency pass — when changing a pattern, sweep for others

<required>
Any time you (or the implementer) change how code handles a pattern — tightening a fallback, renaming a symbol, adding a guard, flipping a default — grep the diff and the wider repo for the same pattern. Skim `git log -p` for the commit that introduced it, in case siblings were added the same way. Apply the change everywhere in the same commit.

The reviewer's job is to catch what you missed. Your job is to minimize what you miss.
</required>

<good-example>
Implementer made `compute_at_k_cursor_l2` raise on empty input to honor "no silent fallbacks". Before the commit lands, grep the diff for sibling metrics (`cursor_l2@L`, `click_f1@L`, `cursor_std_*`) and tighten those the same way, or flag them as deferred with justification.
</good-example>

<bad-example>
Fix one spot, commit, reviewer finds four more siblings, two rounds of fixups, noisier history, tighter-in-some-places-not-others inconsistency in the file.
</bad-example>

## Don't modify upstream specs or external design docs

<required>
The plan is the contract. External spec files (e.g. `docs/superpowers/specs/*.md`) are inputs — read-only during execute. If the implementer finds the spec is wrong, they report it and stop. You (the dispatcher) surface it to the user. The user decides whether to update the spec, revise the plan, or continue with a deviation.

Never edit the plan inline to hide a deviation. Never silently edit an external spec. Deviations live in the task file's `## Conclusion → Deviations from plan` section.
</required>

## Forbidden: inventing fallbacks, defaults, or best-effort behavior

<system-reminder>
No silent fallbacks. No invented defaults. No "best effort" try/except that swallows the error. If you're tempted to write `.get("attr", 0)` and zero is not a genuine, intended default — don't. Crash > corrupt state.

Never add `try: ... except: pass`. Never catch a broad exception to "keep going". Never substitute a placeholder value so the code "works for now".

If the plan is silent on what to do when X is missing, the answer is: let it raise. Then tell the user this is a potential failure point and add it to the task file's `## Conclusion` as a known risk.
</system-reminder>

<bad-example>
```python
# Plan said nothing about missing config. Agent "helpfully" defaults.
timeout = config.get("timeout", 30)
user_id = payload.get("user_id", "anonymous")
```

This hides real bugs. "anonymous" user_ids leak into downstream systems. 30s timeouts mask misconfigured services.
</bad-example>

<good-example>
```python
# Rigid. If it breaks, it breaks loudly.
timeout = config["timeout"]
user_id = payload["user_id"]
```

Then append to the task file's `## Conclusion` under "Known risks":
> `- config["timeout"] will KeyError if config is partial. Plan didn't specify a default; recommend either adding one with user approval, or validating config at load time.`
</good-example>

Raise these potential failure points with the user immediately, not after execute completes.

## Deviations from plan

A deviation is any structural change from what the plan says. File moved to a different location, method signature different, phase ordering swapped, a phase cut, a phase added.

<required>
When a deviation happens:

1. Do not edit the Plan inline. The plan is the contract that was approved; it stays as-is for the review.
2. Record the deviation in the task file's `## Conclusion` under a `### Deviations from plan` subsection (create if missing). Format: `- <what changed> — <why>`.
3. If the deviation is minor (renamed a helper, swapped two steps) — continue execution.
4. If the deviation is structural enough that later phases in the plan no longer apply — stop executing. Invoke `up:uplan` with enough context (what was done, what no longer applies, what new reality is). Let the planner skill update the plan before resuming.
</required>

<good-example>
"Phase 3 planned a new `CacheBackend` class. During phase 2 I discovered an existing `cache/backend.py` with a usable interface. Extending it is simpler.

Appended to `## Conclusion`:
> - Phase 3: used existing `cache.backend.CacheBackend` instead of creating a new one.

Continuing to phase 4 — later phases are unaffected."
</good-example>

<bad-example>
Agent edits `## Plan` inline with `<!-- deviation: ... -->` comments. Reviewer now can't tell what the plan *was*, only what it became. Plan-alignment check is compromised.
</bad-example>

## When to stop and ask

- A plan instruction is ambiguous or self-contradictory
- A dependency the plan assumes is missing
- A test fails in a way that suggests the plan is wrong (not just the implementation)
- Verify would obviously fail even after you finish
- You're about to invent a fallback / default / catch-all

Don't force through. Ask.

## Never

- Start on `main`/`master` without explicit user consent if the plan specified a branch
- Skip the commit between phases
- Claim complete without running what you built
- Push to remote without explicit user consent
- Edit the Plan section to hide a deviation
- Edit an upstream spec file during execute (flag issues, don't mutate)
- Invent a silent fallback to avoid stopping
- Commit without running the plan-diff check and consistency pass

## Terminal state

All phases done and committed → invoke `up:uverify`. Do not skip to review. Do not finish the branch yourself.
