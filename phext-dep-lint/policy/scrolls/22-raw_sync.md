crate: raw_sync
examined-version: 0.1.5
what: Raw OS synchronization primitives (mutexes, events) over
  shared memory, for inter-process coordination.
own-tree: 5 direct deps of its own, 14 packages reachable.
needed-for: SQ's IPC path — SQ coordinates processes through
  shared memory and uses raw_sync's primitives there. It is on
  SQ's critical path, not an edge convenience.
verdict: fail
reasoning: A 0.1.x, slow-moving crate carrying a 14-package tree
  on the critical path of the estate's live-edit substrate is
  the wrong shape: the primitives it provides are a thin layer
  over OS facilities SQ could own directly, and its maintenance
  posture means the estate effectively owns the risk already
  without owning the code. FAIL as the audit verdict. SQ's
  continued use is recorded as a per-project exception in
  policy/exceptions.toml — visible, reasoned, and the first
  candidate for a first-party replacement — not silently
  grandfathered.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
