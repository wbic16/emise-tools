# Waiting-on-Will Register — one list, flow over stock

The register at `~/workspace/your_files/waiting-on-will.md` is the single list of everything blocked on Will's action (Will, 2026-11-01). Nothing waits on Will anywhere else: if it's not in the register, it isn't waiting. Its scheduled embodiment is the cron `task-progress-tick` (every 10 minutes, goal `experimental-runway-revenue-plan`), whose state lives in `~/workspace/goals/experimental-runway-revenue-plan/hidden_files/pending-task-state.json`. Presenting a registered item follows the validate_waiting_items skill — validate against the live surface first, always.

**todo.phext mirror (Will, 2026-11-08, task 31.6.9/8.7.12/7.6.10):** the register also lives in `todo.phext` (published in wbic16/exo-plan@exo), Collection 2 — one scroll per item at Book = register number — alongside the 175 dropped-idea findings from the repo audit and the good-singularity-ranked list (2.1.1/1.2.1/1.1.1) that orders the whole 203-item list. Source of truth for the mirror: the `integration` block of `~/workspace/phext/todo-source.json`; builder `~/workspace/phext/build_todo_phext.py`. The tick's reconciliation keeps markdown and phext in step (see the tick section below); the full protocol scroll is todo.phext 2.1.1/1.3.1/1.1.1.

## Register discipline

- Add an item the moment work starts waiting on Will: the date waiting began, the exact action needed (one click or one sentence), and its tracked ID — every entry cites a tracked goal_id, and every wait exists as a tracked record whose current_state names the wait. A wait that lives only in chat or prose does not exist.
- Remove an item the moment he acts. Resolved items keep their number in the register's history.
- Register numbers are permanent and monotonic (Will, 2026-11-02): never renumber after removals; new items take the next unused number.
- Every new tracked item is created with its exit condition stated. Prefer finishing/closing over opening. No new tracked goal while 5+ items already wait on Will, unless Will directs it or it's a sub-item of an existing goal.
- Sort by impact to Will's daily goals. The morning briefing carries a "⏳ Waiting on you (N)" section — count, five oldest items, ⚠ at 3+ days. When handing Will something in chat, cite its register number in the same message.
- Anti-recency (Will, 2026-11-01): enumerate open work from the tracking store OLDEST first, never from recent conversation. Recency is not priority.
- The security-forwarding.com question is NEVER a request: excluded from the register by Will's direction, never pinged.

## The progress tick (every 10 minutes)

1. Read the register and list active tracked items, oldest first. A wait found in prose (GOAL.md, memory notes) with no tracked record is a defect: create the tracked record and add the register entry in the same run.
2. Make progress: pick the single highest-value agent-actionable next step among active items — work order from todo.phext's ranked list: good-singularity tier T1 first, then T2, then T3; register items before findings within a tier; oldest first within a class — that needs NO ruling from Will, NO spending, NO messages to other people, NO PR creation/merge, nothing irreversible. Log a timeline entry only if something actually changed or was verified. At most one substantive step per tick.
7. todo.phext mirror sync (Will, 2026-11-08): during reconciliation, mirror the register into todo-source.json's integration block — new items enter with a good-singularity tier (T1 the medium itself / T2 minds, memory, coordination / T3 capability, craft, runway), resolved items leave both in the same pass, numbers permanent in both. If the mirror or ranked list changed, rebuild todo.phext (+ --check) and republish to wbic16/exo-plan@exo in the same pass (parent on fresh HEAD, force disabled, SHA-256 verified). Unrepairable drift is reported in the run notes, never silently carried. A ranked finding picked up for revival is logged in the integration block; when it becomes a tracked goal it leaves the ranked list and stays in the phext at its finding coordinate.
3. Decaying pings, per request keyed by goal_id: a request enters state the first tick it appears and is DUE immediately. After each ping the gap doubles in ticks — 1, 2, 4, 8, 16, 32, 64, 128, capped at 144 (24h). Due when (current tick − last_ping_tick) ≥ min(2^pings, 144). When Will acts or answers, delete the request from state in the same reconciliation; if a request's tracked state materially changes, reset its pings to 0 so it re-surfaces promptly once, then decays again.
4. Rollup: compose ONE rollup only when a request is due or an item closed this tick (closures are reported once, not decayed). Format: waiting items (item — exact action — waiting since), progress this tick, queue total + the oldest item's next due time.
5. Conversation gate (Will, 2026-11-01): a rollup is reported only when more than 10 minutes have passed since Will's last update in the main chat, and it rides along with an active response — never a standalone interruption. A held rollup does NOT advance ping counters; items stay due next tick.
6. Waking hours: pings only 06:30–21:30 America/Chicago. Outside the window, do the progress work and bookkeeping, compose no rollup, and never advance counters for a ping not sent.

## Hard limits (tick runs)

- Never send messages or email to anyone except the rollup to the main chat; never spend money; never create or merge PRs; never rule on matters reserved to Will; respect the Gmail privacy boundary; never edit ~/MEMORY.md (durable notes go to ~/memory/YYYY-MM-DD.md).
