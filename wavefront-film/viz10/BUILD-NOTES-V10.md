# wavefront-viz V10 — BUILD NOTES

V10 = the delivered V9 film plus exactly four changes (Will,
2026-11-04): E2 hush floor, G9 anamorphic streak, C13 arc framing,
and the Most Exocortical featured-tweet set. Everything else is V9
unchanged. Base: viz9/render9.py SHA-256 b4dc64aa… (copied, never
modified; the delivered V9 files and outputs are untouched).

Status: DELIVERED 2026-11-04 — both encodes on disk in
~/workspace/wavefront/, SHA-256 verified against the node
originals; all V9 QA gates pass on V10 (below).

## Change 4 — featured tweets: the most Exocortical

Method (`viz10/score_tweets.py`, deterministic; full ranked list in
`viz10/exocortical-tweets.md`, featured set frozen in
`viz10/exo20.json`):

- Pool: Will's original posts only — the V9 strip pool (no replies,
  no retweets, no @-leading posts): 5,974 posts. One placement
  constraint added and disclosed: a featured post must fall inside
  the film's hop timeline (ts ≤ last reply ts); 0 posts dropped for
  this. Texts containing the exclusion substrings ("orai", "shoals")
  are removed before ranking: 2 dropped, listed in the md.
- Scoring (content only; engagement never scored): weighted concept
  terms on word boundaries — phext / exocortex / mirrorborn / SBOR /
  wavefront groups at 5 per distinct term; sentience / neuralese /
  "every neuron a voice" / choir groups at 4; substrate / spanning /
  Kardashev at 3; +2 per additional distinct concept group; +3
  long-horizon bonus (year ≥ 2100, "billion years", Kardashev);
  posts under 8 words score 0; −3 if the post is predominantly a
  list of terms (≥50% of ≥3 raw lines are list items) — a bare term
  list name-drops the vocabulary, a statement develops it. Ties
  break on distinct terms, then word count, then favourites
  (deterministic only), then earliest.
