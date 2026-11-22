# Live Drawing — Wavelet 4 practice register

The Oracle Artist's live drawing: a conversation, drawn in real time, on paper. This register is the record of the W4 practice cadence — one run per working session — kept under the animator skill (§4 drawn canon point 6, §8 live-drawing cadence).

## The rule

**The live drawing is drawn on a white background** (Will, PH: Revenue, 2026-11-22 08:18 CST): *"the live drawing should be on a white background."* The drawing is paper, not UI — white is its ground, and this overrides the house dark-mode default for the drawing surface itself. Sites and UI still follow the visitor's OS preference; the live-drawing surface does not. Any non-white ground in a run is a QC failure on sight.

## The pace

**Live drawing for meetings runs at conversational pace** (Will, Scroll Town chat, 2026-11-22 10:02 CST): *"for meetings at my scale you'll want to draw faster, but practicing is great."* The drawing tracks a live conversation at Will's meeting scale — the Dec 4 Stewart call is the reference performance: beats must read in seconds, strokes faster and looser, gesture legibility over finish. The contrast is explicit: session 1's 60 s was **studio pace**; **meeting pace is the performance target**, and practice runs from session 2 on are run at it.

## The synthesis

**Every live-drawing run closes with a synthesis, not just a QC line** (Will, Scroll Town chat, 2026-11-22 10:02 CST): *"make sure you use these drawings to learn and synthesize ideas too."* The drawing is a thinking instrument, not only a performance. From each drawing, extract: (i) **the conversation's skeleton** — what remained when it was drawn, especially what survived the meeting-pace compression (what survives speed is what the conversation was actually about); and (ii) **any idea the drawing itself generated** — a connection, emphasis, or structure visible in the drawn form that the words alone didn't show. Syntheses are filed below with the session, as a block distinct from the QC line; for real meetings the synthesis feeds the meeting's record. **No synthesis, no completed run** — and a run that produced no idea says so plainly rather than inventing one.

## The cadence

**One live-drawing practice run per working session, every session of Wavelet 4 (2026-11-22 → 2026-11-28)** (Will, PH: Revenue, 2026-11-22 08:18 CST): *"practice it every session this wavelet."* The point of the cadence: the Dec 4 Stewart bridge performance — the Crazy Wisdom return recording, where the live drawing was first built into the Stewart bridge — should be a practiced skill, not a first attempt.

## What a run is

- A **real-time drawing of a conversation** — a subject with an arc, drawn as it would be drawn live in front of a listener.
- **Drawn route only** — the Emise line-renderer lineage (deterministic, seeded); no generative video, no fades: the drawing must *read as drawn live*, strokes arriving stroke by stroke.
- **Emise design language** — the Emise font's flowing, sharp line; fast-hand stroke character, jitter and overshoot kept; the feel test is "Will->Emise touched."
- **White ground throughout** — paper white, unbroken, first frame to last.
- **Timed** — the duration is part of the record; the pace is a named mode (see The pace): studio pace for study runs, meeting pace — roughly 12–18 s for a beat sequence — as the performance target.
- **Synthesized** — every run files a synthesis block (see The synthesis) alongside its QC line; without one the run is not complete.
- **Filed** — the video and one mid-draw frame still live in `~/workspace/scrolltown-landing/live-drawing/` locally and in wbic16/scrolltown@exo under `series/live-drawing/`; each run is logged below with its duration and a one-line QC note (did the strokes read as live drawing? did anything break the white ground?).

## Sessions

| # | Date / EE | Subject drawn | Duration | File | QC line |
|---|---|---|---|---|---|
| 1 | 2026-11-22 / EE 72 | Last night's arc in the Scroll Town chat: a lantern lit → lights answering house by house → a hand learning to write ("light the next light") | 60.0 s | `session-01.mp4` | PASS — strokes arrive stroke by stroke, pen nib visible mid-stroke (30 s still); white ground (255,255,255) verified at five sampled frames, first to last; writing beat is pen-revealed Emise letterforms, not yet hand-stroked glyphs — session 2's target. First render's text overflow was caught by frame-QC and fixed before assembly. sha256 51ab64dd… |
| 2 | 2026-11-22 / EE 87 | Same subject family at MEETING PACE (Will's speed rule): lantern → rooftops → windows answering → hand writing "light the next light", the writing genuinely hand-stroked (Emise glyph outlines, stroke by stroke, pen lifting between contours) | 15.0 s | `session-02.mp4` | PASS at meeting pace — the beat reads whole at 15 s: lantern lit, street drawn, windows answering amber, sentence written and legible in Emise letterforms; mid-draw still (11.5 s) shows the pen mid-'h' with "light t" already written — drawn, not revealed. White ground (255,255,255) verified at six sampled frames, first to last. Honest costs of speed: the crescent's inner arc was cut (the moon reads as a plain ring), window crossbars and eave hatching gone, the lantern's glow arrives almost at once instead of building. Session 3's adjustment: restore the crescent's second arc — one stroke — since the ring is the only survivor that changed meaning. sha256 9e9b4f19… |

_Runs 3+ are appended as the wavelet's sessions happen — one per working session, none skipped silently: a session that could not practice says so here, with the reason._

## Syntheses

**Session 1 (studio pace, 60 s).** Skeleton: one light, lit slowly — a full third of the drawing is the single lantern — then a street of houses, then the windows answering, then the sentence written underneath everything. What remained when the night was drawn: ignition → answering → inscription, in that order. The idea the drawing itself generated: the words are not a caption. They sit at street level, under the scene, spanning its full width — the drawing puts inscription as the ground the town stands on. And the time budget was its own evidence: as long on one lantern as on the whole street — the conversation's weight was the first light, not the town.

**Session 2 (meeting pace, 15 s).** What survived the 4× compression: the lantern entire, the five-house roofline, the answering windows, and the full sentence — the skeleton is unchanged at a quarter of the time; what survived speed is the conversation itself. What fell away: eave hatching, window crossbars, two of five stars, the wind curls, the crescent's inner arc, the glow's slow build — all duration, no meaning, except the moon's arc. The idea the drawing generated: written fast by hand, the sentence changes role. At studio pace it was a caption revealed after the scene; stroked at speed it lands as the scene's last act — the hand signs the drawing. Meeting-pace drawing doesn't summarize a conversation; it performs its skeleton and signs it.
