---
name: uexecute
description: Use to implement an approved plan. When the plan declares `### Interface graph`, derives waves by topo-sort over `[blocks]` IF edges only — non-blocking IF edges (the default) put producer and consumer in the same wave, since the IF declaration is sufficient context. Edits inline when only one implementer would fire (single phase or serial fallback). Runs plan-diff check and consistency sweep after each commit. Forbids silent fallbacks and mutation of external spec/design docs. Dispatches the planner skill when deviations invalidate the plan.
---

# Execute

Implement the approved `## Plan` from `docs/tasks/<slug>.md`. Dispatch concurrent phases to independent implementers. Execute single phases inline.

## Harness adaptation

On Claude Code, use `up:implementer`, `up:implementer-sonnet`, `up:explorer`, and `up:researcher`. On Codex or Pi, use the host's delegation mechanism with the role contract below. Confirm available capabilities rather than assuming a model, tool, or custom agent exists. Use the host's task checklist.

Pass the absolute working directory and expected branch to every child. Preserve file ownership, commit ownership, and report requirements across harnesses.

## Before starting

1. Read the full task file: context, design, invariants, principles, assumptions, unknowns, and plan.
2. Raise ambiguity, missing dependencies, or contradictory instructions before editing.
3. Confirm `git rev-parse --show-toplevel` and `git branch --show-current` match the task file's worktree and branch. Recheck before writes. If the worktree is `none`, use the main checkout. Stop on a mismatch.
4. Create a checklist entry per phase.
5. Read the [brevity rules](../_brevity.md) before writing task progress or responding. Omit empty deviations and risks. Deferrals name the needed path, command, or decision and include evidence and a reason.

## Derive execution waves

Without `### Interface graph`, execute phases in order, inline. With a graph, read each line as:

```text
PH<N>  <consumed-interfaces> -> <produced-interfaces> @ <owned-paths>
```

- An empty consume side means no input interfaces. An empty produce side means no output interfaces.
- Look up each consumed interface in `### Interfaces`. Only `[blocks]` creates an ordering dependency. A consumer of a non-blocking interface can use its declared signature while the producer runs.
- Wave 1 contains phases with no blocking inputs. Each later wave contains phases whose blocking producers have completed in earlier waves. Never invent ordering or hand-declare waves.
- Before each wave, check that its phases' owned paths are disjoint. On overlap, stop and record the conflicting paths and phases under `### Deferred (needs user input)`.
- If only one phase would run, edit inline. Also stay inline for a phase needing interactive input or a small follow-up fix. Plan-diff and consistency checks still apply.

## Dispatch per phase

### Choosing the implementer agent

- Complex implementer is the default for judgment, multi-file changes, new logic, test-driven development, or interface changes.
- Trivial implementer is limited to mechanical, localized edits such as a typo, import cleanup, or version bump. A documentation edit qualifies only when it makes no behavioral claims.
- If the trivial implementer returns `NEEDS_CONTEXT` to request escalation, send the same phase to the complex implementer.

### Dispatch contract

Pass the phase verbatim, its design constraints, and these fields:

```text
Phase: <verbatim phase text from the plan>
Invariants: <definitions from design>
Principles: <definitions from design>
Assumptions: <definitions from design>
TDD: <yes | no (reason)>
Working directory: <absolute path>
Branch: <expected branch>
Commit mode: defer
Owns: <paths from the graph>
Implements: <produced interface IDs, if any>
Consumes: <consumed interface IDs, if any>
Interfaces: <declarations for those interfaces>
```

Do not pass session history, prior-phase chatter, later phases, the full task file, or rationale behind design decisions. The child needs the contract, not the conversation.

Implementers edit only their owned paths, test, stage those paths, and report status, changed files, checks and results, concerns, deviations, and a proposed commit message. They do not commit in defer mode. On Codex or Pi, include these duties explicitly in the child prompt.

### Wave dispatch

Launch all phases in a wave concurrently. On Claude Code, use concurrent `Agent` calls with `run_in_background: true`. On Codex and Pi, use the host's parallel workflow mechanism.

If dispatch was accidentally sequential, report it and track the existing runs. Never relaunch active or completed work merely to make dispatch parallel.

## Per-wave loop

1. Mark the phase or wave `in_progress`.
2. Implement inline or dispatch the wave. Follow the design's test-driven-development decision.
3. Wait for all dispatched phases to finish. Do not abort siblings because one phase failed.
4. Process successful phases in ascending phase order using the serialized commit protocol below.
5. Handle unsuccessful phases after successful work is committed:
   - `NEEDS_CONTEXT`: supply the missing context and re-dispatch.
   - `BLOCKED`: diagnose. Re-dispatch only with corrected context, invoke [uplan](../uplan/SKILL.md) if the plan is wrong, or stop and record the blocker. Do not retry identically.
