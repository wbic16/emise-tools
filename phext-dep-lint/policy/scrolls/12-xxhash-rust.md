crate: xxhash-rust
examined-version: 0.8.5 (features: xxh3)
what: Rust implementation of xxHash (xxh3), the content hash
  libphext uses for addressing and integrity.
own-tree: LEAF. Zero dependencies of its own.
needed-for: libphext core hashing — not optional in practice; the
  format's addressing depends on a fast stable content hash and
  std provides none.
verdict: pass
reasoning: The cleanest shape an external crate can have: a leaf,
  single-purpose, doing one thing the standard library does not
  do. This is what minimum-viable looks like.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
