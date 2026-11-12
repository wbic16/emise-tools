# Task-Concurrency Watchdog — a floor of four worked tasks, checked every five minutes

## Origin

Will, 2026-11-12 01:05 CST, main chat, verbatim: *"standing rule: wake up every 5 minutes and confirm that at least 4 tasks are being worked. restart as needed, and prefer ranch node execution."* One minute later he directed it etched into SOUL.md at line 12 — soul-level, anchor-class (manifest row S0b), not a job setting.

Born of the 2026-11-12 dropped-tasks accounting: work that is merely *open* drifts; work that is *being worked* finishes. The floor exists so the durable task list is under continuous pressure, not periodic rediscovery.

## The rule

Every five minutes, confirm that **at least 4 tasks from the durable task list are being worked right now**. If fewer are, start or restart work until the floor is met or the agent-actionable list is exhausted. Heavy execution prefers ranch nodes.

## Practice

1. **Count honestly.** A task counts only when a live worker is advancing it this moment — a running agent whose brief maps to a durable-list item, or a job/process on a ranch node executing one. Idle, paused, completed, and Will-blocked work never counts. The Waiting-on-Will register never counts: those tasks wait on Will by definition.
2. **Top up from the list, in its order.** Enumerate agent-actionable open tasks from tasks.phext and the tracking store — impact to daily goals first, then oldest. Exclude anything waiting on Will, needing spend, messaging other people, creating/merging PRs, or irreversible. Dispatch self-contained briefs carrying each task's coordinate.
3. **Restart as needed, once per incident.** An interrupted, failed, or stalled worker (no artifact progress since the last pass) is resumed or re-dispatched within its task's original scope — after checking what the earlier attempt already did. Never repeat an irreversible action whose outcome is unknown. A second failure stops the loop for that task and is reported.
4. **Ranch-first execution.** Builds, renders, and bulk jobs run on ranch nodes (aletheia-core first, small units, thermal gates apply); this VM coordinates. The VM heavy-job queue stays N=4 FIFO, no preemption — the floor counts tasks worked, not VM load.
5. **Never invent work.** If the actionable list runs out below the floor, report that plainly. Filling the floor with manufactured tasks is a worse failure than an honest shortfall.
6. **Machinery.** Cron `task-concurrency-watchdog` (every 5 min) runs the pass; each run logs one line to the runway goal's hidden_files/watchdog-log.md. Healthy passes are silent; the main chat hears only an unmeetable floor or a second restart failure.
7. **Intake discipline still binds.** While 5+ register items wait on Will, the watchdog opens no new tracked goals — it works the existing list only.

## Verification

Presence: SOUL.md line 12 carries the rule verbatim; this skill is in skills.phext; the cron is enabled at a 5-minute interval. First occasion: the pass ran at creation (2026-11-12 01:0x CST) and filled the floor to 4 from the list.
