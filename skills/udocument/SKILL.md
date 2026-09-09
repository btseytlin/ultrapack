---
name: udocument
description: Use when writing or editing documentation — project docs, CLAUDE.md, READMEs, SKILL.md, docstrings, inline comments. Auto-triggers on `.md` files and docstring edits. Enforces lead-with-why, kill stale content, lists over tables, no aspirational sentences.
---

# Document

Documentation explains how to use and maintain the system. Apply these rules to project docs, agent guidance, skills, docstrings, and comments.

## Core rules

- Lead with the problem or purpose, then describe behavior and usage.
- Prefer one concrete example over repeated explanation.
- Remove stale descriptions of behavior that no longer exists. Do not add historical notes to preserve them.
- Document supported behavior, not aspirations.
- Use lists instead of tables unless the user requests a table.
- Write short, grammatical sentences. Remove framing and repeated instructions.
- State concrete constraints. "Dataset must not import training" is clearer than "respect boundaries".
- Consolidate duplicated guidance and link to its owner.

## Project docs

Answer what the project does, why it exists, how to use it, and where related documentation lives. Include a minimal working example. Keep a README under 200 lines, moving detail into `docs/` when needed.

## Agent guidance

Put project-wide rules, constraints, style preferences, and pointers in `CLAUDE.md` or its equivalent. Per-task instructions belong in `docs/tasks/<slug>.md`.

## Skills

- Preserve `name` and `description` frontmatter. The description determines when an agent loads the skill.
- Cover when to use it, the process, key rules, required output, and terminal state.
- Use descriptive headings. Aim for a body under about 150 lines without removing required behavior.

## Docstrings

For a large class or module, explain its responsibility and boundaries:

```python
class DatasetBuilder:
    """Build dataset shards from raw episodes.

    Validate inputs, transform records, and checkpoint progress.
    Training-time loading belongs in training/loader.py.
    """
```

For a small utility, one line is enough. Omit docstrings that merely repeat an internal helper's name.

## Inline comments

Explain non-obvious reasons: a workaround, required ordering, hidden invariant, or surprising choice. Remove narration such as `# increment counter`, change-history notes, and placeholder apologies.

Keep a concrete historical cause when it explains a current constraint. "Guard against overflow that corrupted billing totals" explains a guard. "Added in the billing cleanup" does not.

## Process

1. Identify the audience and the question the document must answer.
2. Choose a list, example, or paragraph that fits the content.
3. Draft concise instructions grounded in the implementation.
4. Remove text that adds no instruction or explanation. Do not cut to a percentage target.
5. Include a concrete example where it helps the reader act.
6. Check references and remove stale, aspirational, or duplicated claims.
