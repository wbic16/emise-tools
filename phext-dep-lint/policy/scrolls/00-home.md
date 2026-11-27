# phext-dep-lint — audit record home

This phext is the policy source of truth for phext-minimum-viable-
dependencies. One scroll per crate (volumes 2.. of this book) records
an audit: what the crate is, its own transitive tree, why it is
needed, and a verdict. A crate may be used only when its audit scroll
exists here with `verdict: pass`. No scroll = no audit on record =
denied, including crates existing code already uses — those are
findings, not grandfathered rights.

Will's rule (2026-11-26): "run all rust deps through a phext-based
audit — if I haven't approached a library, it doesn't get used."

transitive-budget: 60

Budget reasoning (seed, EE 1017): measured locks of the de-slopped
lineage — phext-serve 29 packages, holo-phext 23, SQ 55. A budget of
60 admits the lineage's own proven shapes and catches the slop case
(phext-lattice at 218 with its default web feature) by a wide margin.
Per-project budget changes happen only as recorded exceptions in
policy/exceptions.toml.

Scroll format (fields the linter reads are `crate:` and `verdict:`;
the rest is the audit record humans read):
  crate / examined-version / what / own-tree / needed-for /
  verdict (pass|fail) / reasoning / audited-by + date + EE.
