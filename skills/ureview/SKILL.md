---
name: ureview
description: Use after verify passes for the future maintainer's audit — sit in the chair of the person who'll touch this code in 3-6 months and ask "what will bite us later?" at the decision level. Surfaces wrong abstractions, load-bearing-but-unobvious shapes, next-change traps, drift from surrounding code. Raises a Scope flag if the whole change looks like the wrong call. Delegates an independent, critical review and fills the task file's `## Conclusion`.
---

# Review

Find choices that will make the next change difficult: wrong abstractions, implicit constraints, checks in the wrong layer, or drift from surrounding code. Question the scope when the completed work exposes a wrong premise, but leave redesign to the user and [udesign](../udesign/SKILL.md).

In the full [make](../make/SKILL.md) workflow, run after verification passes and before merge or a pull request, regardless of task size. Save the outcome in `## Conclusion`.

## Brevity

Read the [brevity rules](../_brevity.md). Keep the outcome to one sentence plus the commit ID. Omit empty findings, deviations, risks, scope flags, and future work. Retain invariant evidence and assumption or unknown outcomes whenever the task defined them.

Keep `## Code smells` separate from the conclusion. Delete it if empty. Promote a recorded smell to future work only when scheduling its fix, without duplicating the entry.

## Independent reviewer and dispatcher

The reviewer is critical and reports concrete issues at confidence 80 or above, classified by severity. The dispatcher verifies each finding before accepting or rejecting it.

On Claude Code, dispatch `up:reviewer`. On Codex or Pi, use an independent child with the same review contract: check design constraints, plan alignment, bugs, future-maintenance risks, and questionable scope. Do not replace independent review with your own inspection.

## Process

### 1. Dispatch the reviewer

Determine the task's branch point and current commit:

```bash
BASE_SHA=$(git merge-base HEAD main)
HEAD_SHA=$(git rev-parse HEAD)
```

Use the actual branch point if the task did not branch from `main`. Pass:

```text
Task file: <absolute path>
BASE_SHA: <branch point>
HEAD_SHA: <current commit>
Working directory: <absolute worktree path>
```

The reviewer's evidence is the task contract and diff. Do not pass session history or the controller's rationale. On Codex or Pi, include the review contract above in the prompt.

### 2. Evaluate findings

Classify findings as critical, important, or a problem with the plan. For each:

1. Restate it. Ask the reviewer to clarify if its meaning is unclear.
2. Open the affected code and verify that the defect exists.
3. Check whether the proposed fix suits this design and codebase.
4. Decide to fix, reject with technical reasons, or defer to the user.

Do not blindly accept findings, batch unrelated fixes, or respond to part of a linked finding before understanding the rest. Reject suggestions that break intended behavior, contradict the design, or add unused complexity.

### 3. Announce the decision before editing

Give one line per finding: the issue, your decision, and the exact change if fixing it. During authorized implementation, announce and apply verified in-scope fixes without another approval pause. Review-only requests remain read-only.

Example: "The parser accepts an empty identifier. Confirmed. Add rejection at the parser boundary and a regression test."

Hands-off decision logging is defined below.

### 4. Apply fixes

Fix critical and important issues in logical commits. Run [uexecute](../uexecute/SKILL.md#consistency-pass)'s consistency pass for each changed rule or pattern so sibling paths do not remain inconsistent. If fixes are substantial, dispatch the reviewer again on the new diff.

### 5. Write the conclusion

```markdown
## Conclusion

Outcome: <goal achieved or remaining validation, plus commit ID>

Invariants:
- IV1 — <verification evidence>

### Assumptions check
- AS1 — held | violated | unverifiable — <evidence or reason>

### Unknowns outcome
- UK1 — resolved | still-open — <answer or blocker>

Plan adherence: <deviations>

Review findings:
- Critical: <resolution>
- Important: <resolution or justified deferral>

Scope flag:
- <reviewer's flag, preserved for the user>

Future work:
- <item and design-scope justification or newly discovered fact>

Verified by: <material manual checks, deferred smokes, or other non-routine evidence>
```

Omit sections with no content. Do not omit violated assumptions or unresolved unknowns. A violated assumption needs evidence and, if it invalidates the outcome, a revised phase or a user decision. Preserve a scope flag for the user instead of silently redesigning the task.

## Hands-off mode

Read [handsoff](../handsoff/SKILL.md). Apply only verified, high-confidence fixes within the authorized implementation scope. Log each fix under `### Hands-off decisions` as `ureview: fixed <finding> — <change>`.

Record low-confidence or ambiguous findings under `### Deferred (needs user input)` instead of guessing. All fixes retain the contract's safety rules.

## Terminal state

Save the conclusion after critical and important findings are resolved or explicitly deferred with justification. Set status to `validating` and return to [make](../make/SKILL.md) for goal validation. Review does not mark `done` or choose a finish action.

Do not merge with open critical or important findings, accept a merge-ready verdict without evidence, or skip the independent reviewer or conclusion.
