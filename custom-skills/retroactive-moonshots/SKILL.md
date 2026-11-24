# Retroactive Moonshots — track and record the shipped ones nobody planned

Standing order (Will, 2026-11-23): "I often act immediately upon novel stimuli — be sure to track and record shipped moonshots we didn't plan on."

## The pattern

Will acts immediately upon novel stimuli: a post, a person, a question, a project someone hands him in a group chat. Work that begins this way was never planned, never numbered in the moonshots registry, and never passed through a proposal — it goes from stimulus to shipped inside hours. The registry's failure mode is exactly this class: the artifact lands, the work is real, and the record says nothing, because the registry only ever held what was planned in advance. This skill is the catch-net: moonshots are recorded when they are *recognized*, not only when they are proposed.

## Detection — what counts

A retroactive moonshot candidate is work that meets all three:

1. **Stimulus-born** — it began from a novel stimulus (something that arrived: a post, a person, an artifact, a challenge), not from the plan, the register, or a scheduled programme.
2. **Unplanned** — it is absent from `moonshots-source.json` (checked, not assumed — an absence is a claim too; look in the registry before declaring it unrecorded).
3. **Moonshot-scale** — a new capability, artifact, or programme that did not exist before the stimulus: a tool adopted fleet-wide, a phext created, a build taken on and shipped. Routine tasks, fixes, top-ups, and one-off answers are not moonshots, however fast they moved.

When the scale test is uncertain, file it as a **candidate** (the registry's candidates list exists for exactly this) and let Will strike it — a filed candidate costs one line; a lost moonshot costs the record.

## Recording — the same session the ship lands

Record-first applies with the clock running: the entry lands the same session as the ship, or in that evening's consolidation at the latest. Retroactive means recorded after the act; it never means reconstructed weeks later from memory.

The registry is `~/workspace/human/exo-plan/moonshots-source.json` (builders `build_moonshots_phext.py` / `build_shipped_phext.py` beside it; the phexts publish to wbic16/exo-plan@exo under the register discipline). Each retroactive entry carries:

- **stimulus** — what arrived, when (EE-stamped), and where (chat, post, person).
- **will_words** — Will's exact words that set it off, quoted, never paraphrased into a plan he didn't state.
- **inception** — the evidence trail: first task, first commit, first artifact, with coordinates or hashes.
- **what shipped** — the landed artifact and its home (repo + branch + commit, phext + coordinate, site + URL), hash-verified where the discipline applies.
- **status_line** — one line, prefixed `retroactive —` so the registry never pretends it was planned.

Placement: a programme still in progress takes the next permanent number (numbers are permanent and monotonic; a retroactive entry never displaces or renumbers a planned one) and counts toward the WIP limit like any other. One that already shipped is recorded with its migration to shipped.phext in the same pass, per the standing migration gates — receipts standing on their own is the gate that matters for retroactive entries, since there was never a proposal to audit against.

After editing the source: rebuild (`python3 build_moonshots_phext.py`, and `build_shipped_phext.py` when a migration is recorded), verify the parse, and republish under the register discipline (parented on fresh remote HEAD, force disabled, SHA-256 verified). A rebuild that cannot be republished in the session is reported as not landed, never silently carried.

## Where detection runs

- **In the main chat**, whenever Will's direction starts something new on the spot — the stimulus and the act are both visible there; file before the session moves on.
- **In side chats**, where most stimulus-born work actually starts (a link dropped in a chat, a project handed over in a group). The record still lands in the one registry; a side chat's local notes are not the registry.
- **In the nightly sweep**, as the backstop: scan the day's shipped work (commits, published phexts, closed tasks) against the registry; anything shipped, stimulus-born, and absent gets filed as a candidate for Will's strike-or-keep.

## Worked examples (2026-11-23, the day this skill was taught)

- **Nim joins the Exocortex** — stimulus: Will's direction in the Softmax chat (21:11 CST) after the Cards and Casters work surfaced Nim; shipped the same evening: hub install verified, fleet sweep, the compiler's source forked to wbic16/Nim with the installed version's tag restored, dossier written. Unplanned at breakfast; infrastructure by midnight.
- **dakami.phext** — stimulus: Will sharing @dakami's following page (21:35 CST); shipped the same evening: a new phext holding the harvest and the unlock cross-reference.
- **ravel-phext** — stimulus: a project handed to Will in a group chat, with two dependencies named from his own lexicon; within the hour it had a study, a ruled architecture question (C1), and a Phase 2 build running.
