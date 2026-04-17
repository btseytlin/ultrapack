---
name: udocument
description: Use when writing or editing documentation — project docs, CLAUDE.md, READMEs, SKILL.md, docstrings, inline comments. Auto-triggers on `.md` files and docstring edits. Enforces lead-with-why, kill stale content, lists over tables, no aspirational sentences.
---

# Document

Documentation is code's second user-facing surface. Treat it with the same care.

## Scope — when this skill applies

- Project documentation (`README.md`, `docs/**/*.md`)
- CLAUDE.md / AGENTS.md / GEMINI.md instructions
- SKILL.md files for skill packs
- In-code docstrings (classes, modules)
- Inline code comments

## Core rules — apply to every form of documentation

<rules>
- Lead with the why. What problem does this solve? Why does this exist? Answer before describing what.
- Show, don't tell. One concrete example beats three paragraphs of description.
- Kill stale content. If a doc describes behavior that doesn't exist anymore, delete — don't "update" with a note.
- No aspirational sentences. "This system will eventually support X" — either it supports X now, or it doesn't belong in the doc yet.
- Lists over tables. Tables render inconsistently in many viewers and are hard to edit. Lists unless the user explicitly wants a table.
- Be terse. Sacrifice grammar for brevity. Short sentences. No "In this section we will discuss..."
- Concrete always beats abstract. "The `Dataset` class must not import from `training/`" beats "respect module boundaries."
</rules>

## Project docs (README.md, docs/) — answer four questions

<project-doc-questions>
1. What is this?
2. Why does it exist?
3. How do I use it (minimum-viable example)?
4. Where does it fit (links to related docs)?
</project-doc-questions>

Keep READMEs under 200 lines. More than that → split into `docs/`.

## CLAUDE.md / AGENTS.md — project-wide agent guidance

- Principles and constraints that apply across the project
- One-line style preferences ("no markdown tables unless asked")
- Pointers to key files or scripts
- What NOT to do (often more useful than what to do)

Do **not** write per-task instructions here. Those belong in `docs/tasks/<slug>.md`.

## SKILL.md — the frontmatter is load-bearing

- Frontmatter: `name`, `description`. The `description` is the auto-trigger signal — make it specific and action-oriented.
- Short body: when to use, process, key rules, terminal state.
- Section headers should summarize the section. A reader who skims headers should know the gist.
- Target under ~150 lines. A skill the agent won't read is worse than no skill.

## In-code docstrings — for large classes and modules, describe responsibility AND non-responsibility

Every large class or module gets a docstring explaining **what it's responsible for and what it is not**:

```python
class DatasetBuilder:
    """Build dataset shards from raw episodes.

    Responsibilities:
    - Orchestrate download → process → encode → verify stages
    - Persist per-episode progress for restart
    - Validate schema at stage boundaries

    Not responsibilities:
    - Training-time data loading (see training/loader.py)
    - Cloud sync (see ops/sync.py)
    """
```

For small utility functions, one-line docstring is enough. For short internal helpers, no docstring required.

## Inline comments — reserved for non-obvious WHY

<good-inline>
- Workarounds for specific bugs: `# sklearn 1.4.x requires args in this order`
- Hidden invariants or contracts: `# caller guarantees items is sorted`
- Counter-intuitive choices that would look like bugs otherwise
</good-inline>

<bad-inline>
- Narrating what the code does: `# increment counter` next to `i += 1`
- Historical context: `# added for the Y flow` — belongs in the commit message
- Placeholder apologies: `# TODO: clean up later`
</bad-inline>

## Red flags — cut these when you see them

<system-reminder>
- Aspirational content — cut
- Stale content describing removed behavior — delete, don't annotate
- Walls of tables — convert to lists
- Paragraphs longer than ~4 sentences — split or cut
- Duplicate content across docs — consolidate and link
- Comments explaining the obvious — delete
</system-reminder>

## Process — six steps, always including "cut 30%"

<required>
1. Understand the audience (new contributor? operator? agent?)
2. Decide the shape (list, example, paragraph) based on content type
3. Draft terse
4. Cut 30%. Seriously. Re-read and cut 30%.
5. Show one concrete example if none present
6. Verify nothing is stale or aspirational
</required>
