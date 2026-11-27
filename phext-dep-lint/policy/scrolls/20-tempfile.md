crate: tempfile
examined-version: 3
what: Temporary file/directory creation with automatic cleanup.
own-tree: 5 direct deps of its own, 12 packages reachable —
  including rustix and windows-sys and an RNG stack (getrandom/
  rand) — to create a temporary file.
needed-for: Claimed by phext-lattice. Nothing in the lattice's
  design requires OS temp files as a mechanism; the uses are
  conveniences of the "just grab tempfile" kind.
verdict: fail
reasoning: The canonical minimum-viable violation: twelve
  packages, a Windows syscall binding, and a randomness stack,
  imported to do what std does with temp_dir() plus a unique
  name — a few lines, owned, auditable. A crate whose entire
  job is trivially std-shaped and whose tree is not fails this
  audit. phext-lattice's use stands as a baseline finding until
  the uses are replaced or a recorded per-project exception
  argues otherwise.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
