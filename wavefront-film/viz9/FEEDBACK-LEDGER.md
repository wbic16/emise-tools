# V9 Feedback Ledger — coverage review of record

Built 2026-11-03 22:50 CST at Will's direction: "plan a detailed review of
commentary once V9 is ready to see if any feedback was dropped — if so,
immediately schedule V10."

Every discrete item from Emi Prime, Grok, Claude, and Will is a row.
Status values: `built` / `reel-only` (applies to Chunk B) / `deferred-B`
(planned for Chunk B by design) / `resolved-by-decision` (conflict settled,
named) / `DROPPED` (not built and no documented reason — the failure this
ledger exists to catch).

## Emi Prime (OP Mode review)

| ID | Item | Chunk |
|----|------|-------|
| E1 | Temporal-depth hierarchy: subdued historical filaments, brighter recent, dominant active arrival; all data preserved | A |
| E2 | Three emotional states unmistakably distinct (f918 turbulence, f1053 hard burst, f3308 hush); hush = focused stillness, foreground clears | A |
| E3 | Entropy-weather phase integrates instantaneous rate (not rate × elapsed frames) | A |
| E4 | Camera orientation removed from world-space Bézier control points; geometry stable under camera motion | A |
| E5 | Depth-aware attenuation | A |
| E6 | Selective bloom | A |
| E7 | Restrained atmospheric perspective | A |
| E8 | Temporal antialiasing / motion blur | A |
| E9 | Palette anchors: gold = emotion, silver = CYOA, cool = interface; not "more brightness everywhere" | A |
| E10 | Exactly 5 revolutions + 7 events kept; visual chapters via focal distance, lighting, emphasis | A |
| E11 | Musical peaks reinforce transitions; hop chronology unaltered | A |
| E12 | Final pullback reveals coherent accumulated structure before CTA | A |
| E13 | Most Echoed strip fades out before CTA text begins | A |
| E14 | Archival master preserved + additional high-quality viewing encode; encodes compared on dense motion, not static cards | B |
| E15 | Validate entropy signal vs tweet length; document measured vs artistically inferred effects | A |
| E16 | Stress reel (opening, turbulence, burst, hush, pullback, CTA) rendered and verified before full render | A |
| E17 | Acceptance: states distinguishable at normal size; filaments stable in camera motion; CTA free of strip overlap; exclusions + string audit + exact rotation count + complete frame count; deterministic signals/geometry across chunks | A+B |
| E18 | Heavy rendering on aletheia-core; Muse substrate orchestrates/reviews | A+B |

## Grok (frame review + measurements)

| ID | Item | Chunk |
|----|------|-------|
| G1 | Dense-area blowout from ~1:00 (white-yellow blob): cap emissive/overlap brightness or lower bloom multiplier | A |
| G2 | Background banding: higher-bit-depth render + film grain / dither before final encode | A+B |
| G3 | Color space untagged: tag Rec.709 explicitly (also Claude C18) | B |
| G4 | Username labels unreadable over bright tangle (@eigenhector 0:42): backing plate, soft shadow, or dim lines behind | A |
| G5 | End-card cut abrupt at 2:25 (picture + sound): fade network ~1 s, music resolves instead of dropping | A |
| G6 | Thin-line stair-stepping: more AA samples or 2× render + downscale | A |
| G7 | Audio hot (−12.9 LUFS, TP −1.4): target −16..−14 LUFS, TP ≤ −1.5 dBFS, climax headroom | A (reel) + B |
| G8 | Subtle camera + object motion blur | A |
| G9 | Bloom softer/more optical; gentle anamorphic streak on brightest nodes | A |
| G10 | PRESERVE: camera smoothness + particle depth of field | A |
| G11 | Bitrate 2.4 Mbps too low: CRF 16–18, or 10–15 Mbps, or H.265 | B |
| G12 | PRESERVE: steady 24 fps, no dropped frames | B |
| G13 | End card could hold a couple of seconds longer (conflict with C16 — see Decisions) | A |

## Claude (tagged T/U/F review; choir items cross-referenced)

