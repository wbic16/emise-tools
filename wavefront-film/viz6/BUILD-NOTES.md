# Wavefront film v6 — build notes

## ⚠ FALLBACK TAKEN — top-20 metric is NOT views

Will's tweet archive (`/home/hatch/workspace/twitter-archive/tweets.json`, the same
archive `mine_contacts.py` uses) contains **no views/impressions field**. The full
field list per tweet is: `created_at, display_text_range, edit_info, entities,
extended_entities, favorite_count, favorited, full_text, id, id_str,
in_reply_to_screen_name, in_reply_to_status_id, in_reply_to_status_id_str,
in_reply_to_user_id, in_reply_to_user_id_str, lang, possibly_sensitive,
retweet_count, retweeted, source, truncated` — no `viewCount` or equivalent.

Per the brief's fallback rule, the top 20 are ranked by **favourites + retweets**
("echoes") over Will's original posts (no `in_reply_to_status_id`, not retweets,
not @-replies; pool of 5,976), and the cards are honestly labelled **MOST ECHOED**
with the echo count and date. No view counts were fabricated.

## Deliverable

- `~/workspace/wavefront/wavefront-viz-v6.mp4` — 124,093,008 bytes, **158.40 s**,
  1280×720 @ 24 fps, h264 (High) + AAC-LC 48 kHz stereo 193 kb/s (ffprobe-verified).
