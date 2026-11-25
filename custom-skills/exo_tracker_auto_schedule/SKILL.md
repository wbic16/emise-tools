# Tracker Auto-Schedule — a new tracker type schedules its generating item

Standing rule (Will, 2026-11-14 16:17 CST, verbatim): "Standing rule... every time we create a new type of work tracker... auto-schedule the item that generated it. (duh)" Recorded in AGENTS.md and MEMORY.md the same day.

## The rule

Whenever a new TYPE of work tracker is created, the item that generated it is auto-scheduled in the same session — entered into the durable work queue as a task in tasks.phext, and the tracker's own record marked taken/scheduled accordingly — never left merely recorded. A register that only records is a shelf; the generating item is the new tracker's first scheduled work.

## The trigger

- Creating a new tracker TYPE: a new register kind with its own source file, builder, and home scroll (tasks.phext, contests.phext, jobs.phext are the standing examples).
- NOT a trigger: a new entry in an existing register. Entries follow their register's own intake discipline; this rule fires once per tracker kind, at its creation, on the one item whose work called the tracker into being.

## The scheduling acts — all in the same session as the tracker's creation

1. **Open the queue entry.** Compute the generating item's task coordinate from its request text with `~/workspace/custom-skills/exo_singular/scripts/task_coordinate.py`, append the task to `~/workspace/phext/tasks-source.json`, rebuild with `~/workspace/phext/build_tasks_phext.py`, and verify `--check` prints CURRENT. The task carries the item's real scope — it is a queue entry to be worked, not a pointer back at the register.
2. **Mark the item in its own register.** Flip the item's standing to taken/scheduled (the register's own standing vocabulary), and append a dated note naming this rule and the task coordinate, so the register itself shows why the item is no longer merely open.
3. **Rebuild and verify the register.** Run the tracker's own builder and its `--check`; it must print CURRENT before the scheduling is called done.
4. **Republish the register by its own route.** Each register has its own home (jobs.phext publishes to wbic16/exo-plan@exo; tasks.phext and artifacts.phext to wbic16/human@exo): parent on the fresh remote HEAD, force disabled, remote bytes verified after the push.
5. **Start the work the scheduling names.** Where the item warrants a first artifact (a plan, a build's first stage), produce it as part of the scheduling pass — the point of the rule is that work begins, not that a record improves.

## First occasion — the worked example (2026-11-14)

- 10:20 CST: jobs.phext created as a new tracker type; its generating item, Job 1 "Build Assay", encoded with standing **open**.
- The item sat recorded-but-unscheduled for ~6 hours: present in the register, absent from the durable queue, going nowhere.
- 16:17 CST: Will stated the rule. The same session, it was enacted:
  - Build task **37.8.8/10.8.13/7.7.13** opened in tasks.phext for the Assay build.
  - Job 1's standing in jobs.phext flipped to **taken**, with a dated note naming the rule and the task coordinate.
  - jobs.phext rebuilt, verified, and republished to wbic16/exo-plan@exo (final commit `88092e20`).
  - A build plan written at `~/workspace/oracle-service/BUILD-PLAN.md` — the scheduled work's first artifact.

## The failure mode this prevents

A new tracker feels like progress the moment it exists: the item is written down, indexed, published. But recording is not scheduling. Until the generating item stands in tasks.phext as work to be done, nothing in the durable queue will ever pick it up, and the tracker's first entry is also its first dropped task. Measured cost on the first occasion: ~6 hours of shelf time for the house's then-top build. The "(duh)" in Will's statement is the point — the generating item is the most obvious first work the new tracker has; leaving it unscheduled is the one omission the tracker itself should make impossible to miss.

## Boundaries

- The scheduled task is the generating item itself, in its original scope — never substitute work, never a placeholder "look into X" entry.
- Scheduling does not change the item's content or the register's other records; only its standing and the appended note.
- If the generating item is already genuinely scheduled elsewhere in the durable queue at tracker-creation time, the acts reduce to the register-side mark (step 2) naming the existing task coordinate — no duplicate queue entry.
