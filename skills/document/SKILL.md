---
name: document
description: Use when writing or editing documentation — project docs, CLAUDE.md, READMEs, SKILL.md, in-code docstrings and comments. Auto-triggers on .md files and when adding or editing docstrings.
---

# Document

Documentation is code's second user-facing surface. Treat it with the same care.

## Scope

This skill applies to:
- Project documentation (`README.md`, `docs/**/*.md`)
- CLAUDE.md / AGENTS.md / GEMINI.md instructions
- SKILL.md files for skill packs
- In-code docstrings (classes, modules)
- Inline code comments

## Core rules

- **Lead with the why.** What problem does this solve? Why does this exist? Answer before describing what.
- **Show, don't tell.** One concrete example beats three paragraphs of description.
- **Kill stale content.** If a doc describes behavior that doesn't exist anymore, delete — don't "update" it with a note.
- **No aspirational sentences.** Don't write "this system will eventually support X." Either it supports X now, or X doesn't belong in the doc yet.
- **Lists over tables.** Tables render inconsistently in many viewers and are hard to edit. Use lists unless the user explicitly wants a table.
- **Be terse.** Sacrifice grammar for brevity. Short sentences. No filler. No "In this section we will discuss..."
- **Concrete always beats abstract.** "The `Dataset` class must not import from `training/`" beats "respect module boundaries."

## Project docs (README.md, docs/)

Every piece should answer:
1. What is this?
2. Why does it exist?
3. How do I use it (minimum-viable example)?
4. Where does it fit (links to related docs)?

Keep READMEs under 200 lines. If you need more, split into `docs/`.

## CLAUDE.md / AGENTS.md

- Principles and constraints that apply across the project
- One-line style preferences ("no markdown tables unless asked")
- Pointers to key files or scripts
- What NOT to do (often more useful than what to do)

Do **not** write per-task instructions here. Those belong in `docs/tasks/<slug>.md`.

## SKILL.md

- Frontmatter: `name`, `description` (the description is the auto-trigger signal — make it specific and action-oriented)
- Short body: when to use, process, key rules, terminal state
- Keep under ~150 lines where possible. A skill the agent won't read is worse than no skill.

## In-code comments

### Docstrings (classes, modules, public functions)

Every large class or module gets a docstring explaining its **responsibility** and **non-responsibility**:

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

### Inline comments

Reserved for **non-obvious WHY**. Good cases:
- Workarounds for specific bugs (`# sklearn 1.4.x requires args in this order`)
- Hidden invariants or contracts (`# caller guarantees items is sorted`)
- Counter-intuitive choices that would look like bugs otherwise

Bad cases (delete these):
- Narrating what the code does (`# increment counter` next to `i += 1`)
- Historical context (`# added for the Y flow`) — goes in the commit message
- Placeholder apologies (`# TODO: clean up later`)

## Red flags

- Aspirational content — cut it
- Stale content describing removed behavior — delete, don't annotate
- Walls of tables — convert to lists
- Paragraphs longer than ~4 sentences — split or cut
- Duplicate content across docs — consolidate and link
- Comments explaining the obvious — delete

## Process

1. Understand the audience (new contributor? operator? agent?)
2. Decide the shape (list, example, paragraph) based on content type
3. Draft terse
4. Cut 30%. Seriously. Re-read and cut 30%.
5. Show one concrete example if none present
6. Verify nothing is stale or aspirational