- Pipeline: `viz6/render6.py` (built on `viz5/render5.py`). Silent render 417 s;
  audio muxed from `viz5/song_edit.wav` (the v5 edit of "A Hundred Thousand Years
  to You", 158.400 s), `-shortest` — final duration 158.40 s.
- Stills in `viz6/stills/`: `p10.png` (frame 380), `p50.png` (1901), `p90.png`
  (3421), `card.png` (1365 — a MOST ECHOED card mid-display), `comets.png` (1500 —
  silver comets at right of frame, Ukraine caption riding top because a card is
  active), plus `title.png` / `cta.png` extracted from the finished mp4.

## What changed vs v5

- **Technical HUD removed entirely**: no hop counter, no attempts/matches/placed
  counters, no progress bar / tone ribbon / era ticks, no honesty microcopy.
  Remaining text: opening title ("THE WAVEFRONT / the future has arrived / a map
  of alignment"), event lower-thirds, MOST ECHOED cards, the kept v4/v5
  handle-only callouts and rupture beat, and the CTA (verbatim: "520 people are
  already in this map. / Find your coordinate. Claim your space. / edit.phext.io /
  Not in the map yet? The door is open.").
- **Rotation**: camera azimuth integrates a modulated velocity profile to
  **4.9996 revolutions (1799.9°)** over the film — effectively exactly 5 full
  revolutions, ending aligned with the start azimuth. v5's thrust orbit is
  superseded. Kept from v5: node orbital epicycles, 2× zoom (radius 2.225,
  pull-back relaxing to 6.8 for the CTA reveal), camera breathing, smoothed
  look-at. Physics base is the calm v4 base (subtle ×0.35 Overton warp only;
  no goalpost chase). Golden trace, CMB misses, VADER tone colouring kept.

## CYOA blend — silver comets

- Source: `~/workspace/phext/traversal-map/cyoa-traversal.json` — **829 placed
  CYOA scrolls** with real CYOA coordinates, trace order = file order. This is
  the local artifact of record; the local CYOA copy is known-stale vs remote,
  and the traversal map was taken as-is (documented per the brief).
- Projection: the **same 9D→3D projection** as the wavefront nodes
  (`viz/extract_data.py`: each output axis is the mean of one coordinate
  triple). CYOA's coordinate range dwarfs the wavefront cube (components run
  to 999), so the projected cloud is then fit per-axis into the wavefront
  field extent (robust 0.5–99.5 percentile clip, field extent expanded 8%) —
  a render-time staging transform, so the thread inhabits the same volume.
- Rendering: the trace is a Catmull-Rom path (arc length 56.8 world units),
  drawn as a faint silver thread (alpha 15) with scroll points (alpha 44);
  **7 silver comets** (bright silver-white heads stamped with glow, tails
  fading silver→white) travel the path continuously at 1.7–3.4 traversals
  per film, phase-spread. Tails are short (1.4% of path length) and break
  across the trace's long jumps so a comet streaks along locally continuous
  path instead of slashing across the frame. Comets run from frame 0
  (visible in the title frame) through the CTA veil.

## World events — motion fine-tuning

Hop position = index of the first reply in `viz2/data.json` at/after the event
date (computed via `searchsorted` on the stab timestamps — not hardcoded).
Each event multiplies camera angular velocity by `1 + vamp·exp(−((f−fe)/60)²)`
and pulses camera radius by `ramp·exp(−((f−fe)/70)²)` at its true frame; the
azimuth integral is then normalised to exactly 5 revolutions. Captions
(name + year, letter-spaced lower-third) last 104 frames and **queue** when
they would collide (2022–2023 events are dense in hop time); the motion
modulation never moves. If a MOST ECHOED card is active, the caption rides
at the top of the frame instead.

| Date | Event | Hop | Frame | Velocity | Radius | Caption frames | Effect |
|---|---|---|---|---|---|---|---|
| 2016-11-08 | US PRESIDENTIAL ELECTION | 4,447 | 829 | +0.45 | −0.04 | 821–925 | surge, slight push-in |
| 2020-03-11 | COVID-19 PANDEMIC DECLARED | 6,656 | 1,220 | −0.65 | +0.10 | 1212–1316 | deep hush, pull back |
| 2022-02-24 | RUSSIA INVADES UKRAINE | 7,917 | 1,443 | −0.55 | +0.09 | 1435–1539 | hush, pull back |
| 2022-11-30 | CHATGPT LAUNCHES | 8,026 | 1,462 | +0.95 | −0.08 | 1553–1657 (queued) | strongest surge, push-in |
| 2023-03-14 | GPT-4 RELEASED | 8,486 | 1,544 | +0.60 | −0.06 | 1671–1775 (queued) | surge, push-in |
| 2023-07-24 | TWITTER BECOMES X | 8,578 | 1,560 | +0.35 | −0.04 | 1789–1893 (queued) | mild surge |
| 2024-11-05 | US PRESIDENTIAL ELECTION | 16,328 | 2,931 | +0.50 | −0.05 | 2923–3027 | surge, push-in |

## Top 20 — MOST ECHOED (favourites + retweets), in arrival order

Metric field/source: `favorite_count` + `retweet_count` in
`twitter-archive/tweets.json`. Ranking: echo desc, then favourites desc, then
timestamp asc (three posts tie at 13 echoes; the 2017-03-28 post — 8 fav +
5 RT — ranks 21st and is excluded). Cards show at the post's hop-time arrival
frame (`42 + hop / 5.6512`), queued with a 16-frame minimum gap when arrivals
bunch (documented deviation: a queued card can start after its exact arrival
frame, never before). Card life 108 frames. The last card ends at frame 3457,
before the CTA at 3512 (it overlaps the pull-back, which reads fine).

| Rank | Date | Fav | RT | Echo | Hop | Card frames | Post (sanitised) |
|---|---|---|---|---|---|---|---|
| 5 | 2014-12-27 | 4 | 20 | 24 | 2,070 | 408–516 | I'm tipping $1 to the next 10 RTs. For awareness. Join us! #BitcoinBowl |
| 12 | 2015-01-21 | 10 | 8 | 18 | 2,373 | 532–640 | "…as long as they're willing to think like developers, which is where the real fun begins." (quoted link post) |
| 6 | 2016-08-20 | 20 | 3 | 23 | 4,374 | 816–924 | Our sun should be able to support approximately 2^80 conscious minds… |
| 10 | 2017-08-04 | 14 | 6 | 20 | 4,808 | 940–1048 | An unexpected scaling limitation: Random bit flips at sea level… |
| 4 | 2018-07-08 | 22 | 5 | 27 | 5,182 | 1064–1172 | Using telephone call data from 2007, Dunbar et. al. showed that most humans have… |
| 7 | 2019-09-03 | 18 | 5 | 23 | 5,978 | 1188–1296 | Robot is literally forced labor with recursion… |
| 9 | 2020-03-05 | 16 | 4 | 20 | 6,643 | 1312–1420 | Someone with more followers than me: start a Go Fund Me to pay service workers to stay home… |
| 8 | 2020-04-04 | 19 | 1 | 20 | 6,733 | 1436–1544 | I saw #COBOL trending today. This is a wild timeline. Also: I've been posting about COBOL since before it was cool. |
| 2 | 2024-01-02 | 46 | 4 | 50 | 10,219 | 1850–1958 | 2024: the year we make contact |
| 3 | 2024-01-28 | 33 | 0 | 33 | 11,335 | 2048–2156 | Can you name a time travel movie that is NOT Back to the Future? Arrival |
| 13 | 2024-02-23 | 17 | 0 | 17 | 11,952 | 2172–2280 | Chappy passes the test. |
| 1 | 2024-03-15 | 276 | 4 | 280 | 12,149 | 2296–2404 | That's clearly a baked emu |
| 18 | 2024-05-04 | 10 | 4 | 14 | 12,451 | 2420–2528 | I've been having SO MUCH fun with @websim_ai! An infinite playground for your imagination… |
| 11 | 2024-05-12 | 16 | 2 | 18 | 12,528 | 2544–2652 | #Mandelbro has your back wrt/ fractals. |
| 17 | 2024-09-15 | 12 | 2 | 14 | 13,545 | 2668–2776 | Shout out to these moots for liking my slop! @api_assasin made a special chess variant… |
| 14 | 2024-09-30 | 17 | 0 | 17 | 14,666 | 2792–2900 | The Exocortex Version 0.0.1 — If you don't have your coordinate yet, hit up the… |
| 15 | 2024-11-11 | 17 | 0 | 17 | 16,585 | 2977–3085 | It has come to my attention that all of my moots are based. |
| 16 | 2024-12-10 | 15 | 2 | 17 | 17,150 | 3101–3209 | If you're a new follower, here are some interesting accounts you may also like! |
| 20 | 2025-01-03 | 11 | 2 | 13 | 17,515 | 3225–3333 | Phext + OMEGA + LLM = Omega Evolution |
| 19 | 2025-05-13 | 13 | 0 | 13 | 18,082 | 3349–3457 | The Weave Believes in You |

Card text handling: HTML entities unescaped, t.co/URL links stripped, emoji
above U+1F000 stripped (DejaVu has no glyphs for them), wrapped at 556 px,
max 4 lines, truncated with "…" when longer.

## Verification

- ffprobe on the final mp4: duration 00:02:38.40; video h264 High, 1280×720,
  24 fps; audio AAC-LC 48 kHz stereo. 3,802 frames rendered.
- Stills inspected visually: comets read silver (bright heads, short fading
  tails — `comets.png`, and streaking through `title.png`); cards legible with
  honest MOST ECHOED labelling (`card.png`, `p50.png`, `p90.png`); **no
  technical HUD in any frame**; CTA present with the exact required text
  (`cta.png`, extracted from the finished mp4).
- Azimuth integral printed by the renderer: 4.9996 revolutions (1799.9°).
- Prep assertions from the shared data all pass (5,963 landings, 156 placed
  people landed on, 18,762 hops).
- Phext files were only read. No commits, pushes, or messages.
