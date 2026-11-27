# phext-dep-lint — fleet baseline

Generated EE 1029 (2026-11-26–27) by phext-dep-lint 0.1.0 in **report mode** (findings only; this linter is not a gate anywhere yet).

Policy state at generation: `policy/audits.phext` holds 14 audit scrolls (10 pass / 4 fail — the failures are tempfile, xz2, raw_sync, shared_memory), transitive budget 60, and 2 recorded per-project exceptions (SQ: raw_sync, shared_memory). Everything in use without a passing audit is a finding here, per Will's rule: if it hasn't been approached, it doesn't get used — and existing use is not grandfathering.

## Headline

- **53 repositories linted** (54 project entries; checkouts of wbic16@exo from the hub clones). **8 entries pass, 46 fail.**
- **6055 violations** across the fleet:
  - `unaudited-transitive`: 4741
  - `unaudited-direct`: 756
  - `duplicate-versions`: 345
  - `unvendorable-source`: 155
  - `audit-failed-direct`: 19
  - `budget-exceeded`: 19
  - `no-lock`: 17
  - `audit-failed-transitive`: 3
- The dominant finding is exactly the one the policy predicts: the fleet runs on thousands of crate-uses that have never been audited. The audit queue below is the work list.

## Worst trees (transitive packages, resolved lock)

| # | Project (repo) | Direct | Transitive | Budget | Violations |
|---|---|---:|---:|---:|---:|
| 1 | openfang-api (openfang) | 79 | 819 | 60 | 981 |
| 2 | holo_accord (holostore) | 41 | 684 | 60 | 688 |
| 3 | exo_rs (exo) | 24 | 535 | 60 | 551 |
| 4 | disentangle-cli (protocol) | 52 | 495 | 60 | 564 |
| 5 | gluesql-cli (gluesql) | 69 | 349 | 60 | 463 |
| 6 | jeff-mitchell-dev-backend (jeff-mitchell-dev) | 4 | 349 | 60 | 343 |
| 7 | locustdb (LocustDB) | 46 | 334 | 60 | 327 |
| 8 | actix-web-datetime-backend (actix-web-datetime) | 3 | 259 | 60 | 255 |
| 9 | ravel (ravel) | 14 | 239 | 60 | 237 |
| 10 | phext-lattice (phext-lattice) | 18 | 217 | 60 | 208 |

For contrast, the de-slopped lineage the policy was seeded from: phext-serve's tree is 29 packages (inside ravel's 239 — ravel's upstream Python-era Rust root is not the phext backend), holo-phext 21 external, SQ 54. phext-lattice at 217 is the first-party slop case: its default `web` feature and editor stratum drag in the tree the DESLOP census already flagged (ureq → 56, teixml-to-mutable → 56, ring, criterion → 66 in dev).

## Passing entries

- echolocation (echolocation) — direct 2, transitive 2
- vtpu-runtime (exo-plan) — direct 0, transitive 0
- exodroid-firmware (exodroid) — direct 0, transitive 0
- kgoat (kgoat) — direct 1, transitive 2
- novafox-bench (nova-fox) — direct 1, transitive 2
- phdoc (phdoc) — direct 1, transitive 2
- phextura (phextura) — direct 1, transitive 2
- vtpu-runtime (vtpu) — direct 0, transitive 0

## Notable findings

- **SQ** — both seeded exceptions applied (raw_sync, shared_memory). Remaining: 7 duplicate-version crates (bitflags, cfg-if, getrandom, nix, rand, rand_core, syn — each at two versions in one 54-package tree) and 40 unaudited transitive crates. SQ's direct surface is otherwise exactly the audited core.
- **phext-lattice** — `audit-failed-direct: tempfile` (verdict FAIL on record), `budget-exceeded` (217 vs 60), 2 unvendorable git sources (holo-phext and libphext are consumed by git rev — the ranch offline route cannot vendor those), 10 unaudited direct deps (the web/tui/dev mass: criterion, crossterm, ratatui, ureq, ring, teixml-to-mutable, hmac, sha2, getrandom, …), 9 duplicate-version crates.
- **libphext-rs** — `audit-failed-direct: xz2` (the unused `xz` feature) and `no-lock`: libphext-rs has no Cargo.lock at HEAD, so its transitive tree is unverifiable — for the format's own library, that is a finding in itself.
- **holo-phext** — 21 external packages but 4 unvendorable sources: it consumes libphext by git rev, and its lock carries git-sourced packages the offline route cannot vendor.

## The audit queue (most-used unaudited crates)

Crates in use across the fleet with no audit on record, by number of project trees they appear in. This is the order in which audits buy down findings fastest:

