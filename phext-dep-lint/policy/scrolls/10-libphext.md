crate: libphext
examined-version: 0.6.6 (lock resolution; manifests request 0.6.4)
what: The phext format library itself — the substrate every other
  piece of the lineage is built on. First-party (wbic16), not an
  external dependency in any meaningful sense.
own-tree: 3 direct externals of its own — xxhash-rust (mandatory),
  base64 (optional, `binary` feature), xz2 (optional, `xz` feature).
  Each is audited separately in this phext.
needed-for: Everything. phext-lattice, SQ, phext-serve, holo-phext
  all sit on it.
verdict: pass
reasoning: First-party substrate; refusing it would refuse the
  format. Its own external surface is minimal and each external is
  individually audited (xxhash-rust pass, base64 pass, xz2 FAIL —
  the `xz` feature is enabled by no consumer and should stay off).
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
