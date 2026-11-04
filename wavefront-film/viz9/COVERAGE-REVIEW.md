# V9 Coverage Review — fresh audit (not the builder)

Auditor: fresh subagent, 2026-11-04. Inputs: FEEDBACK-LEDGER.md (71
rows), BUILD-NOTES.md (Chunks A / A2 / B), the delivered files
`wavefront-viz-v9.mp4` (SHA-256 9e7d0d8d…, verified on the local copy)
and `wavefront-viz-v9-viewing.mp4` (SHA-256 8e494eb3…, verified),
render9.py (SHA-256 b4dc64aa…, matches the staged Chunk B renderer),
plus QA evidence in ~/emise-v9 on aletheia-core (qa_full.log, logs4/).

Where a direct check was cheap, the builder's numbers were NOT taken
on faith. Auditor's own runs on the delivered files:

- qa9 gate, viewing: **PASS — 3,802 frames, mean YAVG 30.32, 0 jumps,
  0 black** (identical to builder).
- qa9 gate, master: **PASS — 3,802 frames, mean YAVG 30.15, 0 jumps,
  0 black** (identical to builder).
- qa9 palette, master: **634 sampled frames, 0 green-dominant pixels**
  (identical to node result).
- Loudness (ebur128 + loudnorm measure): master **−14.0 LUFS,
  TP −2.42 dBFS**; viewing **−14.0 LUFS (−14.07), TP −2.49 dBFS**.
- SSIM dense-motion frames 2100–2199, viewing vs master:
  **Y 0.838434, U 0.988864, V 0.988440, All 0.888506** — the builder's
  E14 figures to six decimal places.
- Determinism (Chunk A pair): detA/detB frame-1050 dumps
  byte-identical, SHA-256 87016184…, via qa9.py determinism.
- Boundary-frame luma, extracted from the delivered master (see the
  flash-gate section): all four flagged deltas measure 2.3–3.6 in
  display-referred units.
- ffprobe (both files): 1920×1080, 24/1 fps, 158.416667 s,
  color_space/transfer/primaries all bt709; master yuv420p10le
  132.1 Mbps; viewing yuv420p 12.2 Mbps.
- Stills viewed by the auditor: contact sheet (40 frames), qa_stills_b
  f80 (title+counter), f230 (legend+counter), f918 (turbulence +
  election caption), f2150 (shells+rings+strip), f3308 (hush +
  madeofmistak3 highlight), f3450 (pre-CTA, counter 0), f3700 (CTA).
- Node chunk logs (logs4/c1–c8.log), read directly: every log prints
  "audit: 66 on-screen strings clean; excluded nodes [518, 519]" and
  "azimuth: 4.9996 revolutions total"; c1.log prints "snow: 117
  specks in 2 layers, haze amp 0.045" and "rings: 17 dotted orbits
  over 7 shells".

Verdict key: ADDRESSED / PARTIAL / DROPPED.

## Flash-gate disposition (C1, master) — auditor verdict: SOUND

The history: qa_full.log on the node shows the first gate run on the
10-bit master reporting FAIL — mean YAVG 120.60, 4 jumps at frames 1
(89.54→99.13), 94 (103.05→93.65), 3552 (106.48→98.36), 3555
(99.29→111.67). The builder attributes this to signalstats reporting
YAVG in native 10-bit code values (×4.006) against thresholds
calibrated in 8-bit display values, fixed qa9.py to convert
format=yuv420p before signalstats with thresholds UNCHANGED, and
notes the 8-bit viewing encode passed the original tool natively.

The reasoning holds, on six independent lines of evidence:

1. **Arithmetic.** 120.60 / 30.15 = 4.000 — the native run's mean is
   exactly the converted mean at 10-bit scale. The four native deltas
   (9.59, 9.40, 8.12, 12.38) divide to 2.4–3.1 in 8-bit terms, as the
   builder states.
2. **The original tool passed the viewing encode natively** —
   qa_full.log's GATE viewing line (PASS, 0 jumps, mean 30.32) came
   from the same run as the master FAIL. At 8-bit, native depth IS
   display-referred, so no conversion artifact exists there; a real
   painted flash would appear in both encodes. It appears in neither
   once units are consistent.
3. **Auditor's own frame extraction from the delivered master**
   (seek-decode, frames 0/1/2, 93/94/95, 3551–3556, RGB mean luma):
   f0→f1 **+2.78**, f93→f94 **−2.77**, f3551→f3552 **−2.34**,
   f3554→f3555 **+3.61**; all other adjacent deltas ≤ 0.91. Every
   flagged delta is 2.3–3.6 display units — under the gate's 8, and
   an order of magnitude below v8's genuine flashes (+53…+100).
