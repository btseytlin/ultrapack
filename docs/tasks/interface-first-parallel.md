# Interface-first planning and parallel execution

**Status:** done
**Branch:** interface-first-parallel
**Worktree:** .worktrees/interface-first-parallel
**Mode:** hands-off

## Design

Problem. `### Execution batches` (landed in `parallel-phase-exec`) parallelizes by file-path disjointness, but planners still write coarse, coupled phases, so most batches collapse to near-sequential. Theory: forcing interface-first planning atomizes work at the contract boundary; the filesystem-disjointness check becomes a cheap lower-level guard instead of the dispatch primitive.

Approach. `## Plan` gains two subsections — `### Interfaces` (contract definitions) and `### Interface graph` (the execution shape, dataflow grammar). Each phase declares what it produces, what it consumes, and which files it owns. `up:uexecute` topo-sorts the graph into waves; within a wave, phases dispatch in parallel bounded by `@`-disjointness. Two new post-dispatch checks: Boundary (diff ⊆ `Owns`) per returned phase, Wiring (callers of each IF match the declared signature) at end of graph. `up:uverify` adds one CK per IF. Replaces `### Execution batches` (grammar removed, not layered).

Plan subsections:

```
### Interfaces
- IF1 — `Parser.parse(s: str) -> AST` — canonical AST; raises on syntax error
- IF2 — `Runner.run(ast: AST) -> Result` — pure; no I/O

### Interface graph
- PH1  -> IF1             @ parser.py, ast.py
- PH2  -> IF2             @ runner.py
- PH3  IF1, IF2 ->        @ main.py
```

Grammar. `PH<N>  <consumes> -> <produces>   @ <owns>`. Empty left = source; empty right = sink/wiring. Comma-separated IF lists; comma-separated paths after `@`. Single-phase plans omit both subsections.

Execution. Derive waves via topological sort over `->`. Within a wave, check `@` disjointness; dispatch each phase as a concurrent `up:implementer` (`commit: defer`); dispatcher commits each returned phase in PH-order; run Boundary + plan-diff + consistency per commit. After the final wave commits, run Wiring check across the whole graph. Falls back to serial one-phase-at-a-time when `### Interface graph` is absent (IV6).

Boundary check. For each returned phase, `git show <sha>` — every changed path must be in the phase's `Owns`. Trespass = halt, log deviation, re-dispatch with tightened scope or escalate to `up:uplan`.

