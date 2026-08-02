---
name: attack-loop
description: "Run a bounded implement-attack-repair loop for a user-specified task. Use when work needs repeated independent criticism: perform the task, dispatch a fresh attacker, verify significant findings, repair them, and stop on a clean attack or the user's round limit."
---

# Attack loop

Use this standalone workflow when a task needs independent adversarial passes without an `up-make` task file.

## Require a bounded contract

Require these inputs in the user's request:

- Target work — free-form description of what to do.
- Maximum rounds — positive whole number of attacker passes.
- Stop condition — observable condition that defines a clean completion.

Ask before acting if any input is missing or ambiguous. Do not invent defaults.

Pick an authority level before the initial work and state it in the first update:

- Read-only — inspect and report; do not change files or external state.
- Write and probe — change workspace files and run temporary verification probes.
- Full task authority — take actions the request already authorizes, including external writes.

Change authority between rounds only when the request authorizes it. Report each change. Stop when the next needed action exceeds authority.

Example:

```
Use $attack-loop to add CSV import validation. Run at most 3 rounds. Stop when malformed rows fail loudly and a fresh attack finds no confirmed defect.
```

## Run one independent attack per round

1. Perform or repair the target work under the current authority.
2. Dispatch one fresh attacker. Pass the absolute working directory, target work, constraints, stop condition, current authority, and raw current artifacts or diff.
3. Do not pass controller rationale, proposed fixes, or earlier attacker reports. The attacker must form an independent view from the current state.
4. Give the attacker only the current authority. It may run probes but must not repair the deliverable or alter external state solely to manufacture a finding.
5. Have the attacker attack, not confirm. Adapt `uverify`'s categories: valid-input edge cases, invalid-input rejection, stated invariants and contracts, real callers and outputs, state/order/retry behavior, and the shortest end-to-end smoke path.
6. Require each attack to name the hypothesized bite and run an appropriate probe or inspection. Capture real output. An unavailable probe is a coverage gap, never a passing result.

Require this attacker report:

```
Attacks run:
- <hypothesis> — held | broke: <evidence>

Findings:
- F<n> — <severity, violated condition, concrete bad path, evidence, expected behavior>

Coverage gaps:
- <unrun necessary attack and blocker>
```

An attacker may return no findings. Do not require a defect, reword a prior concern, elevate a style preference, or call missing tests a bug without a violated requirement. Unsupported risks belong under coverage gaps or no report.

## Defend findings fairly

For every finding, restate it, verify it against the current artifact, and classify it before changing anything:

- Fix — reproduced break, violated contract or invariant, or highly certain defect with a concrete bad path; material and in scope.
- Record — unsupported, duplicate, cosmetic, hypothetical, or out of scope; do not repair it merely to extend the loop.
- Defer — potentially material but blocked by missing authority, infrastructure, or user direction; do not treat the round as clean.

For a reproduced failure, use `udebug` before editing: reproduce, trace root cause, test one hypothesis, then make one root-cause repair. Re-run the reproduction and relevant checks after the repair. Sweep for the same defect pattern when the root cause can recur.

Do not accept a finding blindly. Do not add a workaround, fallback, dependency, or refactor unless the verified defect requires it and the task scope permits it.

## Stop only on evidence

Start another round after every repair. Stop early only when both hold:

- The explicit stop condition has direct evidence.
- The latest fresh attacker found no confirmed significant defect and no blocking coverage gap.

Stop as `limit reached` after the maximum round count. Do not call this a clean completion unless both conditions above already hold.

Stop as `blocked` when authority is insufficient, required evidence cannot be obtained, the task needs a material user decision, or `udebug` reaches three failed repairs for one defect.

If the stop condition passes before an attack, still run one fresh attack before declaring completion.

## Report every round and the outcome

Before work, state target work, maximum rounds, stop condition, and authority.

After every attack, report one compact update:

```
Round <n>/<max> — <authority>
- Confirmed: <finding IDs and decisions>
- Recorded or deferred: <IDs and reason>
- Next: repair | next attack | clean | limit reached | blocked
```

Finish with:

- Outcome: `clean`, `limit reached`, or `blocked`.
- Stop-condition evidence.
- Authority timeline.
- Round ledger: attacks, confirmed findings, repairs, and verification.
- Deferred coverage gaps and required next action.

Never claim success from passing unit tests, a clean diff, an attacker assertion, or an unrun smoke path.

## Terminal state

Report the final outcome and leave the user with evidence for any remaining action. Do not create a task file or invoke `ureview` as part of this standalone loop.