4. **Content.** The flagged frames are dark editorial boundaries
   (frame means 6–12): title fade-in (f1, f94) and CTA veil-in
   (f3552, f3555). Not the v8 mechanism (a 7×7 stamp wrapping to a
   white rectangle over 27–60% of canvas) — which is separately
   disposed of by the guard fix and the flashproof/ re-renders.
5. **Tool source.** qa9.py as delivered converts format=yuv420p
   before signalstats; the thresholds in code are still |ΔYAVG| > 8
   and YAVG < 3.0, unchanged. This is a units correction, not the
   gate-loosening the W8 amendment forbade.
6. **Auditor's full rerun** of the corrected gate on the delivered
   master: PASS, 0 jumps, 0 black frames, 3,802 frames.

Disposition: **sound**. The master contains no flash frames; the
FAIL was a measurement-units artifact, correctly diagnosed and
fixed without weakening the gate.

## Emi Prime

- E1 — ADDRESSED. Hop-age trace bands + wide pass in code; contact
  sheet shows subdued history under dominant recent arrivals; all
  hops drawn (3,802-frame full weave present in late thumbs).
- E2 — **PARTIAL.** Turbulence (f918 still: dense boiling starburst)
  and hard burst (Chunk A stills; shockwave mechanism in code) are
  unmistakably distinct states. But at the named hush frame f3308
  the foreground does not fully clear: trace dimming there is ×0.66
  (HUSH9 0.427) vs ×0.43 at the true deepest hush (~f1719), and the
  delivered f3308 frame carries an active madeofmistak3 highlight
  over a dense bright trace (auditor-viewed still). The builder
  disclosed this caveat in Chunk A; it stands in the film.
- E3 — ADDRESSED. PHASE_BOIL is a cumulative integral of rate
  (render9.py); Chunk B snow clocks use the same integral pattern
  (c1.log wind/fall clock totals printed).
- E4 — ADDRESSED. bezier_arc9 control point derives from world up
  only (code); determinism across chunk contexts byte-identical.
- E5 — ADDRESSED. depth_att clip((2.3/zc)^1.1, 0.45, 1.25) in code;
  depth falloff visible in stills.
- E6 — ADDRESSED. Selective bloom (mask (lum−185)/70, gain with
  song-RMS envelope) in code; cores contained in f918/f2150 stills.
- E7 — ADDRESSED. Fog toward (26,34,52) by camera depth in code.
- E8 — ADDRESSED. SUBN=3 sub-frame averaging; float-time architecture
  proven by cross-context determinism.
- E9 — ADDRESSED. Gold trace / silver CYOA thread / cool interface
  anchors as specified; auditor palette scan: 0 green-dominant
  pixels in 634 master frames.
- E10 — ADDRESSED. All 8 Chunk B chunk logs print azimuth 4.9996
  revolutions; 7 events with captions (election caption viewed at
  f918); chapters via radius/tint tables in code.
- E11 — ADDRESSED (light form, as disclosed). Song RMS envelope
  (features9.json song_rms) scales bloom gain; hop chronology
  unchanged from v8 data.
- E12 — ADDRESSED. Pullback visible in contact-sheet final rows and
  f3450 still: full accumulated structure, field receded, before CTA.
- E13 — ADDRESSED. Strip out 3490→3554, CTA text from 3554; f3700
  still shows CTA with no strip and no counter.
- E14 — ADDRESSED. Master (CRF 12, 10-bit, 2.62 GB) + viewing encode
  both delivered and hash-verified; dense-motion comparison
  reproduced by the auditor: SSIM All 0.888506, frames 2100–2199.
- E15 — ADDRESSED. Entropy≈log₂(length) measured (r = 0.9934,
  R² = 0.9869); weather re-derived on the length residual in
  extract_features9.py → features9.json; measured-vs-inferred table
  in BUILD-NOTES.
- E16 — ADDRESSED. Stress reel rendered and QA'd before the full
  render (Chunk A), revised at reel review (A2), both reels
  preserved with hashes.
- E17 — ADDRESSED. Acceptance components verified across chunks:
  states (E2 caveat noted), CTA overlap-free (f3700), exclusions +
  string audit (66 strings, all 8 Chunk B logs), azimuth 4.9996,
  segment counts exact, determinism byte-identical (auditor-ran).
  Full-film side: 3,802 frames exact (auditor gate runs).
