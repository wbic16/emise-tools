crate: holo-phext
examined-version: git rev bafed5f (locks pin a rev described as
  0.2.5; the repo's own manifest says 0.2.0 — version drift on
  record, to reconcile in the holo-phext repo)
what: The layer-2 holographic store engine over libphext — the
  transaction/index layer phext-lattice and phext-serve host.
  First-party (wbic16).
own-tree: libphext (git), memmap2, tokio — each audited separately.
  Its own lock resolves to 23 packages total.
needed-for: phext-lattice's store, phext-serve's hosting. The
  Variant C verdict (2026-11-26): holo-phext survives as the
  transaction layer inside the lattice design line.
verdict: pass
reasoning: First-party engine with a small, fully-audited external
  surface (23-package lock). The version drift noted above is a
  bookkeeping defect in the holo-phext repo, not a dependency
  problem; it is recorded here so it is not silent.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
