---
name: qplan
description: "Quickly design and plan, wait for plan approval, then execute sequential phases with focused verification and a manual try. Use when a task needs more than a prompt but does not need the full ultrapack make workflow, or the user asks for a quick plan."
---

# Quick plan

Use `qplan` for a bounded change that needs a clear design and an actionable plan without the full `make` flow. Invoke as `/up:qplan` in Claude Code, `$qplan` in Codex, or `/skill:qplan` in Pi.

Example: `Use $qplan to add a date filter to the activity list.`

## Design and plan in one pass

0. Grill the user until their intent is clear to you and there is no blocking ambiguity. Only ask if something is not resolvable by common sense and existing guidance.
1. Read the relevant docs, code, project guidance, and current changes. Find existing patterns to reuse. Keep exploration tied to the request.
2. Ask only for decisions that block a safe, correct implementation. State small assumptions in the plan. If the work spans independent goals or needs a major architectural decision, propose a split or `make` and stop for direction.
3. Write one compact plan using the shape below. Save it to `docs/tasks/<slug>.md`, or update the task file supplied by the user. In native plan mode or a read-only request, use the permitted plan location or chat and do not change project files.
4. Present the combined design and plan, then stop and wait for the user's explicit approval of that plan before execution. The initial task request or general permission to implement does not count as plan approval.
5. If the user invoked `/skill:handsoff` or specified or mentioned hands-off mode for this task, read and follow the [handsoff skill](../handsoff/SKILL.md) for planning and execution. Record `Mode: hands-off` in the task file. The presented plan is auto-approved under that contract. Explicit plan-only requests and harness read-only restrictions still prevent execution.

Use plain bullets. Keep context short, omit empty sections, and add detail only where it prevents a likely mistake. No mandatory IDs, interface graphs, risk registers, or separate stage approvals.

```markdown
# <Task>

## Context
- <current behavior and why it needs to change>

## Desired design
<observable outcome, chosen approach, and scope boundary>

## Invariants and principles
- <behavior that must remain true and how to check it>
- <task-specific rule that guides implementation>

## Implementation plan
### Phase 1 — <working outcome>
- <files or symbols to change and the concrete change>
### Phase 2 — <next working outcome, only if needed>
- <files or symbols to change and the concrete change>

## Verification
- <smallest relevant test, lint, or build check and expected result>
- Manual try, positive: <realistic user path and expected result>
- Manual try, negative: <likely misuse or edge case and expected rejection or safe behavior>
```

## Execute after plan approval

- Start only after explicit plan approval or hands-off auto-approval under the rule above.
- Implement phases in order in the current session. No subagent dispatch, parallel work, or automatic calls to `make`, `udesign`, `uplan`, `uexecute`, or `ureview`.
- Follow the repository's branch, worktree, and commit rules. Preserve unrelated changes.
- Use existing code and focused regression tests where behavior warrants them. Update phase progress briefly in the same task file.
- Do not overengineer. Choose the smallest correct change. Avoid speculative abstractions, extensive validators, new dependencies, compatibility layers, unrelated cleanup, and extra features unless the goal requires them.
- Check each phase against the desired design and invariants. Adjust implementation details inline. If a finding changes the goal, scope, or a material design choice, stop and get approval before expanding the plan.

## Verify and finish with a manual try

1. Run the planned focused checks. Keep verification proportional to the changed behavior and invariants. Do not add broad suites or new test infrastructure without a concrete need.
2. Finish with the `try` skill: run one realistic positive case and one adversarial negative case against the implemented behavior. Capture actual results and report failures before fixing them.
3. Fix in-scope failures, then rerun affected checks and the manual try. If a required check cannot run, report the blocker and leave verification incomplete. Do not claim an unrun check passed.
4. Append a short `## Result` to the task file with the outcome, checks run, manual try results, and any remaining blocker. Report completion only when the desired outcome has direct evidence and the planned checks pass.

Stop after the result. No automatic review stage, documentation sweep, or extra workflow ceremony.
