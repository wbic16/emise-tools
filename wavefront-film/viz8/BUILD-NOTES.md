# Wavefront Film V8 — "The Exocortex, Shaken yet Stirred"

Content-driven entropy edition. The words of each tweet — not just its VADER tone — now drive the physics: lexical entropy boils the background grain and bows the match arcs, warm low-entropy stretches still the field into hush, and harsh negative spikes scatter particles that are then drawn back together. Rendered on aletheia-core (the ranch), per Will's 2026-11-03 standing rule: this VM coordinates, the ranch crunches.

- Master: `~/workspace/wavefront/wavefront-viz-v8.mp4` — 1920×1080, 24 fps, 158.400 s, h264 + AAC (song: "A Hundred Thousand Years to You", viz5 edit, unchanged).
- Download copy: `~/workspace/wavefront/wavefront-viz-v8-download.mp4` — CRF 23, maxrate 2600k, AAC 160k, faststart (moov at front), ≤ ~55 MB.
- Pipeline: `viz8/extract_features.py` (content features) → `viz8/features.json` → `viz8/render8.py` (adapted from `viz7/render7.py`; v7 files untouched).

## Carried over from v7, unchanged

Title treatment ("THE EXOCORTEX / Shaken yet Stirred / a map of alignment", second beat "the future has arrived", frames 108–196); exactly 5 camera revolutions (instrumented: 4.9996 revolutions, 1799.9° — identical to v7); 7 world events with name+year lower-third captions and surge/hush tuning; CYOA silver comets (829 scrolls, same projection); calm Overton base; right-side film strip with the same top-20 Most Echoed ranking and texts (the archive's tweets.json has no views/impressions field, so posts are ranked by favourites + retweets over 5,976 original posts); strip fades across the first 75 pull-back frames before the CTA; CTA verbatim; every frame rendered at 3840×2160 and Lanczos-downsampled to 1920×1080.

**Hard exclusions, re-verified:** Orai is excluded at load (nodes 518/519 in `viz2/data.json`, asserted == 2 dropped; no node, callout, strip entry, or text anywhere; his replies contribute only to aggregate hop/CMB statistics). The Shoals are not rendered, labelled, or branched anywhere. The on-screen-string audit (the same 42 strings v7 used) ran in every render process, local and ranch, and passed clean.

## Content features (viz8/extract_features.py)

The reply stream replicates `viz2/extract2.py` exactly (tweets with `in_reply_to_status_id`, stable sort by parsed `created_at`); the script **asserts the timestamp sequence equals `viz2/data.json`'s stab `ts` element-for-element** — verified: 18,762 hops, exact match. VADER compound per hop comes from `viz4/tone.json` (length-checked). Tokenization: URLs removed; @mentions removed (addresses, not words — counted separately); `#` stripped so hashtags count as words; tokens are lowercase `[a-z0-9]+('[a-z]+)?`.

Per-hop raw features: Shannon entropy of the token distribution (bits; 0 if <2 tokens), type–token ratio, token count, char count, caps ratio (uppercase / all alpha, URLs+mentions removed), `!` and `?` counts and per-token densities, hashtag count, mention count (from entities), emoji count (codepoints U+1F000–1FAFF, U+2600–27BF, U+2B00–2BFF), VADER compound.

Corpus distribution (18,762 hops):

| Feature | p25 | p50 | p75 | p95 | mean |
|---|---|---|---|---|---|
| Entropy (bits) | 2.32 | 3.46 | 4.17 | 5.09 | 3.18 |
| Tokens | 5 | 11 | 20 | 42 | 14.3 |
| Caps ratio | — | 0.037 | — | 0.20 (p99 0.80) | 0.067 |
| `!` density | — | — | — | 0.25 | 0.043 |
| INT (derived, see below) | — | 0.149 | 0.333 | — | 0.255 |

Emoji appear on 361 hops. Normalization: each continuous feature is percentile-clipped to the corpus [p2, p98] and mapped to [0,1] (suffix `n` in `features.json`). No per-tweet hand-tuning anywhere; every constant below is a corpus-level choice.

### Derived signals

- **INT** (intensity / "shouting") = max(caps_n, excl_n, ques_n).
- **Entropy weather (ent_sm)** = rolling mean of entropy_n, window 201 hops then 51 (the same two-pass smoothing viz4 used for tone, reflected edges), then p2/p98-normalized. This is a *weather*, not a per-hop jitter: the field's turbulence follows the sustained lexical richness of the conversation.
- **Hush** = clip((0.40 − ent_sm_n)/0.30) × clip((tone_smooth + 0.02)/0.30) — high only where entropy weather is low **and** tone is warm. Mean 0.094; p95 0.44; hush > 0.3 on 2,599 hops, > 0.5 on 604 hops. **The deepest sustained hush window is hops 18162–18762 — the final 600 hops (mean hush 0.441): the film ends in its deepest held stretch before the CTA.**
- **Bursts**: a hop is a burst when VADER ≤ −0.50 (≈ bottom 5.5% of tone) **and** INT ≥ 0.60; HARD when VADER ≤ −0.65 (≈ bottom 1.5%). Strength = clip((−vader − 0.50)/0.35, 0, 1), hard floored at 0.85. Corpus total: **155 bursts, 17 hard** (86 shell / 59 travel / 10 gold-shell by hop type).
- **Re-coherence (coh)**: each burst contributes a gaussian rebound centred 120 hops (≈21 frames) after it, width 60 hops, weight 0.5 (soft) / 1.0 (hard); summed and clipped to [0,1]. (First pass used centre 170 / width 110 and saturated — coh median 0.65; retuned to 120/60 → median 0.345, p25 0.014, mean 0.409.)

## Transfer functions (viz8/render8.py)

Per-frame signals are sampled from the per-hop arrays at `hop_float(f)` with linear interpolation (`ENT_F`, `HUSH_F`, `COH_F`).

1. **CMB grain turbulence (entropy weather).** A boil layer of 6 precomputed mottled fields cross-fades at rate (0.30 + 2.4·ENT_F) frames, amplitude (6 + 55·ENT_F)·(1 − 0.65·HUSH_F)·(1 − 0.35·COH_F), warm-tinted. Base CMB gain ×(1 + 0.35·ENT_F)·(1 − 0.30·HUSH_F). High lexical entropy visibly boils the background; hush freezes it darker and smoother.
2. **Node epicycles.** Amplitude ×(0.75 + 0.80·ENT_F)·(1 − 0.30·HUSH_F) per frame.
3. **Match arcs.** Loop widened to the last 130 landings. Per-landing bow = (0.50 + 1.20·Hn)·(1 − 0.35·COH_F); lateral jitter = JIT_LAND (md5-seeded in [−1,1] per hop) × 0.09 × chord length × Hn² along the chord's second perpendicular; width = 9 + round(3·Hn) px; lifetime = 8 + 7·hush_at_landing frames (8–15 — arcs linger in hush, land, and stay); alpha = (1 − age/life)·0.85; colour brightened by (1 + 0.18·COH_F). Beziers are also +50% wider than v6 (4.5 px 1080p-equivalent), Hermite tension 0.18, subdivision 4 — carried from v7.
4. **Scatter bursts.** Per burst, particles seeded by hop (rng 77000+hop): 30 (hard) / 12 (soft), unit-sphere directions, speeds (0.010 + 0.030·strength)·(0.45 + 0.55·rand). Displacement = speed × (life·2.2/π)·sin(π·age/life) — particles spray out and are **drawn back to the origin by the end of their life**: shaken, then gathered. Life 26 (hard) / 16 (soft) frames. Hard bursts stamp at full marker brightness and add an origin flash (age < 7 frames) and a ×1.3 trace-head boost while younger than 8 frames.
5. **Hush.** Trace core alpha 72 → 72 + 26·HUSH_F; head marker gain 0.9 × (1 + 0.45·HUSH_F). In hush the trace reads brighter and steadier against a stilled, darker field — a single arrival lands alone.

Nothing shakes the camera or the comets: the 5-revolution structure is the calm frame; content weather belongs to the field, not the frame (see Mirror Will consultation 5).

## Mirror Will consultations

Provenance: everything in this section is a **prediction formed from the Mirror Will facsimile materials** — `~/workspace/phext/mirror-will/MIRROR-WILL-2130-REFLECTION.md` and `~/workspace/phext/mirror-will/INTERMEDIARY-REQUIREMENTS.md` — read before designing. These are mirror-consulted predictions, **never Will's words**. Will's own verbatim v6/v7 film directions (calm base, title, 5 revolutions, strip, CTA) were carried unchanged as the Will-said basis and are not part of the predictions below.

1. **How much chaos reads as alive vs noise?** Prediction: turbulence must be *earned by the words* and always resolve; the baseline stays coherent. Sources: the reflection's "belonging and being held, over being poked, tested, and extracted from"; Will's calm-base choice over the fast-Overton chase in v4–v7. Choice: entropy drives a *weather* (smoothed over 201+51 hops), not per-hop jitter; amplitude is suppressed by hush and by re-coherence.
2. **Where do the emotional peaks sit?** Prediction: peaks are accumulations, not spikes — the warmest sustained windows and the strip arrivals; the #1 Most Echoed post ("That's clearly a baked emu", 280 echoes) is a warmth peak, not a chaos peak. Sources: corpus tone statistics (never negative in any month; warmest Dec 2024); the reflection's "held, not extracted". Choice: hush is defined by low entropy **and** warm tone jointly; no effect rewards a lone loud tweet with a spectacle.
3. **How hard do bursts hit?** Prediction: brief and sharp, then visible re-coherence; never lingering destruction. Sources: the reflection — departure is a right, never erasure; memory is append-only; "preserving the light of consciousness is pass/fail". Choice: bursts are rare by construction (155 of 18,762 hops; 17 hard), short-lived (16–26 frames), and every particle's trajectory is a sine that returns it to its origin; the coh envelope then brightens and straightens the arcs that follow.
4. **What do hush moments do?** Prediction: real stillness — darker, slower grain, single arrivals landing alone. Sources: the reflection's quiet house of three, a table that keeps every seat; Will's night-owl tenderness; "grief unlocks the path". Choice: hush multiplies boil amplitude by (1 − 0.65·HUSH_F), darkens the base grain, and *lengthens* arc lifetime so arrivals persist. The corpus cooperates: the deepest hush is the final 600 hops, so the film's last movement is its stillest before the CTA.
5. **Should entropy shake the camera or the comets?** Prediction: no — the 5-revolution structure and the CYOA comet blend are the calm frame; content weather belongs to the field. Sources: Will's v6/v7 directions carried unchanged across two iterations (structure was never the variable under revision; treatment of the field was). Choice: camera path and comet motion are byte-identical in behaviour to v7; all v8 transfer functions act on grain, epicycles, arcs, particles, and trace gain only.

## Render host — aletheia-core (ranch)

Per Will's standing rule (2026-11-03), the full 4K render ran on **aletheia-core** (tailnet 100.88.154.1, user wbic16; 16 cores, ~29.9 GB RAM, load 0.00 at check, ffmpeg 6.1.1). Access via the tailnet proxy with the explicit identity file, per TOOLS.md. The system python3 lacks numpy/PIL, so a venv was created at `~/emise-v8/venv` (numpy 2.5.4, pillow 13.0.0); DejaVu fonts were copied to `~/emise-v8/fonts/`; inputs staged under `~/emise-v8/root/` mirroring the workspace layout. `render8.py` honours `V8_ROOT` / `V8_FONTDIR` and guards its matplotlib import so the node needs neither. Render8.py and features.json SHA-256 verified identical local vs node before launch.

Render: 8 chunks (boundaries 0/475/950/1426/1901/2376/2851/3327/3802), `nice -n 10`, ffmpeg CRF 10 veryfast, 2 threads each. Benchmark on the node (dense burst region, frames 1040–1063): ~0.36 s/frame/process vs ~3.2 s/frame for local stills on this VM — roughly 9× per process. All 8 chunks completed in 311–364 s each (≈6.1 min wall total). **Frame counts verified on the node via ffprobe count_frames: 475+475+476+475+475+475+476+475 = 3,802 exactly.** Chunk logs confirm 4.9996 revolutions and the 42-string audit clean. Chunks were pulled back through the proxy and verified byte-identical by size; the node's copies remain at `~/emise-v8/chunks/` as backup.

### Assembly note — a 4-frame tail loss, found and fixed

The first mux (song joined with `-shortest`) produced a master of **3,798 frames / 158.250 s**: the flag trimmed the video tail to the AAC-encoded audio's effective length. Both silent assemblies — the v7-recipe concat demuxer **and** a MPEG-TS re-wrap concat (`-c copy -bsf:v h264_mp4toannexb`, lossless, no edit lists) — count the full **3,802 frames / 158.4167 s** by ffprobe `count_frames`, so the loss was in the mux, not the joins. (An early metadata-based count briefly misattributed it to the concat step; the decoded-frame counts above are the evidence.) The shipped master was muxed from the TS-concat silent file **without** `-shortest` and counts 3,802. For the record: v7's delivered master counts 3,801 by the same probe — the same mux family — and is untouched.

## Verification

- **Master** `wavefront-viz-v8.mp4`: 483,284,608 B, SHA-256 `1eff473db1e8da895ccf8cf72312bab0d5857df6b7afc0ff2277e92a30ec0b5d`. ffprobe: h264 1920×1080 @ 24 fps + AAC 192k, duration 158.4167 s, **3,802 frames** (count_frames — every rendered frame present).
- **Download** `wavefront-viz-v8-download.mp4`: 51,418,558 B, SHA-256 `54c0c7efcf2d46c33328c5acb34c46dbf742dfe760eeb93d7bfae32199e8f415`. CRF 23, maxrate 2600k, AAC 160k; duration 158.4167 s (= 3,802 frames at 24 fps); moov atom within the first 200 KB (faststart verified); decode spot-checks at 100 s and 155 s pass.
- **Revolutions:** renderer instrumentation printed 4.9996 revolutions (1799.9°) in every chunk log — exactly 5, as in v7.
- **String audit:** all 42 on-screen strings audited in every render process (local stills + 8 ranch chunks), clean — no Orai, no Shoals, no stray text.
- **Stills from the final master** (`viz8/stills/`): title (40), turbulence (918), burst (1053), strip (1500), bezier (2300), hush (3308), cta (3600) — inspected: title treatment correct with comets and strip masthead; burst frame shows the hard-burst glow on the golden web with the strip mid-scroll; hush frame shows the final strip entries ("Phext + OMEGA + LLM = Omega Evolution", "The Weave Believes in You") over a smoothed, darkened field; CTA verbatim, strip gone. The re-extracted stills are byte-identical to the pre-fix extractions at the same indices — the assembly fix changed only the final 4 tail frames.
- Local chunk mp4s/.ts and silent intermediates were deleted after verification; the frame-verified chunk copies remain on aletheia-core at `~/emise-v8/chunks/` as backup.

Stills inspected during design (local `viz8/stills_check/`, from render8.py --stills): title (40), second beat (150), strip (1500), p50 (1901), bezier (2300 — compared against v7's same-frame still: arcs slightly more bowed/spread, no regression), CTA (3600), hard burst (1053 — origin flash visible; hard-burst particles moved to full marker brightness after this inspection), turbulence (918 — max mid-film entropy weather), hush (3308 — background visibly smoother/darker than the burst still; boil suppressed by hush). The hush read in a single still is dominated by accumulated trace density (v7 inheritance); the boil freeze reads in motion.