- Result: 527 posts carry Exocortical content. Featured top 20
  (score): #1 2023-12-17 WPOE/Kardashev welcome (20), #2 2025-05-18
  SBOR announcement (16), 2024-08-23 560 phext changes (15),
  2025-01-10 Exocortical Algorithm Priming with definitions (14),
  then statements at 12 — phext address allocation 1.1.1/*/*,
  Tensor's Horizon, Woot Nodes, "exits", the neuron-as-a-service
  game, neocortex modeling in 5 phext dimensions, and the rest in
  the md.
- Placement: the featured era is 2023-12 → 2025-05 — the Exocortex
  vocabulary does not exist in the archive before that — so strip
  arrivals run frames 1704–3286 (computed from the hop timeline),
  in the film's dense final act, instead of V9's echo-driven spread.
  The first card (the #1 WPOE post) arrives at frame 1704, inside
  the deepest-hush window; its arrival pulse is hush-suppressed
  under the E2 rule, the card itself fades in normally.
- On-screen text follows the new metric: masthead "EXOCORTICAL"
  (the longer "MOST EXOCORTICAL" collided with the year readout in
  the first stills — same 11-glyph footprint as V9's "MOST ECHOED"
  keeps the V9 layout exact), subtitle "Top 20 by content · in
  time order", cell footer "exo score N". The string audit covers
  the new set (66 strings; asserted in every render log).
- Display sanitization: Inter has no ⟡ (U+27E1) glyph — it
  tofu-boxed in the rank-17 cell — so `sanitize()` substitutes "•"
  for it on screen; the tweet's words are untouched. ⟡ was the
  only non-ASCII character in the featured 20.
- Consequence of the set, stated plainly: because the arrivals
  cluster (five cards land within frames 3154–3286, six within
  2346–2412), the strip scrolls fast there and V9's unchanged
  SUBN=3 temporal averaging motion-blurs the cell text in those
  stretches (visible in the f2400/f3274 stills; at playback speed
  it reads as scroll blur). The strip machinery is V9's, unchanged;
  the clustering is inherent to the featured era.

## Change 1 — E2: the hush floor

V9's linear hush left the named hush frame (3308, HUSH9 0.427) at
trace ×0.66 vs ×0.43 at the deepest hush (~1719, HUSH9 0.71), with an
active @madeofmistak3 highlight over the trace (coverage review).
V10 (render10.py):

- `HUSH_EFF = min(1, HUSH_F / 0.42)` — a saturating foreground
  response. At/above the knee every hush moment reaches the same
  floor: trace ×0.20 (was the 0.80 coefficient on the effective
  value), arcs ×0.40, nodes ×0.60. Frames 3308 and 1719 now sit at
  identical foreground depth by construction.
- Highlights suppressed by (1 − 0.97·HUSH_EFF) inside
  `highlight_env` — pulse stamps, expanding ring, label plate (all
  driven by that envelope) and the boosted arc (same envelope) go
  to ~3% in deep hush. Card-arrival pulses get the same factor in
  `card_pulse`.
- The backdrop is deliberately NOT re-mapped: snow settle,
  background gain and epicycle amplitude keep raw HUSH_F; the head
  keeps its (1 + 0.60·HUSH_F) stand-alone gain — in hush the head
  carries the frame, as in V9's intent.

Verification (production stills, `viz10/qa_stills/`):
foreground energy = pixels with luma > 40 in the field region
(x < 1520, 1080p), V9 measured on the delivered master:

    frame   V9 bright px   V10 bright px   V9 field mean luma   V10
    1719        86,679         48,944            13.41          11.27
    3308       170,691         57,401            16.72          11.40

V9's defect in one row: its shallower hush frame carried nearly
twice the foreground energy of its deepest. V10's two frames sit
at the same floor (the residual difference is scene content —
3308's era is denser; per-element dimming is identical by
construction). Stills: at f3308 and at the highlight's peak f3274
there is no @madeofmistak3 label, plate, ring or boosted arc —
the field is the dimmed web, the shells, and the head's marker
light (kept at its hush gain by design: in hush the head carries
the frame). Outside hush the system is untouched: f1186 shows the
@dakami label at full strength at its peak.

One implementation finding worth recording: Pillow 13's
`ImageDraw.text` IGNORES the fill alpha (verified in isolation —
alpha-2 text renders at full ink while shapes blend correctly),
so in V9 the label text never actually faded with its envelope;
it popped. An envelope can only clear text by not drawing it:
the label loop now skips env ≤ 0.05, and the boosted-arc width
bump uses the same threshold. In deep hush the suppressed env is
~0.012 — fully clear, no pop residue. (All other on-screen text
shares the Pillow behavior in V9 and V10 alike — captions, counter,
strip — and is unchanged.)

Scope note: the four handle-only callouts (e.g. @eshear, visible
at f1719) and the event captions are editorial overlays, not
highlights; like V9 they are not hush-suppressed.

## Change 2 — G9: anamorphic streak

In `film_grade`, after the radial halation (step 3b): pixels above
225 are masked (squared rolloff over 30 levels), collapsed 24×
horizontally (1920→80) and re-expanded — a purely lateral smear —
tinted warm white-gold (1.0, 0.86, 0.62) at gain 0.38, so R ≥ G ≥ B
and the palette gate cannot trip. The strip region (x ≥ 1520 at
1080p) is masked out — its bright cell text is UI, not a bright
node — and the pass is off for frames < 340 (title + legend) and
≥ 3530 (CTA), where the bright objects are type, not field.

Verification (production stills): the streak is plainly visible
as a horizontal flare on the brightest nodes — f2400's two bright
convergence nodes (unmissable), f1186's @dakami node, f1053's burst
convergences — while ordinary nodes keep the radial halation. The
strip's bright text shows no smear (region masked) and the CTA
still f3700 is clean (pass off). Palette safety is structural
(R ≥ G ≥ B in the added light) and the full-film palette gate
runs at QA.

## Change 3 — C13: arcs stay in frame

Measured, not tuned by eye. A one-time prep in render10.py
re-projects every live arc with the v9 (relief-free) camera at every
frame of its life, exactly as drawn (same bow/jitter/u_max growth,
exclusion rule), counting only comfortably in-field points
(zc ≥ 0.9 — a point nearer the camera is a flyby streak, a V9
artifact class of its own), and records the deepest overshoot above
the top edge per frame (capped 1200 px, 4K). The series is
gaussian-smoothed (σ 6 f), normalized at 260 px = full pressure,
cached in `viz10/arc_edge_cache.json` (version 4). Relief, all
scaled by that pressure and released during the pull-back:
`camera()` radius +18%, the vertical projection centre eased down
up to 240 px (4K) via a `CY_CUR` global `project()` reads, and the
arc bow itself flattened up to 75% toward its chord. Azimuth,
chapters and hop chronology are untouched (the pressure series is
computed with ARC_EDGE = None — provably the v9 camera).

Baseline (v9 camera): 880 frames carry an in-field arc overshoot;
p50 788, p90 1536, max 3069 px (4K); worst frames 1242–1249 and
2162–2167. With the relief (same audit, `viz10/edge_audit.py`):
628 frames (−29%), p50 486 (−38%), p90 1382, max 2445. Named
frames: f918 296→91 px, f3308 385→0, f2150 no arc overshoot in
either version. The residual extremes (frames ~1460 ChatGPT era,
~2616) are arcs whose endpoints fly close past the camera —
framing eases them (and locally re-rolls them: f1461 and f2617
measure worse under relief than baseline) but cannot contain them;
stated plainly, C13's fix is a large measured reduction, not an
elimination.

Scope note, also measured: the golden TRACE also crosses the top
edge in the dense era (2–5% of drawn trace points sit above the
frame at sampled late-era frames, bulk overshoot 1200–3600 px),
but it crosses every edge — left, right, bottom and top alike, in
V9's approved frames as much as anywhere; that is the web's
established immersion. An early V10 iteration drove the pressure
from arcs+trace combined; the trace saturates it (≥1200 px
overshoot in ~2,990 frames), which would have re-framed most of
the film — a different, wider movie, against the brief's
"everything else unchanged". The shipped pressure is arcs-only,
which is C13's subject ("long arcs … exit the frame top").

Verification: A/B geometry audit above + stills (f918, f2150,
f3308 in `viz10/qa_stills/`).

## Render / QA / deliverables

Renderer: viz10/render10.py SHA-256
08109bd3f016cde682a87b4073313d3007a1ccbaa5771608a580f7714eda3bd1
(local and node copies hash-identical). Render on aletheia-core,
~/emise-v10/: 8 chunks (0–476 … 3328–3802), SUBN=3,
OMP_NUM_THREADS=2, nice -n 10 — the V9 recipe unchanged
(run_full10.sh; chunk c4 also carries V10_DUMP for the
determinism spot-check on frame 1427). Finish: finish10.sh
(concat → loudnorm two-pass, WAV-stage TP −1.7 → master CRF 12
10-bit + viewing CRF 16 / 12M, C17 recipe). QA: qa10_node.sh —
the corrected qa10 gate (8-bit conversion before signalstats,
thresholds unchanged), palette, contact sheet, probes, loudness,
SSIM/PSNR 2100–2199.

Status: stills verified for all four changes (qa_stills/);
full render launched 2026-11-04 ~09:11 CST — results appended
below as they land.

Render log:
- Determinism spot-check PASSED during the render: frame 1427
  rendered solo (1-frame range) and as chunk c4's first frame are
  byte-identical (raw RGB SHA-256 2294b5c87333eac5…). Chunk logs
  print azimuth 4.9996 revolutions and the 66-string clean audit.
- All 8 chunks done 09:47–09:53 CST; concat frame count exactly
  3,802. Loudnorm mix measured −12.81 LUFS / TP −1.23 → applied
  per the V9 recipe.

QA (qa10_node.sh, corrected gate — 8-bit conversion before
signalstats, thresholds unchanged):

    GATE master   PASS — 3802 frames, mean YAVG 28.58,
                  flash-jumps 0, black frames 0
    GATE viewing  PASS — 3802 frames, mean YAVG 28.73,
                  flash-jumps 0, black frames 0
    palette       0 green-dominant pixels (634 sampled frames)
    duration      158.416667 s, both encodes; 24 fps
    tags          bt709 primaries/transfer/space, both encodes
    master        1920×1080 yuv420p10le, AAC 320k
    viewing       1920×1080 yuv420p, faststart, AAC 192k
    loudness      master −14.0 LUFS / TP −2.4 dBFS
                  viewing −14.0 LUFS / TP −2.5 dBFS
                  (identical to V9's delivered values)
    E14 compare   frames 2100–2199: SSIM All 0.8878,
                  PSNR avg 37.35 dB
    contact sheet viz10/qa_stills/v10-contact-sheet.png
                  (opening 156 frames — clean)

Deliverables (~/workspace/wavefront/):

    wavefront-viz-v10.mp4          2,618,934,048 B
      SHA-256 0a24cb61ed25552cc6e673f4c74a888dac32aa8c405cf24f94b66dc283d3c5d9
    wavefront-viz-v10-viewing.mp4    241,519,467 B
      SHA-256 f01e83ef39ad53afadd0e3a8024cb061cc1c3445d6197b51226840cefc85698e

Both transferred single-writer from aletheia-core and verified
bit-identical locally. The delivered V9 files were never touched.
