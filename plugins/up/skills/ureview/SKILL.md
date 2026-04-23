---
name: ureview
description: Use after validate to get an independent quality check on the FR document. Dispatches up:reviewer (FR format + sourcing + validation presence checker), processes findings fairly, fills the task file's `## Conclusion`.
---

# FR Review

Independent quality check on the FR document. End product: `## Conclusion` in the task file, based on the reviewer's findings and the validate results.

## When to invoke

- After `up:uverify` passes or partially-passes
- Never skipped, regardless of document size or simplicity

## Brevity

<required>
`Outcome:` is ≤1 sentence + document code. Omit subsections whose content would be "none" / "clean" / "no findings". `Open questions:` and `Assumptions outcome:` stay even on pass — they carry audit value. Findings always carry evidence and "why". The Exception clause: any Critical finding, mismatch, or deferred item always includes evidence.
</required>

## Two roles, two attitudes

<reviewer-role>
`up:reviewer` is **critical**. It reads the FR document and WRITING_GUIDE.md — but not session history or the rationale behind writing choices. It flags format violations, unsourced claims, missing sections, and absent curl results. Confidence-filtered (≥80). Severity-tiered.
</reviewer-role>

<dispatcher-role>
You (the dispatcher) are **fair**. Restate → verify against the FR → evaluate → decide. Neither reflexive agreement nor reflexive pushback.
</dispatcher-role>

## Process

### 1. Dispatch `up:reviewer`

Dispatch with:
- Task file path (`docs/tasks/<slug>.md`)
- FR document path (`docs/FR/<code>. <name>.md`)
- WRITING_GUIDE.md path (`docs/FR/WRITING_GUIDE.md`)
- Working directory (explicitly — agent does not inherit cwd)

### 2. Process findings

For each finding from reviewer:
- Restate → verify (read the FR to confirm the issue exists) → evaluate (is it real?) → decide (fix or dismiss with reason).
- Fix all Critical findings before filling Conclusion.
- Document Important findings in Conclusion with resolution note.

### 3. Fill `## Conclusion`

```markdown
## Conclusion

**Outcome:** FR <code> ready for Confluence | FR <code> needs rework

**Validation result:** <from Verify — passed / partially-blocked; list blocked items>

**Review findings:** <from reviewer — or "no findings ≥80 confidence">

**Open questions remaining:**
- Q-01: resolved as <X> | still open — deferred to: <owner / next task>
- Q-02: ...

**Assumptions outcome:**
- AS1: held (confirmed by curl CK2) | not held (evidence: ...)
- AS2: ...

**Unknowns outcome:**
- UK1: resolved as <X> | still open — deferred to: <next task slug or owner>
- UK2: ...
```

## After Conclusion is filled

- Update `context.md` section 5 with the final document status (В работе → Готово / Заблокировано).
- If open questions remain: add them to `context.md` section 7 with owner and FR reference.
- Present options to user: push to Confluence, start next FR in coverage plan, close task.

## Rules

- Never skip review, even for single-endpoint FRs.
- Every open question (Q-NN) must appear in Conclusion — either resolved or explicitly deferred with owner.
- Blocked validation items → note in Conclusion as "pending environment access: <what's needed>".
- Do not auto-push to Confluence — user decides at finish.

## Hands-off mode

Read `up:handsoff` for full contract. Review runs unchanged in hands-off. Deferred items go to `### Deferred (needs user input)`.

## Terminal state

Conclusion filled. `context.md` updated. User chooses next action.