Wiring check. For each IF, `grep` callers; verify each call site matches the declared signature (name, arity, argument types if expressible). For doc-only targets (SKILL.md edits in this repo's own meta-tasks), "signature" degenerates to the declared section anchor / public contract and wiring check becomes an anchor-presence grep.

Verify addition. Checklist grows a CK per IF: "IF<n> honored" — contract asserted end-to-end (real call, real return, or structural match).

Backwards-compat. `### Execution batches` grammar removed. No in-flight tasks use it (all `docs/tasks/*.md` are `done`). External users' existing plans with old grammar will be ignored by the new executor; plans without `### Interface graph` fall back to serial. Hard break, no shim — PC4.

TDD: no (reason: doc-only plugin change — SKILL.md and agent markdown; no runtime code to test).

### Invariants
- IV1 — `## Plan` declares every cross-phase contract as `IF<n>` with signature + contract sentence.
- IV2 — Every phase in `### Interface graph` declares `@ <paths>`; `<consumes> ->` and `-> <produces>` are declared when relevant.
- IV3 — Boundary check runs after each phase's commit: diff ⊆ phase's `Owns` or halt (no silent widening).
- IV4 — Wiring check runs once, after the last wave's phases commit: every IF has a caller match (or an anchor-presence match for doc targets).
- IV5 — Verify checklist has ≥1 CK per IF.
- IV6 — Plans without `### Interface graph` execute serially, one implementer per phase — no behavior change for single-phase or legacy plans.
- IV7 — One commit per phase, regardless of wave or parallelism (carried over from `parallel-phase-exec`).

### Principles
- PC1 — Interfaces are plan-text. Code stubs (a PH0 scaffolding phase) are optional and decided per task; not required by the skill.
- PC2 — `@` (owned files) is the filesystem-parallelism boundary; IFs are the logical-coupling boundary. Both must be declared; neither subsumes the other.
- PC3 — Fail loud on boundary and wiring violations. No silent re-dispatch, no silent scope expansion.
- PC4 — Replace, don't layer. `### Execution batches` grammar is removed; IFs + `@` are the single source of truth for dispatch.
- PC5 — Waves are derived from the graph, never hand-declared. The planner writes the graph; the executor infers the waves.

### Assumptions
- AS1 — Interface-first planning yields strictly more parallel dispatch than file-path batching (the task's load-bearing hypothesis; conclusion must report whether observed).
- AS2 — Planners can nail interface signatures before seeing implementations (standard top-down design assumption).
- AS3 — `git show <sha>` against the phase's declared `@` paths is sufficient for Boundary; implementers don't silently touch files outside their declared scope.
- AS4 — `grep` of caller sites + signature string-match is sufficient for Wiring for most tasks; tasks needing stronger checks can escalate to an integration-smoke phase.
- AS5 — For doc-only tasks, "interface" reduces to SKILL.md section anchors / declared public contracts; the same grammar applies without strain.
- AS6 — Removing `### Execution batches` strands no in-flight task in this repo (all current task files are `done`).

### Unknowns
- UK1 — Plan-text interfaces vs a dedicated PH0 stub phase that lays down empty types/protocols before the parallel wave. Current lean: plan-text only; stubs are an optional pattern the planner can choose per task.
- UK2 — Wiring-check mechanism for code targets — structural grep vs a tiny integration smoke vs a dedicated terminal phase. Current lean: structural grep; planner can escalate to a terminal wiring phase (a sink node) when the integration is non-obvious.
- UK3 — Boundary-check strictness — strict file-scope (any diff outside `Owns` halts) vs semantic (allow formatting-only touches to neighbors). Current lean: strict file-scope, rg-checkable.
- UK4 — When an IF is discovered wrong mid-execute (consumers coded against a bad signature): re-dispatch all consumers, or invoke `up:uplan` to rewrite the graph. Plan/execute will decide.
- UK5 — Whether the wave scheduler needs an explicit "max parallelism" cap (e.g. don't dispatch >N implementers at once). Current lean: no cap; surface if we hit practical limits.

## Plan

Approach. Four disjoint doc edits across `uplan`, `implementer`, `uexecute`, `uverify`. Interfaces-as-plan-text are the integration points; no runtime coupling between these files, so all four phases dogfood wave-1 parallelism.

### Interfaces

- IF1 — `### Interfaces` subsection format in `## Plan`: bullet list of `IF<N> — signature — contract sentence`; one bullet per cross-phase contract; omit subsection when no cross-phase contracts exist.
- IF2 — `### Interface graph` subsection format in `## Plan`: one bullet per phase, grammar `PH<N>  <consumes-CSV> -> <produces-CSV>   @ <owned-paths-CSV>`; empty left = source, empty right = sink/wiring; omit subsection for single-phase plans.
- IF3 — `up:implementer` dispatch-input contract: fields `Owns: <paths>`, `Implements: <IFs>` (optional), `Consumes: <IFs>` (optional) appended to "What you receive"; `commit: defer` is the normal mode when dispatched as part of a wave.
- IF4 — Wave dispatch protocol in `up:uexecute`: read `### Interface graph`, topo-sort by `->` arrows into waves, within a wave verify `@`-disjointness then fire one `Agent` tool call per phase in a single response, serialize commits in PH order after all return.
- IF5 — Boundary check protocol: for each returned phase's commit, `git show <sha> --name-only` and assert every path ∈ the phase's declared `@` set; trespass → halt, log deviation, re-dispatch with tightened scope or escalate to `up:uplan`.
- IF6 — Wiring check protocol: after the final wave commits, for each IF declared in `### Interfaces`, grep callers of the IF's named symbol and verify signature match (or anchor presence for doc targets); mismatch → log under `## Conclusion → Deviations from plan` and either re-dispatch or escalate.
- IF7 — Verify-checklist rule: `up:uverify` Phase 1 checklist grows one CK per IF declared in the Plan's `### Interfaces`; each IF-check asserts the contract end-to-end (real call, structural match, or — for doc targets — anchor/reference lookup).

### Interface graph

- PH1  -> IF1, IF2                       @ plugins/up/skills/uplan/SKILL.md
- PH2  -> IF3                            @ plugins/up/agents/implementer.md
- PH3  -> IF4, IF5, IF6                  @ plugins/up/skills/uexecute/SKILL.md
- PH4  -> IF7                            @ plugins/up/skills/uverify/SKILL.md

(All sources: consume arrows are omitted because interfaces are plan-text and there is no runtime coupling between these four doc files — see design note on consume-arrow semantics. PC5 derives a single wave of four.)

### PH1 — uplan: interface-first grammar

- **1.1** `plugins/up/skills/uplan/SKILL.md:77` (modify) — "Required when relevant" list
  - Replace `- Execution batches: ...` with two entries: `- Interfaces: declare cross-phase contracts when ≥2 phases share a signature / anchor / API shape. Omit for single-phase plans.` and `- Interface graph: declare phase shape when ≥2 phases exist. Omit for single-phase plans.`
  - Respects: IV1, IV2, IV6, PC4, PC5
- **1.2** `plugins/up/skills/uplan/SKILL.md:82-112` (modify) — Format block
  - Delete the `### Execution batches` example line (PC4).
  - Insert `### Interfaces` and `### Interface graph` subsections into the format template with the grammar: `- IF<N> — <signature> — <contract sentence>` and `- PH<N>  <consumes> -> <produces>   @ <owned files>`.
  - Respects: IV1, IV2, PC2
- **1.3** `plugins/up/skills/uplan/SKILL.md:114-118` (modify) — replace section "When to declare batches" with "When to declare interfaces"
  - Points to cover: what counts as an interface (cross-phase signature, shared anchor, API shape, grammar); consume arrow semantics (runtime coupling, not semantic hand-wave — if phases are doc-only plan-text references, they are sources, not dependents); `@` paths are the filesystem boundary and must be disjoint across phases in the same wave; omit the whole subsection pair for single-phase plans.
  - Respects: PC1, PC2, PC5, UK1, UK2
- **1.4** `plugins/up/skills/uplan/SKILL.md:120-129` (modify) — Self-review item 6
  - Replace the `### Execution batches` disjointness item with: `If ### Interface graph is present, every phase declares @ <paths>; paths declared by phases in the same wave (phases that share a consumes set or are all sources) are disjoint; every IF consumed by any phase is defined in ### Interfaces; every IF defined is produced by exactly one phase.`
  - Respects: IV1, IV2, IV3
- Commit: `feat(uplan): interface-first plan grammar (replaces Execution batches)`

### PH2 — implementer: dispatch contract

- **2.1** `plugins/up/agents/implementer.md:8-10` (modify) — remove multi-phase bundle paragraph (bundles were a workaround for tight phase dependencies; interfaces now express those dependencies as consume arrows, and the wave scheduler handles ordering).
  - Respects: PC4 (replace, don't layer)
- **2.2** `plugins/up/agents/implementer.md:13-19` (modify) — "What you receive"
  - Add: `Owns: <comma-separated paths>` — files this phase may edit; anything outside is out of scope and will halt on the dispatcher's boundary check.
  - Add: `Implements: IF<n>, ...` (optional, present when the phase produces an interface).
  - Add: `Consumes: IF<n>, ...` (optional, present when the phase depends on another phase's produced artifact).
  - Rephrase `Commit mode` line: `commit: defer` is the normal mode in a wave dispatch; `commit: self` is for solo-phase or serial-fallback dispatches.
  - Respects: IV2, IV3, PC2
- **2.3** `plugins/up/agents/implementer.md:31` (modify) — Commit step
  - Simplify: `commit: self` → one commit, `commit: defer` → stage + report, as today. Drop the "one commit per phase, always — including when the dispatch is a multi-phase bundle" clause (bundles removed).
  - Respects: IV7
- **2.4** `plugins/up/agents/implementer.md:32` (modify) — remove "`defer` is only used for single-phase dispatches" clause (bundles removed; defer is now the wave-dispatch default).
- **2.5** `plugins/up/agents/implementer.md:47-48` (modify) — Forbidden list
  - Strengthen "Editing files outside the phase's scope" to reference `Owns` explicitly: `Editing any file outside the declared Owns set. The dispatcher runs a boundary check after your commit; trespass halts the wave.`
  - Respects: IV3, PC3
- **2.6** `plugins/up/agents/implementer.md:55-68` (modify) — Report Format, Variant A (self)
  - Drop the "(one Commit line per phase if the dispatch was a multi-phase bundle)" parenthetical.
- Commit: `feat(implementer): Owns/Implements/Consumes dispatch contract; drop bundle mode`

### PH3 — uexecute: wave dispatch, boundary + wiring

- **3.1** `plugins/up/skills/uexecute/SKILL.md:40-70` (modify) — replace "Per-batch loop" section with "Per-wave loop"
  - If `### Interface graph` present, derive waves via topo-sort over `->` arrows (sources = phases with no `Consumes`; wave N+1 = phases whose consumes are all produced by phases in waves 1..N); iterate wave by wave.
  - Before dispatching a wave: collect `@` paths from every phase in the wave; verify pairwise disjointness; on overlap halt and log under `### Deferred (needs user input)` (PC4, IV2).
  - Inner step loop (unchanged shape): dispatch → on return handle status → plan-diff check → consistency pass → mark completed.
  - Fallback: no `### Interface graph` → serial one-phase-at-a-time (IV6).
  - Respects: IV2, IV3, IV6, IV7, PC3, PC5
- **3.2** `plugins/up/skills/uexecute/SKILL.md:72-98` (modify) — "Dispatch per phase"
  - Replace `Commit mode: self | defer — default self; set defer only when this phase is in a parallel bundle per ### Execution batches` with `Commit mode: self | defer — self for solo-phase or serial-fallback dispatch; defer when the phase is in a multi-phase wave per ### Interface graph.`
  - Add bullets: `Owns: <paths>` (verbatim from the phase's `@` list), `Implements: <IFs>` (from `->` right side), `Consumes: <IFs>` (from `->` left side). Pass these to the implementer (IF3).
  - Delete the "Parallel dispatch: See Batched dispatch below ..." paragraph (section is replaced below).
  - Respects: IV3, IV4, IV5, PC5
- **3.3** `plugins/up/skills/uexecute/SKILL.md:100-122` (modify) — replace "Batched dispatch" section with "Wave dispatch"
  - Content: reading the graph (parse each `PH<N>  <consumes> -> <produces>   @ <paths>` line); wave derivation via topo-sort; disjointness check on `@`; dispatch one `up:implementer` per phase in the wave as concurrent `Agent` tool calls in a single response (AS1) with `commit: defer` (AS3); after all return, serialize commits in ascending PH order — for each: `git add <staged>` → `git commit -m <proposed>` → Boundary check (IF5) → plan-diff check → consistency pass.
  - Boundary check (IF5) expanded: `git show <sha> --name-only` must be a subset of the phase's declared `@` set; on trespass halt the wave, log under `### Deferred (needs user input)` with the trespassed path, and either re-dispatch with tightened scope or escalate to `up:uplan`.
  - Failure handling unchanged in spirit: a wave-sibling's `BLOCKED` / `NEEDS_CONTEXT` does not abort other siblings; wait for all, commit successes, then diagnose.
  - Respects: IV3, IV4, IV7, PC3
- **3.4** `plugins/up/skills/uexecute/SKILL.md` (insert, after "Wave dispatch" section) — new section "Wiring check"
  - Runs once, after the final wave's phases commit (IF6). For each `IF<n>` declared in the Plan's `### Interfaces`: grep the repo for the IF's named symbol (callers); verify each call site matches the declared signature. For doc targets (non-code IFs where the "signature" is a section anchor or declared public contract of a SKILL.md), grep for the declared anchor/reference and verify it resolves.
  - Mismatch → log under `## Conclusion → ### Deviations from plan` with `IF<n>: <mismatch>`; decide whether to re-dispatch the offending phase or invoke `up:uplan` (plan is wrong) or continue with a recorded deviation.
  - Respects: IV4, PC3, UK2
- **3.5** `plugins/up/skills/uexecute/SKILL.md:70` (modify) — "Batch only per `### Execution batches` ..."
  - Replace with: `Parallelism comes only from the Plan's ### Interface graph via the wave scheduler; never infer waves at runtime (IV4, PC5).`
- Commit: `feat(uexecute): wave dispatch with boundary and wiring checks`

### PH4 — uverify: CK per IF

- **4.1** `plugins/up/skills/uverify/SKILL.md:16-27` (modify) — Phase 1 checklist categories
  - Add a fourth category after Positive / Negative / Invariant: `Interfaces (CK): one check per IF declared in the Plan's ### Interfaces. Each asserts the contract end-to-end — a real call that exercises the declared signature (for code IFs), or a structural grep / anchor lookup that the declared contract is present and callable (for doc IFs). Reference the source as IF<n>.`
  - Respects: IV5, IF7
- **4.2** `plugins/up/skills/uverify/SKILL.md:28-43` (modify) — good-example checklist
  - Extend example with an Interfaces block: `Interfaces: - CK8 (IF1) — grep 'Parser.parse' callers → all match (arg: str) -> AST`, plus one more illustrative entry.
- **4.3** `plugins/up/skills/uverify/SKILL.md:77-97` (modify) — Phase 4 Format template
  - Add an `Interfaces:` block mirroring Positive/Negative/Invariants: one bullet per IF with `- CK<N> (IF<n>) — <how verified>`.
- Commit: `feat(uverify): add per-IF contract checks (CK per IF)`

### Order & dependencies

All four phases are sources in the interface graph (no `Consumes`). They share no `@` paths. PC5 derives a single wave of four. Executor dispatches four concurrent `up:implementer` agents, serializes commits in PH order.

### Risks / rollback

- RK1 — Wiring check as described is a grep; for doc IFs the "declared contract" may not have a single unambiguous anchor, leading to false negatives. Mitigation: PH3 section states grep-based wiring is the default and planners can escalate to a dedicated sink phase (a terminal `IF<n> ->` row) when the IF's contract is structural and grep can't capture it; follow-up task if this bites.
- RK2 — Removing the `|| / →` batch grammar is a hard break (PC4, AS6). Any external user with a mid-flight task using the old grammar has to re-plan. Mitigation: design confirmed hard-break acceptable; mention in README if it materially affects external users (deferred to the docs-refresh pass after review).
- RK3 — Bundles removed in PH2; if a future task genuinely needs "one implementer, two commits in sequence" (tight dep not expressible as an IF), the pattern has to come back. Mitigation: interfaces-as-plan-text makes this unlikely; if it happens, treat as a new design.

### Backwards-compat check

Per design AS6: all `docs/tasks/*.md` in this repo are `done`; no in-flight task uses `### Execution batches`. PH1 removes the grammar from the Format; PH3 removes the code path that dispatched by batch. External users' plans with old grammar execute via the serial fallback (IV6) because `### Interface graph` is absent — they do not crash, just run serially. One-line mention in README docs-refresh after review.

## Verify

**Result:** passed

Positive:
- CK1 — `### Interfaces` and `### Interface graph` subsections documented in `uplan/SKILL.md:111, 115` with the grammar `- IF<N> — <signature> — <contract>` and `PH<N>  <consumes> -> <produces>   @ <paths>`.
- CK2 — Topo-sort wave derivation described in `uexecute/SKILL.md:42, 106-109` (source phases form wave 1; wave N+1 consumes are produced by 1..N).
- CK3 — Boundary check documented in `uexecute/SKILL.md:124` (`git show <sha> --name-only` ⊆ `@` set; halt on trespass).
- CK4 — Wiring check documented in `uexecute/SKILL.md:135-146` (per-IF grep + signature/anchor match).
- CK5 — `up:implementer` accepts `Owns` / `Implements` / `Consumes` at `implementer.md:17-19`.
- CK6 — `up:uverify` Phase 1 Interfaces (CK) category at `uverify/SKILL.md:25`; Phase 4 Format Interfaces block at `:99-101`.

Negative:
- CK7 — No references to `### Execution batches`, `Batched dispatch`, "multi-phase bundle", or `||`/`→` batch grammar anywhere under `plugins/up/`.

Invariants / assumptions:
- CK8 (IV6) — Serial fallback preserved: `uexecute/SKILL.md:42, 44` dispatch serially when `### Interface graph` absent.
- CK9 (IV7) — One commit per phase: `uexecute/SKILL.md:122-123` (dispatcher commits per phase in wave), `implementer.md:32` (one commit per `commit: self` phase).

Interfaces:
- CK10 (IF1) — `### Interfaces` grammar: `uplan:112-113` defines; `uverify:25` and `uexecute:140` reference it by name; shapes consistent.
- CK11 (IF2) — `### Interface graph` grammar: `uplan:116-118` defines; `uexecute:104` parses same grammar; example corrected in c762c10 (removed double-arrow typo).
- CK12 (IF3) — Implementer dispatch-input contract: `implementer.md:17-20` declares `Owns`/`Implements`/`Consumes`/`commit mode`; `uexecute:82-85` passes the same four fields — field names match exactly.
- CK13 (IF4) — Wave dispatch protocol: `uexecute:99-133` (parse graph → derive waves → disjointness → concurrent `Agent` calls → serialized commits).
- CK14 (IF5) — Boundary check protocol: `uexecute:124` (`git show <sha> --name-only` subset check, halt on trespass).
- CK15 (IF6) — Wiring check protocol: `uexecute:135-146` (per-IF grep of callers/anchors, signature match, mismatch → Deviations from plan).
- CK16 (IF7) — Verify-checklist rule: `uverify:25` new category; `uverify:99-101` Format template.

Dogfood smoke: the task's own plan declared `### Interface graph` with 4 source phases (PH1-PH4, pairwise-disjoint `@` paths); executor derived wave-1, verified disjointness, dispatched 4 concurrent `up:implementer` agents with `commit: defer`, then serialized commits in PH order — 38c2cf7 (PH1 uplan) → 37d1432 (PH2 implementer) → 6ba3b9d (PH3 uexecute) → 364c8ea (PH4 uverify). Boundary check per commit: each diff ⊆ its declared `@` (confirmed via `git show --name-only`). Wiring check across the final tree: IF1/IF2/IF3 cross-file references consistent; grammar example fix (c762c10) landed during verify. Full new workflow end-to-end on itself.

Notes: one inline verify fix — the `### Interface graph` example in `uplan/SKILL.md` had a double `->` typo and a `(source)` literal that wasn't part of the grammar; fixed in c762c10 (see CK11).

## Conclusion

Outcome: interface-first planning replaces `### Execution batches` across uplan / implementer / uexecute / uverify; new grammar `PH<N>  <consumes> -> <produces>   @ <owns>` drives wave dispatch with Boundary + Wiring checks. Landed in 26465a3 (tip).

Invariants:
- IV1 — `### Interfaces` grammar defined in `uplan/SKILL.md:111-113`.
- IV2 — `### Interface graph` grammar + `@ <paths>` requirement in `uplan/SKILL.md:115-118, 125`.
- IV3 — Boundary check: `uexecute/SKILL.md:124`.
- IV4 — Wiring check: `uexecute/SKILL.md:135-146`.
- IV5 — ≥1 CK per IF: `uverify/SKILL.md:25, 99-101`.
- IV6 — Serial fallback preserved: `uexecute/SKILL.md:42, 44`.
- IV7 — One commit per phase: `uexecute/SKILL.md:122-123`, `implementer.md:32`.

### Assumptions check
- AS1 — held — dogfood run produced a 4-way wave-1 (vs. likely ≤2 under file-path batching, given coarse per-skill scope).
- AS2 — held — IF1-IF7 written up front in plan, implementers matched signatures without re-plan.
- AS3 — held — all four implementer commits' `--name-only` ⊆ declared `@`.
- AS4 — held for this doc task — grep of IF symbol names across the repo matched exactly the declared contracts.
- AS5 — held — SKILL.md section anchors / format blocks functioned as interfaces without grammar strain.
- AS6 — held — `git grep "Execution batches"` post-change empty; no other task files reference the old grammar.

### Unknowns outcome
- UK1 — resolved: plan-text only; no PH0 stub phase needed for this restructure.
- UK2 — resolved for doc targets: structural grep was sufficient; code-target mechanism remains the planner's per-task call.
- UK3 — resolved: strict file-scope (`git show --name-only` subset check).
- UK4 — still-open: not triggered in this task; escalation path documented as "re-dispatch or invoke `up:uplan`" in IF6.
- UK5 — still-open: no cap introduced; 4-way parallel worked cleanly. Revisit if we hit practical limits.

Review findings:
- Important: 3 resolved in 26465a3 — (1) `uplan:124` `(source)` literal contradicted empty-left grammar → rephrased to empty-left convention; (2) `uexecute:83-85` listed `Owns`/`Implements`/`Consumes` unconditionally in "Dispatch per phase" despite serial fallback not having them → collapsed to one conditional bullet pointing to Wave dispatch; (3) `plugin.json` still at 0.3.0 → bumped to 0.3.1 per CLAUDE.md patch-bump-on-landing rule.

### Hands-off decisions
- make: size=Medium — multi-skill restructure (uplan, uexecute, uverify); hands-off default.
- make: dedicated branch + worktree at .worktrees/interface-first-parallel — hands-off safest-reversible default.
- uplan: plan auto-approved (hands-off).
- ureview: fixed `uplan:124` `(source)` literal — rephrased to empty-left convention.
- ureview: fixed `uexecute:83-85` unconditional dispatch contract — collapsed to one conditional bullet.
- ureview: fixed `plugin.json` version 0.3.0 → 0.3.1 per CLAUDE.md patch-bump rule.

### Deferred (needs user input)
<empty>

## Seed (from /up:make args)

Prior work added batch execution and parallelization, but execution still trends sequential. Proposed shift:

1. Plan defines interfaces. As many components as possible should be developable knowing only the interfaces.
2. Phases build components that implement those interfaces.
3. Executor dispatches as many implementers in parallel as possible.
4. Executor checks each implementer didn't alter internals of components outside its assigned scope.
5. Executor checks components wire together as intended after implementers finish.
6. Verify also checks interfaces.

Hypothesis: explicit interface separation and independent execution improves both planning and execution quality, for free.
