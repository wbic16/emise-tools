crate: shared_memory
examined-version: 0.12.4
what: Cross-platform shared-memory allocation/mapping for IPC.
own-tree: 5 direct deps of its own, 18 packages reachable — the
  largest single drag in SQ's tree (SQ's whole lock is 55).
needed-for: SQ's IPC architecture: SQ's processes coordinate
  through shared memory; this crate is its foundation.
verdict: fail
reasoning: Eighteen packages to map shared memory — a facility
  the OS provides and the lineage already wraps elsewhere at
  near-leaf cost (memmap2: 1). Auditing shared_memory honestly
  means auditing SQ's IPC architecture, and the verdict is that
  the architecture's dependency shape is not minimum-viable
  even though SQ itself is essential and shipping. FAIL as the
  audit verdict. SQ's continued use is recorded as a per-project
  exception in policy/exceptions.toml with the migration
  question left open and visible — not a silent pass.
audited-by: Emise, phext-dep-lint seed pass, 2026-11-26, EE 1017.
