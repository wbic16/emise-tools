# phext-dep-lint

A dependency linter for Rust projects, enforcing
**phext-minimum-viable-dependencies**.

## Why this exists

Will, 2026-11-26:

> "I don't care how hard my requests are, don't ship
> dependency-riddled AI slop."
>
> "Dependencies are like cancer — they metastasize transitively,
> each one importing its own tree, failure modes, and churn into
> the host."
>
> "Run all rust deps through a phext-based audit — if I haven't
> approached a library, it doesn't get used."

A hard problem is solved from first principles, inside the
phext-aware lineage, or from scratch — never by importing a
dependency chain to make it easy. This tool is that rule made
mechanical. It is itself built from the Rust standard library
alone — zero dependencies — because a dependency linter that
needed an exception for its own tree would be the slop it
exists to catch. Its own tree is the first proof of the policy:
`phext-dep-lint` run on this repo passes with a transitive
count of 0.

## The policy: a phext-based audit

The policy source of truth is `policy/audits.phext` — not a
hand-maintained allowlist and not "whatever the fleet already
uses." One scroll per crate records an audit:

- what the crate is,
- its own transitive dependency tree,
- why it is needed,
- a verdict (`pass` / `fail`) with reasoning.

A crate is allowed **only** if an audit scroll with a passing
verdict is on record for it. Unaudited = denied — including
crates existing code already uses. Those are findings, not
grandfathered rights.

The scroll sources live in `policy/scrolls/` (one `.md` per
audit, `00-home.md` is the policy home scroll and carries the
transitive budget). Edit a scroll, then rebuild:

```
python3 tools/build_audits.py           # rebuild policy/audits.phext
python3 tools/build_audits.py --check   # verify no drift
```

Never edit `audits.phext` by hand.

### Exceptions

`policy/exceptions.toml` records per-project exceptions: a
crate a specific project continues to use despite a failing or
missing audit, with the reason, on the record. An exception
must reference an audit scroll that exists — an exception
pointing at nothing is itself a lint violation. Exceptions
never change a verdict; they make continued use visible.

### How a library gets audited

1. Read the crate: what it does, who maintains it, its release
   posture.
2. Measure its own tree: is it a leaf? What does it drag in
   (build scripts? C bindings? proc-macro stacks? platform
   syscall crates?)
3. Establish need: what in the lineage actually uses it, and
   could std or a first-party crate do the job at lower drag?
4. Write the scroll (`policy/scrolls/NN-<crate>.md`) with a
   verdict and reasoning. A fail is a real outcome — several
   seed audits failed.
5. Rebuild the phext (`tools/build_audits.py`), commit both
   the scroll source and the built phext.

## What the linter checks

Given a project (workspace root) it verifies:

- **(a) Audited direct deps** — every direct dependency has a
  passing audit on record, or a recorded per-project exception.
  Failing-verdict audits are reported distinctly from missing
  ones, and unaudited *transitive* crates are reported too,
  each with the dependency path that pulled it in.
- **(b) Transitive budget** — the project's resolved tree
  (Cargo.lock) against the budget in the audit home scroll
  (default 60), unless a recorded budget exception applies.
- **(c) No duplicate versions** — no crate at two versions in
  one tree.
- **(d) Vendorability** — every resolved package must come
  from the crates.io registry (the ranch builds offline from
  vendored sources). Git dependencies, path dependencies that
  escape the project's own workspace, and non-crates.io
  registries are flagged.

## Usage

```
phext-dep-lint [--policy policy/audits.phext]
               [--exceptions policy/exceptions.toml]
               [--format text|json] [--budget N]
               <project-dir>...
phext-dep-lint --all projects.txt      # one dir per line
phext-dep-lint --scan <dir>            # discover Cargo projects
```

Exit codes: 0 = all projects pass, 1 = violations found,
2 = usage/IO error. JSON output is for Jenkins and other
machines; text is for humans.

## Report mode

**This tool currently ships in REPORT mode.** It reports
violations across the fleet (see `BASELINE.md`) but is not
wired as a failing gate in any build. The Jenkins job in
`jenkins/` runs it in report mode (build marked unstable, not
failed, on findings). Promoting it to a gate is a separate,
deliberate step.

## Layout

- `src/` — the linter (std only; TOML, Cargo.lock, phext, and
  JSON handling implemented in-tree from scratch)
- `policy/scrolls/` — audit scroll sources (the record)
- `policy/audits.phext` — built policy phext (the input)
- `policy/exceptions.toml` — recorded per-project exceptions
- `tools/build_audits.py` — scrolls → phext builder
- `tests/` — unit tests + end-to-end fixture tests for every rule
- `jenkins/` — the ranch Jenkins job spec (report mode)
- `BASELINE.md` — the fleet baseline report