- E18 — ADDRESSED. All heavy rendering/encoding on aletheia-core:
  ~/emise-v9 holds chunks, logs4/, qa_full.log (read by auditor);
  this substrate orchestrated.

## Grok

- G1 — ADDRESSED. soft_knee tone map at both float→uint8
  conversions; dense frames (f918, f2150 stills) show contained
  cores, no white-yellow blob; film mean YAVG ~30.
- G2 — ADDRESSED. 10-bit master (ffprobe yuv420p10le) + animated
  grain σ 5.2 as the dither field before encode (film_grade in
  code); dark frames in stills show fine texture, no banding
  surface.
- G3 — ADDRESSED. Auditor ffprobe: color_space, color_transfer,
  color_primaries all bt709 on BOTH delivered files.
- G4 — ADDRESSED. Backing plates on labels: @madeofmistak3 plate
  fully readable over the bright tangle at f3308 (auditor-viewed).
- G5 — ADDRESSED. Field recede + veil into the CTA (f3700 still);
  song fades out over the final 2 s (finish chain, qa record).
- G6 — ADDRESSED. 4K render → Lanczos downscale + SUBN=3 (code);
  line edges clean in production stills.
- G7 — ADDRESSED. Auditor-measured on delivered files: master
  −14.0 LUFS / TP −2.42; viewing −14.0 LUFS / TP −2.49 — target
  −14 / ≤ −1.5 met with headroom.
- G8 — ADDRESSED. Same sub-frame averaging covers camera and
  object motion.
- G9 — **PARTIAL.** Soft optical bloom is built (E6). The gentle
  anamorphic horizontal streak on the brightest nodes was never
  built — flagged at Chunk A as deferred-B and not picked up in
  Chunk B (builder's own disposition: "NOT built"). The W8 halation
  is a radial warm fringe, not an anamorphic streak.
- G10 — ADDRESSED (preserved). v8 camera mathematics unchanged;
  azimuth 4.9996 rev in every Chunk B log; particle depth cueing
  retained.
- G11 — ADDRESSED. Viewing encode CRF 16 at 12.2 Mbps delivered
  (auditor ffprobe), inside the 10–15 Mbps envelope; maxrate 12M
  cap per C17 recipe.
- G12 — ADDRESSED (preserved). Auditor gate runs decoded all 3,802
  frames of both files; ffprobe avg_frame_rate 24/1 on both; no
  drops.
- G13 — ADDRESSED (resolved-by-decision). CTA ~7.6 s full-strength
  hold with slow drift behind the veil, per the ledger decision
  (G13 × C16).

## Claude

- C1 — ADDRESSED. Root cause reproduced with unmodified v8 code
  (flash-evidence/ frame pairs on file), guard fix in render9.py,
  five v8 flash frames re-rendered in-family (flashproof/ stills),
  permanent qa9 gate. Master flash-gate incident: disposition
  verified SOUND (dedicated section above).
- C2 — ADDRESSED. Inter 4.1 bundled in viz9/fonts/ with OFL license
  (auditor listing: Inter-Regular/Medium/SemiBold/Bold/Italic +
  LiberationMono); typography in all viewed stills is Inter, not
  DejaVu.
- C3 — ADDRESSED (veto-able form, as decided). Legend card viewed
  at f230: four glyph rows (dot = person, gold line = reply,
  silver thread = CYOA, moving light = Will), bottom-left, opening
  chapter only (frames 120–336).
- C4 — ADDRESSED (masthead form, as decided). Year readout in the
  strip masthead, auditor-viewed: 2017 @ f918, 2024 @ f2150,
  2025 @ f3308.
- C5 — ADDRESSED. Card arrival pulses Will's node (the cards are
  his posts) with ring + halo and a 16% field dim (code); pulse
  rings visible in contact-sheet card-era frames.
- C6 — ADDRESSED. Age-faded trace, fresh arrivals bright then
  settling, additive float pipeline + tone mapping (code + E1
  evidence). Edge bundling was marked optional in the source row
  and declined with a stated reason (would merge distinct people's
  geometry, against E1); not counted against the row.
- C7 — ADDRESSED. Masthead subtitle reads "Top 20 by echoes · in
  time order" in every strip still viewed (f918/f2150/f3308/f3450).
