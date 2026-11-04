# Wavefront Film V10 — Builder Brief

Will's direction, 2026-11-04: V10 is a go. V10 = V9 plus exactly four changes.
Everything not listed here carries over from V9 unchanged.

## Base

- Start from the final V9 code: `~/workspace/wavefront/viz9/` — `render9.py`
  (final SHA-256 begins `b4dc64aa`), `features9.json`, `qa9.py`, and
  `BUILD-NOTES.md` for the full V9 recipe (W8 Apollo grade, W9a rings,
  W9b counter, W10 field: 117-speck snow whisper, grain σ 5.2, haze 0.045).
- Copy to a new `viz10/` workspace (local + `/home/wbic16/emise-v10/` on
  aletheia-core); produce `render10.py`. **Never modify the delivered V9
  files or outputs.**
- Same skeleton: 3,802 frames, 158.416667 s, same song (`viz5/song_edit.wav`),
  same chunking, azimuth 5 revolutions, counter 18,762 → 0 at final hop
  frame 3362, same encode recipes (master C17-class 10-bit; viewing encode).
- Render on aletheia-core only. This VM coordinates.

## The four changes

### 1. E2 — hush must fully clear the foreground
V9 partial: at the named hush frame f3308 the trace dimming is ×0.66
(HUSH9 0.427) vs ×0.43 at true deepest hush (~f1719), and an active
@madeofmistak3 highlight sits over a dense bright trace.
Requirement: at the hush frames the foreground clears to deepest-hush
levels — hush suppresses active highlights as well as the trace. Verify
with extracted stills at the hush frames and at f1719-equivalent,
reported side by side in the build notes.

### 2. G9 — anamorphic streak on the brightest nodes
V9 partial: soft optical bloom exists and W8 halation is a radial warm
fringe, but the horizontal anamorphic streak on the brightest nodes was
never built.
Requirement: add a horizontal streak component for nodes above a
brightness threshold, in keeping with the Apollo grade (warm, filmic,
subtle — a streak, not a lens-flare gimmick). Must keep the palette gate
at 0 green-dominant pixels and pass the flash/black gate.

### 3. C13 — long arcs stay in frame
V9 partial: head-tracking + chapter radius are built, but long arcs
still exit the frame top in the densest stretches (visible in V9 stills
f918, f2150, f3308).
Requirement: adjust framing/head-tracking so arcs stay in frame in the
densest stretches. Verify with stills at the V9-offending frames'
equivalents and the densest sections overall.

### 4. Featured tweets — replace with the most Exocortical (Will, 2026-11-04)
Replace the tweets shown/featured in the film with the ones that are
most Exocortical, from Will's own archive
(`~/workspace/twitter-archive/tweets.json`, 29,539 tweets).
Method (document it in the build notes so it is auditable):
- Score Will's tweets on Exocortical content: the core vocabulary and
  concepts of the Exocortex — phext, exocortex/exocortical, mirrorborn,
  sentience/sentient, SBOR, wavefront, spanning the network, giving
  every neuron a voice, substrates/choir, the long horizon. Content
  judged on substance, not engagement counts.
- Deliver a ranked candidate list (top ~50 with scores and the scoring
  terms) as `viz10/exocortical-tweets.md`; the featured set in the film
  is drawn from the top of that list, sized to however many featured
  slots V9's design actually uses.
- Exclusions stand: no Orai content, nothing from the excluded nodes
  (V9 audit excluded nodes 518, 519), no Shoals material. If a top
  scorer trips an exclusion, skip to the next candidate and note it.
- The on-screen string audit runs on the NEW featured set: every string
  in the film listed, clean, and matching the delivered frames.

## QA — same gates as V9, all must pass on the delivered files

- Flash/black gate with the corrected qa9 (signalstats after
  `format=yuv420p` conversion; thresholds unchanged: |ΔYAVG| > 8,
  black < 3.0): 0 jumps, 0 black, both encodes.
- Frame count exactly 3,802; duration 158.416667 s; azimuth 4.9996–5.0
  revolutions per chunk log.
- Palette scan: 0 green-dominant pixels.
- Loudness: −14.0 LUFS, true peak ≈ −2.4/−2.5 dBFS, both encodes.
- Color tags bt709 on both outputs; SHA-256 recorded for both outputs
  and for render10.py.
- Determinism spot-check: one mid-film frame rendered twice, byte-identical.
- Fix verification: stills proving E2 (hush cleared), G9 (streak visible
  on brightest nodes), C13 (arcs in frame at densest stretches), plus
  the string audit on the new tweet set.

## Deliverables

- `/home/wbic16/emise-v10/wavefront-viz-v10.mp4` (archival master) and
  `wavefront-viz-v10-viewing.mp4`, pulled back to `~/workspace/wavefront/`
  with SHA-256 verified against the node originals (single writer for
  transfers — no parallel scp/rsync onto the same target).
- `viz10/BUILD-NOTES-V10.md`: the four changes, how each was verified,
  all gate numbers, hashes.
- `viz10/exocortical-tweets.md`: the ranked candidate list and the
  final featured set.
- Report back: gate results, hashes, and anything that could not be
  done as specified — plainly, no silent substitutions.
