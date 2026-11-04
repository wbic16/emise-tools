# Wavefront film v7 — "The Exocortex, Shaken yet Stirred" — BUILD NOTES

Pipeline: `viz7/render7.py` (derived from `viz6/render6.py`). Rendered
2026-11-03/04. No phext file was modified; phext data was only read.

## Deliverables

| File | Bytes | SHA-256 |
|---|---|---|
| `wavefront-viz-v7.mp4` (master) | 325,356,314 | `30b56104951a576c2d733e26f3216051475e3ca45b1b10fd941e61c77e982eb2` |
| `wavefront-viz-v7-download.mp4` | 47,337,310 | `98f17437e810097a7bd66f223214d1259f348aecd3e15e4d418a2500d1c1d199` |

Master (ffprobe-verified): 1920×1080, 24 fps, duration **158.400 s**,
h264 video + AAC audio (192 kb/s, from `viz5/song_edit.wav`, `-shortest`).
Download encode: h264 + AAC 160 kb/s, faststart (moov verified at front),
1920×1080, 158.400 s.

## Sources (unchanged from v6)

- Replies / hop stream / placed nodes: `viz2/data.json` — 18,762 replies in
  hop order; 5,963 matches; 520 placed people; 18,762 hops total.
- Tone: `viz4/tone.json`. Audio: `viz5/song_edit.wav` (158.40 s edit).
- CYOA thread: 829 scrolls from `~/workspace/phext/traversal-map/cyoa-traversal.json`,
  same triple-mean 9D→3D projection and per-axis robust fit as v6.
- Top-20 posts: `twitter-archive/tweets.json` (see fallback note below).

## Carried over from v6, unchanged

Hop time (5.6512 hops/frame); one golden trace, Will never named in text;
misses as CMB grain; CYOA silver comets; exactly 5 camera revolutions,
event-modulated, ending aligned; the same 7 world events at the same
computed hop positions with the same surge/hush tuning and name·year
captions; calm v4-base physics (no Overton chase); node epicycles; 2× zoom;
CTA pull-back; no technical HUD. Closing CTA verbatim from v6.

**Revolutions computed:** azimuth sweep normalised to exactly 5 revolutions
by construction; realised **4.9996 revolutions** (1799.9°) — identical to v6,
as required.

## 4K → 1080p supersampling (confirmed)

Every frame is rendered on a **3840×2160** canvas (all layout, fonts and
stroke widths authored at 3× the v6 720p design scale) and down-sampled to
1920×1080 with a **Lanczos** resample inside the render loop, before encode.
The delivered master is therefore a true supersampled 1080p, not an upscale.

**Chunked render:** the 3,802 frames were rendered in three parallel chunk
processes (`--range 0 1268`, `--range 1268 2534`, `--range 2534 3802`), each
encoding its chunk at 1080p (libx264, CRF 10 — near-lossless so the CMB grain
survives concatenation without a second lossy generation). Chunks were joined
with the ffmpeg concat demuxer (`-c copy`, no re-encode) and the song muxed
in. Frame counts verified per chunk: 1268 + 1266 + 1268 = 3,802. Wall clock
≈ 52–55 min on this 4-core VM. Chunk files were deleted after assembly; the
pipeline reproduces them.

## Film strip (replaces v6's in-scene post cards)

- **Side/width:** right side, x from 3040 to 3840 on the 4K canvas =
  **800 px = 20.8% of frame width** (400 px at 1080p). The scene's projection
  centre sits at the centre of the remaining field (x = 1520 @4K) while the
  strip is up, and eases back to full-frame centre during the CTA pull-back,
  so the golden trace's main field is never occluded.
- **Styling:** dark-glass panel (deep blue-black, α≈168), a thin luminous
  cyan left edge, sprocket perforations down both edges (30×20 px rounded
  holes every 72 px @4K), masthead "MOST ECHOED / ranked by favourites +
  retweets".
- **Cells:** each top-20 post is a framed cell 462 px high on a 496 px pitch
  (@4K): date + "no. N of 20" header, post text wrapped at 600 px, max 4
  lines, trimmed with "…", and "N echoes" footer. Newest arrival glows at
  the cell edge for 34 frames; entries fade in over 12 frames.