6. Mark a phase completed only after its commit and checks. A failed phase never rolls back a sibling's committed work.

### Serialized commit protocol

A successful phase returns `DONE` or `DONE_WITH_CONCERNS`. Resolve or record concerns before continuing. For inline work, the dispatcher performs the same checks and commits.

1. Stage the phase's owned changes and inspect its diff. Check every plan bullet is covered and every change has a plan bullet or reported deviation. Run the consistency pass and the phase's checks before committing.
2. Commit only that phase's paths. In a shared worktree, use `git commit --only -m "<message>" -- <owned-paths>` so another phase's staged changes do not enter this commit.
3. Read `git show <sha>` for the plan-diff check. Record structural gaps as deviations or correct them. Confirm sibling patterns were handled.
4. Run `git show <sha> --name-only` for the boundary check. Every changed path must belong to that phase. On trespass, halt the wave, record the paths and phase under `### Deferred (needs user input)`, then re-dispatch with corrected ownership or escalate to [uplan](../uplan/SKILL.md).

Do not skip phase commits or amend history without user approval.

## Wiring check

Run once after the final wave's commits. For each interface in `### Interfaces`:

1. Find its named symbol or section anchor and all callers or references.
2. For code, check each call matches the declared signature. For documentation, check each target and anchor resolves.
3. Record mismatches under `## Conclusion → ### Deviations from plan` with the interface ID and evidence. Re-dispatch an implementation error, invoke [uplan](../uplan/SKILL.md) for a wrong contract, or continue with an explicitly recorded deviation.

## Test-driven development

If design records `TDD: yes`, follow [test-driven-development](../test-driven-development/SKILL.md): observe a failing test, implement the minimum change, and refactor with tests green. If `TDD: no`, skip test-first development and verify through [uverify](../uverify/SKILL.md).

## Supporting investigation

Use an explorer when missing code context, a call graph, or essential-file discovery exceeds a quick local read or search. Use a researcher for external information requiring synthesis across sources. A single documentation lookup does not need delegation.

Pass a tight question or scope and the absolute working directory. For research, include relevant subquestions and source or depth limits. Use tools available in the host, without assuming a particular documentation service is installed.

## Consistency pass

When tightening a rule, renaming a symbol, or changing a pattern, search the diff and wider repository for siblings. Check the introducing commit when it helps locate them. Apply the same in-scope change in the same commit, or record a justified deferral. Verify a child's claimed consistency pass rather than repeating it blindly.

For example, if a metric now rejects empty input, check sibling metrics for the same silent fallback.

## Incidental code smells

Follow the [global principles](../_principles.md): fix in-scope or easy, low-risk defects. Record other smells under `## Code smells` as `file:line — issue` for review to consider as future work. Do not expand the task into a broad refactor.

## External specs and deviations

External specs, including `docs/specs/`, are read-only inputs. If a spec is wrong, stop and let the user choose whether to revise it, revise the plan, or accept a deviation.

Never edit the approved plan to hide what changed. Record a deviation under `## Conclusion → ### Deviations from plan` as `what changed — why`, with evidence.

- Minor changes, such as a helper rename or a small reorder, can continue when later phases remain valid.
- Structural changes that invalidate later phases stop execution. Give [uplan](../uplan/SKILL.md) the completed work, invalidated steps, and new facts so it can revise the plan through its approval process.

## No silent fallbacks

Do not invent defaults, swallow exceptions, or return placeholder success. If required data is missing and the plan defines no fallback, fail loudly. Tell the user immediately and record the failure point under `## Conclusion → Known risks`.

For a required timeout, use `config["timeout"]`, not `config.get("timeout", 30)`. If partial configuration is possible, record that it raises and ask whether the contract needs explicit validation or an approved default.

## When to stop and ask

- An instruction is ambiguous or self-contradictory.
- A required dependency is missing.
- A failed test shows the plan is wrong.
- Verification cannot pass with the current approach.
- Continuing would require an invented fallback or default.

In hands-off mode, record these blockers under `### Deferred (needs user input)` and follow the contract below.

## Hands-off mode

Read [handsoff](../handsoff/SKILL.md). Keep its worktree-first safety rules, external-spec protection, and prohibition on destructive git operations and unauthorized pushes.

When every stage auto-approved without intervention, collapse the decision log to `all stages auto-approved, no interventions`. Otherwise keep one entry per intervention. Deferrals and risks retain evidence and reasons.

## Terminal state

All phases committed and checked → invoke [uverify](../uverify/SKILL.md). Do not skip to review, claim completion without verification, merge, push, or finish the branch yourself.
