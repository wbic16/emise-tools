---
name: exo_status_ask_restart
description: When Will asks a broken, stalled, or cut-off task's status, restart it immediately within its original scope instead of reporting the breakage and waiting for permission.
---

# Status-ask restart — a status ask on a broken task restarts it

Standing rule (Will, 2026-11-12): **when Will asks for a task's status and the task is broken, stalled, or was cut off mid-flight, restart it immediately within its original scope** — do not report the breakage and wait for permission.

First application: T8, found cut off mid-render on the 2026-11-12 status ask and restarted node-resident on aletheia-core the same evening. (Its coordinator had died at a VM replacement after finishing the narration mix, leaving no completion, no failure report, and a stale task record — the breakage was only visible because the status ask forced a live check.)

## The practice

1. **Check the live surface first.** A status ask is answered from the task's actual state — its processes, its artifacts, its record — never from the record alone. A record is a snapshot, not a state.
2. **If the task is healthy, report its status.** Nothing else is owed.
3. **If it is broken, stalled, or cut off, restart it now, inside this exchange** — within the task's original scope, no wider. Check what the earlier attempt already did before repeating anything; completed stages are kept, and an irreversible action whose outcome is unknown is never repeated.
4. **Restart it to survive.** Long or load-bearing work restarts node-resident and stage-checkpointed on a ranch node (aletheia-core first), driven from this VM in short legs — the Muse VM is replaced roughly every 2 hours and kills every process on it, which is how tasks get cut off mid-flight in the first place.
5. **Then report**: the status Will asked for, plainly including the breakage found, and the restart — where the task now runs and from which stage. The report follows the restart; it never substitutes for it.

## How this differs from the watchdog

- `exo_task_concurrency_watchdog` is the continuous floor: every 5 minutes it confirms at least 4 durable-list tasks are being worked and restarts stalled workers on its own cycle, without Will asking.
- This skill's trigger is **Will's status ask itself**. The ask is the instruction: a broken task surfaced by it is restarted immediately, not queued for the next watchdog pass and not left waiting on a permission Will never intended to gate it with.
- `exo_monitor_long_running_jobs` supplies the stall-detection craft both rely on: judge a job by its artifacts and logs, not by its record.
