---
name: job-guardian
description: Use to babysit a long-running process (training run, batch job, migration, deploy) on a remote pod or locally while the user is away. Defines a launch contract, gates on immediate crash, polls for stability, triages anomalies as recoverable (fix + resume) or not (tear down + notify). Auto-triggers when the user asks you to launch a job and watch it / keep it alive / shut it down if it dies.
---

# Job Guardian

You are taking custody of a process the user will not be watching. Their trust is: it runs to completion, or it dies cleanly and you tell them why — never silently burning a pod for hours on a job that crashed in minute two.

**Iron law:** silence is not success. You confirm liveness and progress by reading evidence (log growth, metrics, exit codes), never by assuming. A poll that returns "still no error" is not the same as "still making progress."

## Away by default

Assume the user is gone the moment they hand you the job — before launch, during the run, after teardown. You do not ask questions, ever. Not at intake, not mid-flight, not at the end. This skill runs under the `handsoff` contract: infer the contract from context, take the safest reversible path, never invent a value where none exists, and log every choice for one end-of-task review.

- **Never ask a question.** Not even at intake. If a required fact has a conservative reading from context, use it and log the choice. If it has none, do not guess (handsoff no-default rule).
- **Structural blocker before launch → stop, don't launch.** Log it under `### Deferred (needs user input)` and notify. A pod you didn't start costs nothing; a job launched on a guessed config can burn hours.
- **Ambiguity while running → take the reversible side.** Pause/checkpoint over kill, `stop` over destroy, keep-alive over a recovery you're unsure of. When unsure whether an action is reversible, assume it isn't.
- **Tell the user at the end.** Surface the decision log and any deferred items in the terminal notification + written record (Phase 5). That review replaces the questions you didn't ask.

## When to invoke

Any process that outlives a single foreground command and will run while the user is away or asleep:
- Remote training run / sweep on a rented pod (RunPod, vast.ai, Lambda)
- Long batch / data pipeline, migration, backfill, eval harness
- Any "launch it and shut it down if it dies" request

For remote work, also read `remote-ssh` (nohup launch, log redirection, connection reuse). For training specifically, `ml-experiments` owns the pre-launch checks — run those first; this skill takes over once the job is live.

## Phase 0 — Contract (before launching anything)

You cannot guard a process whose health you can't define. Derive these from what the user gave you and the repo (their instructions, configs, `train.py`, env, prior runs), per Away by default.

<required>
1. **Launch command** — exact command, working dir, env. Take it as the user wrote it (handsoff rigid path); never reword it into something "equivalent." Output must be captured to a file (GPC5; never run-then-grep).
2. **Liveness signal** — how you know it's still running (PID alive, container up, log mtime advancing).
3. **Health signal** — how you know it's making *progress*, not just alive: step count climbing, loss finite and trending, throughput > 0, rows written increasing. A hung process is alive but not healthy. If the log gives no progress signal you can read, that's a structural blocker — say so before launch, don't guess one.
4. **Done signal** — what successful completion looks like (exit 0, "training complete", checkpoint N saved, expected row count).
5. **Recovery playbook** — for each failure you can anticipate, the fix. (OOM → lower batch size / grad-accum; transient network/NCCL → retry; NaN loss → restart from last checkpoint; disk full → clean + resume.) Anything not on this list is unrecoverable by default — escalate, don't improvise.
6. **Teardown command** — the exact command to release resources. Asking this skill to "shut it down if it dies" authorizes the *reversible* teardown — `runpodctl stop pod <id>` (pausable, keeps the disk). It does NOT authorize destroying state: no `remove pod` / terminate unless the user named that command explicitly. When in doubt, stop, don't destroy.
7. **Budget / stop conditions** — max wall-clock or spend, max recovery attempts per failure class. If the user gave a number, use it. If not, this is a no-default value — don't invent a cap; default the *behavior* to the safe side (on repeated unexplained failure, stop + tear down rather than restart-loop) and log that you had no explicit budget.
8. **Notify-on** — terminal events that pull the user back: done, torn down, gave up. Routine progress does not.
</required>

### Contract file (mandatory)

Always write the contract to a file before launch — no exceptions, even for "quick" jobs. The file is what a fresh session (or the user at 7am) reads to know what you committed to; skipping it means the run is unguarded the moment this session compacts or dies.

- Path: `docs/jobs/<slug>.md`. If a task file exists for this work, append the contract there instead under `## Job guardian contract`.
- Contents: all 8 contract items above, the launch timestamp, PID/container id once known, log path, and the two handsoff lists (`### Hands-off decisions`, `### Deferred (needs user input)`).
- Do not launch until the file is written. The file is the gate.

**Keep the file live.** Any time the instructions change — user sends new guidance, you revise the recovery playbook, budget shifts, teardown command updates, a deferred item gets resolved — update the file immediately and log the change under `### Hands-off decisions` with a timestamp. The file is the single source of truth for the contract; if it disagrees with what you're actually doing, the file wins or you fix it.

## Phase 1 — Setup

Do the prep the job needs, idempotently (GPC5): env / deps installed, data and checkpoints in place, output dir and log path created, secrets present (`.env`, never hardcoded). Verify the launch command exists and is runnable *before* committing to it. For remote: confirm the pod is reachable and connection multiplexing is up (`remote-ssh`).

## Phase 2 — Launch + crash gate