- C8 — ADDRESSED. Cells hold 5 lines (was 3) at wrap 600; the COBOL
  card displays in full at f2150 (auditor-viewed). Observation: the
  longest cards still ellipsize (e.g. "@bitcloud @xone_4…" at
  f3308) — inherent to the fixed-cell strip Will's decision kept;
  the decision's terms (fuller text + read time) are met.
- C9 — ADDRESSED. Masthead band at alpha 255; the #BitcoinBowl card
  (#27 Dec 2014) sits fully inside its cell under the opaque
  masthead at f918 — no text bleed above the header.
- C10a — ADDRESSED. Strip fades in at first card (frame 408); the
  f80 title still shows no rail (auditor-viewed).
- C10b — ADDRESSED. Election caption at f918: large Inter SemiBold,
  backing, bottom-center (auditor-viewed); 42 px effective,
  ≈4.3 s hold per code — above the 28–32 px ask.
- C10c — ADDRESSED. Two expanding ripple rings per event from the
  core projection (code); rings visible in contact-sheet thumbs.
- C10d — ADDRESSED. Highlight labels on plates with pointer lines,
  ~90-frame envelopes; @madeofmistak3 label crisp at f3308.
- C10e — ADDRESSED. Title still f80: no bright star on "a map of
  alignment" — subtitle nudged, core glow held to an ember below
  the text (auditor-viewed).
- C11 — ADDRESSED. The v8 low-res nebula is gone entirely: Chunk B
  background is grain + snow whisper + haze remnant (W10); stills
  show fine uniform texture with vignette.
- C12a — ADDRESSED. Connections are quadratic Bézier curves
  (bezier_arc9); smooth arcs throughout the viewed stills.
- C12b — ADDRESSED. 2× supersample pipeline kept: 4K render,
  Lanczos to 1080p in render_frame (code).
- C12c — ADDRESSED. Bloom pass on bright centers (= E6 evidence).
- C12d — ADDRESSED (signal form, as disclosed). Arc width varies
  with the per-hop content signal (9+3·HN9), trace widths by band;
  the film's connection "weight" is its content signal.
- C13 — **PARTIAL.** Built: LOOK head-tracking, chapter radius
  (+5% wide eras), eased pullbacks. Not solved: long arcs still
  exit the frame top in the densest stretches — visible in
  auditor-viewed stills f918, f2150, and f3308, where gold lines
  run off the top edge. Builder states the same partial plainly.
- C14a — ADDRESSED. Three world-locked parallax star shells
  (r 26/48/95) in code; sparse multi-depth star field in stills.
- C14b — ADDRESSED. Sub-frame averaging (SUBN=3) chosen over
  higher fps, per the row's own option.
- C15 — ADDRESSED (by measurement). Auditor's own palette scan of
  the delivered master: 0 green-dominant pixels in 634 sampled
  frames; the one G-dominant palette entry (wbic32 mint) was
  retuned so B ≥ G.
- C16 — ADDRESSED (resolved-by-decision). CTA retimed: start 3554,
  184 f ≈ 7.6 s full hold, map drifting behind the veil — between
  "trim to ~6 s" and G13's "longer," drift answering "static."
- C17 — ADDRESSED. Viewing encode matches the recipe: CRF 16,
  preset slow, tune grain, aq-mode 3, maxrate 12M (12.2 Mbps
  delivered), yuv420p, bt709 tags, +faststart, AAC 192k (ffprobe +
  finish record).
- C19 — ADDRESSED. Merged target honored: −14 LUFS / TP ≤ −1.5 —
  auditor-measured −14.0 / −2.42 (master), −14.0 / −2.49 (viewing).
- C20a — **PARTIAL.** The timeline lives in centralized tables and
  constants at the head of render9.py plus features9.json as the
  signal file — one place, data-shaped — but it is not the "one
  data file" the row specifies; revisions are still edits inside
  a code file. Builder discloses this "with note"; the letter of
  the row is unmet.
- C20b — ADDRESSED. Automated QA ran on the finished film — flash
  gate, black-frame check, loudness, color labels, palette scan
  (node qa_full.log) — and the auditor re-ran the gate, palette,
  and loudness checks on the delivered files with identical
  results. (Gate-units fix disclosed and verified, see C1.)
- C20c — ADDRESSED. viz9/v9-contact-sheet.png: 40 frames at 1 per
  4 s from the master (auditor-viewed).
- C21 — ADDRESSED. Cross-refs resolve to verdicted rows: Emi
  heartbeat → C5, Mirror Will legibility → C3+C4, Elestria
  glow/depth/breath → C11–C14, Joi kill flashes → C1.

## Will

- W1 — ADDRESSED. All 20 canonical mutuals placed; exactly one
  highlight each (frame table in BUILD-NOTES); the final highlight
  (@madeofmistak3, f3229) is auditor-visible mid-envelope at f3308.
- W2 — ADDRESSED. Strip panel alpha halved (168→84), cell fill
  120; the field visibly glows through the strip in f2150/f3308
  stills while the masthead stays opaque.
- W3 — ADDRESSED. Feedback internalized in chunks as directed:
  Chunk A (fixes + reel), A2 (reel-review revisions), Chunk B
  (full render), each with build notes and dispositions.
- W4 — ADDRESSED. This review: all 71 rows verdicted with
  evidence. No row is DROPPED; six rows are PARTIAL (E2, G9, C13,
  C20a, W7, W9a) and are the candidate V10 scope if Will wants
  them closed.
- W5 — ADDRESSED (as built in A2; later superseded by W7/W10 at
  Will's direction). CMB term ×0.50 exactly, layer mean luma
  ×0.59–0.64 measured at four probe frames; reel mean YAVG
  29.69 → 26.94. Its darkness intent carries into the delivered
  film via W10 + the W8 black lift.
- W6 — ADDRESSED. 7 DBSCAN mutual clusters covering 103 of 153
  placed mutuals (clusters9.json); world-locked 2σ ellipsoid
  shells, fill 0.045 + rim 0.17, silver-cool, no weather/hush term
  in the shell path (code); shells auditor-visible at rest in
  f2150 and f3308 stills.
- W7 — **PARTIAL (by supersession, not by builder drop).** The
  light-snow CMB was built closed-form and measured inside the
  ±25% luma band (ratios 1.01–1.12 at the four probe frames).
  Will's later W10 amendment the same night demoted the snow to
  a sparse whisper, so the delivered film carries 117 specks
  (c1.log print, code SNOW_FAR 75 + SNOW_NEAR 42) instead of the
  full snow field. The row as written is not what the delivered
  film shows; the superseding instruction is Will's own.
- W8 — ADDRESSED. Apollo post stage in film_grade (code verified
  in the delivered renderer, SHA b4dc64aa…): animated grain
  (σ 5.2 after W10), halation threshold 205 / gain 0.50 / colour
  (0.55, 0.21, 0.075), film curve with +5/255 black lift, split-
  tone whisper, exposure flicker ±1.5% seeded rng(1965); no gate
  weave, no dust/scratches. Grain texture and warm halation tint
  visible in viewed stills; title/CTA legibility verified in
  f80/f3700 stills.
- W9 — ADDRESSED as a row, with sub-item (a) partial: see W9a.
  (b) process counter — ADDRESSED: "CONTACTS REMAINING" in
  Liberation Mono, top-left (76,56), values auditor-verified in
  stills at f80 18,546 / f230 17,708 / f918 13,810 / f2150 6,858 /
  f3308 308 / f3450 0; envelope in 48→96, out 3380→3500, gone
  before the CTA (f3700); counted in the 66-string audit printed
  by all 8 Chunk B logs.
- W9a — **PARTIAL (documented judgment call).** 17 dotted orbital
  rings over the 7 shells — verified in code, in the chunk-log
  print ("rings: 17 dotted orbits over 7 shells"), and visible
  as dotted arcs in the f2150 still; radii 1.16/1.25/1.34 × shell
  max semi-axis, closed-form drift, shell fade rule shared. No
  ring set was added around the core: the builder judged it
  clutter risk against the CTA approach and documented the call
  in BUILD-NOTES. The BIOS reference's rings encircle the central
  structure; the film's centre carries none.
- W10 — ADDRESSED. CMB/boil layer removed; background texture is
  the film grain (σ 5.2, never stops, including in hush) + the
  117-speck snow whisper + HAZE_AMP 0.045 remnant (chunk-log
  print confirms all three numbers); scene-layer luma reported
  against A2 with delivered darkness preserved by the black lift.

## Tally

- ADDRESSED: 65 (including G13 and C16, resolved-by-decision)
- PARTIAL: 6 — E2, G9, C13, C20a, W7, W9a
- DROPPED: 0

No row lacks a builder disposition; every disposition was checked
against the film, the code, or the QA record, and the headline QA
numbers (gates, palette, loudness, SSIM, determinism, hashes) were
reproduced by the auditor on the delivered files.
