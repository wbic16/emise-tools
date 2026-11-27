crate: tokio
examined-version: 1 (features in use: rt-multi-thread, macros,
  net, io-util, sync, time, signal)
what: The async runtime — executor, reactor, timers, async IO —
  under phext-serve's HTTP hosting and holo-phext's engine.
own-tree: The heaviest legitimate tree in the core: 2 direct deps
  at minimal features, 6–15 reachable depending on the feature set
  (mio, socket2, parking_lot, pin-project-lite class packages).
needed-for: phext-serve (async HTTP server) and holo-phext. An
  async server in Rust without a runtime means hand-building an
  executor/reactor — not a serious option, and pretending
  otherwise is how estates rot.
verdict: pass
reasoning: Passed WITH feature discipline, which is where tokio's
  real risk lives: the approved surface is the feature set named
  above, the set the lineage actually uses. Enabling new tokio
  features (fs, process, full, …) widens the tree silently and
  requires re-audit before use. The runtime itself is essential,
  maintained, and bounded under that discipline.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
