# Trim and fix skills

Status: executing

Branch: `trim-skills`

Worktree: `.worktrees/trim-skills`

Progress: phase 1 complete. Packaging and whitespace checks passed. Phase 2 pending.

## Context

- Shared skills contain repeated instructions and references that require missing context. `skills/uexecute/SKILL.md` repeats wave scheduling and cites unexplained task-specific identifiers such as `IV6` and `IF5`.
- `skills/handsoff/SKILL.md` and `skills/ureview/SKILL.md` refer to numbered workflow steps that differ from `skills/make/SKILL.md`. Shared execution instructions mandate Claude-specific `Agent` calls despite supporting Codex and Pi.
- `skills/udocument/SKILL.md` mandates cutting 30 percent regardless of content. `skills/_principles.md` misattributes a failure maxim to Parkinson's law.

## Desired design

Skills give concise, self-contained instructions with resolvable references, explicit approval gates, and correct harness guidance. Scope is `skills/**/*.md` and this task file. Read commands, agents, and packaging metadata as reference material without expanding the cleanup into them. Keep useful examples and leave already concise skills unchanged.

## Invariants and principles

- Preserve skill names, frontmatter triggers, required outputs, and workflow order. Compare each changed skill against its original instructions.
- Preserve qplan's required reading, saved plan, context, desired design, invariants and principles, sequential phases, and verification. Request approval only after saving the plan. Implementation still requires plan approval.
- Hands-off mode follows the linked contract, auto-approves the completed plan, and retains isolation and safety rules. It does not skip planning or override explicit read-only restrictions.
- Preserve full-workflow dependency scheduling, file ownership, commit ownership, failure handling, and goal confirmation. Shorter wording must not remove an operational requirement.
- Keep evidence requirements and failure reporting. Do not silently change verification pass/deferred semantics or other ambiguous policies during prose cleanup. Ask before resolving a conflict that requires a new policy.
- Remove repetition only when the surviving instruction remains explicit and reachable. No deletion quota, new framework, new dependency, or new test infrastructure.
- Execute sequentially without subagents after approval, in a dedicated worktree under `.worktrees/`. Preserve the existing qplan whitespace change and unrelated `.pi/` artifacts. No merge, push, or reinstall without user approval.

## Implementation plan

### Phase 1 — Repair references and concrete errors

- Read every skill before changing it. Check local links, section references, skill names, and agent names against their actual targets. Distinguish illustrative placeholders from broken references.
- In `skills/uexecute/SKILL.md`, remove unexplained historical identifiers while retaining the rules they annotate. Scope Claude tool syntax to Claude and retain host-native delegation for Codex and Pi. Remove the instruction to relaunch all phases merely because an earlier dispatch was sequential, which can duplicate active work.
- In `skills/handsoff/SKILL.md` and `skills/ureview/SKILL.md`, replace fragile workflow step numbers with named stages and links to the relevant skill.
- In `skills/make/SKILL.md`, state that only a literal first-token `handsoff` is removed from the task description.
- In `skills/_principles.md`, remove the misattributed maxim while retaining the fail-fast rule. Repair other confirmed reference defects within `skills/` using the same approach.

### Phase 2 — Trim without losing requirements

- In `skills/uexecute/SKILL.md`, consolidate repeated scheduling, ownership checks, inline-execution rules, and consistency checks. Keep dispatch inputs, outcomes, and commit ordering explicit.
- In `skills/udesign/SKILL.md`, `skills/uplan/SKILL.md`, `skills/uverify/SKILL.md`, and `skills/ureview/SKILL.md`, shorten repeated explanations and examples. Retain required task sections, approval gates, evidence, and handoffs. Correct examples that contradict their surrounding rule, such as restating a global principle as a task-specific principle.
- In `skills/udocument/SKILL.md`, replace the fixed cut quota with removal of text that adds no instruction or explanation. Trim repetition in `skills/_brevity.md` while retaining its evidence exception.
- Review the remaining skills for the same defects. Preserve qplan's explicit required-planning-output gate. Leave unrelated policy choices unchanged.

## Verification

- Run `python3 scripts/validate_pack.py` and `git diff --check`. Check changed local links and named references against their targets. The packaging validator alone does not verify every reference.
- Compare the diff against the invariants above and record any unresolved conflict rather than choosing a new policy silently.
- Manual try, positive: walk a concrete approved two-phase task through the revised full-workflow instructions. Confirm inputs, dependency ordering, ownership, verification, and goal confirmation can be followed without unexplained references or unavailable tool assumptions.
- Manual try, negative: walk an ordinary qplan request without plan approval through the revised instructions. Confirm it requires reading and saving every required plan section, then stops before implementation. A chat summary alone must fail this check.
- Record these as instruction walkthroughs, not live harness execution. Append the actual results after implementation. No paid agent runs or additional smoke infrastructure.
