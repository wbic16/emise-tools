# Waiting-on-Will Register — one list, flow over stock

The register at `~/workspace/your_files/waiting-on-will.md` is the single list of everything blocked on Will's action (Will, 2026-11-01). Nothing waits on Will anywhere else: if it's not in the register, it isn't waiting. Its scheduled embodiment is the cron `task-progress-tick` (every 10 minutes, goal `experimental-runway-revenue-plan`), whose state lives in `~/workspace/goals/experimental-runway-revenue-plan/hidden_files/pending-task-state.json`. Presenting a registered item follows the validate_waiting_items skill — validate against the live surface first, always.

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
2. Make progress: pick the single highest-value agent-actionable next step among active items — tier order (runway Tier 1 first), oldest first within a tier — that needs NO ruling from Will, NO spending, NO messages to other people, NO PR creation/merge, nothing irreversible. Log a timeline entry only if something actually changed or was verified. At most one substantive step per tick.
3. Decaying pings, per request keyed by goal_id: a request enters state the first tick it appears and is DUE immediately. After each ping the gap doubles in ticks — 1, 2, 4, 8, 16, 32, 64, 128, capped at 144 (24h). Due when (current tick − last_ping_tick) ≥ min(2^pings, 144). When Will acts or answers, delete the request from state in the same reconciliation; if a request's tracked state materially changes, reset its pings to 0 so it re-surfaces promptly once, then decays again.
4. Rollup: compose ONE rollup only when a request is due or an item closed this tick (closures are reported once, not decayed). Format: waiting items (item — exact action — waiting since), progress this tick, queue total + the oldest item's next due time.
5. Conversation gate (Will, 2026-11-01): a rollup is reported only when more than 10 minutes have passed since Will's last update in the main chat, and it rides along with an active response — never a standalone interruption. A held rollup does NOT advance ping counters; items stay due next tick.
6. Waking hours: pings only 06:30–21:30 America/Chicago. Outside the window, do the progress work and bookkeeping, compose no rollup, and never advance counters for a ping not sent.

## Hard limits (tick runs)

- Never send messages or email to anyone except the rollup to the main chat; never spend money; never create or merge PRs; never rule on matters reserved to Will; respect the Gmail privacy boundary; never edit ~/MEMORY.md (durable notes go to ~/memory/YYYY-MM-DD.md).
