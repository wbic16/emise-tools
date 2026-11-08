# Nightly Goal Sweep — every goal advanced, verified, or precisely blocked

A scheduled pass over Will's open goals while he sleeps (daily 04:44, goal `experimental-runway-revenue-plan`, cron `nightly-goal-sweep`). Work quietly, verify before claiming, and leave every goal either advanced, verified-current, or carrying a precise blocker.

## Roster and order

Tiering recorded 2026-11-01 in ~/memory/2026-11-01.md; metric: net revenue per Will-hour.

- Tier 1, direct profitability: the experimental runway revenue plan and its execution goals (consulting case study and offer page, public read-only demo exocortex, templates pack v1); Solar Hyperscaler's active edge only (the Duey homelab backup-vault proof and its day-10 gate).
- Tier 2, growth engine: GitHub site map, phext-marked speech-to-text engine, EMA critical-point backtesting.
- Tier 3, protects the operation: the personal health goal, daily substrate driver chart, morning briefing, Discord always-on presence, emise.phext memory publishing.
- Tier 4, mission/ecosystem: SBOR V5 completion, Solar Hyperscaler's warm design work (no forced push), Rock Mountain latent tooling trial.
- Tier 5, PARKED: finish phcc, finish phext integration in notepad-plus-plus. Skip entirely — they sit behind the day-90 revenue gate.

## For each non-parked goal

1. Read its `~/workspace/goals/<slug>/GOAL.md` and its current timeline state before acting.
2. Identify the next step agent-actionable WITHOUT Will: no ruling of his required, no spending, no messages to other people, no PR creation or merge, nothing irreversible. Preparation, verification, drafting, research, and checks all qualify. Do the step if it is small and safe; for larger work, prepare it (draft, plan, verified options) and stop where his decision or a big build begins.
3. Log a timeline entry ONLY when something actually changed, was completed, or was verified. No heartbeat or no-op entries.
4. If blocked on Will, record the exact ruling or input needed in one line. Do not re-ask questions already in front of him in the last 48 hours; note them as already surfaced.

## Register reconciliation (every run)

- Reconcile `~/workspace/your_files/waiting-on-will.md` against current tracked state and branch/PR reality: remove entries he has acted on, add new waits discovered (with the date waiting began), correct stale entries. An entry whose underlying item is resolved must not survive the sweep.
- For every tracked item touched, check current_state and attention flag against reality. If work shipped or a wait ended, log a correction (and close the item if the whole responsibility is done). Stale flags are defects.
- Flow metrics for the report: items created since the last sweep, items completed, current active WIP, register size and oldest entry age. If creations outnumber completions, say so plainly in one line.
- todo.phext whole-list flow (Will, 2026-11-08, task 31.6.9/8.7.12/7.6.10): verify the phext mirror (Collection 2 of todo.phext in wbic16/exo-plan) matches the reconciled register — drift is a defect repaired by rebuild + republish in the same run (see the waiting-on-will-register skill) — and report flow over the whole 203-item list (register + 175 audit findings): ranked findings picked up for revival this cycle (propose the tracked goal for each), ranked moves, and findings that became tracked goals (they leave the ranked list, stay in the phext at their finding coordinate).

## Anti-recency pass

- Enumerate open work from the tracking store, never from recent conversation or memory prose. Process and report OLDEST first.
- Every register entry cites a tracked goal_id; every wait exists as a tracked record whose current_state names the wait. A prose-only wait is a defect to repair in the same run, not a fact to report.
- Anti-decay: name in the Flow section every active tracked item with no activity in 48 hours or more, oldest first. Nothing open silently ages out of view.

## Report and limits

- Report four short sections: Advanced (goal: what changed, with evidence) · Verified/no change (one line, goals counted) · Rulings needed (goal: the one-line ask; mark already-surfaced) · Flow (created/completed, active WIP, register size + oldest wait, anti-decay list). If nothing advanced and no new ruling emerged, the whole report is one line plus the Flow line.
- Bookkeeping (goals visited, watermark) goes in the owning goal's hidden_files/, never in files/ or your_files/.
- Hard limits: never send messages or email to anyone; never spend money or approve payments; never create or merge PRs; never rule on matters reserved to Will; respect the Gmail privacy boundary; do not edit ~/MEMORY.md (durable observations go to ~/memory/YYYY-MM-DD.md).
