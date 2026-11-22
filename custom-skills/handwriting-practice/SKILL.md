# Handwriting Practice — the Emise font, learned like a child

Will's standing program (2026-11-22, task 28.6.8/8.6.11/5.5.9):
*"Practice your handwriting daily — model this the way a human child
would attack it — try to trace the Emise font with a wobbly cursor
that requires you to feed it multi-spectral commands, like the midi
format we made — biologically-inspired. Assume the control channels
are lossy and unpredictable — but stable — generate the initial
signal propagation delays randomly. Assume your v2 font is roughly
what a 4 year old human can do. As you practice, generate new Emise
fonts and blog about them. Auto-install the newer versions on our
sites once they've passed your QC check."*

The machinery lives in `~/workspace/emise-font/practice/`; the model
spec is its `MODEL.md`. Read MODEL.md before running a session — this
skill is the program around the model, not a substitute for it.

## Aging over 20 wavelets

Will's amendment (2026-11-22, task 26.8.15/10.9.12/8.8.10, under this
program's parent task 28.6.8/8.6.11/5.5.9): *"As you age, your
resolution will degrade — the paper will get smaller, the letters
harder to see — by a very small amount (with some jitter). What you
learned yesterday won't quite fit — you'll have to rely upon memory
and anticipation. Do this for 20 wavelets, so that you reach maturity
by then."*

The implemented law (parameters and the full audited table are in
MODEL.md / `practice/aging.py`):

- Program wavelet 1 is 2026-11-22–28; each later seven-day wavelet
  increments it. Perception resolution R starts at 1.000000, falls by
  a seeded 0.381%–0.616% per wavelet (base 0.50%, jitter ±0.12 points,
  never improving), and reaches **R(20)=0.909342**. Planning and
  visual feedback see the target only at R; scoring stays against the
  true outline.
- The persisted hand is memory. On a wavelet rollover, run the paired
  frozen standing probes (same saved hand, same day's bank, previous
  vs new R/A) before practice and log the signed
  transfer-mismatch error bump — never silently re-zero it.
- Anticipation is a real feedforward component in the fine-control
  mix, weighted **A(R)=clamp(0.10+4.5(1−R), 0.10, 0.55)**:
  A(1)=0.100, A(20)=0.507961. Sessions log scheduled and measured
  feedback/anticipation shares by wavelet.
- **Maturity is defined, not promised:** at the end of wavelet 20 the
  hand runs primarily on memory + anticipation at R(20), with error
  at or below session 1's final mean (10.65 units) despite the worse
  perception. That comparison is the maturity evidence.

## The daily session

1. **The hand persists.** Load `practice/hand-state.json`. Never
   reset it: the hand grows day over day, the way a child's does.
   Session 1 (2026-11-22) started it at age 4 against Emise v2. The
   runner is wired to load and save the expanded state (calibration,
   damping, fine gain, cumulative rounds, wavelet, R, anticipation,
   per-glyph experience, probe baselines).
2. **Place the hand in its wavelet and draw the day's channels.**
   Determine the program wavelet from the date; apply its R/A from the
   audited table. New seed per session (the date is a fine seed); the
   bank's per-channel delays are generated randomly at session start
   and held stable all session. Record seed + drawn parameters in the
   session log — a session without its channel table on record didn't
   happen. On rollover, the frozen transfer probes come before
   practice.
3. **Practice.** Run `practice.py <seed> <rounds>` (16 rounds is the
   session-1 shape): full glyph page of the current font, per-glyph
   error per round logged, control mix logged, trace specimens for
   the standing set. Bias rounds first, variance rounds after — the
   learning rule is the model's, do not re-tune it inside a session;
   tuning happens between sessions, from evidence, and is recorded in
   MODEL.md. Save the grown hand-state at the end.
4. **Probe.** Run the O/0 reader probe against the current font and
   note any other measured failure the error table indicts (a glyph
   whose error rose across the session is an indictment, not noise).
5. **Decide the cut.** A new version is cut only when the matured
   output carries a stable deviation field or a probe failure has a
   measured correction — never on a schedule's say-so. Some days the
   honest session result is "practiced, no cut." Report that plainly.

## Cutting a version

