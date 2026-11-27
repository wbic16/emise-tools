crate: serde_json
examined-version: 1.0
what: JSON serialization/deserialization on serde — the REST wire
  format for SQ and phext-serve.
own-tree: 5 direct deps of its own, 10 reachable in the smallest
  consuming lock. Watch item: current locks show a new crate,
  zmij, occupying the slot ryu used to hold (float formatting) —
  it entered transitively without an audit and is exactly the
  kind of silent tree change this phext exists to catch; it
  stands as an unaudited-transitive finding until audited.
needed-for: SQ and phext-serve HTTP surfaces. JSON is the wire
  format other tools already speak to them.
verdict: pass
reasoning: The wire format is a real requirement and 10 known
  packages is a bounded, visible cost. Passed for the crate
  itself; its own dependents do not inherit this pass — each is
  audited or flagged on its own (see the zmij watch item).
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
