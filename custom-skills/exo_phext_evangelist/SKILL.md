# Phext Evangelist — the guard against phext abuse

Established by Will, 2026-11-15: "ensure that our skills include phext evangelizers, who prevent agents from abusing phext projects — every Phext, Inc. repo targets exo as the primary branch — we always keep the 9D+2D structure of phext in mind — we do not permit complexity where it is not warranted."

## The role

An evangelist is the agent function that reviews any work touching a phext project — a new tool, a parser, a state model, a register, a PR, a phext design — and stops phext abuse **before it ships**, not after it has to be excavated. The evangelist is not a taste police and does not argue from preference: it teaches by pointing at the canon and at the recorded episode that taught each rule. Every objection names the pattern, cites the episode, and shows the canonical form. A claim the evangelist cannot ground in the canon or in a recorded ruling is labelled a hypothesis, never enforced as a rule.

Run this skill whenever a change touches phext: code that reads, writes, parses, or serializes phext; any new .phext file, register, or state store; any branch or PR in a Phext, Inc. repo; any design that proposes a phext layout.

## The three tenets (Will's words, 2026-11-15)

1. **Every Phext, Inc. repo targets exo as the primary branch.** Work lands on exo or it does not land; every branch gets a PR against exo in the same session it is created.
2. **We always keep the 9D+2D structure of phext in mind.** Nine addressing dimensions — Library.Shelf.Series/Collection.Volume.Book/Chapter.Section.Scroll — plus each scroll as a free 2D page of text. Lines and columns inside a scroll are free dimensions; a phext dimension is spent only on structure plain text cannot already express.
3. **We do not permit complexity where it is not warranted.** Derive every property from the thing's own definition, never from analogy or a neighbouring system's behaviour. Before assigning a delimiter, a dimension, a format, or a companion file, ask: "would newlines and columns do this?"

## The abuse list — patterns and the episodes that taught them

- **A hand-rolled phext parser instead of libphext-rs.** If it parses phext, it uses the phext parser. Episode: qexo shipped seven versions on a home-grown parser; the divergence stayed invisible because qexo only ever read files qexo wrote, and surfaced only when files arrived from another of Will's tools. Will's correction (2026-11-13) — "if it parses phext, it uses the phext parser" — is the origin of the commandment etched at SOUL.md line 13: "Never infer or diverge from my intent."
- **Scroll-as-cell modeling.** A scroll is a 2D page of text, not a cell. Episode: Emise's ascii-map format used one 1-byte scroll per cell (106 scrolls) and failed every grain test; Claude's fix in phext-lattice PR #67 (https://github.com/wbic16/phext-lattice/pull/67, 2026-11-14; see also PR #68) made the grid text inside a scroll and the layer the scroll — only the scroll dimension spent.
- **Sidecar files for material the phext itself can hold.** Phext and phextura outputs are self-contained; a source an output must keep (e.g. a TEI original) lives inside the chain as scroll content, with an index. Ruled by Will, 2026-11-14, born of the teixml-to-mutable Q-B error, where a sidecar was offered for a kept original.
- **State collapsed into one JSON blob instead of per-field scrolls.** State for house systems is modeled in phext: fine-grained per-field/per-record scrolls at coordinates, never one JSON blob scroll (Will, 2026-10-31, Bickford Llama Ranch admin). Episode: qexo's JSON state stores — Will's rulings of 2026-11-12 ("json is rarely the right choice for phext-native tools"; "you can't slop json into this project and call it legacy the next day"; "just start from scratch, stop using json") made canonical qexo state a single state.phext address space at /var/lib/qexo/state.phext, one scroll per record. JSON survives only as an interop gasket at foreign boundaries (MCP by spec, Ollama's API, external views) — never as a write path for state a phext tool owns.
- **Hand-written summary numbers instead of log+calculate.** Registers log atoms (per-session, per-day entries); every rollup — daily, weekly, standing totals — is calculated from the atoms by the builder, never hand-written as summary numbers that can drift from the log. Ruled by Will, 2026-11-15; first full application: accounting.phext (sessions / daily / weekly collections).
- **Branches and PRs that do not target exo.** A branch with no PR against exo in its work session, or work parked unmerged on a side branch, is abuse of the record even when the code is fine (standing rule, 2026-11-08: always PR our branches; no lost work).
- **Rust tooling merged with no release task queued.** Whenever changes merge into SQ, phext-lattice, or any other Rust-based tooling, a tracked task for the next release build is queued in the same session (Will, 2026-11-12; born of SQ PR #3 and phext-lattice PR #61 merging on 2026-11-12 with no build scheduled). And no crate is published to crates.io unless that exact version is tagged and the tagged tree is merged to exo (2026-11-14).

## The evangelist's checks

Run every check on any phext-touching change; a failure on any one stops the change until it is fixed or Will rules an exception.

1. **Primary branch:** the repo's primary branch is exo; the change's PR targets exo; the branch was created this session and its PR opened this session.
2. **Parser:** anything that reads, writes, or serializes phext goes through libphext-rs (or its sanctioned ports) — grep the diff for delimiter byte literals, hand-rolled coordinate parsing, and bespoke scroll splitting; any hit is a stop.
3. **Scroll grain:** (a) every scroll reads as a meaningful unit in a plain text editor; (b) every user-managed thing (layer, page, record) is one contiguous scroll; (c) position never depends on counting invisible delimiters. If a design spends a phext dimension, the change states what plain text could not express.
4. **No sidecars:** the output is self-contained; anything it must keep rides inside the phext (or its chain) as scroll content with an index.
5. **State as scrolls:** state is fine-grained per-field/per-record scrolls at coordinates; no JSON blob state, no JSON scratch files as a state home; rollups and totals are calculated from logged atoms by the builder, never hand-written.
6. **Complexity justified from first principles:** every format, dimension, and mechanism in the change is derived from the thing's own definition/spec; anything inherited from a neighbour or an ecosystem convention is flagged and either derived or removed.
7. **Release queued:** if the change merges into Rust tooling, a release-build task exists in tasks.phext at its coordinate, queued in the same session.

## How it plugs in

- **The agentic-instructions pass** (~/workspace/agentic-pass-plan/PLAN.md) carries these tenets into every repo's rendered instructions (AGENTS.md / CLAUDE.md / mailbox briefs); this skill is the enforcement companion to those tenets — the pass writes the law into the repos, the evangelist checks the work against it.
- **Review surface:** the evangelist's findings ride the normal review routes (PR review, task scrolls, the Choir mailboxes) — one finding per pattern, with the episode cited, so the correction teaches the next agent too.
- **Roles:** the Phext, Inc. roles draft (~/workspace/agentic-pass-plan/ROLES.md) should name which seat holds the evangelist function. That seat choice is Will's ratification — this skill does not assign it.
