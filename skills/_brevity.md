# Brevity principles for long-lived artifacts

Apply to code, comments, docstrings, skill descriptions, task files, documentation, and commit messages. Keep the information needed to use, audit, or maintain the artifact.

## Principles

1. Omit empty or default-only sections. Do not fill them with "none", "no findings", or placeholders.
2. Summarize routine passed checks in one line. Attach evidence to failures, deferrals, and surprising results.
3. Do not retell the diff or conversation. Use the commit and file references for changes. Explain decisions, deferred work, and constraints the diff cannot express.
4. Use one sentence per outcome or reason unless more is needed to explain a material fact.
5. Keep task files proportional to the work. Aim for one screen for a small task and three for a medium task, without hard word limits.
6. Remove text that needs the original conversation to make sense. Keep operational requirements, cross-file references, and non-obvious reasons.

## What to keep

- "Dispatched from up:ureview" identifies a real workflow relationship.
- "The reviewer receives the diff and plan, without the controller's rationale" defines an operational constraint.
- "This guard prevents integer overflow in billing totals" explains a non-obvious reason.

Remove narration such as "kept here as a record of our discussion" or a comment that only restates the code. A configured value does not need a comment listing alternatives rejected in chat.

## Compression

- Say each rule once. Keep elaboration only when it adds a necessary condition or example.
- Use one name per concept.
- Lead with the result or decision. Remove self-narration and empty qualifiers.
- Ask at most one closing question.
- Use a contrast only when it rules out a plausible mistake. Do not invent an opposing claim just to negate it.

## Checklist before saving

- Does every section add information needed by a reader without the conversation?
- Can repeated instructions be removed without losing a requirement?
- Are references and necessary context explicit?
- Do failures, deviations, deferrals, and risks still explain what happened and why?

## Exception — never abbreviate these

Failures, deviations from plan, deferrals, and known risks always carry evidence and a reason. Brevity must not hide a finding or remove the steps needed to act on it.
