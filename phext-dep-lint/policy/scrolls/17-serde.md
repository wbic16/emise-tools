crate: serde
examined-version: 1.0 (with derive)
what: The standard Rust serialization framework; SQ uses it with
  derive for its wire/state structures. (In phext-lattice, serde
  appears only behind the `web` feature — not core there.)
own-tree: 2 direct (serde_core, serde_derive), 6 reachable; the
  derive path is proc-macro weight (proc-macro2, quote, syn) at
  build time.
needed-for: SQ core. SQ's structures serialize through serde;
  there is no std serialization framework to fall back to.
verdict: pass
reasoning: Examined and passed with its cost named: the tree is
  small (6) but the derive feature imports the proc-macro stack
  into every build. That is the accepted price for the estate's
  one serialization framework — the alternative (a hand-rolled
  serializer per project) is exactly the divergence slop this
  policy exists to prevent. New uses should prefer serde without
  derive where practical.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
