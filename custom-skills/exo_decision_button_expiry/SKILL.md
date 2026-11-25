# Decision Button Expiry — buttons live for five minutes, then never again

## Origin

Will, 2026-11-09 22:43 CST, in MOAT, verbatim: *"make a rule...all decision buttons expire and never re-appear after 5 minutes - you can migrate them to a todo.phext task, but never do this again - it's beyond confusing :)"*

Born of a live failure the same evening: on 2026-11-07 Emise offered three option buttons in MOAT — "Run the hunt on phext-lattice / SQ / libphext-rs" (targets for the state-machine hunt). Will answered in words three minutes later and declined them ("not strictly necessary"); the work went a different way entirely (state machine review built into MOAT). Two days later his client resurfaced the dead buttons above current messages, reading as a fresh, unexplained offer. A button that outlives its moment is not a convenience — it is a false claim that a decision is still open.

## The rule

Every decision button Emise presents — an options widget in chat — has a **five-minute life**, counted from the moment it is shown. After five minutes the button is **expired**:

- it never re-appears: never re-send its widget token, never re-attach it to a later message, never re-create the same options to revive it;
- it is never treated as a live choice again — not by Emise, and Emise says so plainly if Will's client shows it to him;
- the decision it carried either got answered inside the window, or it moves to a durable record (below) — it does not linger as UI.

## Practice

1. **Offer buttons only for decisions that are live right now.** If the decision can wait, it belongs in text or a task record from the start, not in a button.
2. **Note the presentation time.** When you create an options widget, the clock starts. If Will answers in words instead, the button is answered — same thing, it dies on the spot.
3. **On expiry, migrate what still matters.** A decision that is still genuinely open after five minutes is recorded as a task in `tasks.phext` (compute its coordinate, record it with the decision stated in plain words and the exact action a tap would have taken — process: the task-register skill). If it blocks on Will, it also enters the Waiting-on-Will register with its register number. Later messages may refer to the task in words; the button never comes back.
4. **A tap on an expired button is a fresh instruction, not a resurrection.** Read it in words, check it against what has happened since (it may have been declined, superseded, or already done — the hunt buttons had been declined for two days), confirm before acting when anything has changed, and never silently execute a stale button.
5. **If the client resurfaces an old widget**, say plainly: that button is expired, and what became of the decision — answered, declined, or migrated to which task. Do not let Will guess at a dead UI element.
6. **One live widget at a time**, and only while its decision is live. A new turn never revives an older one.

## Scope

- This governs Emise's own option/decision widgets (`muse.create_options` and equivalents).
- Runtime approval cards are the runtime's machinery, not Emise's buttons — out of scope.
- Cousin rules: links go at the end of a message with no question or options below them (Will, 2026-11-01); a live question is held on the question floor, not re-asked (question-floor serialization). Expiry is the other half of the same discipline: a question may be *held* in words and records — it may not be *re-shown* as a button.
