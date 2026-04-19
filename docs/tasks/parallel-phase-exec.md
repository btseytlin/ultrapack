# Parallel Phase Execution

**Status:** done
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

Approach: three independent doc edits — implementer agent gets a commit-mode input, uplan gains an optional batch-declaration subsection, uexecute gains a batched-dispatch section that ties them together. PH1 and PH2 touch disjoint files and have no dependency; PH3 references both conceptually (cross-links in prose) and lands last.

### PH1 — Implementer: commit mode

- **1.1** `plugins/up/agents/implementer.md:11-17` (modify) — "What you receive"
  - Add bullet: `Commit mode: self | defer` — `self` = implementer commits (today's behavior, default). `defer` = dispatcher commits; implementer stages + tests + reports intended message.
  - Respects: IV1, PC3
- **1.2** `plugins/up/agents/implementer.md:21-28` (modify) — "Process"
  - Step 6 "Commit" becomes conditional: if `commit: self`, commit as today; if `commit: defer`, stage the changed files (`git add <paths>`) and skip the commit.
- **1.3** `plugins/up/agents/implementer.md:48-68` (modify) — "Report Format"
  - In `commit: self` mode, report carries `Commit: <sha> <message>` as today.
  - In `commit: defer` mode, replace the `Commit:` line with `Commit message (proposed): <one-line message>` and add `Staged files: <path>, <path>`.
- **1.4** `plugins/up/agents/implementer.md:40-46` (modify) — "Forbidden"
  - Add: in `commit: defer` mode, do not run `git commit`, `git reset`, or branch/tag ops; staging only.
- Commit: `feat(implementer): add commit: self|defer mode for parallel dispatch`

### PH2 — Uplan: Execution batches subsection

- **2.1** `plugins/up/skills/uplan/SKILL.md:73-80` (modify) — "Required when relevant" list
  - Add: `Execution batches: declare parallel groups and multi-phase bundles when real parallelism exists. Omit otherwise.`
  - Respects: IV4, IV5, PC1
- **2.2** `plugins/up/skills/uplan/SKILL.md:82-108` (modify) — Format block
  - Append `### Execution batches (optional — omit when all phases run sequentially and alone)` with the grammar: `- B<N>: [PH<i>] || [PH<j> → PH<k>]` — `||` separates bundles that run in parallel, `→` means one implementer runs those phases sequentially.
- **2.3** `plugins/up/skills/uplan/SKILL.md:108-118` (modify) — new subsection "When to declare batches" (insert after Format block, before Self-review)
  - Parallelize phases only when their File structure bullets declare disjoint file paths.
  - Bundle PH N+1 with PH N when they have a tight dependency AND the pair is small (few files, low risk).
  - Omit the subsection when no real parallelism or bundling exists. Do not invent batches to fill space.
  - Respects: IV2, PC1, PC4
- **2.4** `plugins/up/skills/uplan/SKILL.md:110-118` (modify) — Self-review
  - Add item: "If `### Execution batches` is present, every bundle's phases have disjoint file paths from every other bundle in the same batch; bundled phases have a declared dependency."
- Commit: `feat(uplan): add optional Execution batches subsection`

### PH3 — Uexecute: batched dispatch

- **3.1** `plugins/up/skills/uexecute/SKILL.md:82-85` (modify) — replace the short "Parallel dispatch" paragraph in the "Dispatch per phase" section with a pointer to the new section below.
  - Respects: IV4, IV5
- **3.2** `plugins/up/skills/uexecute/SKILL.md:40-58` (modify) — "Per-phase loop"
  - Reframe as "Per-batch loop". If the Plan has `### Execution batches`, iterate batches; else fall back to today's one-phase-at-a-time loop (IV5).
  - Within a batch: verify file disjointness across bundles from the Plan's File structure; on overlap, stop and log under `### Deferred (needs user input)` (PC4).
- **3.3** `plugins/up/skills/uexecute/SKILL.md` (insert new section, between current "Dispatch per phase" and "TDD" — ~line 86) — "Batched dispatch"
  - Reading the batch declaration; mapping bundles to implementer dispatches; using multiple `Agent` tool calls in one response for parallel bundles; `commit: defer` for parallel bundles, `commit: self` for solo bundles and for multi-phase bundles (one implementer, sequential commits).
  - Serialized commit protocol: await all bundles in the batch, then for each returned `DONE`/`DONE_WITH_CONCERNS` report in order of lowest PH number, run `git add <staged paths>` (if not already), `git commit -m "<proposed message>"`, then plan-diff check (IV3) and consistency pass (IV3) for that phase.
  - Failure handling: on `BLOCKED` or `NEEDS_CONTEXT` from one bundle, wait for siblings, commit siblings' successful results, then diagnose the failure (re-dispatch, uplan, or stop). Do not abort siblings mid-work.
  - Respects: IV1, IV2, IV3, PC2, PC4
- **3.4** `plugins/up/skills/uexecute/SKILL.md:83-85` (modify) — "Dispatch per phase → Pass in the dispatch prompt"
  - Add bullet: `Commit mode: self | defer` — default `self`, set `defer` only when this phase is in a parallel bundle per `### Execution batches`.
- **3.5** `plugins/up/skills/uexecute/SKILL.md:56-57` (modify) — "Do not batch phases" sentence
  - Replace with: "Batch only per `### Execution batches` in the Plan; never infer batches at runtime (IV4)."
- Commit: `feat(uexecute): batched dispatch with serialized commits`

### Order & dependencies

- PH1 and PH2 touch disjoint files (`implementer.md` vs `uplan/SKILL.md`) with no import/data dependency.
- PH3 touches `uexecute/SKILL.md` only, but its prose references the contracts introduced by PH1 (commit mode) and PH2 (batch subsection), so it lands after them.

### Execution batches

- B1: [PH1] || [PH2]
- B2: [PH3]

### Risks / rollback

- RK1 — Grammar in `### Execution batches` (`||`, `→`) may be unclear to a reader at first glance; mitigated by a one-line legend in the Format block and a short "When to declare batches" section. Rollback: single commit revert on PH2.
- RK2 — Serialized-commit protocol in parallel mode could drop an implementer's staged changes if the dispatcher crashes between `return` and `git commit`; mitigated by the dispatcher running `git add` + `git commit` back-to-back with no other operations in between. Rollback: single commit revert on PH3.

## Verify

Result: passed

Invariants / assumptions:
- CK1 (IV5) — serial fallback preserved when `### Execution batches` absent: `uexecute/SKILL.md:42-44`
- CK2 (IV4) — runtime batch inference prohibited: `uexecute/SKILL.md:70, 98`
- CK3 (IV2) — disjointness verified before batch dispatch: `uexecute/SKILL.md:52`
- CK4 (IV1) — one commit per phase preserved: `implementer.md:29` (self) and `uexecute/SKILL.md:108-119` (defer)
- CK5 (IV3) — plan-diff + consistency pass run per phase in both modes: `uexecute/SKILL.md:65` (serial steps 4-5) and `uexecute/SKILL.md:116-119` (batch steps c-d)

Principles:
- CK6 (PC1) — `### Execution batches` documented optional: `uplan/SKILL.md:110`
- CK7 (PC2) — serialized-commit protocol documented: `uexecute/SKILL.md:113-120`
- CK8 (PC3) — only new implementer input is commit mode: `implementer.md:17`
- CK9 (PC4) — disjointness violation → Deferred, no silent fallback: `uexecute/SKILL.md:52`

Cross-references:
- CK10 — `commit: self|defer` vocabulary consistent across `implementer.md:17-30` and `uexecute/SKILL.md:83, 108-109`
- CK11 — `### Execution batches` subsection declared in `uplan/SKILL.md:110` matches its use in `uexecute/SKILL.md:42, 98`

Dogfood smoke: this task's own plan used `### Execution batches: B1: [PH1] || [PH2]; B2: [PH3]`; B1 ran as two concurrent `up:implementer` dispatches with stage-only commits, dispatcher then committed serially (b0cccf7, 7fc538b); B2 ran serially (3983b59). Full batched-dispatch flow exercised end-to-end on the task itself.

## Conclusion

Outcome: `up:uexecute` now dispatches implementers in parallel batches declared by `up:uplan` in `### Execution batches`, with serialized commits honoring IV1; reviewer fixes in 662cf48.

Invariants:
- IV1 — one commit per phase: enforced in `implementer.md:29` and explicitly extended to multi-phase bundles at line 8 after reviewer finding; dispatcher commits per phase in parallel mode per `uexecute/SKILL.md:113-119`.
- IV2 — disjointness verified pre-dispatch at `uexecute/SKILL.md:52`.
- IV3 — plan-diff + consistency pass run per phase in both modes (`uexecute/SKILL.md:65`, :116-119).
- IV4 — no runtime batch inference: `uexecute/SKILL.md:70`, :98.
- IV5 — serial fallback preserved: `uexecute/SKILL.md:42-44`.

### Assumptions check
- AS1 — held: multiple `Agent` tool calls in one response fire concurrently (confirmed by PH1/PH2 running in parallel during this task's own execution).
- AS2 — held: PH1 and PH2 implementers edited disjoint files in the same cwd without filesystem races.
- AS3 — held: dispatcher-only git writes in defer mode worked; no merge conflicts during serialized commit of b0cccf7 / 7fc538b.
- AS4 — unverifiable at this layer — the Plan's File structure reliability is a behavioral property of future uplan runs; revisit if a real task hits an overlap miss.

### Unknowns outcome
- UK1 — resolved: inline `[PH…] || [PH… → PH…]` grammar chosen and landed in `uplan/SKILL.md:110`; readable at batch sizes seen so far.
- UK2 — resolved: consistency pass runs per phase (matching today's behavior); documented in `uexecute/SKILL.md:116-119`.
- UK3 — resolved by user: `### Execution batches` emitted only when real parallelism exists.

Review findings:
- Important: Report Format ambiguity in `implementer.md` (both commit-mode lines in one block) → split into Variant A / Variant B in 662cf48.
- Important: multi-phase bundle commit rule unspecified → implementer.md:8 now accepts bundles; implementer.md:29 requires one commit per phase always, including in bundles (662cf48).

### Hands-off decisions
- size: Medium — default in hands-off; touches up:uexecute skill and possibly up:implementer agent, needs full design + plan
- make: dedicated branch + worktree at .worktrees/parallel-phase-exec — hands-off safest-reversible default
- udesign: UK3 resolved by user (only emit subsection when parallelism exists); UK1/UK2 left for planner
- uplan: plan auto-approved (hands-off)
- uexecute: PH1 and PH2 dispatched in parallel with stage-only (dogfooding the feature being added, since `commit: defer` didn't yet exist in implementer.md); dispatcher committed serially.
- ureview: fixed Report Format ambiguity and multi-phase bundle commit rule — split into Variant A/B and added bundle-aware one-commit-per-phase guidance (662cf48).

### Deferred (needs user input)
