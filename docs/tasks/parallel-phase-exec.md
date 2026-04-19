# Parallel Phase Execution

**Status:** planning
**Branch:** parallel-phase-exec
**Worktree:** .worktrees/parallel-phase-exec
**Mode:** hands-off

## Design

Goal: let `up:uexecute` dispatch multiple `up:implementer` agents in parallel when phases don't depend on each other, and let one implementer carry multiple small sequentially-dependent phases. Keeps the current serial behavior as the default so existing plans work unchanged.

Approach (opt-in via the Plan). `up:uplan` gains an optional `### Execution batches` subsection that declares how phases are grouped for dispatch. `up:uexecute` reads that subsection and dispatches each batch; within a batch, each group ("bundle") runs in one implementer and groups run in parallel via multiple `Agent` tool calls in one response. When the subsection is absent, execute falls back to today's one-phase-per-implementer serial loop.

Batch declaration format in `## Plan`:

```
### Execution batches
- B1: [PH1] || [PH2 → PH3]    # two bundles in parallel; bundle B does PH2 then PH3
- B2: [PH4]                    # solo phase
- B3: [PH5] || [PH6]
```

- `||` separates bundles that run in parallel within the batch.
- `→` inside a bundle means the implementer runs those phases sequentially in one dispatch, commits each.
- Bundling criterion: PH N+1 depends on PH N (imports a symbol, edits what N just created) AND the pair together is still small (a handful of files, low risk, no structural divergence from Plan).

Disjointness invariant. Phases in different bundles of the same batch must touch disjoint file paths (exact paths, not directories). `up:uplan` declares files per phase already (File structure section). `up:uexecute` verifies disjointness from the Plan before dispatching the batch; on overlap, stops and logs under Deferred. Bundled phases in the same bundle may overlap freely (same implementer, sequential).

Commits in parallel batches. The dispatcher serializes git. In a parallel batch, each implementer does edits + tests + self-review but does NOT commit. It reports the changed files and the intended commit message. The dispatcher commits each returned phase sequentially (one commit per phase, order: B1's bundles alphabetically or by lowest-PH-number), runs plan-diff check and consistency pass after each commit, then moves to B2. Solo and bundled-single-implementer phases commit as today (implementer commits). Rationale: git index and HEAD are process-global in one worktree; parallel `git add`/`git commit` races are the failure mode we're avoiding. Serializing only the commit step keeps code edits parallel.

Failure handling in a parallel batch. If any implementer in the batch returns `BLOCKED` or `NEEDS_CONTEXT`, wait for all siblings in the batch to complete, commit the ones that returned `DONE`, then handle the failure(s) before moving to the next batch. Do not abort siblings mid-work (their results are still useful and their commits are reversible). If an implementer returns `DONE_WITH_CONCERNS`, commit and surface the concern per the existing rule.

Changes required:

- `plugins/up/skills/uplan/SKILL.md` — add optional `### Execution batches` subsection to the Format block; add a short "When to declare batches" paragraph (when to parallelize, when to bundle, disjoint-files rule); leave plans without it working as today.
- `plugins/up/skills/uexecute/SKILL.md` — replace the short "Parallel dispatch" paragraph with a dedicated "Batched dispatch" section: read `### Execution batches`, verify file disjointness, dispatch one or more implementers per batch (parallel Agent calls in a single response for parallel bundles), handle the serialized-commit protocol, run plan-diff + consistency after each phase, proceed to next batch.
- `plugins/up/agents/implementer.md` — add a "commit mode" to the What-you-receive list: `commit: self` (default, today's behavior) vs `commit: defer` (parallel batch — stage/summarize only, dispatcher commits). In `commit: defer` mode, the Report Format includes `Commit message (proposed): <message>` and omits `Commit: <sha>`.

TDD: no (reason: doc-only plugin change — SKILL.md and agent markdown; no runtime code to test)

### Invariants
- IV1 — One commit per phase, regardless of execution mode (preserves rollback surface).
- IV2 — Phases in different bundles of the same batch must touch disjoint file paths; dispatcher verifies from the Plan before dispatching the batch.
- IV3 — Plan-diff check and consistency pass run after each phase's commit, in every mode (serial, parallel, bundled).
- IV4 — The Plan is the contract for parallelism: batching is declared in `### Execution batches`, never inferred by the dispatcher at runtime.
- IV5 — Plans with no `### Execution batches` subsection execute exactly as today (serial, one implementer per phase). No behavior change by default.

### Principles
- PC1 — Opt-in parallelism. Absence of a batch declaration means serial execution.
- PC2 — Serialize git, parallelize edits. Code changes can run concurrently; commits do not.
- PC3 — Keep the implementer contract minimal. The only new thing it learns is "commit: self | defer".
- PC4 — Fail loud on disjointness violations. No silent fallback to serial when files overlap — stop and log under Deferred.

### Assumptions
- AS1 — Claude Code's Agent tool supports multiple concurrent invocations in a single response (the tool docs state this explicitly).
- AS2 — Parallel implementers running Edit/Write/Read in the same working directory on disjoint file paths do not race at the filesystem layer.
- AS3 — Parallel implementers do not invoke git write operations themselves in `commit: defer` mode, so only the dispatcher touches the git index/HEAD.
- AS4 — The existing Plan's per-phase File structure listing is reliable enough for disjointness checking; implementers don't silently touch files outside their phase's list.

### Unknowns
- UK1 — Exact grammar for `### Execution batches`: the `[PH1] || [PH2 → PH3]` shape proposed here is one option; plan stage may propose a cleaner alternative (e.g. nested list) if the inline grammar is hard to read for bigger batches.
- UK2 — Whether the consistency pass in a parallel batch needs to wait for ALL bundles in the batch to commit before running (so it sees the whole batch's diff), or can run per-phase as phases commit. Current lean: per-phase, matching today's behavior; revisit if it surfaces false-negatives.
- UK3 — Resolved: `up:uplan` emits `### Execution batches` only when real parallelism exists; single-phase / obviously-sequential plans omit it. Planner owns ordering and batch composition.

## Plan
<empty — filled by up:uplan>

## Verify
<empty — filled by up:uverify>

## Conclusion
<empty — filled by up:ureview>

### Hands-off decisions
- size: Medium — default in hands-off; touches up:uexecute skill and possibly up:implementer agent, needs full design + plan
- make: dedicated branch + worktree at .worktrees/parallel-phase-exec — hands-off safest-reversible default
- udesign: UK3 resolved by user (only emit subsection when parallelism exists); UK1/UK2 left for planner

### Deferred (needs user input)