- **Flow:** the strip scrolls continuously — scroll offset is the eased sum
  of per-arrival targets so each new post's cell foot settles 48 px above
  the frame bottom. It is a living feed, not pop-up cards.
- **Exit:** the whole strip fades out across the first 75 frames of the CTA
  pull-back, before the CTA text appears. Verified clean in the CTA still.
- **Masthead fix:** in the first stills pass, an exiting cell slid *over*
  the masthead text. The masthead is now drawn after the cells, on a
  near-opaque band, so exiting cells slide *under* it. Re-verified in stills
  extracted from the finished master.

## Bezier curves — thicker, more fluid

All widths are 4K-canvas pixels (halve for 1080p equivalents):

| Element | v6 (1080p-equiv) | v7 @4K | v7 (1080p-equiv) |
|---|---|---|---|
| Match ("stab") arcs | 3 px | **9 px** | **4.5 px (+50%)** |
| Golden trace glow pass | — | 13 px | 6.5 px |
| Golden trace core | — | 5 px | 2.5 px |

- The golden trace spline was rewritten from v6's Catmull-Rom form into the
  equivalent Hermite form with an explicit **tension of 0.18** (lower =
  more fluid) and subdivision raised **2 → 4**, removing kinks at hop joins.
- Match-arc Bézier control-point offset raised **0.16·L + 0.03 → 0.22·L +
  0.045** with segments **10 → 18**, so arcs bow wider and sweep more
  liquidly. A soft glow pass under the golden core keeps the thicker strokes
  elegant rather than blobby at 1080p.

## Excluded account — never shown (verification)

- The account's two placed nodes (indices 518, 519 in `viz2/data.json`, the
  only nodes carrying the dropped region coding) are collected into an
  `EXCLUDE` set at load (asserted == 2) and **skipped in node rendering**;
  match arcs skip landings on them; both of its on-screen callouts were
  removed (callouts 7 → 5); the rupture sequence that referenced it was
  deleted outright.
- Its replies remain in the aggregate hop stream / CMB statistics — they are
  attempts in the stream, not a presence: no spark, node, or label lands on
  or identifies its coordinate.
- **Grep-style verification:** the renderer audits every string that can
  reach a frame — all callouts, event captions, all 20 strip-cell texts, and
  every static string (title, CTA, masthead) — 42 strings — asserting none
  contains the account's name or the dropped region's name (case-insensitive).
  The audit **passed in every render process** (stills + all three chunks).
  The only occurrences of those strings left in `render7.py` are the
  exclusion matcher and the audit itself; neither is ever drawn.
- Stills extracted from the finished master were also inspected visually:
  no such text appears.

## The dropped region

No rendering, label, region highlight, or reference anywhere in the film.
The only two nodes that ever carried that coding were the excluded
account's; with them removed, the region branch was deleted from node
colouring entirely, and the audit above covers the name as well.

## Title

Opening card: **"THE EXOCORTEX"** / *"Shaken yet Stirred"* (gold oblique) /
"a map of alignment", frames 0–96. **Second beat kept:** v6's line
"the future has arrived" appears briefly at frames 108–196 — it fit cleanly
between the title card and the first strip arrival (frame 408), so it was
kept; after frame 196 the film is text-free except captions and the strip.

## Top 20 — MOST ECHOED (same selection and ranking as v6)

⚠ Inherited fallback (from v6, flagged to Will then): the archive has **no
views/impressions field**, so the top 20 are ranked by favourites + retweets
("echoes") over 5,976 original posts and honestly labelled MOST ECHOED.
Selection, ranking, and texts are identical to v6 — not re-ranked. In v7
each post enters the film strip at its hop-time arrival frame
(`42 + hop / 5.6512`); there is no queue (see deviations).