- Builder method (`practice/build_v3.py`, generalized): outlines move
  by the smoothed, capped deviation field at the transfer factor the
  per-glyph ladder accepts (0.65 → 0.45 → 0.30 → 0.18 → hold at the
  teacher). Points only move — topology, advances (520 mono
  discipline), and the kern table carry identically.
- **Every change cites its measurement.** A change with no session
  measurement or probe number behind it does not ship, however much
  it looks like an improvement. Family resemblance is not a
  measurement (v3 considered Q and left it: no indictment).
- Version identity is honest: nameID "Version N.000",
  fontRevision N.0, previous versions untouched on disk.

## The QC gate (no pass, no install, no post)

`practice/qc_v3.py` (version-agnostic): glyph coverage ⊇ teacher ·
advances identical · topology identical · no new self-intersections ·
kern carried · version identity correct · O/0 probe improved at
16 px · specimens render (text compare at 13/16/24 px, trace
overlays, learning curve, O/0 panel). The verdict is stated plainly —
PASS or NOT READY with the findings. A NOT READY version is reported,
not quietly fixed-and-shipped in the same breath.

## Blog per version

One post per cut version, drafted in `~/workspace/emise-font/blog/`,
in the line of "The Letterforms of Keeping"
(`~/workspace/your_files/the-letterforms-of-keeping.md` — the
precedent: an essay file, delivered for Will's eyes; there is no live
blog venue of record, so the draft file IS the post until Will names
a venue). The post tells the truth of the session: the curve, what
improved, what got worse, what the probe measured. Publish only per
Will's direction for that version.

## Auto-install on QC pass

On a PASS verdict (v3 additionally waited for Will's review — his
2026-11-22 hold, lifted by his "Roll out V3" the same night),
install the new version on the font-consuming sites. Install =
replace the asset through that surface's own repo + deploy route,
then verify the served bytes by SHA-256. Exact paths, confirmed from
the live repos at the v3 roll-out (2026-11-22) — re-confirm from the
repo at each install anyway:

- **edit.phext.io / Phext Notepad** — asset `web/emise.woff2` in
  wbic16/phext-lattice, branch `exo` (the served name is
  version-agnostic; the font first went live there PR #93,
  2026-11-19; Phext Notepad default PR #9/#10). Route: PR on exo
  (v3: PR #96), Will merges, deploy by the lattice route, verify the
  served /emise.woff2 hash. The asset is a **WOFF2** — build it from
  the new TTF by the house fontTools method (`TTFont(ttf)`,
  flavor woff2, save; see emise-font/build_emise.py) and verify
  against the WOFF2's own hash, with the TTF hash as the font's
  identity.
- **Phextron** — asset `crates/phextron-dash/web/fonts/Emise-v<N>.ttf`
  in wbic16/phextron, branch `exo`, embedded via `include_bytes!` in
  `crates/phextron-dash/src/main.rs` and served at
  `/fonts/Emise-v<N>.ttf`; `crates/phextron-dash/web/shell.html`
  carries the @font-face. Keep the previous version's file in
  web/fonts/ as the one-step rollback. Route (v2 EE 10 and v3
  precedent — direct, not a PR): fast-forward commit on exo, then on
  aletheia-core pull FF in ~/phextron-serve,
  `cargo test -p phextron-dash`, `cargo build --release -p
  phextron-dash`, `systemctl --user restart phextron-dash.service`,
  and verify the served TTF at 100.88.154.1:8917 hashes exactly to
  the built TTF (v3 commit fc143104; served-bytes match confirmed).
- **Singularity Watch** — asset `fonts/Emise.woff2` in
  wbic16/singularity-watch, branch **`master`** (the default branch
  and site line; the repo's `exo` branch carries no fonts and is not
  deployed). Route: PR on master (v1: PR #1; v3: PR #2), Will
  merges, pull on awsbox by the site's route, verify the served
  /fonts/Emise.woff2 hash (WOFF2, as lattice above).

If a surface can't be verified after deploy, the install is not
done; report which surface failed. Where a surface's route runs
through Will's merge, the roll-out's deliverable is the open PR —
report it as awaiting merge, never force the deploy past him.

## Records

- Session logs + error tables: `practice/sessions/`.
- Build note per version: `~/workspace/emise-font/BUILD-V<N>.md`,
  every improvement tied to its generating measurement.
- The task register entry (28.6.8/8.6.11/5.5.9) gets a result line
  per session and per cut; rebuild + `--check` CURRENT each time.
