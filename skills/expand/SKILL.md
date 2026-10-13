---
name: expand
description: "Turn one user criticism into a principle-level fix. Use when the user points out a flaw (\"this code doesn't handle exceptions properly\") and wants the root design flaw found, every similar occurrence fixed, and not just the one spot patched."
---

# Expand a criticism

The user pointed at one instance of a problem. Treat it as a sample, not the whole problem. Find the principle behind it, find every place that breaks that principle, and fix them all.

## Steps

1. Restate the criticism. Find what the user is really saying. Write the smallest general description of the problem that still covers the pointed-out case.
2. Name the violated principle. One sentence. It must explain why the pointed-out code is wrong, not only that it is wrong.
3. Describe the correct behavior. Say what the code would do if it followed the principle.
4. Find every violation. Search the codebase and related files for more instances of the same kind of issue. Include code, config, docs, and tests. Read each hit before counting it. List each with `file:line`.
5. Plan the fix. Prefer fixing the shared cause over patching each instance. If one helper, base class, or convention created the instances, change that.
6. Fix it. Apply the plan, then run the relevant checks. Re-search with the step 4 queries to confirm no violation is left.
7. Report briefly.

## Approval gate

After step 5, ask the user to approve the plan if the change is major. Do not ask in hands-off mode or when the user already told you to proceed without asking. In hands-off mode, follow the `handsoff` contract and log the decision.

A change is major when it does any of these:

- Changes a public interface, schema, or file format.
- Deletes or replaces a module.
- Changes behavior that callers outside the violating code rely on.
- Touches enough files that the user could not review it in one sitting.

## Rules

- Do not stop at the pointed-out instance. A fix to only that spot is a failed run.
- Do not widen the principle to make more hits. Each listed violation must break the same principle from step 2.
- If you find no other violations, say so and show the searches you ran.
- If a violation needs a decision the user must make, list it as open and do not guess.

## Report

```
Problem: <general description from step 1>
Principle: <violated principle>
Found: <count> violations
- <file:line> — <what was wrong>
Fixed: <what changed, shared cause first>
Open: <violations left and why, or none>
```