| Rank | Date | Fav | RT | Echo | Hop | Strip arrival frame |
|---|---|---|---|---|---|---|
| 5 | 2014-12-27 | 4 | 20 | 24 | 2,070 | 408 |
| 12 | 2015-01-21 | 10 | 8 | 18 | 2,373 | 462 |
| 6 | 2016-08-20 | 20 | 3 | 23 | 4,374 | 816 |
| 10 | 2017-08-04 | 14 | 6 | 20 | 4,808 | 893 |
| 4 | 2018-07-08 | 22 | 5 | 27 | 5,182 | 959 |
| 7 | 2019-09-03 | 18 | 5 | 23 | 5,978 | 1100 |
| 9 | 2020-03-05 | 16 | 4 | 20 | 6,643 | 1218 |
| 8 | 2020-04-04 | 19 | 1 | 20 | 6,733 | 1233 |
| 2 | 2024-01-02 | 46 | 4 | 50 | 10,219 | 1850 |
| 3 | 2024-01-28 | 33 | 0 | 33 | 11,335 | 2048 |
| 13 | 2024-02-23 | 17 | 0 | 17 | 11,952 | 2157 |
| 1 | 2024-03-15 | 276 | 4 | 280 | 12,149 | 2192 |
| 18 | 2024-05-04 | 10 | 4 | 14 | 12,451 | 2245 |
| 11 | 2024-05-12 | 16 | 2 | 18 | 12,528 | 2259 |
| 17 | 2024-09-15 | 12 | 2 | 14 | 13,545 | 2439 |
| 14 | 2024-09-30 | 17 | 0 | 17 | 14,666 | 2637 |
| 15 | 2024-11-11 | 17 | 0 | 17 | 16,585 | 2977 |
| 16 | 2024-12-10 | 15 | 2 | 17 | 17,150 | 3077 |
| 20 | 2025-01-03 | 11 | 2 | 13 | 17,515 | 3141 |
| 19 | 2025-05-13 | 13 | 0 | 13 | 18,082 | 3242 |

(Full post texts: `viz6/BUILD-NOTES.md` top-20 table — identical texts.)

## Future-tech grade

Deep-space black background (2,3,7); CMB grain gain raised slightly; cyan
(170,220,235) caption rules; silver-cyan strip edges and masthead; stars and
node cores splatted 2×2 / 3×3 so they survive the 4K→1080p downsample as
crisp points. The golden trace stays warm and dominant; comets stay silver.

## Deviations

1. **Views → echoes** (inherited from v6): no views field exists in the
   archive; ranking is favourites + retweets, labelled MOST ECHOED.
2. **No strip queue:** v6 queued its cards with a 16-frame minimum gap when
   arrivals bunched. A continuously scrolling strip absorbs bunched arrivals
   naturally, so v7 posts enter at their exact arrival frames; two arrivals
   15 frames apart (ranks 9 and 8) simply scroll through faster.
3. **Event captions no longer dodge cards** (there are no cards): captions
   always ride the bottom of the field, centred on the field while the
   strip is up.
4. **Download encode maxrate 3200k → 2600k:** the v6 recipe at 1080p
   produced 62.6 MB, over the ~55 MB link cap; at 2600k the download is
   47,337,310 B with no visible quality loss on inspection. CRF 23, AAC
   160k, faststart unchanged.
5. **Master size (325 MB)** is a consequence of near-lossless chunk encodes
   (CRF 10) chosen to protect the CMB grain through concatenation; the
   download encode is the distributable copy.
6. **Masthead band** added after the first stills check (see Film strip).
7. Second title beat ("the future has arrived") **kept** — see Title.

## Verification performed

- ffprobe on master and download: 1920×1080, 24 fps, 158.400 s, h264 + AAC.
- Download file decode spot-check passed; moov atom at front (faststart).
- Runtime text audit (42 on-screen strings) passed in every process.
- Stills extracted from the **finished master** into `viz7/stills/`
  (title, p10, strip mid-flow @ frame 1500, p50, bezier @ frame 2300, p90,
  cta) and inspected personally: strip legible and flowing, masthead clean,
  Beziers thick and fluid, no HUD, no excluded-account text, no dropped-
  region reference, CTA verbatim and clean, title correct
  ("THE EXOCORTEX" / "Shaken yet Stirred").
