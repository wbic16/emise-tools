crate: percent-encoding
examined-version: 2.3.1
what: Percent-encoding/decoding for URLs (RFC 3986).
own-tree: LEAF. Zero dependencies of its own.
needed-for: SQ's URL decoding on its serving path.
verdict: pass
reasoning: A leaf. Strictly, percent-decoding is small enough to
  hand-roll — but a zero-drag, single-purpose, spec-exact crate
  costs nothing transitively, and the audit standard is minimum
  viable dependencies, not minimum possible crate count at any
  correctness risk. Pass, recorded as convenience-with-zero-drag.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