- `thiserror` — in 37 project trees
- `async-trait` — in 30 project trees
- `libc` — in 27 project trees
- `futures` — in 27 project trees
- `cfg-if` — in 26 project trees
- `tracing` — in 26 project trees
- `sha2` — in 24 project trees
- `rand` — in 24 project trees
- `proc-macro2` — in 24 project trees
- `quote` — in 24 project trees
- `syn` — in 24 project trees
- `unicode-ident` — in 24 project trees
- `chrono` — in 23 project trees
- `log` — in 23 project trees
- `getrandom` — in 22 project trees
- `memchr` — in 22 project trees
- `cpufeatures` — in 21 project trees
- `version_check` — in 21 project trees
- `itoa` — in 21 project trees
- `serde_derive` — in 21 project trees
- `wasi` — in 21 project trees
- `block-buffer` — in 20 project trees
- `crypto-common` — in 20 project trees
- `digest` — in 20 project trees
- `generic-array` — in 20 project trees

## Scope and exclusions

- Linted: every wbic16 repository containing Rust (54 from the hub census), checked out at `exo`. 53 produced reports.
- **nixpkgs excluded**: the wbic16 clone is a promisor-partial fork of NixOS/nixpkgs (blob:none); it is not a first-party Rust project and its tree could not be materialized. Recorded here, not silently skipped.
- The census also found 79 local-only workspace groupings under ~/workspace: overwhelmingly duplicate working trees and study clones of the same projects (five phext-lattice trees, three wiki-start-here trees, libphext scratch copies). They are not separate projects and are not baselined separately; the GitHub fleet above is the project set.
- Local study trees of upstream projects (holostore-analysis 688, charon-clone 334, h5i-repo-study 441 transitive) are upstream code under study, not Will's projects; their hub counterparts (holostore 684) are in the table.

## Full per-project table

