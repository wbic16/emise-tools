# wavefront-viz V9 — BUILD NOTES (Chunk A: fixes + renderer + stress reel)

Chunk A deliverable: `wavefront-viz-v9-stress-reel.mp4` (42.83 s, 1,028
frames, 1920×1080, 50,181,737 B, SHA-256 d9efdcda3473089ac955565286ad81…),
rendered on aletheia-core from `viz9/render9.py` (SHA-256
f54db063363a3a33007bb9b7c7e5263dba663bffd5ee7cde5c4b86e4db0c2d0b).
The full film was NOT rendered — that is Chunk B, gated on reel review.

## P0-1 — the v8 flash frames: root cause, CONFIRMED WITH EVIDENCE

Main-agent YAVG scans of both v8 files (3,802 frames each) found exactly 9
frames with |ΔYAVG| > 8, identical in master and download → the defect was
baked in at render time, not encode. Events: 1466 (38.4→127.7), 1467
(106.1), back to normal 1468; singles 2106 (138.7), 2161 (91.5), 2198
(111.9). Not chunk boundaries (≈475 f; 1425/1900), so not a seam.

**Mechanism.** In viz8/render8.py `render()`, the trace-head core block
`arr[max(0, cy-3):min(H, cy+4), max(0, cx-3):min(W, cx+4)] = 255.0` is
UNGUARDED (the node-core block in the same function is guarded). When the
projected trace head is in front of the camera (ok=True) but off-canvas at
negative (cx, cy), `min(H, cy+4)` returns a negative stop → NumPy reads it
as from-the-end → the 7×7 stamp becomes a giant white rectangle anchored
at the canvas corner.

**Reproduction** (`viz9/repro_flash.py`, unmodified v8 code; PNGs in
`viz9/flash-evidence/`): head coords on the flash frames — 1466 (−10,−952)
paints 56.0% of canvas; 1467 (−201,−1240) 40.6%; 2106 (−238,−794) 59.6%;
2161 (−1103,−1356) 26.7%; 2198 (−390,−1156) 42.0%; all neighbour frames
on-canvas, 0.0%. Re-render YAVG matches the shipped values after the YUV
limited-range conversion (×0.859+16). Airtight.

**Fix (render9.py).** The head block is guarded:
`if 3 <= cx < W-3 and 3 <= cy < H-3`.

