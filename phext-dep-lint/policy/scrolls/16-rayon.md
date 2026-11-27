crate: rayon
examined-version: 1.10
what: Work-stealing parallelism (parallel iterators) for CPU-bound
  batch work.
own-tree: Small tree: 2 direct deps of its own, 5 packages
  reachable (rayon-core, crossbeam-deque/epoch/queue/utils class).
needed-for: phext-lattice's parallel search and index paths — a
  measured performance surface of the lattice core, not decoration.
verdict: pass
reasoning: Bounded, known tree (5 packages), all of them small
  concurrency primitives, used on a real hot path. The alternative
  is hand-rolled thread pools in the lattice — a worse correctness
  surface than this drag. Pass; if the tree grows materially the
  audit is re-opened.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