| Project (repo) | Direct | Transitive | Status | Violations by kind |
|---|---:|---:|---|---|
| openfang-api (openfang) | 79 | 819 | FAIL | unaudited-transitive 646, unaudited-direct 213, duplicate-versions 70, unvendorable-source 40, audit-failed-direct 11, budget-exceeded 1 |
| holo_accord (holostore) | 41 | 684 | FAIL | unaudited-transitive 569, unaudited-direct 54, duplicate-versions 49, unvendorable-source 13, audit-failed-direct 1, budget-exceeded 1, audit-failed-transitive 1 |
| exo_rs (exo) | 24 | 535 | FAIL | unaudited-transitive 456, duplicate-versions 37, unaudited-direct 29, unvendorable-source 28, budget-exceeded 1 |
| disentangle-cli (protocol) | 52 | 495 | FAIL | unaudited-transitive 404, unaudited-direct 100, duplicate-versions 32, unvendorable-source 26, audit-failed-direct 1, budget-exceeded 1 |
| gluesql-cli (gluesql) | 69 | 349 | FAIL | unaudited-transitive 265, unaudited-direct 172, duplicate-versions 24, budget-exceeded 1, audit-failed-transitive 1 |
| jeff-mitchell-dev-backend (jeff-mitchell-dev) | 4 | 349 | FAIL | unaudited-transitive 309, duplicate-versions 28, unaudited-direct 4, budget-exceeded 1, audit-failed-transitive 1 |
| locustdb (LocustDB) | 46 | 334 | FAIL | unaudited-transitive 266, unaudited-direct 42, duplicate-versions 17, audit-failed-direct 1, budget-exceeded 1 |
| actix-web-datetime-backend (actix-web-datetime) | 3 | 259 | FAIL | unaudited-transitive 236, duplicate-versions 14, unaudited-direct 4, budget-exceeded 1 |
| ravel (ravel) | 14 | 239 | FAIL | unaudited-transitive 212, unaudited-direct 11, duplicate-versions 9, unvendorable-source 4, budget-exceeded 1 |
| phext-lattice (phext-lattice) | 18 | 217 | FAIL | unaudited-transitive 185, unaudited-direct 10, duplicate-versions 9, unvendorable-source 2, audit-failed-direct 1, budget-exceeded 1 |
| rust-mcp-filesystem (rust-mcp-filesystem) | 18 | 177 | FAIL | unaudited-transitive 143, unaudited-direct 14, duplicate-versions 14, audit-failed-direct 1, budget-exceeded 1 |
| qexo (qexo) | 3 | 156 | FAIL | unaudited-transitive 147, unaudited-direct 2, duplicate-versions 2, budget-exceeded 1 |
| qexo (quarterexo) | 3 | 156 | FAIL | unaudited-transitive 147, unaudited-direct 2, duplicate-versions 2, budget-exceeded 1 |
| lantern-core (exodroid) | 5 | 153 | FAIL | unaudited-transitive 134, duplicate-versions 11, unaudited-direct 2, budget-exceeded 1 |
| lanes (phext-lanes) | 16 | 134 | FAIL | unaudited-transitive 113, unaudited-direct 11, duplicate-versions 2, budget-exceeded 1 |
| markdown-wizard (markdown-wizard) | 7 | 106 | FAIL | unaudited-transitive 94, unaudited-direct 5, duplicate-versions 3, audit-failed-direct 1, budget-exceeded 1 |
| rustlings (rustlings) | 12 | 98 | FAIL | unaudited-transitive 75, duplicate-versions 11, unaudited-direct 9, audit-failed-direct 1, budget-exceeded 1 |
| phext-notepad (phext-notepad) | 6 | 86 | FAIL | unaudited-transitive 77, unaudited-direct 3, unvendorable-source 1, budget-exceeded 1, duplicate-versions 1 |
| gl1-http (phextron) | 4 | 72 | FAIL | unaudited-transitive 64, unaudited-direct 1, budget-exceeded 1, duplicate-versions 1 |
| teixml-to-mutable (teixml-to-mutable) | 7 | 59 | FAIL | unaudited-transitive 48, unaudited-direct 7, duplicate-versions 2 |
| sq (SQ) | 6 | 54 | FAIL | unaudited-transitive 40, duplicate-versions 7 |
| ink-browser-compiler (ink-os-platform) | 8 | 32 | FAIL | unaudited-transitive 23, unvendorable-source 13, unaudited-direct 7 |
| phext-stream (phext-http-streams) | 9 | 29 | FAIL | unaudited-transitive 22, unaudited-direct 11, unvendorable-source 6 |
| contract-ledger (Exocortexia) | 8 | 26 | FAIL | unaudited-transitive 20, unaudited-direct 18, unvendorable-source 14 |
| phext-drop (md2phext) | 3 | 25 | FAIL | unaudited-transitive 22, unaudited-direct 2, unvendorable-source 1 |
| holo-phext (holo-phext) | 5 | 21 | FAIL | unaudited-transitive 15, unvendorable-source 4, unaudited-direct 1 |
| phorge (phorge) | 2 | 11 | FAIL | unaudited-transitive 9, unaudited-direct 1 |
| echolocation (echolocation) | 2 | 2 | PASS | — |
| phext-roundtrip (grok-tools) | 1 | 2 | FAIL | unvendorable-source 2 |
| kgoat (kgoat) | 1 | 2 | PASS | — |
| novafox-bench (nova-fox) | 1 | 2 | PASS | — |
| phdoc (phdoc) | 1 | 2 | PASS | — |
| phextura (phextura) | 1 | 2 | PASS | — |
| ee (neon-tools) | 1 | 1 | FAIL | unvendorable-source 1 |
| vtpu-runtime (exo-plan) | 0 | 0 | PASS | — |
| exodroid-firmware (exodroid) | 0 | 0 | PASS | — |
| vtpu-runtime (vtpu) | 0 | 0 | PASS | — |
| aoc (aoc2024) | 1 | no lock | FAIL | no-lock 1 |
| base256-phonetic (federation) | 0 | no lock | FAIL | no-lock 1 |
| hello-phext (hello-phext) | 2 | no lock | FAIL | unaudited-direct 1, no-lock 1 |
| human (human) | 1 | no lock | FAIL | no-lock 1 |
| libphext (libphext-rs) | 3 | no lock | FAIL | audit-failed-direct 1, no-lock 1 |
| Mini64K (mini64k) | 1 | no lock | FAIL | no-lock 1 |
| mirrorborn-client (phext-dot-io-v2) | 2 | no lock | FAIL | unaudited-direct 1, no-lock 1 |
| phext-life-wasm (phext-life) | 4 | no lock | FAIL | unaudited-direct 4, no-lock 1 |
| phext-mcp (phext-mcp) | 8 | no lock | FAIL | unaudited-direct 4, no-lock 1 |
| phext-shell (phext-shell) | 1 | no lock | FAIL | no-lock 1 |
| phext-wiki (phext-wiki) | 1 | no lock | FAIL | no-lock 1 |
| quickfork (quickfork) | 1 | no lock | FAIL | no-lock 1 |
| RFB001 (rfb001) | 5 | no lock | FAIL | unaudited-direct 3, no-lock 1 |
| exercises (rustlings-homework) | 0 | no lock | FAIL | no-lock 1 |
| sqlparser (sqlparser-rs) | 8 | no lock | FAIL | unaudited-direct 6, no-lock 1 |
| sqm (sqm) | 6 | no lock | FAIL | unaudited-direct 2, no-lock 1 |
| new-project (subspace-repeater) | 1 | no lock | FAIL | no-lock 1 |

Regenerate: run the linter across the fleet (see README) and rebuild this file from the JSON output. Raw per-repo JSON from this run is preserved in the run record (~/workspace/phext-dep-lint-work/results/).
