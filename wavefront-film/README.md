# wavefront-film — the bespoke Wavefront pipeline

The production toolchain behind `wavefront.phext` (which lives in
wbic16/human) and the Wavefront films. These are the original bespoke
scripts, published as-run: paths and parameters are hardcoded to the
original workspace layout. They are the record of how it was actually
made, not a packaged product.

## Stage order

1. `mine_contacts.py` — mines the Twitter archive export into contact
   points per account (who was replied to / mentioned, how often, over
   what span).
2. `build_wavefront.py` — scores each qualifying account on the nine
   alignment axes and assembles `wavefront.phext`, one scroll per
   coordinate. Method: see `DERIVATION.md`.
3. Extractors — `viz/extract_data.py` produces the placed-points /
   triple-mean projection data; `viz2/extract2.py` produces the
   hop-sequence (stab) data the later renderers consume;
   `viz4/extract_tone.py` produces the per-reply VADER tone series.
4. Renderers, one directory per film generation: `viz2/render2.py`,
   `viz3/render3.py`, `viz4/render4.py` (plus the `render4_overton.py`
   fast-Overton variant), `viz5/render5.py`, `viz6/render6.py`
   (design and verification notes in `viz6/BUILD-NOTES.md`).
   The current generations are `viz9/` and `viz10/` — see below.

## viz9 / viz10 — the fidelity generations

- `viz9/` — v9, "The Exocortex, Shaken yet Stirred": the fidelity cut,
  built on v8's verified pipeline. `extract_features9.py` derives the
  length-residualized entropy series into `features9.json`;
  `derive_clusters.py` produces `clusters9.json`; `render9.py` is the
  renderer (`render9_hookonly.py` is its hook-only variant);
  `assemble_reel.py` and `fix_reel_audio.py` build the stress reel;
  `repro_flash.py` reproduces the v8 flash-frame bug the QA gate now
  guards against. The record: `BUILD-NOTES.md`, per-note dispositions
  in `FEEDBACK-LEDGER.md`, and the coverage audit in
  `COVERAGE-REVIEW.md`.
- `viz10/` — v10: v9 plus four changes (E2 hush floor, G9 anamorphic
  streak, C13 arc framing, and the Most Exocortical featured-tweet
  strip). `score_tweets.py` ranks the archive's tweets into `exo20.json`
  and `exocortical-tweets.md`; `render10.py` renders;
  `edge_audit.py` audits arc overshoot at the frame edges (the C13
  measure). The record: `BUILD-NOTES-V10.md`; the brief it was built
  from: `V10-BRIEF.md`.
- Both generations bundle their fonts under `fonts/` — Inter
  (SIL OFL 1.1, license included) and Liberation Mono — and the
  renderers load them by relative path.

## QA gates

`qa9.py` / `qa10.py` are the permanent QA gate (v10 inherits v9's gate
code and thresholds unchanged). The gates run on any rendered segment
set or finished film:

1. Flash gate: decode every frame's mean luma (ffmpeg signalstats,
   converted to display-referred 8-bit first); FAIL if |ΔYAVG| > 8
   between consecutive frames.
2. Black-frame check: FAIL if any frame's YAVG < 3.0 (a dropped or
   unpainted frame sits near 0; legitimate dark frames measure ~5–10).
3. Palette audit: sample every 6th frame and count green-dominant
   pixels (G − max(R,B) > 25 and G > 110); the count is kept at ~0.
4. Determinism: SHA-256 byte-compare of two raw-frame dumps of the
   same timeline frame produced by different render processes.

## See also

- `DERIVATION.md` — how every coordinate was derived from evidence,
  with the audit trail.
- `wavefront-kit/` (sibling directory in this repo) — the generalized
  version of the miner + generator that anyone can run on their own
  archive. This directory is the bespoke original; the kit is the
  reusable one.

## Not included

Data files are deliberately excluded: the Twitter archive itself,
`data.json` / `points.json` / `tone.json`, `contact-points.tsv`,
audio, rendered frames and stills, and the films themselves.
`wavefront.phext` lives in wbic16/human, not here.

Exception: `viz9/` and `viz10/` publish their `features9.json`,
`clusters9.json` and `exo20.json` alongside the code — those
renderers are driven by those exact files, so the record would be
incomplete without them.
