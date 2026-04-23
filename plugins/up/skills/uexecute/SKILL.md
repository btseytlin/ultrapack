---
name: uexecute
description: Use to write or update an FR document. Reads the coverage plan, follows WRITING_GUIDE.md format exactly, sources every claim from OpenAPI/code/DB, marks unknowns as open question stubs. Dispatches up:explorer to trace endpoints when needed.
---

# Document FR

Write the FR document for one plan phase. Every claim is sourced. Every unknown is a stub with an open question. The document becomes done only after `up:uverify` confirms it against the real endpoint.

## Before starting

<required>
1. Read `docs/tasks/<slug>.md` — the plan tells you what to write for this phase.
2. Read `docs/FR/WRITING_GUIDE.md` — format rules are mandatory, not guidelines.
3. Dispatch `up:explorer` with the endpoint name to get: route, controller, service, OpenAPI entry, DB fields.
4. Read `docs/context.md` section 7 for any open questions on this scenario.
5. Check `context.md` section 4 — confirm the scenario is in scope before writing.
</required>

## Source hierarchy

Always prefer higher-ranked sources. Never descend to a lower rank if a higher one is available.

1. Recorded curl response from `up:uverify` (highest — actual system behavior)
2. Source code (controller + service)
3. OpenAPI spec (`OpenApi/*.json`)
4. `DECOMPOSITION.md` stakeholder comments
5. Memory / assumption — never use

## Writing process

<required>
For the current plan phase:

1. Create the file at `docs/FR/<code>. <name>.md` (exact naming per `WRITING_GUIDE.md`).
2. Add Confluence metadata macro and version history macro.
3. Write `## Контекст` if the endpoint's purpose needs explanation.
4. Write `## Конфигурация` if there are env variables or config parameters.
5. Write `## Формат запроса` from the actual `routes.php` + OpenAPI spec entry.
6. Write `## Алгоритм` step by step, sourced from the controller/service code:
   - Each step that calls DreamCRM API: include inline HTML auth header table + body macro + GEN-01-02 reference.
   - Each step that calls DreamCRM Accounting API: use `X-Api-Key = DREAMCRM_ACCOUNTING_API_KEY`.
   - Each unknown or unconfirmed step: write `> **Открытый вопрос Q-NN:** <what is unknown>` — do not write a guess.
7. Write `## Таблица маппинга БД` if the response includes user fields (always 3 columns).
8. Self-review against WRITING_GUIDE.md checklist (see below).
9. Commit: `doc: draft <code> <name>`.
10. Update `context.md` section 5 with the new document status.
</required>

## Open questions — exact format

When a piece of behavior is unknown or unverified:

```markdown
> **Открытый вопрос Q-01:** <what is unknown and why it matters>
```

Then add to the task file as `UK<N> — <same text>`.

Never write a placeholder algorithm step where the behavior is unknown. A step with wrong behavior is worse than an explicit open question.

## DreamCRM call format

Every DreamCRM External Integrations API call in the algorithm must have all four elements:

```
N. Выполнить запрос POST {DREAMCRM_BASE_URL}/api/v1/crm-external-integrations/[путь]
   (см. [Описание переменных окружения](<URL>)).
   В заголовках запроса передать:

   <table><colgroup><col><col></colgroup><tbody><tr><th>Наименование</th><th>Комментарий</th></tr><tr><td>X-Api-Key</td><td>= DREAMCRM_API_KEY (см. <a href="...">Описание переменных окружения</a>)</td></tr></tbody></table>

   В body передать:
   :::CONFLUENCE-MACRO ...
   В случае ошибки DreamCRM применить политику retry (см. [GEN-01-02. Обработка ошибок DreamCRM, retry](<URL>)).
```

Missing any of these four elements → format error, not a style nit.

## Algorithm format rules

- Steps: numbered list, 3-space indent for sub-steps.
- Conditions: always "Если ..., то ...". Never "в случае если", "при условии что".
- Quotes: always `"double"`, never `'single'`.
- No `###` headings inside algorithm sections.
- DB fields: always verified against `docs/DB_description.md` before writing.

## Self-review checklist before committing

<required>
- [ ] DECOMPOSITION.md scenario comments reflected
- [ ] All DB fields verified against real schema
- [ ] All request/response fields verified against OpenAPI or code
- [ ] All routes confirmed in `routes.php`
- [ ] All HTTP codes and error values explicit
- [ ] No vague formulations ("как правило", "обычно", "может быть")
- [ ] All DreamCRM calls have: method, header table, body macro, GEN-01-02 reference
- [ ] DB mapping table has 3 columns
- [ ] Confluence metadata and version history macros present
- [ ] context.md section 5 updated
</required>

## Hands-off mode

Dispatch `up:explorer` without prompting. Log each defaulted decision. Any ambiguity with no safe default → log under `### Deferred (needs user input)` and continue with the next document.

## Terminal state

FR document written, self-reviewed, committed. Invoke `up:uverify`.
