crate: memmap2
examined-version: 0.9
what: Cross-platform memory-mapped file access — the mechanism
  the lattice store is built on (a phext file is mmapped, not read).
own-tree: Near-leaf: 1 dependency of its own (libc on unix).
needed-for: phext-lattice core storage and holo-phext. This is
  not a convenience; mmap IS the storage mechanism of the design.
verdict: pass
reasoning: Essential mechanism, one-package drag, and the safe
  wrapper over mmap syscalls is precisely the kind of unsafe-
  adjacent surface a small audited crate should own instead of
  every consumer hand-rolling it. Pass.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
