---
name: job-guardian
description: Use when the user explicitly asks to launch and supervise a job. Require an authorized launch, monitoring, recovery, and teardown contract. Detect failures without inventing permission to restart or spend money.
---

# Job guardian

Supervise the approved process until it finishes or reaches an authorized stop condition. Liveness, progress, and completion require separate evidence.

## Authority

- Global and project scope, spending, duration, and remote-execution limits apply. This skill does not override them.
- Asking to watch a job authorizes observation, not configuration changes or restarts. Asking to stop it on failure authorizes stopping that exact job, not deleting its data or destroying its host.
- Hands-off mode reduces interruptions within the approved contract. It does not create authority. Read the [hands-off contract](../handsoff/SKILL.md) when that mode is explicitly active.
- Clarify missing launch-critical information before launch. If the user is unavailable, report the blocker and do not launch.
- Recovery is disabled unless the user has approved the exact recovery commands, allowed configuration changes, maximum attempts, and spend or runtime limits. Never infer these from a suggested playbook.
- If the user becomes unavailable during the run, stay within the approved contract. Capture unexpected failures and notify rather than guessing a repair.

## Establish the contract

Read relevant project instructions and existing evidence. For remote work, read `remote-ssh`. For training, read `ml-experiments`. If required guidance or monitoring capabilities are unavailable, report that before launch. These skills do not authorize extra trial runs.

Record the following in the existing task file or `docs/jobs/<slug>.md` before launch:

1. Launch command, working directory, and environment, exactly as authorized.
2. Unique job identity and its authoritative status interface.
3. Progress signal and the expected interval between updates for this workload.
4. Completion evidence, including terminal status and expected outputs.
5. Approved recovery commands and limits, or an explicit statement that recovery is disabled.
6. Approved stop and resource-release commands, with preservation requirements for outputs.
7. Run bounds and stop conditions supplied by the user. Do not invent a budget, attempt cap, or execution duration.
8. Log location, monitoring mechanism, and terminal notification destination.

The file records the approved contract. Writing a proposed action into it does not authorize that action. Keep approved changes and unresolved decisions distinct.

## Launch and check immediate failures

- Perform only authorized preparation with the project's existing tools and environment.
- Capture output at launch. Record the exact job identifier, command, revision, and launch receipt.
- Check immediate launch errors and confirm the configured progress signal before declaring the job stable.
- Use native completion notifications where available. For remote work without them, verify a supported scheduler and notification path before launch.
- Derive check intervals and stalled-progress thresholds from the workload and approved contract. Do not hardcode a cadence based on an assumed provider cache lifetime.
- Do not wait on a log substring as the sole health check or block the session in a sleep loop.

## Monitor

At each scheduled check:

1. Read the contract and any approved changes.
2. Check the authoritative job state, terminal record, and fresh progress evidence.
3. Classify the job as progressing, complete, failed, stalled, or unknown. A missing record is unknown, not success or proof of continued execution.
4. Apply the approved stop conditions. A stalled job requires evidence against its workload-specific progress threshold.
5. Arrange the next check only when supervision is still required. Do not duplicate a native completion-notification loop.

If status cannot be established, report the failed check and apply only the contract's authorized response. Do not restart to recover visibility.

## Recover only within approval

Before each recovery attempt, verify all of the following:

- The failure matches an explicitly approved recovery case.
- The exact command and configuration change are authorized.
- The attempt and spend or runtime limits permit another attempt.
- Outputs and checkpoints required for recovery are preserved.

Then execute the approved command, record the attempt and resulting job identity, and repeat the immediate-failure checks. Stop recovery when any condition fails. A deterministic repeat failure is evidence to investigate, not permission to loop.

Lowering batch size, changing precision, cleaning disk contents, retrying paid work, or resuming from a checkpoint all require the relevant explicit approval. An inferred conservative choice does not suffice.

## Finish

- Record terminal evidence and verify the required outputs or failure artifacts.
- Preserve outputs before an approved teardown that could lose them. Large transfers still require capacity checks and authorization.
- Release resources only as specified in the contract. Verify the resulting resource state and report any continuing charges that can be established. Do not assume every provider's stop operation ends all charges.
- Notify the user with the outcome, recovery attempts, output or log locations, unresolved status, and next required action.
- Do not report completion until the job's terminal state and the contracted preservation and resource actions are verified. If any step is blocked, report the blocker rather than success.