**Proof.** The five frames re-rendered with render9.py at production
quality (SUBN=3) on the ranch (`viz9/flashproof/`): luma means 1466: 23.40,
1467: 24.05, 2106: 25.67, 2161: 23.81, 2198: 21.27 — all in family with
their neighbours (largest adjacent step ≈ 1.8, vs v8's +89/+68/+100/+53/+74).

**Permanent gate.** `viz9/qa9.py gate` — per-frame YAVG via ffmpeg
signalstats; FAIL if any |ΔYAVG| > 8 between consecutive frames or any
frame's YAVG < 3.0 (black). Runs on every segment now and on the full film
in Chunk B. Chunk A results: PASS on all 8 segments (1,076 frames) and on
the assembled reel (the 0.4 s editorial dissolves stay under the gate too).

## Scientific integrity — v8's "entropy" was a length meter

Measured over the 18,762 hops of viz8/features.json: r(entropy_bits, ntok)
= 0.8526 (Spearman 0.9912); **r(entropy_bits, log2 ntok) = 0.9934**; OLS
entropy ~ a + b·log2(ntok): a = 0.0737, b = 0.9489, **R² = 0.9869**; median
entropy/log2(ntok) = 1.000 (most tweets' tokens are nearly all unique, so
Shannon entropy ≈ log2 of the count, mechanically). Residual std 0.1551
bits; r(residual, ntok) = −0.1512; r(TTR, ntok) = −0.1573.

**Correction (extract_features9.py → features9.json).** The v9 weather
signal is `ent_sm9`: the OLS residual of entropy on log2(ntok) (Hres),
[p2,p98]-normalized, smoothed with v8's two-window smoother and
re-normalized. Consequences, stated plainly:

- The boil still breathes with lexical diversity *beyond* length, but most
  of what v8 called "entropy weather" was tweet length. v8's BUILD-NOTES
  claim is superseded by this measurement.
- The deepest hush window MOVES: under the corrected signal it is hops
  9175–9775 (mean hush 0.459, center ≈ frame 1719), not the final 600 hops
  as in v8. The ending remains a hush (final-600 mean 0.345; frame 3308
  sits at HUSH9 = 0.427 with weather at its floor, ENT_SM9 = 0.000), just
  not the deepest one. The reel's hush segment stays at ~3308 per the
  brief; frame 1719 is documented here as the deepest-hush center.
- Cohesion (VADER/caps/punctuation), intensity, bursts, and tone are
  carried from v8 unchanged — they never touched entropy.

**Measured vs artistically inferred (the ledger E15 table).**

| MEASURED from data | ARTISTICALLY INFERRED (design) |
|---|---|
| Landing times, nodes, coordinates (data.json) | Hush as a state (a rule over weather + tone) |
| VADER sentiment, caps/punct density, cohesion | Chapter tints and radius easing |
| Burst membership (155 hops, 17 hard) | Bloom, depth attenuation, fog, soft knee |
| Song RMS envelope (features9 `song_rms`) | Highlight moments (densest-window rule) |
| Hop chronology, CYOA traversal positions | Card pulse target (Will's node — the cards are his posts) |
| Weather = length-residual lexical diversity | Legend card and year readout (interface, not data) |

## Renderer changes (render9.py, from render8.py; v8 files untouched)

- **Phase integration (E3):** `PHASE_BOIL = cumsum(0.30 + 2.4·ENT_FRAME)`;
  `boil_phase(ff)` interpolates the integral. v8 multiplied rate × elapsed.
- **Camera-free geometry (E4):** `bezier_arc9` builds its control point
  from world up (0,0,1) (fallback (1,0,0) when the chord is parallel);
  the camera is never consulted, so filaments are stable under camera
  motion by construction.
- **Temporal depth (E1/C6):** trace alpha by hop-age — <250: 105, <1200:
  74, <2600: 44, else 20 (widths 6/6/5/4), plus a faint wide pass (alpha 6,
  width 13) under 1,600 hops of age. History subsides; the active arrival
  (head stamp + boosted arcs) dominates. Nothing is deleted.
- **Hush clears the foreground (E2):** trace ×(1−0.80·HUSH_F), wide pass
  likewise, arcs ×(1−0.60·HUSH_F), nodes ×(1−0.40·HUSH_F), head gain
  ×(1+0.60·HUSH_F), boil amplitude ×(1−0.65·HUSH_F). (Strengthened after
  stills review: the first pass at 0.55 did not read at 2025-era density.)
- **Lighting:** `soft_knee` tone map (linear to 200, tanh knee above) at
  both float→uint8 conversions; selective bloom at 1080p (mask
  (lum−185)/70, GaussianBlur 7, gain 0.45·(0.85+0.30·song-RMS envelope));
  depth attenuation clip((2.3/zc)^1.1, 0.45, 1.25); fog toward (26,34,52),
  factor clip((zc−2.3)/4, 0, 0.5); 5-octave background (vs v8's single
  low-res nebula) + one fixed seeded grain field (σ = 2.0) + vignette;
  three world-locked parallax star shells (r 26/48/95).
- **Chapters (E10):** the 7 event boundaries split 7 chapters; radius
  multipliers [0.96, 1.00, 1.05, 1.03, 0.94, 0.98, 1.00] × RADM and warm
  tints [0.0, 0.10, −0.70, −0.90, 0.80, 0.30, 0.20] on the background,
  midpoint-interpolated and 201-frame smoothed. Azimuth untouched —
  every render log prints "azimuth: 4.9996 revolutions total".
- **Float-frame architecture:** camera, signals, envelopes are continuous
  functions of ff; `render_frame` averages SUBN sub-frames at f ± 1/3
  (reel: SUBN=3), then one Lanczos resize to 1080p, then bloom.
- **Top mutuals (W1):** all 20 canonical mutuals verified placed (72–187
  type-1 landings each). Highlight = the landing opening their densest
  ±150-hop landing window (frame ≥ 150, earliest on ties): halo + core
  stamps, expanding ring, the arrival arc boosted and whitened, backed
  name plate with a gold pointer line, ~90-frame envelope. Frames: ctzn5
  655, dakami 1141, eigenhector 1236, mimi10v3 1610, megs_io 1688,
  jaelruble 1727, prmshra 1813, eloffd 1902, heyellieday 2011,
  vveeveeanna 2012, bitcloud 2150, viemccoy 2215, sporadicalia 2221,
  jaivinwylde 2370, djcows 2473, izzyz 2481, ki11switch03 2653,
  wordgrammer 3037, 1mortrix 3134, madeofmistak3 3229. eigenhector was
  removed from the legacy callouts — his one moment is the highlight;
  the other four legacy callouts remain, now on backing plates.
- **Card↔map pulse (C5):** Most Echoed cards are Will's own posts, so the
  pulse lands literally on the author: Will's node (index 520) gets halo
  + core stamps and an expanding ring while the field dims 16%
  (envelope exp(−age/14), age < 60).
- **Strip (W2/C7/C8/C9/C10a):** panel alpha halved (168→84), cell fill
  120, sprockets 26 — the field glows through; masthead band FULLY opaque
  (255 — at 245 the exiting cells' bright text still ghosted through,
  verified in a v9 still before the fix); header subtitle corrected to
  "Top 20 by echoes · in time order"; cells hold 5 lines (was 3) at wrap
  600 — several posts now display in full; strip fades IN at the first
  card (arrival frame 408) instead of sitting empty, and is fully out
  across 3490→3554, before the CTA.
- **Captions (C10b/C10c):** Inter SemiBold 84 @4K (42 px at 1080p),
  backing plate, 104-frame (≈4.3 s) hold; each event fires two expanding
  ripple rings from the core projection (delays 0/14 f, speeds 13/9,
  alphas 100/55).
- **CTA (decision G13/C16):** CTA_F0 moved 3512→3554; fade 64 f; full-
  strength hold 184 f ≈ 7.6 s with the map drifting slowly behind the
  veil (azimuth settle retimed automatically); field recede
  ×(1−0.22·smooth(3528,3618)) answers Grok's abrupt-cut note. Text is
  verbatim v6–v8.
- **Title (C10e):** core glow and head marker are held to embers while
  the title is up (ramp frames 42→130) and the subtitle nudged down —
  no bright sun sits in "a map of alignment" (verified in stills).
- **Font (C2):** Inter 4.1 bundled in `viz9/fonts/` (SIL OFL 1.1, license
  file included), loaded by explicit path; glyphs inspected in stills —
  Inter, not DejaVu, everywhere (title, legend, captions, labels, strip).
- **Green (C15):** no lime-green line exists in the v8 master at Claude's
  timestamps — frames 2136/2880/2900 measure ZERO green-dominant pixels
  (mask G−max(R,B)>25 & G>110). The only G-dominant palette entry was
  wbic32's node mint (134,188,174); tightened to (126,176,182) and its
  callout to (198,226,228) so B ≥ G. The reel scans 0 green-dominant
  pixels in 172 sampled frames; the scan is part of qa9.py.

**Incident during ranch rendering (fixed, verified):** the first launch
crashed in the hard-burst shockwave ring — `project()` returns arrays and
two ellipse coordinates missed their `[0]` index; the ranch venv's Pillow
13 raises TypeError on shape-(1,) coordinates (this VM's Pillow tolerated
them, which is why local stills passed). All renders were stopped, the
two call sites fixed (plus float() hardening on the event-ripple ellipse),
frame 1050 re-verified on the node, and all segments relaunched clean.
Chunk B must use the staged render9.py at SHA-256 f54db063….

## Stress reel — segment map

| Reel (approx.) | Timeline frames | Content |
|---|---|---|
| 0.0–12.5 s | 0–301 | title, legend (120–336), first arrivals, first cards |
| 11.7–16.3 s | 868–969 | turbulence (center 918), 2016 election caption |
| 15.9–20.6 s | 1003–1104 | hard bursts at 1048.7 + 1063.9 (center 1053) |
| 20.2–28.5 s | 1096–1286 | dakami highlight 1141, eigenhector 1236 |
| 28.1–32.7 s | 3258–3359 | hush (center 3308; HUSH9 0.427, weather at floor) |
| 32.3–42.8 s | 3520–3802 | pullback, strip-out, CTA (≈7.6 s full hold) |

Blocks join with 0.4 s dissolves; the song is sliced at the same timeline
offsets, crossfaded to match, faded out over the final 2 s.

**Audio:** single-pass loudnorm undershot (−11.9 LUFS / −1.3 dBTP
measured). Finished with two-pass measured loudnorm
(`viz9/fix_reel_audio.py`; WAV TP target −1.7 to pre-compensate AAC
overshoot). **Delivered reel, measured on the file: −14.1 LUFS
integrated, true peak −1.7 dBFS** — target (−14 / ≤−1.5) met.

## QA results (all on the delivered files)

1. **Emotional states** — qa_stills/stress_turbulence_918.png (woven,
   boiling starburst), stress_burst_1053.png (particle spray smeared by
   sub-frame blur + shockwave ring, distinct from the weave),
   stress_hush_3308.png (weather frozen at ENT 0.000, foreground dimmed,
   head standing alone). Hush reads strongest in motion; at 3308 its
   dimming is ×0.66 trace (HUSH9 0.427) — the deepest hush (frame ~1719,
   ×0.43) is the stronger still. One constant deepens the ending if the
   review wants it.
2. **Filament stability** — world-space Bézier geometry (E4) + SUBN=3;
   adjacent-frame pair qa_stills/burst_prev_1052.png vs
   stress_burst_1053.png.
3. **CTA overlap** — qa_stills/reel_cta.png + stills_check/cta.png: zero
   strip elements; strip fully out 42 frames before CTA text starts.
4. **Exclusions** — renderer asserts in EVERY process (logs kept on the
   node): "audit: 65 on-screen strings clean; excluded nodes [518, 519]";
   forbidden substrings "orai"/"shoals" asserted absent from all strings.
5. **Determinism** — frame 1050 rendered in two chunk contexts (101-frame
   range render with V9_DUMP vs single-frame process): raw RGB dumps
   byte-identical, SHA-256 8701618446d833f51f3cd2ef69d200a2dddcac6c702611206d.
6. **Flash gate + black-frame check** — PASS on all 8 segments and on
   the assembled reel (0 jumps > 8, 0 black frames; reel mean YAVG 29.69).
7. **Contact sheet** — viz9/reel-contact-sheet.png (1 frame / 4 s).
8. **Palette** — 0 green-dominant pixels in 172 sampled reel frames.
9. **Rotation / counts** — azimuth 4.9996 rev in every log; segment
   frame counts exact: 150/151/101/101/190/101/141/141 = 1,076; reel
   1,028 frames after 5 dissolves.
10. **Flash fix proof** — the five v8 flash frames re-rendered in family
    (see P0-1).

## Two judgment calls (veto-able at reel review)

1. **Legend card** (C3 vs Will's no-HUD direction): four glyph rows —
   "a dot is a person" / "a gold line is a reply that reached them" /
   "the silver thread is CYOA — a book of choices" / "the moving light
   is Will, writing" — frames 120–336 only, bottom-left, then gone.
2. **Year readout** (C4 in masthead form): the current hop year, Inter
   SemiBold 44, right-aligned inside the strip masthead; exists only
   while the strip does.

## Conflict resolutions on record

- CTA hold: ~7.6 s at full strength with slow drift (between Grok's
  "longer" and Claude's "~6 s"; drift answers "static").
- Strip format kept (Will's design); the fix is fuller cells + read time.
- Loudness: −14 LUFS / TP ≤ −1.5 (G7 × C19), achieved −14.1 / −1.7.
- Header wording: "Top 20 by echoes · in time order" (it runs in time
  order; it is not a ranking display).
- Hush geography: the brief's 3308 kept for the reel segment; the
  corrected signal's deepest hush is at ~1719 (documented above).
- wbic32 green: no green line exists in the master (measured); the one
  G-dominant palette color was retuned anyway.

## Dispositions per FEEDBACK-LEDGER ID (Chunk A rows)

Emi Prime:
- E1 — built: hop-age trace bands (105/74/44/20) + wide pass; recent
  brighter, head dominant; all hops still drawn.
- E2 — built: turbulence (boil + dense arcs), burst (spray + shockwave
  ring), hush (foreground dimming stack + frozen weather) are separate
  mechanisms; stress stills in qa_stills/. Hush caveat in QA item 1.
- E3 — built: PHASE_BOIL is a cumulative integral of the rate.
- E4 — built: bezier_arc9 control point from world up only.
- E5 — built: depth_att clip((2.3/zc)^1.1, 0.45, 1.25).
- E6 — built: 1080p selective bloom, song-envelope gain.
- E7 — built: fog_mix toward (26,34,52) by camera depth.
- E8 — built: SUBN sub-frame averaging (reel SUBN=3).
- E9 — built: gold/silver/cool anchors kept; soft_knee caps overlap
  instead of global brightening.
- E10 — built: 4.9996 revolutions (log-verified), 7 events, chapters via
  CH_R radius + CH_WARM background tint.
- E11 — built (light form): the song's measured RMS envelope scales
  bloom gain, so musical peaks brighten the picture; hop chronology
  bit-identical to v8 (hop_float unchanged).
- E12 — built: pullback to R 6.8, center recentres, field recedes before
  the CTA (qa_stills/reel_cta.png; stills_check/cta.png).
- E13 — built: strip fully out 3490→3554; CTA text starts 3554.
- E15 — built: entropy ≈ log2(length) (r = 0.9934, R² = 0.9869); weather
  re-derived on the length residual; measured-vs-inferred table above.
- E16 — built: this stress reel, QA'd below the line in this file.
- E17 — built (Chunk A side): states distinguishable (QA 1), filaments
  stable (QA 2), CTA overlap-free (QA 3), exclusions + 65-string audit
  (QA 4), exact rotation (QA 9), exact segment frame counts (QA 9),
  determinism byte-identical (QA 5). Full-film 3,802-frame count is
  Chunk B's verification.
- E18 — built: all heavy rendering on aletheia-core (~/emise-v9); this
  VM orchestrated, assembled, and QA'd only.

Grok:
- G1 — built: soft_knee tone mapping at both conversions; bloom masked
  to highlights; dense segments' mean YAVG 34–37 with contained cores
  (see burst/turbulence stills) — no white blob.
- G2 — built (Chunk A side): fixed seeded grain (σ = 2.0) + vignette in
  every frame pre-encode (the dither function). A 10-bit pipeline is
  deferred-B (encode side; the reel chain is 8-bit yuv420p).
- G4 — built: backing plates on every callout and highlight label,
  pointer lines, longer holds; verified in dakami still + eshear crop.
- G5 — built: field recede + veil into the CTA (no hard cut); reel audio
  fades the final 2 s. The full film's song ending is a Chunk B mux on
  the same pattern.
- G6 — built: 4K supersample → Lanczos (kept) + SUBN=3 sub-frame
  averaging; production burst still shows the smoothed streaks.
- G7 — built (reel side): two-pass loudnorm; delivered reel measured
  −14.1 LUFS / −1.7 dBTP. Full-film side is Chunk B.
- G8 — built: the same sub-frame averaging (camera and objects share
  the float-time architecture).
- G9 — partially built: soft optical bloom built; the anamorphic
  horizontal streak is NOT built — deferred-B (needs a directional
  pass; flagged for reel review against Emi's restraint note).
- G10 — built (preserved): v8 camera mathematics unchanged (azimuth,
  RADM, LOOK verbatim); particle depth cueing retained and extended.
- G13 — resolved-by-decision: CTA ≈7.6 s full hold with slow drift
  (see C16).

Claude:
- C1 — built: root cause + reproduction + guard fix + re-render proof +
  permanent qa9.py gate; PASS everywhere in Chunk A (see P0-1).
- C2 — built: Inter 4.1 bundled with OFL license in viz9/fonts/;
  glyphs inspected in stills.
- C3 — built (veto-able): opening legend card, frames 120–336 only.
- C4 — built (veto-able): year readout inside the strip masthead.
- C5 — built: card arrival pulses Will's node (the cards are his own
  posts — the author literally), ring + halo, field dims 16%.
- C6 — built: age-faded trace, fresh arrivals bright ~250 hops then
  settling bands, additive float pipeline + tone mapping. Edge bundling
  NOT built (Claude marked it optional; it would merge distinct
  people's geometry, against E1's preserve-everything rule).
- C7 — built: "Top 20 by echoes · in time order".
- C8 — built: 5-line cells (was 3), wrap 600; several posts now complete
  (COBOL post verified in the strip still).
- C9 — built: masthead band alpha 255 (245 still ghosted — caught in a
  v9 still, fixed, re-verified in production stills).
- C10a — built: strip fades in at the first card (frame 408), no empty
  rail in the title stills.
- C10b — built: captions at 42 px effective (Inter SemiBold 84 @4K) —
  above the 28–32 px ask, matching the film's display type — with
  backing plate and ≈4.3 s hold.
- C10c — built: two ripple rings per event from the core projection.
- C10d — built: callouts 33 px effective on plates, 84 f holds;
  highlight labels 38 px with pointer lines, ~90 f envelopes.
- C10e — built: title-era ember rule for core glow + head; subtitle
  nudged; title still verified clean.
- C11 — built: 5-octave background noise (finest octave 384×216) +
  fixed grain + vignette; the v8 mottling is gone in stills.
- C12a — built: connection curves are quadratic Béziers, and the actual
  scribble source (camera-coupled control points) is fixed under E4.
- C12b — built: 2× supersample pipeline kept and exercised (4K →
  Lanczos → 1080p in render_frame).
- C12c — built: bloom pass on bright centers (E6).
- C12d — built (signal form): arc width 9+3·HN9 (per-tweet content
  signal), trace widths 13/6/6/5/4 by band, comet tails taper — in this
  film a connection's "weight" IS its content signal.
- C13 — built (partial, stated): LOOK head-tracking + chapter radius
  (+5% in wide eras) + eased pull retained; long world-bowed arcs still
  exit the frame top in the densest stretches (visible in the turbulence
  still) — inherent to the geometry at close camera; reel review may
  ask for a wider default radius in Chunk B.
- C14a — built: three world-locked parallax star shells.
- C14b — built: sub-frame averaging chosen over higher fps.
- C15 — built (by measurement): zero green-dominant pixels in the v8
  master at the cited times and in the v9 reel scan; the one G-dominant
  palette color (wbic32) retuned so B ≥ G.
- C16 — resolved-by-decision: CTA retimed (3554 start, 184 f ≈ 7.6 s
  full hold, slow drift behind the veil).
- C20a — built (with note): timeline data is centralized as tables and
  constants at the head of render9.py (events, chapters, CTA timing,
  highlight rule) plus features9.json as the signal file; revisions are
  edits to those tables. It is not a separate external data file.
- C20b — built (Chunk A side): qa9.py flash + black-frame gates ran on
  every segment and the reel; loudness measured on the delivered reel;
  the reel encode carries explicit bt709 tags. Full export recipe is
  Chunk B (C17/G3).
- C20c — built (Chunk A side): reel contact sheet generated (1 frame /
  4 s). Chunk B renders get theirs from the same tool.

Will:
- W1 — built: all 20 canonical mutuals verified placed; exactly one
  highlight each (frames table above); highlight treatment = pulse +
  boosted whitened arc + plate + pointer + ring.
- W2 — built: strip panel alpha halved (168→84), cell fill 120 — the
  field glows through; masthead stays opaque per C9.
- W3 — built (Chunk A side): revisions chunked as directed; Chunk A
  ends at this verified reel; the full render was not run.

Rows assigned to Chunk B by the ledger (E14, G3, G11, G12, C17, C19)
and the W4 coverage review are not dispositioned here — they belong to
the full-film delivery and its audit.

---

# Chunk A2 — Will's two reel-review revisions (W5, W6)

Deliverable: the revised stress reel at the canonical path
`wavefront-viz-v9-stress-reel.mp4` — 42.83 s, 1,028 frames, 1920×1080,
44,006,148 B, SHA-256 f9852d988d00809b9cfbc997a84be0e590efa50cd681a1…,
audio measured on the delivered file at **−14.1 LUFS integrated, true
peak −1.7 dBFS** (target −14 / ≤ −1.5, same two-pass finish as Chunk A).
The Chunk A reel is preserved untouched as
`wavefront-viz-v9-stress-reel-a.mp4` (SHA-256 d9efdcda…, verified after
the rename); Chunk A segments are preserved in viz9/segs_a/.
**Staged renderer for Chunk B: render9.py SHA-256
1a906e97134df3f144682b85c5da17caa41927d10c45e81c05eff58102a026bb**
(local file and the copy staged on aletheia-core are byte-identical;
supersedes f54db063…). All A2 segment renders ran on the node
(~/emise-v9/segs2, logs2) at SUBN=3. The full film was NOT rendered.

## W5 — darken the CMB

Change (render9.py): the static afterglow term is scaled by
`CMB_DARK = 0.50`; the boil amplitude keeps `BOIL_KEEP = 0.70` of its
Chunk A value, so the entropy weather still reads — as motion over a
quieter field and through the gold trace, not as background
brightness. Hush composes exactly as before, multiplicatively on top:
the gain's (1 − 0.30·HUSH_F) multiplies the darkened CMB term, and
the boil's (1 − 0.65·HUSH_F) multiplies the kept amplitude.

Measurement (not a vibe): a V9_BG_DUMP hook — present in both a
hook-only build of the Chunk A baseline (render9_hookonly.py, kept for
the record) and the A2 build — dumps the background layer
pre-composite (BASE_BG + CMB + boil + chapter warmth, after vignette
and grain, before stars/nodes) at exact frames. Rec.709 luma:

| frame | layer mean luma before → after | corner (top-left 800×500) before → after | layer std before → after |
|---|---|---|---|
| 150 | 6.88 → 4.39 (×0.639) | 5.63 → 3.52 (×0.625) | 5.30 → 3.94 |
| 918 (turbulence) | 12.83 → 8.04 (×0.627) | 11.69 → 7.27 (×0.622) | 3.81 → 2.89 |
| 2150 | 17.25 → 10.19 (×0.591) | 17.85 → 10.67 (×0.598) | 4.45 → 3.12 |
| 3308 (hush) | 15.16 → 8.99 (×0.593) | 14.49 → 8.57 (×0.592) | 3.40 → 2.46 |

The CMB term itself is exactly ×0.50; the whole layer lands at
×0.59–0.64 because BASE_BG and the zero-mean grain do not scale, and
the std falling to ×0.72–0.76 says the texture is quieter but still
present (the weather is not flattened). Corroboration on the finished
reels: mean YAVG 29.69 (Chunk A) → 26.94 (A2). Before/after still:
viz9/qa_stills/stress_turbulence_918.png vs
viz9/qa_stills_a2/a2_turbulence_918.png.

## W6 — stable micro-shells around the mutual clusters

Mutual derivation (derive_clusters.py → clusters9.json): mutual status
is NOT tabulated per placed person in viz2/data.json (its kind field
marks only a small measured set), so it is derived the way
viz2/extract2.py defines a match — accountId in BOTH follower.js and
following.js (897 mutual ids in the archive snapshot), with handles
tied to accountIds through the mention/reply-target map harvested
from tweets.json. Anchors verified against the record: @ctzn5 and
@eigenhector are mutuals; @Grady_Booch and @eshear are not (follows,
not followed back). Result: **153 of the 522 placed nodes are
mutuals** (the one node with no archive id is Will's own keyless
node). The excluded account is in no cluster (members ∩ {518, 519} = ∅,
checked).

Clustering, in the film's own xyz space over the 153 mutuals:
single-linkage connected components were tried first and REJECTED on
measurement — the mutual cloud is dense (median NN distance 0.099),
so chaining percolates: one component holds 118 of 153 at τ = 0.15
and 148 at τ = 0.25. DBSCAN at eps 0.13 (just below the eps-0.15
percolation cliff), min_samples 3, minimum cluster size 4 → **7
clusters covering 103 mutuals**; the other 50 are DBSCAN noise at this
density (isolated or in sub-4 groups) and get no shell.

| # | size | centre (xyz) | semi-axes | best-known members (replies Will sent) |
|---|---|---|---|---|
| 1 | 37 | (−0.11, 0.21, −0.80) | 0.36 / 0.29 / 0.21 | @madeofmistak3 (187), @Vveeveeanna (134), @jaivinwylde (100), @megs_io (97) |
| 2 | 21 | (−0.09, 0.19, −1.21) | 0.30 / 0.17 / 0.16 | @wordgrammer (106), @slimefren132450 (45), @TheAIObserverX (34), @kuberdenis (33) |
| 3 | 13 | (0.22, 0.04, −0.76) | 0.27 / 0.19 / 0.10 | @CTZN5 (188), @bitcloud (174), @codexeditor (64) |
| 4 | 9 | (0.27, 0.55, −0.84) | 0.32 / 0.14 / 0.10 | @WagieWeeb (33), @TechBroTino (32), @HunterALanier (26) |
| 5 | 9 | (−0.07, 0.58, −0.81) | 0.33 / 0.10 / 0.10 | @JungleSilicon (62), @SterlingCooley (30), @nooriefyi (29) |
| 6 | 8 | (0.10, 0.24, −0.67) | 0.15 / 0.14 / 0.10 | @mimi10v3 (102), @sporadicalia (88), @heyellieday (86), @Ki11switch03 (73) |
| 7 | 6 | (−0.07, 0.07, −0.47) | 0.24 / 0.10 / 0.10 | @viemccoy (116), @prmshra (106), @eloffd (77) |

Shell rendering: one ellipsoid per cluster — centre = member mean,
axes = covariance eigenvectors, semi-axes = 2·√eigenvalue (floor
0.10, cap 1.60 world units). Centre and axis endpoints ride to_world
with the nodes every frame (world-locked); the screen silhouette is
the image of the unit ball under the 2×3 map of projected axis
vectors (E2 = Σ vₖvₖᵀ), rasterized analytically per pixel: fill alpha
0.045 plus a gaussian rim band (σ 0.16 in normalized radius) peaking
at 0.17 where the surface turns away — fresnel-style. Colour is a
desaturated silver-cool (158, 180, 208), fog-blended by the same law
as the nodes and depth-attenuated (clip 0.55–1.0). Shells are painted
far-to-near by centre depth, under the nodes and trace. **Stability
is structural: the shell block contains no ENT/HUSH/COH/pulse term —
its only time-dependence is the world's own transform, depth, and
the fade-in rule:** invisible below 30% of members landed (by
first-landing hop), full at 55%. In hush the shells simply hold
(qa_stills_a2/a2_hush_3308.png: foreground dimmed, shells at rest).
Honest note: at 2σ the nested near-core clusters' shells overlap and
read as soft overlapping forms (qa_stills_a2/a2_shells_2150.png);
SHELL_FILL / SHELL_RIM are the two constants to turn if review wants
them quieter still.

## QA results (A2, all on the delivered files)

1. **Flash gate + black-frame check** — PASS on all 8 segments
   (150/151/101/101/190/101/141/141 = 1,076 frames, 0 jumps, 0 black)
   and on the assembled reel (1,028 frames, 0 jumps — the 0.4 s
   editorial dissolves stay under the gate — 0 black, mean YAVG 26.94).
2. **Determinism** — frame 1050 rendered in two chunk contexts
   (1-frame range vs 21-frame range, both SUBN=3 with raw dumps):
   byte-identical, SHA-256 bcb1315b5bbc8108….
3. **Exclusions / string audit** — every render process log asserts
   "audit: 65 on-screen strings clean; excluded nodes [518, 519]".
4. **Rotation** — every render log prints azimuth 4.9996 revolutions.
5. **Palette** — 0 green-dominant pixels in 172 sampled reel frames.
6. **Contact sheet** — viz9/reel-contact-sheet.png regenerated.
7. **Audio** — measured on the delivered reel: −14.1 LUFS, TP −1.7.
8. **Colour tags** — bt709 matrix tag present; transfer/primaries
   untagged, byte-for-byte the same behaviour as the accepted Chunk A
   reel chain (full primaries/trc tagging is Chunk B's C17/G3 export).
9. **Stills** (production SUBN=3, viz9/qa_stills_a2/):
   a2_turbulence_918.png (darkened CMB), a2_shells_2150.png (shells
   around the near-core clusters — five silhouettes readable),
   a2_hush_3308.png (hush, shells at rest), a2_pullback_3480.png.

**Disclosed incident (recovered, no deliverable affected):** the
first determinism attempt failed — a single-frame `--frame` render
does not write V9_DUMP raw frames (only `--range` does), and the
range-side dump directory was cleaned before the compare ran. The
check was redone properly with two range contexts (item 2 above).

## Dispositions per FEEDBACK-LEDGER ID (Chunk A2 rows)

Will:
- W5 — built: CMB_DARK 0.50 on the static afterglow, BOIL_KEEP 0.70
  on the weather's amplitude, hush dimming composing multiplicatively
  as before; measured layer mean luma ×0.59–0.64 across four probe
  frames (table above), reel mean YAVG 29.69 → 26.94.
- W6 — built: 7 DBSCAN mutual clusters (eps 0.13, min_samples 3,
  min size 4) covering 103 of 153 placed mutuals; world-locked 2σ
  covariance ellipsoids, fill 0.045 + rim 0.17 fresnel band,
  silver-cool, depth-sorted under nodes/trace, arrival fade-in
  30%→55%, no weather/hush modulation anywhere in the shell path.

Chunk B note: the full render must use render9.py @ 1a906e97… with
clusters9.json beside it (both staged on the node under
~/emise-v9/root/wavefront/viz9/). render9_hookonly.py is a
measurement artifact only — never a render baseline.

## Chunk B — the full render (2026-11-04)

Renderer: render9.py SHA-256 b4dc64aa06e311f314f10055f55cb840b806e0a41432d9d976a4f35608c9f7f8
(local == aletheia-core copy, verified by hash after staging).

**The render was stopped and relaunched at Will's direction.** The
first full launch (snow + Apollo grade) was halted minutes in when
Will's 00:51 CST stop-and-amend arrived (ledger W9/W10): partial
chunks were deleted, the amendments were folded in, stills were
re-verified, determinism was re-proven on the final code, and the
render relaunched from frame 0. Nothing from the aborted pass
survives in the delivered film.

1. **W7 — CMB → light snow (as first built).** The CMB grain/boil
   layer was deleted outright and replaced with snow whose motion is
   closed-form per particle: FALLCLK/WINDCLK are precomputed
   cumulative clocks (integrals of the per-frame weather rates — the
   E3 pattern), so any chunk context renders byte-identical frames.
   Wind rate = (0.30 + 1.60·ENT_FRAME + 0.90·GUST_F)·(1 − 0.80·HUSH);
   fall rate = (1.00 + 0.45·ENT_FRAME + 0.55·GUST_F)·(1 − 0.88·HUSH);
   GUST_F = burst-strength gaussians capped at 1.2. Two speck layers
   (far 300 × kernel(11,1.3), near 170 × kernel(19,2.3)) over a
   480×270-upsampled haze (HAZE_AMP 0.125, tinted (146,170,212)); the
   haze gain carried a miss-fraction ramp so the layer tracked A2's
   arc. Measured pre-composite layer luma vs A2's darkened CMB
   (targets 4.39/8.04/10.19/8.99 at frames 150/918/2150/3308):
   ratios 1.08 / 1.01 / 1.07 / 1.12 — inside the ±25% band.
   This configuration was then superseded by W10 (item 3).
2. **W8 — 1965 Apollo film treatment (post stage, `film_grade`).**
   Applied after the selective bloom in render_frame; every element
   a pure function of frame number. Animated monochrome grain,
   zero-mean, per-frame seed rng(900000+f), attenuated ×(1 − 0.55·lum)
   in highlights; halation: threshold 205, gain 0.50, colour
   (0.55, 0.21, 0.075), GaussianBlur radius 16 on the
   threshold-masked highlights; film curve S: t − 0.055·sin(2πt)
   with black lift +5/255 and a soft shoulder; split-tone whisper —
   highlights (R+8, G+1.5, B−6), shadows (R−2.5, G−0.5, B+5.5),
   masks normalised to peak 1 at the extremes; exposure flicker
   ±1.5% (seeded rng(1965) walk smoothed σ60; max frame-to-frame
   Δgain 0.00019 → implied max ΔYAVG 0.008 against the gate's 8);
   extra vignette 0.13. OUT per the amendment: no gate weave, no
   dust/scratches, no scene changes. No QA gate needed loosening.
   Grain strength as launched: σ 3.8 (raised to 5.2 by W10).
3. **W10 — CMB replaced almost entirely by the film grain.** The
   snow was demoted to a sparse whisper: far 75 specks at g0 0.20,
   near 42 at g0 0.30 (117 total, 25% of the first Chunk B pass,
   and dimmer); the haze remnant cut to HAZE_AMP 0.045 so the field
   never falls to a flat void; film grain raised to σ 5.2 so the
   grain itself carries the dark field's texture (zero-mean — the
   YAVG gate is untouched by construction, and the grain never
   stops, even in hush: it is the film stock). Hush re-map: the
   snow's fall/sway clocks still settle to near-still; the trace
   dims as before. Scene-layer luma, same V9_BG_DUMP measurement as
   A2/W5 (frames 150/918/2150/3308): 3.50 / 4.70 / 5.71 / 5.41 vs
   A2's 4.39 / 8.04 / 10.19 / 8.99 — ratios 0.80 / 0.58 / 0.56 /
   0.60. The scene layer is deliberately darker (its source was
   removed, per W10); the DELIVERED field darkness is preserved by
   the W8 black lift: a 4.70 scene level at frame 918 delivers at
   ≈8.0 through the film curve, against A2-era ≈8.04 delivered.
4. **W9a — dotted orbital rings.** 17 rings over the 7 shells (3
   per shell of ≥13 members, else 2), radii 1.16 / 1.25 / 1.34 ×
   the shell's max semi-axis, planes tilted per ring in the shell
   frame (each cluster's set rotated by 0.7 rad × cluster index).
   Dots: kernel(9,1.6), colour (168,192,218), gain 0.13 × shell
   fade × depth attenuation, 36–84 dots per ring at ~0.055 world
   units spacing; drift is a closed-form phase in ff with periods
   2600/3300/4000 frames, alternating direction per ring. Rings
   paint far-to-near with their shell, under nodes/trace, and
   share the shell fade rule exactly (invisible below 30% of
   members landed, full at 55%). Judgment call, documented per
   the amendment: NO ring set was added around the core — the
   shells' rings plus the core's own event ripples and glow
   already instrument that region, and a core set read as clutter
   risk against the CTA approach. Verified in stills
   (qa_stills_b/b_shells_rings_2150.png, b_hush_3308.png).
5. **W9b — process counter.** "CONTACTS REMAINING 18,762" counting
   down as hops land (remaining = 18,762 − ⌊hop⌋, exact — stills
   show 18,546 @ f80, 17,708 @ f230, 13,810 @ f918, 6,858 @ f2150,
   308 @ f3308, 0 @ f3450), reaching 0 at the final hop (frame
   3362). Liberation Mono (OFL; bundled in viz9/fonts/), 54 px at
   4K, colour (150,190,215), alpha ≤ 150, top-left of the field
   area at (76,56). Envelope: fades in 48→96 (coexists with the
   title card without collision — verified f80), full through the
   film, fades out 3380→3500, gone before the CTA. The label is in
   the string audit: **66 on-screen strings clean** (65 + counter),
   excluded nodes [518, 519], printed by every chunk log.
6. **The film.** 8 chunks on aletheia-core under the N=4 rule (one
   track, internal chunk parallelism as in A/A2), SUBN=3, ranges
   0–476/951/1427/1902/2377/2853/3328/3802; frame counts
   476/475/476/475/475/476/475/474 = **3,802 exactly**; concat
   -c copy. Azimuth: **4.9996 revolutions** (every chunk log).
   Determinism: frame 1427 rendered in two contexts on the node
   (detA4 range 1427–1428, detB4 range 1420–1440) byte-identical,
   SHA-256 ee01f7719ea89153445861e64b160cdcc8718395de31e3d1397dceeaeb4c9d30
   in both. QA stills in viz9/qa_stills_b/ (counter+title,
   counter+legend, turbulence, shells+rings, hush, pre-CTA, CTA).
7. **Audio.** Full song (viz5 edit, 158.400 s) + afade out over the
   final 2 s. Mix measured: −12.81 LUFS integrated, TP −1.23 dBFS,
   LRA 9.90. Applied two-pass loudnorm (measured_*, linear=true,
   WAV TP target −1.7 pre-compensating AAC overshoot). Delivered,
   measured by ebur128 on the finished files: **master −14.0 LUFS,
   TP −2.4 dBFS; viewing −14.0 LUFS, TP −2.5 dBFS** — on the −14
   LUFS target, under the −1.5 TP ceiling with headroom.
8. **Encodes (E14 comparison).** Master: libx264 CRF 12, preset
   slow, tune grain, aq-mode 3, yuv420p10le, bt709 tags, AAC 320k
   → 2,616,664,549 B, 132.1 Mbps, SHA-256
   9e7d0d8dcdd12cd055068147662c8ef5f40eac96e41f255a9689b3777da3bd46.
   Viewing (C17 recipe exactly): CRF 16, preset slow, tune grain,
   aq-mode 3, maxrate 12M, bufsize 24M, yuv420p, bt709 tags,
   +faststart, AAC 192k → 241,806,383 B, 12.2 Mbps, SHA-256
   8e494eb3d9ff97bb34e8273a715ad69cb0a5ed7959eff10d75e35aecd702f4b3.
   Dense-motion comparison, frames 2100–2199: **SSIM All 0.8885
   (Y 0.8384, U 0.9889, V 0.9884); PSNR avg 37.10 dB**. What
   differs: chroma is essentially identical; the luma gap is the
   animated grain — the viewing encode rides its 12 Mbps cap
   essentially throughout (12.2 Mbps delivered) because σ5.2
   grain is incompressible, and the cap is spent smoothing grain
   fineness, not structure: the trace, shells, and text are
   preserved (37 dB on the densest motion in the film). The
   viewing encode is 241.8 MB — far over the ~55 MB chat line,
   because the W8/W10 grain holds the encode at its 12 Mbps cap
   for essentially the whole duration. Delivery routing is the
   parent's call, per the brief.
9. **QA results (all on the delivered files).**
   - Flash/black gate (qa9.py gate): master PASS — 3,802 frames,
     mean YAVG 30.15, 0 flash-jumps, 0 black frames. Viewing PASS
     — 3,802 frames, mean YAVG 30.32, 0 / 0.
   - **Gate-units incident, disclosed:** the first master gate run
     reported FAIL with 4 jumps and mean YAVG 120.60. Root cause:
     qa9 measured signalstats in the file's native depth — on the
     10-bit master YAVG is in 10-bit code values (×4.006), so
     thresholds calibrated in 8-bit display values misfired (the 4
     "jumps" were 2.4–3.1 in true 8-bit terms, at editorial
     boundaries: frames 1, 94, 3552, 3555). Fix: yavg_series now
     converts format=yuv420p before signalstats, measuring
     display-referred luma on any depth; thresholds UNCHANGED
     (|ΔYAVG| > 8, black < 3.0). The 8-bit viewing encode passed
     the original tool natively, corroborating. This is a units
     correction, not the gate loosening W8 forbade — the grade
     passes the gate as calibrated.
   - Palette scan (master, every 6th frame, 634 sampled): **0
     green-dominant pixels**.
   - ffprobe both: 1920×1080, 24 fps, duration 158.416667 s,
     color_space/transfer/primaries all bt709; master yuv420p10le,
     viewing yuv420p.
   - Loudness/TP: item 7 above.
   - Contact sheet: viz9/v9-contact-sheet.png (40 frames, 1 per
     4 s, from the master).
   - String audit: 66 strings clean (item 5); azimuth 4.9996 rev
     (item 6); frame count 3,802 exact (item 6).
10. **Transfers.** The tailnet proxy path degraded mid-task from
    ≥2 MB/s to ~90–170 KB/s, then recovered to ~1.1 MB/s; both
    files were pulled by resumable rsync and **hash-verified
    locally on arrival** — master SHA-256 9e7d0d8d… and viewing
    8e494eb3… match the node originals exactly. Both deliverables
    are in ~/workspace/wavefront/; node originals also remain in
    ~/emise-v9/ on aletheia-core.

## Dispositions per FEEDBACK-LEDGER ID (Chunk B rows)

- E14 — built: archival master preserved (CRF 12 10-bit) plus the
  C17 viewing encode; compared on dense motion (frames 2100–2199),
  SSIM/PSNR and the grain/bitrate analysis in item 8 above.
- E17-B — built: full-film acceptance battery green — states
  distinguishable (A/A2 stills + B contact sheet), CTA free of
  strip overlap (strip out 3490→3554), exclusions + 66-string
  audit clean, azimuth 4.9996 rev, frame count 3,802 exact,
  determinism byte-identical across chunk contexts (frame 1427).
- E18-B — built: all heavy rendering and encoding on
  aletheia-core; this substrate orchestrated, staged, and reviewed.
- G2-B — built: 10-bit master + the W8/W10 animated grain (σ 5.2)
  as the dither field before the final encode; no banding surface
  left untextured in the dark field.
- G3 — built: master and viewing both carry explicit bt709
  color_space / color_transfer / color_primaries (ffprobe-verified).
- G7-B — built: delivered −14.0 LUFS integrated, TP −2.4/−2.5 dBFS
  on both files (two-pass measured loudnorm; item 7).
- G11 — built: viewing encode at CRF 16 within a 10–15 Mbps
  envelope (12.2 Mbps delivered, maxrate 12M cap) — with the
  disclosed consequence that grain holds it at 241.8 MB (item 8).
- G12 — built: steady 24 fps end to end (avg_frame_rate 24/1 on
  both outputs), 3,802 frames, no drops (gate decodes every frame).
- C17 — built: the viewing encode follows the recipe exactly
  (CRF 16, slow, tune grain, aq-mode 3, maxrate 12M, bufsize 24M,
  yuv420p, bt709 tags, faststart, AAC 192k).
- C19 — built: merged target honored — −14 LUFS, TP ≤ −1.5 dBFS
  (delivered −14.0 / −2.4 master, −14.0 / −2.5 viewing).
- C20b-B — built: automated QA on the finished film: flash gate,
  black-frame check, loudness, color labels, palette scan,
  determinism — item 9. (Includes the disclosed gate-units fix.)
- C20c-B — built: contact sheet from the master at
  viz9/v9-contact-sheet.png (1 frame / 4 s, 40 frames).
- W7 — built, then superseded in part by W10: snow implemented
  closed-form and measured inside the ±25% luma band (item 1);
  Will then demoted it to a whisper (item 3), where it stands in
  the delivered film.
- W8 — built: Apollo post stage with the numbers in item 2; grain
  σ 3.8 at W8, raised to 5.2 under W10; title/CTA legibility
  verified in stills; no gate loosened.
- W9 — built: (a) 17 dotted orbital rings over the 7 shells
  (item 4; core ring set judged and declined, documented there);
  (b) CONTACTS REMAINING process counter (item 5), audited as the
  66th on-screen string.
- W10 — built: CMB/boil already gone under W7; the background
  layer was then reduced to the film grain + a 117-speck snow
  whisper + HAZE_AMP 0.045 remnant; scene-layer luma reported
  against A2/W5 in item 3, delivered darkness preserved by the
  W8 black lift.
