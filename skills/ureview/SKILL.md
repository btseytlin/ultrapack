---
name: ureview
description: Use after verify passes to get an independent check on the work. Dispatches up:reviewer (critical, high-confidence filter), processes its findings fairly (no performative agreement, no reflexive acceptance), fills the task file's `## Conclusion`.
---

# Review

Review is a process, not just a section. Its end product is the `## Conclusion` section of the task file, filled in based on an independent code review and the work that was done.

## When to invoke

- After `up:uverify` passes
- Before merge to main
- Before opening a PR
- Never skipped, regardless of task size

## Two roles, two attitudes

<reviewer-role>
The `up:reviewer` subagent is **critical**. It is dispatched with a diff, a plan, and invariants — but not the rationale behind the changes. It looks for violated invariants, plan misalignment, bugs, and risks. Confidence-filtered (≥80). Severity-tiered.
</reviewer-role>

<dispatcher-role>
You (the dispatcher) are **fair**. Fair means: take every finding seriously, but verify it against the codebase before acting. Fair is neither reflexive agreement nor reflexive pushback. Fair is: restate → verify → evaluate → decide.
</dispatcher-role>

The asymmetry is deliberate. A tough reviewer catches more real issues; a fair dispatcher avoids overcorrecting on mistaken calls.

## Process

### 1. Dispatch `up:reviewer`

Get git SHAs:
```bash
BASE_SHA=$(git merge-base HEAD main)   # or the branch point for this task
HEAD_SHA=$(git rev-parse HEAD)
```

Dispatch the `up:reviewer` agent with:
- Task file path (`docs/tasks/<slug>.md`)
- `BASE_SHA` and `HEAD_SHA`
- Working directory (explicitly — the agent does not inherit `cwd` reliably)

<system-reminder>
Do **not** pass session history to the reviewer. The reviewer must not see the rationale behind changes — only the Plan, Invariants, and diff. Independence is the point.
</system-reminder>

### 2. Read feedback without reacting

Receive the reviewer's output. Do not immediately reply with fixes or pushback. Classify first:

- Critical: fix before proceeding
- Important: fix before merge
- Plan finding: the plan itself may be wrong

### 3. Evaluate each item fairly

<required>
For every finding:

1. Restate in your own words. If you can't restate it, ask the reviewer to clarify — don't guess.
2. Verify against the codebase. Does the issue actually exist as described? Open the file, read the lines.
3. Evaluate technically: is the suggested fix right for *this* codebase and the Design?
4. Decide: implement, push back with technical reasoning, or escalate to the user.
</required>

### 4. Announce the plan before editing

<required>
Before any fix goes in, tell the user what you decided for each finding. One line per finding:
- what the reviewer said,
- your verdict (fix / push back / defer),
- if fixing: the exact change you are about to make.

This is a short summary, not a negotiation. The user can interject. Then apply the fixes.
</required>

<bad-example>
"Evaluating reviewer findings fairly." *(then a flurry of edits with no explanation)*
</bad-example>

<good-example>
"Reviewer findings:
- Important #1: reviewer tool list missing `Bash`. Verdict: fix. Editing Design section of task file.
- Important #2: try.md and step-back.md missing frontmatter. Verdict: fix. Adding frontmatter to both.

Applying now."
</good-example>

### 5. Apply fixes

Fix Critical and Important issues. Commit each as its own logical unit.

<required>
For every fix, run the consistency pass (same rule as `up:uexecute`): if you're tightening a rule or changing a pattern, grep the diff and the wider repo for the same pattern and apply the change everywhere in the same commit. Do not leave siblings in a mixed state — that's how the reviewer's next round finds the same class of issue four more times.
</required>

If fixes are substantial, re-dispatch the reviewer on the new diff.

### 6. Write the `## Conclusion`

```markdown
## Conclusion

Outcome: <one paragraph — what works now>

Plan adherence: <any deviations already recorded during execute, summarized here>

Invariants: <each invariant, and how it was verified>

Review findings:
- Critical: <resolved, how>
- Important: <resolved or explicitly deferred with justification>

Future work:
- <item> — Justification: <Design-scope line that excluded this> OR <new fact discovered during execution>
- (No unjustified items. This section is not a dumping ground for incomplete in-scope work.)

Verified by: <smoke tests run, manual checks, reviewer verdict>
```

## Receiving feedback — rules

<dispatcher-rules>
Never:
- "You're absolutely right" / "Great catch" / "Thanks for catching that"
- Implement blindly without verifying against the codebase
- Batch fixes without checking each independently
- Respond partial when multiple findings may be linked — clarify all first

Do:
- Verify against codebase reality before acting
- Push back with technical reasoning when the reviewer is wrong
- Ask for clarification when a finding is unclear
- Show the fix in a diff — actions over words

Pushback is legitimate when:
- The suggestion breaks existing behavior
- The reviewer lacks context only the Design has (e.g. intentional tradeoff)
- The suggestion violates YAGNI (over-engineering an unused path)
- The suggestion conflicts with explicit Design / Invariants decisions
</dispatcher-rules>

## Never

- Accept "ready to merge" without evidence
- Merge with open Critical or Important findings
- Skip the Conclusion write-up
- Run review on yourself (always use the subagent — preserve independence)

## Terminal state

Conclusion written, all Critical/Important resolved or explicitly deferred with justification → present merge / PR / cleanup options to the user. The user chooses; you don't auto-merge.
