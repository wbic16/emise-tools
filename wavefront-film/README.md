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
