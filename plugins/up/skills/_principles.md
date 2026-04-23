# SA Global Principles

SAPC1–SAPC8. Apply to every FR task. Deviations name the SAPC and the reason in one line.

- **SAPC1 — Verify-driven documentation.** An FR is not complete until the real endpoint returns a real response to a real curl. "Looks right" is not verified. Like TDD: describe → validate → update.
- **SAPC2 — Every claim has a source.** OpenAPI spec, source code, DB schema, or recorded curl response. Never write from memory or assumption.
- **SAPC3 — Gaps are first-class artifacts.** Unknown behavior = open question stub (`> **Открытый вопрос Q-NN:**`), never a guess. Document the unknown explicitly; don't paper over it.
- **SAPC4 — As-is and to-be are always distinct.** When documenting a system in transition, never mix current and target behavior in the same requirement block. Label which state each section describes — "current system", "target system", or the specific version/integration names relevant to the project.
- **SAPC5 — Single source of truth.** `context.md` for project state and open questions. `WRITING_GUIDE.md` for FR format. `DECOMPOSITION.md` for scope decisions. When sources conflict, OpenAPI and running code win over prose.
- **SAPC6 — Scope discipline.** Out-of-scope scenarios are never described. Check `context.md` section 4 before starting any FR. If the scenario isn't in scope, stop.
- **SAPC7 — Stubs over speculation.** If the spec isn't ready, write a stub with an explicit open question. Never guess at behavior that isn't confirmed by a source.
- **SAPC8 — Format is not optional.** Follow `WRITING_GUIDE.md` exactly. A requirement in wrong format will be rejected in review. Format compliance is checked by `up:reviewer` before publication.

## How to use

- `up:udesign` — surface SAPC scope decisions; record gaps as UK (unknowns); mark as-is vs to-be boundary.
- `up:uexecute` — every algorithm step cites its source (SAPC2); unknown steps are open question stubs (SAPC3, SAPC7); as-is/to-be labeled (SAPC4).
- `up:uverify` — the only acceptable evidence is a real curl response (SAPC1). Do not claim pass without running it in this session.
- `up:udebug` — diagnose mismatches between FR claims and curl evidence; follow SAPC2 to trace root cause.
