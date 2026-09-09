---
name: git-worktrees
description: Use when a task needs an isolated checkout. Verify the worktree location, keep mutable environments and build outputs local, and run only authorized setup and checks.
---

# Git worktrees

Worktrees isolate branch changes without stashing or switching another checkout. Use one for concurrent writers or a task that needs its own checkout.

## Choose the location

1. Follow the user's or project's worktree-location rule.
2. Otherwise use the repository's `.worktrees/` directory.
3. For a directory inside the repository, verify the chosen directory is ignored before creating it. An ignored sibling directory is not evidence that this path is ignored.

```bash
directory="<selected-dir>"
git check-ignore -q "$directory/"
```

If the path is not ignored, add the required ignore entry before creating the worktree.

## Create the checkout

Confirm the repository root, base revision, branch name, and destination. Do not replace an existing directory or change another checkout's state.

```bash
branch="<branch-name>"
base_ref="<base-ref>"
git worktree add "$directory/$branch" -b "$branch" "$base_ref"
```

After creation, confirm the new checkout's root, branch, and revision before editing.

## Keep environments local

- Each worktree owns its mutable virtual environment, installed dependencies, and build outputs.
- Do not symlink or copy `.venv`, `node_modules`, `vendor/bundle`, `target`, or equivalent mutable directories from another checkout.
- Share download caches only when the package manager supports safe concurrent cache access.
- Use the project's declared manager and lockfile to create a fresh local environment when the required environment is missing.
- If a worktree already points to shared mutable state, stop before installing or testing. Propose replacing that link with a local environment without modifying its target.
- Before trusting tests or diagnostics, confirm project imports and source resolution point into this worktree. Editable installs and ancestor dependency lookup can resolve the original checkout even when manifests match.

## Establish a baseline

Run the relevant existing checks within the approved task scope and runtime limits.

If a check fails before implementation, record its command, revision, and failure. Ask before continuing when the failure prevents meaningful verification. If a check cannot run, report it as unrun rather than treating an absent environment as a passing baseline.

Report the worktree path, branch, revision, environment state, and the checks actually performed.

## Clean up after approval

After the user chooses cleanup, check the worktree is clean and its work is merged or otherwise preserved. Then remove it and use safe branch deletion:

```bash
git worktree remove <path>
git branch -d <branch-name>
```

If deletion is refused because work is unmerged, stop and report it. Never force deletion without explicit approval. Never delete or repair another worktree's environment during cleanup.

## Completion

The requested worktree exists with verified identity and isolated mutable state, or the setup blocker is reported. Record unrun checks and the next authorized action.
