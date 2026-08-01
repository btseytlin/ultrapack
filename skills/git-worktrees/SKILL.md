---
name: git-worktrees
description: Use when a task needs isolation from the current workspace. Picks a worktree directory via a fixed priority order, verifies it's gitignored, creates the worktree, auto-detects project setup, runs baseline tests.
---

# Git Worktrees

Worktrees let you work on multiple branches simultaneously without stashing or switching. Use one when:
- The task is large enough to warrant isolation
- You want to run different branches in parallel
- You're dispatching subagents that shouldn't step on the active workspace

## Directory selection — priority order

<priority>
1. `.worktrees/` exists → use it
2. `worktrees/` exists → use it
3. Both exist → `.worktrees/` wins
4. Neither exists → check `CLAUDE.md` for a preference (grep `worktree.*director`); if present, use it
5. Still nothing → ask the user: project-local `.worktrees/` or a global path?
</priority>

## Safety — confirm project-local dirs are gitignored before creating

For project-local directories (`.worktrees/` or `worktrees/`), verify gitignore:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

If not ignored: add the line to `.gitignore`, commit (`chore: ignore worktree directory`), then proceed.

For global directories (outside the project), no gitignore check needed.

## Creation

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
path="<selected-dir>/<branch-name>"  # e.g. .worktrees/feature-auth
git worktree add "$path" -b "<branch-name>"
cd "$path"
```

## Share environment from main

At creation, a fresh worktree has no project environment — tools that resolve deps via ancestor walks (LSPs, language resolvers) either emit bogus diagnostics or reinstall from scratch. Avoidable: at this moment the worktree's deps are identical to the parent's (same commit base, same manifest). Share the main repo's environment into the worktree. Rebuild locally only if deps later diverge.

Worked example — Python (uv / venv):

```bash
main=$(git worktree list --porcelain | awk '/^worktree / {print $2; exit}')
if [ -f pyproject.toml ] && [ ! -e .venv ] && [ -d "$main/.venv" ]; then
  ln -s "$main/.venv" .venv
fi
```

Absolute symlink target so the link survives nested worktree paths. The `! -e .venv` guard means an existing real env or symlink is never overwritten. If main has no `.venv`, skip — baseline setup below falls through to the install command.

For other stacks, do the analogous share-from-main (`node_modules`, `vendor/bundle`, `target`, …). Go and Gradle share caches globally (`$GOMODCACHE`, `~/.gradle`) — nothing to link.

If the worktree later changes its manifest or lockfile, replace the shared env with a local install (e.g. `rm .venv && uv sync`). The skill doesn't detect this; it's guidance for whoever edits deps.

## Baseline setup — auto-detect and run

```bash
[ -f package.json ] && npm install
[ -f Cargo.toml ]   && cargo build
[ -f pyproject.toml ] && [ ! -e .venv ] && (uv sync || pip install -e .)
[ -f go.mod ]       && go mod download
```

Then run the project's tests to confirm a clean baseline. If tests fail before you've changed anything: stop and report. You can't distinguish future bugs from pre-existing ones.

## Report to the user

```
Worktree ready at <full-path>
Baseline: <test summary, or "skipped — no test command">
```

## Cleanup when task is done

```bash
git worktree remove <path>
git branch -D <branch-name>  # only if not merged
```

Don't leave stale worktrees around. `git worktree prune` cleans up broken references.

## Never

- Create a project-local worktree without verifying it's gitignored
- Skip the baseline test run
- Proceed with failing baseline tests without asking
- Hardcode setup commands — detect from project files
