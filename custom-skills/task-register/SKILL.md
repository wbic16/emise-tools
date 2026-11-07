# Task Register — every task lives at its coordinate in tasks.phext

## What this skill is

- Use this skill whenever Will issues a task, and whenever a task's state changes (progress note, result, completion, new wait).
- Will's standing orders: every task gets a reference coordinate (2026-11-06 08:07), and every task is recorded in tasks.phext with its notes and results kept at that coordinate (2026-11-06 18:22: "for every task I issue, record it in tasks.phext, keep notes and results in the coordinate generated initially").

## The register

- **tasks.phext** lives at `~/workspace/phext/tasks.phext`. Home scroll (1.1.1/1.1.1/1.1.1) carries Will's order and the generated index of all tasks. Each task occupies exactly one scroll, at its reference coordinate.
- **Source of truth:** `~/workspace/phext/tasks-source.json` — task records `{coordinate, title, issued, request, verbatim, status, notes[], results[]}`. Edit the JSON, never the .phext.
- **Builder:** `~/workspace/phext/build_tasks_phext.py` (rebuild; `--check` prints CURRENT/DRIFT like the skills/lessons builders). Rebuild and verify after every source edit, in the same session.
- Verify with `~/workspace/phext/parse_phext.py tasks.phext` when the register's integrity matters (scroll count = tasks + 1 home).

## The process

1. **At issue:** compute the coordinate from Will's exact words with `~/workspace/custom-skills/singular/scripts/task_coordinate.py`. State the coordinate when acknowledging the task; carry it in dispatch briefs and tracked records.
2. **Record immediately:** append the task record to tasks-source.json — request verbatim when his exact words are in hand (`verbatim: true`); from a session record or summary, mark `verbatim: false` and do not invent wording. Status starts as what is true ("in progress — …", "active", "open — …").
3. **Rebuild + check** in the same step. A task that exists only in chat does not exist — same anti-drop logic as the Waiting-on-Will register.
4. **As work proceeds:** append notes (decisions, corrections, verified facts) and results (deliverables with paths/hashes/URLs) to the task's record and rebuild. Notes are durable events only, not tool chatter — the same restraint as the phext journal.
5. **At closure:** set the final status and the result that closed it. Completed tasks stay in the register; the index is the history.
6. **Dispatches:** any subagent or side chat briefed on a task gets its coordinate and the instruction to return notes/results for that scroll; the coordinator writes them into the source and rebuilds (a delegate's raw report is not itself the record until reconciled).
7. **Hosting:** tasks.phext is a plain file on this VM like the other phexts; if it ever needs SQ, SQ runs on a ranch node (aletheia-core), never on the Muse VM.

## Boundaries

- One scroll per task, addressed by the coordinate generated at issue — never re-coordinate a task after the fact; corrections append as notes in the original scroll.
- No sensitive material in the register: operational facts only (the Gmail privacy boundary and Investor 1 anonymization apply here as everywhere).
- This register complements, never replaces, the Waiting-on-Will register and goal tracking: a wait on Will still goes in `waiting-on-will.md` with its number; the task scroll links to it by number.