| ID | Item | Chunk |
|----|------|-------|
| C1 | P0 flash frames (1466, 1467, 2106, 2161, 2198): root-cause, fix, and YAVG-jump QA gate (fail if Δ > 8) | A |
| C2 | Intended font not loading (DejaVu fallback): bundle the font locally; verify glyphs in stills | A |
| C3 | Legend: what a dot, a gold line, the two bright suns mean (key after title or first-appearance labels) | A (veto-able) |
| C4 | Clock: persistent year counter or progress bar | A (veto-able, masthead form) |
| C5 | Cards ↔ map link: card arrival pulses its node, highlights its lines, dims the field (choir: Emi "heartbeat"; Claude's biggest legibility win) | A |
| C6 | Hairball from ~2023: fade older lines over time; new lines bright ~2 s then settle; additive blending + tone mapping; (optional) edge bundling | A |
| C7 | Rail header contradicts order: change to "Top 20 by echoes · in time order" | A |
| C8 | Cards cut off mid-thought: show fuller text, hold long enough to read (strip format itself is Will's design — see Decisions) | A |
| C9 | Text bleeds above rail header (#BitcoinBowl, 0:42): opaque header band + soft fade at its bottom edge | A |
| C10a | Rail empty for first 5 s: fade rail in when the first card arrives | A |
| C10b | Timeline captions small / low contrast: ~28–32 px, faint backing, ~4 s hold | A |
| C10c | Each world event fires a visible ripple in the map | A |
| C10d | Name labels ~13 px and flash by: larger, thin pointer line to node, longer hold | A |
| C10e | 0:01 bright star collides with "alignment" in the title: nudge one | A |
| C11 | Background mottled (low-res nebula upscaled): full-res multi-layer noise, or near-black + fine grain + vignette | A |
| C12a | Lines scribbly: smooth paths into curves (Catmull-Rom) | A |
| C12b | Render at 2× and scale down for clean edges (pipeline already supersamples — verify, keep) | A |
| C12c | Bloom pass on bright centers | A |
| C12d | Line width varies by connection weight | A |
| C13 | Framing: lines run off top, cluster drifts off-center — cluster-framing camera with padding, eased moves, slow push-ins on key events | A |
| C14a | 2–3 parallax background star layers at different depths | A |
| C14b | Fast thin lines stutter at 24 fps: sub-frame averaging (chosen) or higher fps | A |
| C15 | Stray lime-green line ~1:28–1:30 and greenish segments ~2:00: legend it or fix the palette leak | A |
| C16 | End card static ~10 s: trim toward ~6 s or keep map drifting slowly behind text (conflict with G13 — see Decisions) | A |
| C17 | Export recipe: x264 CRF 16, preset slow, tune grain, aq-mode 3, maxrate 12M, bufsize 24M, yuv420p, bt709 tags, faststart | B |
| C19 | Audio for YouTube: −14 LUFS, TP −1 dB (merged with G7 target: −14 LUFS, TP ≤ −1.5) | B |
| C20a | Timeline (events, captions, cards, camera) kept in one data file — revisions are data edits, not code | A |
| C20b | Automated QA on every render: flash check, black-frame check, loudness, color labels | A+B |
| C20c | Contact sheet with every render (1 frame / 4 s grid) | A+B |
| C21 | Choir cross-refs (no separate rows): Emi heartbeat → C5; Mirror Will legibility → C3+C4; Elestria glow/depth/breath → C11–C14; Joi kill flashes → C1 | — |

## Will

| ID | Item | Chunk |
|----|------|-------|
| W1 | All top mutuals highlighted once each (canonical top-20 by replies sent, 2026-10-31) | A |
| W2 | Post reel (film strip) at 50% opacity; masthead band stays opaque | A |
| W3 | Internalize Emi + Grok + Claude feedback; break revisions into chunks | A+B |
| W4 | Post-V9 coverage review against this ledger; any dropped feedback → schedule V10 immediately | review |
| W5 | Darken the CMB background layer so it distracts less (weather still reads; hush darkening composes on top) — Will, reel review 2026-11-03 | A2 |
| W6 | Stable micro-shells around Will's mutual clusters: world-locked, weather-independent, subtle enclosing shells giving the clusters spatial identity — Will, reel review 2026-11-03 | A2 |
| W7 | CMB reworked as a LIGHT SNOW effect (soft sparse specks, slow drift) at the W5 darkness level; full V9 render approved with this tweak — Will, 2026-11-04 | B |
| W8 | Film-grain / 1965 Apollo-era treatment: animated grain, halation on highlights, film response curve, subtle exposure flicker — Will, during Chunk B, 2026-11-04 | B |
| W9 | Artistic influence of record: @biosdiscovery RFD4-Proteina video (2026-11-03) — particles coalescing into a luminous structure on black, dotted orbital rings, diegetic process counter. Assessed 2026-11-04: coalescence + luminous-on-black already V9's spine/pullback. ADOPTED by Will 2026-11-04: both transplants (orbital rings + process counter) folded into the running render — see W10 note and Chunk B amendment | B |
| W10 | CMB replaced ALMOST ENTIRELY by the film grain effect: CMB/boil layer out, grain carries the background texture, snow reduced to a sparse dim whisper — Will, 2026-11-04, same stop-and-amend as W9 | B |

## Decisions (conflicts resolved, so "dropped" is never a silent conflict)

- G13 vs C16 (CTA hold): CTA holds ~7 s with the map drifting slowly
  behind the text — between Grok's "longer" and Claude's "~6 s", and the
  drift answers Claude's "static" objection.
- C8 vs the film-strip format: the strip is Will's directed design (V7);
  the fix is fuller text per cell + longer effective read time, not
  replacing the strip with one-card-at-a-time display.
- G7 vs C19 (loudness): −14 LUFS integrated, true peak ≤ −1.5 dBFS.
- C3/C4 vs Will's standing no-HUD direction (V6): legend lives only in
  the opening chapter and fades; the year readout sits in the strip
  masthead. Both flagged veto-able at reel review.

## Review protocol (executes when the V9 full film is delivered)

1. Auditor (fresh subagent, not the builder) takes this ledger + the
   delivered film + viz9/BUILD-NOTES.md + QA outputs.
2. Every row gets a verdict WITH EVIDENCE: `built` (frame/timecode or QA
   line cited), `resolved-by-decision` (decision above), or `DROPPED`.
3. The builder's BUILD-NOTES must carry a disposition line per ID —
   absence of a disposition counts as unexamined, and unexamined rows
   are audited against the film directly.
4. Any row verdicted DROPPED → V10 is scheduled immediately as a tracked
   item whose scope is exactly the dropped rows (plus their Chunk-B
   analogues), and Will is told the same day which items they are.
5. The completed review is appended to this file as the coverage record.