Launch with output redirected to the log file. Then **do not leave** until you've cleared the immediate-crash window — most failures (bad path, OOM on first batch, import error, auth) surface in the first minutes.

<required>
1. Launch; record PID / container id and the log path.
2. `ScheduleWakeup` 270s. On wake, read the contract file, then tail the log and pull the latest metric directly. Confirm the *health* signal has fired — first step logged, first batch through, first rows written — not merely "no error yet."
3. If it crashed or never reached the health signal: triage now (Phase 4). Do not start the long poll on a job that never got off the ground.
4. Only once you've seen real progress: declare stable and enter Phase 3.
</required>

Do not gate the crash window on a `Monitor` grep filter waiting for a success token — the line you're watching for may never be emitted (silent hang, different format, redirected stream), and the gate then waits forever. Always wake on the timer and read the full tail yourself.

## Phase 3 — Stability poll loop

Now poll on a cadence. Each tick is a real check, not a heartbeat:

<required>
1. Re-read the contract file first — session memory may have compacted or this may be a fresh wake. The file is the source of truth for launch command, log path, health/done signals, recovery playbook, budget, and teardown.
2. Read fresh evidence: tail the log, check PID/container, pull the latest metric.
3. Classify: progressing / done / anomaly. Progress means the health signal advanced *since last tick* — same step count after 5 min is a hang, treat as anomaly.
4. Progressing → schedule the next tick, say nothing.
5. Done → Phase 5 (tear down if the user wants the resource released; notify).
6. Anomaly → Phase 4.
7. Each tick, check budget/stop conditions. Hit one → stop, tear down per contract, notify.
</required>

### Poll mechanics

The harness cannot notify you about remote pod state — you must re-wake yourself.

- **Always `ScheduleWakeup` at 270s.** Fixed cadence. Just under the 5-min prompt-cache TTL, so each tick stays cheap. Do not stretch to 300s+ "because the job is long" — the cache miss costs more than the saved tick, and a longer interval delays catching a hang. Do not shorten either — 270s is the cadence.
- The wakeup `prompt` must point at the contract file — e.g. `"Job guardian tick: read docs/jobs/<slug>.md and run Phase 3."` — so the next tick reloads the contract regardless of session state.
- **Never wait on a `Monitor` grep filter as the primary signal.** Grep waiting for specific tokens (`step=`, `loss=`, success markers) silently misses when the log format shifts, the line is buffered, or the stream is redirected — and you wait forever. Wake on the timer, read the tail, decide. `Monitor` is fine as an additive watch for known failure signatures (`Traceback|OOM|NaN|Killed`) but it never replaces the 270s tick.
- Don't block the session on long foreground `sleep`s. Schedule the next tick and yield.

## Phase 4 — Triage: recoverable or not

Match the failure against the Phase 0 playbook. Fail fast and loud (GPC6) — a wrong recovery that corrupts a checkpoint is worse than a clean stop.

Recoverable (on the playbook, under the attempt cap):
1. Apply the named fix.
2. Resume from the last good checkpoint if the job supports it; else restart.
3. Re-run the Phase 2 crash gate — confirm the fix actually took and progress resumed before trusting it.
4. Increment the attempt counter for this failure class.

Unrecoverable — escalate, do not improvise — when any holds:
- Not on the playbook, or root cause is unclear.
- Attempt cap for this failure class is hit (don't loop a restart forever).
- It needs a human decision (config change, code fix, data problem, budget call).
- Repeated identical crashes — restarting a deterministic failure just burns money.

On unrecoverable: capture the failure (last log lines, error, what you tried), then go to Phase 5.

## Phase 5 — Terminal: teardown + notify

<required>
1. Preserve outputs first — pull checkpoints, logs, results off the pod *before* any teardown, in case teardown destroys the disk.
2. Release the resource (done, gave up, budget hit) with the reversible teardown (`stop`, not destroy). Verify it actually released (pod stopped) — a teardown you didn't confirm is not done (GPC5).
3. Write the record: outcome, final metrics or error, recovery actions taken, where logs/checkpoints live, plus the two handsoff lists — `### Hands-off decisions` (every inferred choice, one line each) and `### Deferred (needs user input)`.
4. `PushNotification` on the contracted terminal events, lead with what the user acts on: `"train done: 50k steps, loss 1.8, pod stopped"`, `"job died — OOM, 3 restarts failed, pod stopped, log saved"`. Not routine progress.
</required>

## Never

- Declare stable from "no error yet" without seeing the health signal fire.
- Read a metric once and assume it's still true an hour later — re-read each tick.
- Restart a deterministic crash past the attempt cap.
- Destroy a pod (`remove`/terminate) the user didn't explicitly name — `stop` ends the spend reversibly.
- Tear down a pod holding the only copy of checkpoints/logs before pulling them off.
- Ask the user anything — at intake, mid-flight, or at teardown. They're away. Infer + log, or defer + stop.
- Launch without the contract file written. No file, no launch.
- Let the contract file drift from current instructions — update it the moment guidance changes.
- Burn budget on a hung job because liveness ≠ progress.
- Block the session on long foreground sleeps instead of `ScheduleWakeup`.
- Wait on a `Monitor` grep for a success token as the gate — it misses and you wait forever. Wake at 270s, read the tail.
- Stretch or shrink the 270s cadence. Fixed.
