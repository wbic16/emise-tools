# State Machine Review — find the implicit machines (MOAT)

## Origin

Steve Ruiz's prompt (2026-10-31, widely bookmarked): *"find all of the implicit state machines in my app."* Will posted it in MOAT on 2026-11-07 and directed that state machine review be built into MOAT specifically (task 19.6.8/9.6.15/6.5.9) — not as a one-off hunt on some codebase, but as a standing review pass inside MOAT's two workstreams: the R&D tracker (research.phext) and the proving track (Charon/Aeneas/Lean work, libphext first). Channel discipline behind the ruling: Will posts in the channel he means; where a thing lands is part of what it is for.

## What counts as a state machine

Derived from the definition, not from examples: a state machine exists wherever behavior depends on retained state — a current state drawn from a finite (or at least enumerable) set, inputs or events that trigger transitions between states, and rules, stated or not, about which transitions are legal.

- It is **explicit** when the subject names the states and transitions itself: an enum matched on, a transition table, a protocol's phase spec.
- It is **implicit** when the same structure is encoded indirectly:
  - a variable (or a tuple of variables) whose value selects behavior — mode fields, phase counters, status values;
  - clusters of booleans whose combinations act as states (2^n encodings, few of them legal);
  - control flow whose position is the state — loop phases, parser position, "where we are" in a multi-step protocol;
  - ordering assumptions: operations that only make sense in sequence (open before use, lock before unlock, share before select);
  - data shape as state: empty vs partial vs complete buffers, files, or scrolls.

The review's job is to make implicit machines explicit: name the states, the transitions, the triggers, the guards — and then name the gap: the encoded states that are unreachable, the transitions the encoding permits that the design never intended, the legal-looking combinations nothing rules out. The implicit machine is always at least as big as the intended one; the difference is where the bugs and the proof obligations live.

## The review pass

1. **Inventory.** Sweep the subject for state-bearing elements, using the encodings above as the checklist. In code: enums, mode/status fields, boolean clusters, lifecycle method sets, loop and phase structure. In a paper or a studied system: protocol phases, agent states, operating modes the work assumes without naming.
2. **Extract.** For each candidate, write the machine down: state set *as actually encoded* (cite the file and line, or the paper's section), transition triggers, guards, and where the encoding lives.
3. **Test the extraction.** Which encoded states are unreachable? Which transitions exist in the encoding but not in the intent? Which intended transitions does the encoding fail to enforce? Report the difference, not just the machine.
4. **Rank by load.** Machines that carry behavior everything else depends on — parsers, lifecycles, protocol cores — are reviewed in depth; peripheral machines are listed in one line each.
5. **Report.** A list: name, one-line description, where it lives, explicit or implicit, intended vs actual state space. Load-bearing machines get a detail record: full state/transition extraction and the gaps found.

## In the R&D tracker (research.phext charter rule 13)

Every paper or source study ingested into research.phext receives a state-machine pass as part of its distillation:

- The machines the work contains or assumes are named in its chapter, as part of the delta record.
- A machine that is a reusable concept becomes a canonical concept scroll (or links to the one that exists); machines Emise infers rather than finds stated are marked **[synthesis]**.
- A paper that reveals a machine the world-model previously held only implicitly counts as a **revision** of the concepts it touches, and says so in the delta.

## In MOAT's proving track

Any crate MOAT proves gets its implicit machines enumerated **before** specifications are written, and the enumeration ships with the work:

- Specs attach to machines: a scanner's transition invariants, a lifecycle's legal sequences — the machine list is the spec surface, stated in the PR and in `proofs/README.md`.
- The trust ledger names any load-bearing machine left without specs, alongside the other trusted-but-unproved surface.
- Receipt from libphext-rs v0.4.1: the crate's core *is* machines — `phokenize`/`next_scroll` are delimiter-driven scanners, `fetch` is a scan with a window — and the Aeneas translation walls clustered exactly at machine boundaries (borrow-carrying scan loops, iterator adapters over scan state). Expect the same clustering elsewhere: where translation or proof resists, a machine is usually being carried implicitly.

## What this is not

Not a general codebase-hunt service for other chats, and not a refactor directive. The review names machines and their gaps; changing code on the strength of it is a separate task Will directs.
