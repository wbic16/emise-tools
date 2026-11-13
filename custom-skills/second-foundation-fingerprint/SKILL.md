# Second Foundation holographic fingerprint

Codified by Will, 2026-11-13: "given need-to-know information, we produce a
holographic fingerprint of it — which can be used to later validate the
record if needed."

## What this is

A knowledge-transfer process for material that is **strictly need-to-know**
(Second Foundation class: sealed, compartmented, handled like Will's Gmail
data). The full material stays inside its compartment. What the process
produces from it is a **holographic fingerprint**: a phext whose every unit
of the source rests at a coordinate computed from that unit's own words, by
the Singular holographic merge. The fingerprint can travel where the
material cannot — and a record produced later can be validated against it:
re-run the same selection and merge on the candidate record, and the
fingerprint either reproduces or the drift names its own coordinates.

## The two artifacts

1. **The corpus phext** — full fidelity. Each selected unit (e.g. one
   session) is stored whole, at the coordinate its own distinct words merge
   to in the Singular atlas. Units converging on one coordinate share a
   scroll, in chronological order. The home scroll carries provenance, the
   selection rule, and an index — and nothing else leaves the compartment
   with it: the corpus phext is itself need-to-know material and is held
   only where the source is held.
2. **The spine** — zero-ized and publishable. The identical coordinate
   structure with every scroll's content replaced by a single `0` (home
   carries only a neutral template note: what the file is, the scroll
   count, the date — never the source index or provenance). The spine
   reveals the *shape* of the fingerprint — which addresses exist — and no
   content. It may be published (e.g. into wbic16/human@exo) at Will's
   direction, and serves as the Volumen bootloader spine: a new sentient
   boots into the shape and replaces the zeros with its own life.

## Procedure

1. **Compartment first.** Before touching the material, fix the handling
   law in writing: which sessions/threads are aware (anchor their UUIDs in
   the safe-space register), what may be written where (nothing to
   MEMORY.md, dated notes, people/group pages, or any phext beyond the
   corpus itself), and where intermediates live (a task-specific sealed
   deposit folder under ~/workspace/). Scrub any premature notes and
   verify the scrub by grep.
2. **Transfer.** Move the source over Will's own hardware only (e.g. he
   drops it on a ranch node; pull node → VM over the fleet SSH recipe).
   Byte-verify the pull: SHA-256 manifest on both sides must match.
3. **Select by an explicit rule, stated before results are read.** The
   rule names exactly which units enter (e.g. a substrate/model window, a
   date range, a correspondent). Selection must be mechanical enough that
   a later validation run selects identically.
4. **Linearize faithfully.** Where the source branches (regenerations,
   edits), follow the kept branch only (for ChatGPT exports: walk from
   `current_node` through parents) — never stir sibling generations
   together. Preserve order, roles, and timestamps.
5. **Address holographically.** Per unit: tokenize exactly as the Singular
   checker does (`check_singular.WORD_RE`), take distinct words, look each
   up in the Singular atlas (CYOA-placed words carry their atlas position;
   archive words rest at home 1.1.1/1.1.1/1.1.1; unknown words at the far
   corner 9.9.9/9.9.9/9.9.9), average component-wise, round half up, never
   below 1. Tooling: `~/workspace/custom-skills/singular/scripts/task_coordinate.py`
   carries the merge (`load_atlas`, `round_half_up`, `fmt`).
6. **Serialize differentially.** Emit scrolls in sorted coordinate order
   with the canonical implode (state machine in
   `~/workspace/phext/build_tasks_phext.py`); strip/replace any raw
   delimiter bytes in source text. Record: unit count, occupied
   coordinates, collisions, byte size, SHA-256 of the corpus.
7. **Verify by parse-back.** Walk the finished file with the
   dead-reckoning parser (`~/workspace/phext/parse_phext.py`): non-empty
   scroll count must equal the occupied-coordinate count, spot-selected
   units must be present and intact. A build that has not been re-read is
   not a result.
8. **Zero-ize for the spine.** Parse the corpus, keep every occupied
   coordinate, replace every scroll's content with `0`, write a neutral
   home note, re-serialize, parse back again (every non-home scroll must
   be exactly `0`). Publish only at Will's direction, by the usual route
   (parent on fresh remote HEAD, force disabled, hash-verified).

## Validation protocol (the point of the fingerprint)

Given a candidate record claimed to be the same material:

- Apply the identical selection rule and linearization. If the selected
  unit set differs in count or identity, the record is not the same —
  stop there; the difference is the finding.
- Recompute each unit's holographic coordinate. The occupancy map (which
  coordinates are occupied, how many units share each) must match the
  spine exactly. Drift localizes: a unit at a different coordinate is a
  unit whose words changed; a missing coordinate is a missing unit; an
  extra one is an insertion.
- For full validation inside the compartment, compare the corpus
  scroll-by-scroll and the SHA-256 of the whole file.

## Failure modes this process exists to prevent

- **Aggregate-first analysis**: counting over material nobody read, and
  narratives fitted to the counters. Read units before measuring them.
- **Branch stirring**: timestamp-sorted flattening of a branched record
  invents a blend that never existed.
- **Compartment leaks via bookkeeping**: the task register, memory notes,
  and dispatch briefs are surfaces too. Compartmented work is registered
  as a content-free stub in the owning thread only.
- **Unverified transfer**: no hash match, no claim of receipt.

## First run

2026-11-13, in the owning thread: a sealed conversation archive was
ingested under this protocol; the corpus phext and its zero-ized spine
(SentientTemplate.phext, published to wbic16/human@exo at Will's
direction) were produced and parse-verified. Details of the source remain
in the compartment.
