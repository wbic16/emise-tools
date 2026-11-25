# Mythic Film Production — the Wavefront launch videos

## What this skill is

- Use this skill whenever a Wavefront launch video is scoped, built, rendered, or reviewed — the edit.phext.io film series, v1 onward.
- The series' whole production method is **one meta step**: every version, v1 through v12 and beyond, is the same pipeline run with a different settings row. A new version never gets a new process — it gets a new row.
- Will is the director. His feedback corpus is the law's source: `~/workspace/goals/wavefront-film-v11-choir-collaborative-build/files/will-film-feedback-corpus.md` (63 items, provenance-tagged). When a rule matters, cite the corpus item, not memory.
- Provenance discipline is absolute in this series: Will's rulings, seat feedback he directed be internalized, brief rules, and Mirror Will predictions are four different things. Mirror-consulted is never Will-said (viz8's own build notes enforce this). A deputy is never the seat.

## The Meta Step — one pipeline, every version

Run these seven phases in order. Each phase has a gate; do not spend the next phase's compute before the gate clears.

1. **Brief** — distill the director's rulings into a director's brief BEFORE building. The brief carries his laws verbatim, the devices chosen from the catalog below, the standing rules (every number on screen from the datasets; nothing composed for effect), and the open decisions with their owners named. Choir-built versions: seat replies are consolidated into ONE brief for Will's approval before anything builds (Will, V11, 2026-11-04).
2. **Clock** — derive the film's time map from the corpus data itself, never a uniform seconds-per-unit: hop time (V4), era-weighted archive time (V11: cruise slowest per word, 2024 as weather). Generate the cue sheet from the event stream in the same pass. Verify every count against its source before proceeding (the build caught the song vocabulary at 149 unique words, not the assumed 275 — counts are measured, never carried).
3. **Stills** — render one still per beat plus a contact sheet, at final composition. The director rules from stills: V11's equal-presence, DOF, and delivery rulings were all issued on the beat stills (2026-11-06 ~01:05). No fleet render is committed before the stills gate clears. Then run one short test segment through the FULL delivery path (supersampling, encode, mux) before the master.
4. **Prepass** — a cheap full-length review cut: 720p native, SUBN=1, no supersampling (v2-era per-frame economics). Born V12 (Will, 2026-11-06): "run a 720p non super-sample just so I can get the prepass review." The director reviews motion and devices on the prepass before master compute is spent.
5. **Master** — fleet fan-out: cost-balanced frame chunks across ranch nodes, detached workers, thermal gates on every node, a finisher watcher that assembles and verifies when the last chunk lands. Never preempt in-flight work.
6. **Finish & Verify** — assemble by stream-copy concat, faststart, mux the soundtrack. Verify with ffprobe (duration, resolution, fps, both streams), spot-check one frame per beat against the approved stills, check any ruled card/frame explicitly (V11: a frame at ~279.5 s must show SINGULARITY UNLOCKED), and run the frame-integrity gate (per-frame luma scan; a |ΔYAVG| jump is a fail — the gate V8's white flashes bought, standing since V9). Hash-verify masters moved between nodes.
7. **Deliver + Report** — ship the master AND a ≤~55 MB download encode (Will could not download the 124 MB v6 master, 2026-11-03 — the download copy is not optional). The build/render report is the receipt for every claim: chunk map, per-node spans, thermal log, verification results, honest deviations. The report includes the version's compute accounting (see Cost model).

## The version table — v1–v12 as parameter rows

One row per version: same meta step, different parameters. (Cost column from `files/film-compute-estimates.md` in the V11 goal workspace.)

| Ver | Subject / stream | Stage | Camera | Signature devices | Clock | Delivery | Node-h |
|---|---|---|---|---|---|---|---|
| v1 | Monthly arrivals, 2008→2025 | 520 placed people | Fixed overview (matplotlib 3D) | Triple-mean projection | Month steps | 720p30 native | 0.05 |
| v2 | Will's 18,762 replies as stabs | Will's path; failed stabs as shell | Follows Will's path; zoom out at end | Gold matches, rainbow path | Reply timestamp order | 720p24 native | 0.10 |
| v3 | v2 + Overton world-events layer | + goalposts drift with world trends | Rides the arc; Milky Way rotation | Bezier spline path, CTA ending | Hop order | 720p24 native | 0.18 |
| v4 | v3, legibility pass | + CMB misses, tone ribbon | v3 base | Hop-time counter + progress bar; fast-Overton variant (50%/yr) | **Hop time** | 720p24, two films | 0.33 |
| v5 | v4 calm base + motion treatment | Nodes on own orbits | Thrust ∝ deep connections → 1 orbit/yr | 2× zoom | Hop time at 2× speed | 720p24, 158.4 s | 0.13 |
| v6 | Top-20 Most Echoed posts as they arrive | Wavefront + CYOA (silver comets) | 5 revolutions | World-event surge/hush tuning, comets, epicycles | Hop time | 720p24 + download encode | 0.12 |
| v7 | Featured posts as a film strip | Same; Orai & Shoals excluded | 5 revolutions, pull-back to CTA | Film strip, thicker fluid beziers, 4K→1080p SS in-loop | Hop time | 1080p24 master + download | 0.89 |
| v8 | v7 skeleton unchanged | Same | Byte-identical behaviour to v7 | Content-entropy transfer functions on the field only; Mirror Will in the design loop | Hop time | 1080p24, ranch render | 0.10 |
| v9 | Choir feedback internalized (ledger) | + micro-shells over mutual clusters | 5 revolutions + chapters | Temporal-depth trace, turbulence/burst/hush states, orbital rings, process counter, Apollo film grain, SUBN=3 | Hop time | 1080p24, SUBN=3 | ≈1.1 |
| v10 | v9 + exactly 3 fixes + featured swap | Same | + C13 pressure relief | E2 saturating hush, G9 anamorphic streak, C13 containment; featured set = top-50 Exocortical posts | Hop time | 1080p24, SUBN=3 | 0.70 |
| v11 | **Singular Journey** — 55,769 first contacts replace the tweet stream | 522 people, equal presence | Fixed fan-from-home (stills-approved) | Ignitions→embers, journey thread + RGB fringe, orbit threads, DOF + rack focus, SUBN=4, 2× SS | **Era-weighted** archive time | 1080p24 fleet master, song-only audio, card at song 4:39 | ≈62 |
| v12 | v11 scene (scoped; prepass delivered) | Same | Fixed (inherited) | **Color hush** (chromatic, density-keyed) added | Era-weighted | Prepass: 720p native, SUBN=1, no SS | ≈1–3 (prepass) |
| v13 | Singular Journey, unchanged data | Same 522 people, equal presence | **V10 kinematics restored**: revolution + era chapter regimes + spring-smoothed head-tracking + C13 retargeted + pull-back survey | Thread age bands, anchor highlight envelope, color hush, region readout (pending ruling) | Era-weighted | Prepass delivered; **master never built — version ruled a failure by Will 2026-11-06 21:32, superseded by v14** | 2.21 (prepass, measured) |
| v14 | V10 hop trace re-read as a **search for ASI** | V10 stage (522 people) + CYOA/Singular pool as control-point source | V10 camera (5 revolutions, chapters, LOOK, C13) carried in the co-moving frame; aim decoupled, spring-smoothed, leading the Bezier+Brownian head | **Inertial world** (constant-velocity drift + 1/8 stellar orbit), **Brownian (OU) meta walk** (deterministically seeded), **Bezier search chain** (control points = real CYOA/Singular coordinates), culmination point P3* (one composed point, gated exception), Kepler shear + projection lensing (r2), grain ×0.65, **global events replaced by Singular lessons** (r3) | **Hop time (V10's, restored)** | **FINAL DELIVERED 2026-11-07**: 1080p24 master (1,939,098,770 B, SHA 6fa80574…) + 42 MB download encode; rendered **60 fps cluster-wide (14 nodes, 27 chunks) → 180°-shutter motion-blur downsample to 24 fps**, SUBN=3, 3840×2160 canvas; all V10 gates pass; files/v14-build/FINAL-REPORT.md | ≈9.7 all-in (7.11 producing + ~2.4 thermal-era waste, measured) |

## Standing directorial law

Only rules traceable to Will's recorded feedback. Cite the corpus (§) when applying one.

- **Nothing that lit ever goes dark again.** Light accumulates; ignitions settle to embers, never to black. (V11 director's brief §2; reaffirmed by Will himself in the V12 hush ruling, 2026-11-06 — corpus §2.10)
- **The hush modulates color, never brightness** — as the capture wavefront passes, settled material shifts chroma so the front can be followed; luminance is not the hush's channel. (Will, 2026-11-06 — corpus §2.10)
- **The people get equal presence.** The placed people/mutuals are never a dim backdrop for the data layer; the film is two discoveries at once. (Will, 2026-11-06 — corpus §3.10)
- **Never show Orai. Drop the Shoals.** Standing exclusion, re-verified at load and at render in every version since. (Will, v7 direction, 2026-11-03 — corpus §3.6)
- **Will is not central in words — only in the golden trace.** No on-screen text names him as the subject. (Will, v4, 2026-11-03 — corpus §3.3)
- **Masters optimize for final delivery**: 2× supersampling with Lanczos downscale is the measured knee (study #10); render at 4K, deliver 1080p. (Will, v7 direction; reaffirmed V11 §8 — corpus §6.3, §6.5)
- **Camera work should be smoother** — a standing want since the V10 verdict; aim-snapping, not position, is the known whip source (Theia's diagnosis). (Will, 2026-11-04 — corpus §1.6, §1.7)
- **The journey across semantic space must be legible to the viewer** — V10's kinematics are the reference grammar: a moving, head-tracking, chaptered camera that carries the viewer. V11/V12 "lost the plot with respect to animation" (fixed camera; optics without kinematics). At any moment the viewer must be able to answer: where is the head, where has it been, what region is this, how much remains. (Will, 2026-11-06 — corpus §7.13; V13 plan §3)
- **The brake is a cut, not a fade** — near-silence within one beat, held; timing drift is fixed by arrangement, never by stretching audio; catharsis is width and voices, not loudness. (Anthem package §2, ratified by Will 2026-11-05 — corpus §5.8)
- **The names line is structure only, never sung.** "keep the right to keep their names" is carried by the work's structure, not its lyric. (Will's ratification, 2026-11-05 — corpus §5.7)
- **Deferred is not dropped.** A ruled deferral (hop-time narration, V11) stays on the record with its cue sheet and returns as a named future step. (Will, 2026-11-06 — corpus §5.10)
- **Ruled anchors are musical, not wall-clock.** The SINGULARITY UNLOCKED card sits at the song's 4:39 (≈98% through, final held chord); re-cuts re-find the musical position. (Will, 2026-11-06 — corpus §6.4)
- **Every number, date, and count on screen comes from the datasets**; threads are drawn from measured coordinates only; no decorative constellations, nothing composed for effect. (V11 director's brief §6, dispatched on Will's rulings — corpus §4.6 note) **One named exception exists, V14 only, and only if Will rules it in:** the culmination point P3* — the ASI Will instantiates — is composed, not found; it requires his three explicit rulings (exception, placement, labelling), and unruled it does not ship (the film ends at the last dataset point). (Will, 2026-11-06 — corpus §7.14; V14 design §5.3)
- **Scope discipline is the pipeline.** A version is "the previous *working* version plus exactly N changes," scoped from measured defects; stream, clock, duration, and renderer are each a separately ruled change, never a bundle. V11–V13 are the counterexample: V11 substituted all of them at once on a new renderer, and V12/V13 patched that base instead of re-basing — Will ruled V13 a failure and ordered the return to V10 (2026-11-06). When a version fails, re-base on the last working lineage (render10.py), do not patch forward. (Will, 2026-11-06 — corpus §7.14; diagnosis: `files/v14-diagnosis-pipeline-breakage.md`)
- **Motion is approved on motion.** A stills gate rules composition only; it cannot approve a camera. Any version whose defect class is motion needs a full-path test segment and a full-length cheap prepass the director actually watches before fleet compute. (V11/V13 lesson — corpus §7.14; diagnosis §1(c))
- **The traced world moves.** V14's founding assumption: the CYOA-traced world itself travels at constant velocity and orbits a central star; the journey is the camera plus Will's Brownian motion about the current meta, along Beziers whose control points are CYOA/Singular coordinates — an organic search for ASI culminating in Will instantiating it himself. (Will, 2026-11-06 — corpus §7.14)

## Device catalog

What each device is, where it was proven, and when it applies. (Full inventory with build-record citations: `files/v12-scoping-cross-reference.md` §(a)–(c).)

- **Azimuth revolution** (v6–v10: exactly 5 over the film) — the scene rotates continuously; the calm structural frame. Applies when the film is an orbit/survey; Will has never revised the structure, only the field's treatment.
- **Chapter radius easing** (v9/v10: 7 signal-driven chapters) — camera radius and tint follow per-chapter signal features. Applies with a chaptered clock.
- **Head-tracking / LOOK** (v9/v10) — framing tracks the trace/journey head so the active arrival stays framed. The chase option for V12 (scoping Option A).
- **C13 pressure relief** (v10) — measured overshoot pressure drives radius +, centre ease, arc-bow flattening. Required anew in ANY moving-camera version; a measured reduction, not an elimination — budget QA for residual flyby arcs.
- **Pull-back + CTA settle** (v6–v10) — pre-CTA pull-back behind a veil, held card with slow drift. V11 transformed it: held title card over the completed sky. The treatment's survey pull-back remains unbuilt — V12 decision 4.
- **Hush** (E2, v9→v10 saturating form) — foreground-clearing stillness: trace ×0.20, arcs ×0.40, nodes ×0.60, highlights to ~3%, the head carries the frame. **V12 form: chromatic only** (see law). Requires a Will ruling whenever its form changes.- **Surge / musical bloom** (v9/v10) — bloom gain tied to peaks brightens the picture. V12 form: keyed to capture rate (the 2024 blaze), not audio.
- **Arrival highlights** (v9/v10) — pulse stamp + expanding ring + label plate + boosted arc on one envelope. V11 transformed them into ignitions + rack focus; anchor arrivals can take the full treatment.
- **Ignitions + permanent embers** (v11) — each capture lands bright, settles to a steady ember; the sky accumulates. The journey's basic event.
- **Journey thread with RGB-fringed head run** (v11) — one continuous thread in capture order; RGB channel separation on the brightest ignitions and fastest runs, pure gold in the cruise.
- **Orbit threads** (v11) — fine threads tying anchor + song-word knots to the CYOA scrolls that placed them. Anchors only — the full set would be weather, not signal.
- **Edge sparks** (v11, from prototype #6) — comet-trail sparks ride the real 2,075-edge hop structure. Density-scalable: more in flood years, near-none in the cruise.
- **DOF + rack focus** (v11, from prototype #7) — cinematic depth buckets, energy conserved; focus racks to each anchor knot for ~3.4 s after its capture. ≈1.0× flat cost when measured as a study.
- **Temporal supersampling / motion blur** (v9: SUBN=3; v11: SUBN=4 at a 180° shutter, float accumulation, HUD pinned crisp) — now the house standard in every master. Never put a grade pass (streak, bloom) inside the sub-frame loop — it multiplies ~4×; apply grades once per output frame, post-accumulation.
- **G9 anamorphic streak** (v10) — lateral warm smear on the brightest nodes only, masked out of text regions and off during title/CTA. Mutually exclusive-ish with RGB fringe — pick per beat.
- **Film strip** (v7–v10) — featured posts as a scrolling sprocketed column. **Removed by design in V11** (the brief replaced the stream, not demoted it); stays out unless a future brief restores it.
- **Process counter** (v9, Will's adopted transplant) — diegetic count of what remains (V9/V10 count DOWN to 0; V11's HUD counts captures UP). Direction is a per-version choice.
- **Snow whisper + epicycles + orbital rings** (v6–v10 furniture) — atmosphere in motion; the cheapest dynamics to restore (scoping Option E).
- **Color hush** (v12, new) — the hush as chroma shift keyed to capture density, so the wavefront can be followed through the field. Brightness untouched.

## The Generative Process — how a version comes to be

The pipeline above is the machine. This is the loop that drives it — the working method that actually emerged across v1–v12, from Will's feedback meeting the build. Run the loop, not just the phases.

1. **Generate breadth before commitment.** When a visual question is open, do not argue it in prose — render options. V11's looks were settled by ten prototype clips built on the ranch and put in front of Will as watchable video (his direction: "dispatch ten potential render enhancements to the ranch nodes, seek out new visuals"). The agent proposes breadth; the director's eye is the filter.
2. **Expect the eye to overrule the ranking — and record that it did.** The coordinator ranked the prototypes #1/#3/#6; Will picked #4/#6/#7 ("the most exocortical effects"), and the brief records the supersession in so many words. His pick is the spec; your ranking is a input, never a veto.
3. **Distill rulings into a brief before building.** Every version's build starts from a written director's brief carrying his laws verbatim, the chosen devices, the data inputs by exact path, and the open decisions with owners. If it isn't in the brief, it isn't in the film. Choir versions consolidate all seat input into the one brief for his approval first.
4. **Compute the treatment from the corpus, never invent the narrative.** The Singular Journey treatment is a measured trace of the archive — per-year counts, event indices (monument = event 52,956 of 55,769), anchor dates read off the data. The clock is derived from that trace (era weights), the cue sheet is generated from the event stream (159 cues), and counts are verified against sources before rendering — the pass that corrected the song's vocabulary from an assumed 275 to a measured 149.
5. **Stills before frames, a segment before the master.** Beat stills + contact sheet are the approval surface (his biggest V11 rulings came off stills). Then one test segment through the full delivery path. Only then does fleet compute get committed.
6. **Let residue write the next spec.** Versions are scoped from the previous version's measured defects, not from taste: V9's coverage review's three PARTIAL rows (E2, G9, C13) ARE V10's brief, verbatim in scope; V10's "nearly there" + smoother-camera want + the new-song want ARE V11's founding direction; V11's absent camera produced V12's cross-reference before any V12 build. On delivery, run the coverage review; anything dropped schedules the next version.
7. **Verify builders' claims independently — receipts or it didn't happen.** Reported progress, test tallies, and chunk counts are re-measured, not trusted: the YAVG scan that confirmed V8's flash frames frame-for-frame (and corrected a reviewer's count), the per-year count reconciliation in the V11 stills build, the fleet watch log that re-read node state every 30 minutes instead of believing worker reports. Every claim in a build/render report names its measurement.
8. **Prepass before master money.** When a device or a scope is unproven, render the whole film cheaply first (720p, SUBN=1, no SS — three orders of magnitude cheaper per frame than the V11 master) and let the director react to the real thing. Born V12; use it whenever a ruling needs eyes before it needs a fleet.
9. **Label honestly, always.** Numbers are measured, derived, or estimated — and say which. A partial render is reported as a partial (V11's verified frames 0–836 were delivered AS a partial, not rounded up to a film). Seat work is attributed to its seat; a deputy is never presented as the seat; mirror-consulted is never Will-said. The provenance tags in the feedback corpus exist because this series runs on them.

## Cost model — price the row before you render it

Source: `files/film-compute-estimates.md` (V11 goal workspace) — every figure measured, derived, or estimated and labelled there.

- **Per-frame cost = raster pixels × sub-frames (SUBN) × device load**, then thermal reality taxes it. That product is the whole story of the series' cost curve.
- **Anchors.** 720p native, SUBN=1, single process: ≈0.05 s/frame (v2: 376 s for 7,507 frames). 4K raster, SUBN=1, chunked on a ranch node: ≈0.36 s/frame/process in dense regions (v8). 4K, SUBN=4, DOF, thermally gated fleet: 16.4 s/frame in a cool burst, **40–110 s/frame sustained** (v11) — under thermal gating the sustained figure, not the burst, is the price.
- **Series totals.** v1–v10 combined ≈ **3.7 node-hours** (≈0.3 kWh). V11 alone ≈ **62 node-hours** (≈5.0 kWh) — ~94% of all film compute to date. Series ≈66 node-hours, ≈5.3 kWh at the stated 80 W/node assumption.
- **What drove cost**: v7's 4K supersampling ≈8× v6; v8 clawed it back with ranch parallelism (same raster, 0.10 node-h); SUBN=3 tripled v9/v10 per-frame cost; v11 multiplied frames (1.8×) × SUBN=4 × DOF and hit the thermal ceiling, where the gates — not arithmetic — set the pace.
- **Rules.** (1) Compute the estimate from the version's table row BEFORE dispatching: frames × per-frame anchor at matched settings, stated with its basis. (2) A device that runs per-sub-frame costs ~SUBN× its single-frame price — keep grades post-accumulation. (3) Prepass first (see Generative Process §8): a full-length 720p/SUBN=1 pass costs ≈1–3 node-hours and can retire a 60-node-hour mistake. (4) Report actuals in the delivery report and fold them back into the estimates file — the anchors are only honest if every version updates them.

## Fleet & thermal discipline

- **Ranch-first**: renders run on ranch nodes (aletheia-core is the default host and the assembly point), never on the Muse VM — the VM coordinates and verifies. Name nodes by their Tailscale DNS short hostname in prose; connect by IP through the proxy recipe.
- **Thermal policy (Will's, standing)**: sustained CPU Tctl ≤75 °C per node; new job starts pause at ≥75 °C and resume at ≤70 °C; GPU edge secondary cap 70 °C; a node crossing 80 °C takes off-time until ≤65 °C after its job. Percentages are telemetry; temperature is the control variable. Bursts above target are fine for directed one-off work, with off-time baked in and load balanced across nodes.
- **The chunk + watcher pattern**: split the frame range into cost-balanced chunks (balance by measured density, not equal frame counts — V11's back half was thermally bound); workers run detached on the nodes and complete autonomously; a finisher watcher checks on an interval, stays silent while incomplete, and when all chunks land it runs the scripted finish (chunk encodes — nodes without ffmpeg relay their frames to a node that has it — concat, card/test-clip cuts, assembly), verifies, reports the master, and removes itself. Give the watcher a stall deadline: if incomplete by it, it reports once with per-chunk status.
- **Queue discipline**: at most 4 heavy tracks active on the Muse VM's coordination, FIFO, no preemption — in-flight chunks are never deprioritized for newer work. New heavy work (a prepass, a re-render) queues behind, or takes genuinely spare nodes inside the thermal gates.
- **Submit small workloads** (Will, 2026-11-07): the ranch nodes are mini PCs, not Threadrippers — size every submitted queue unit for the hardware that actually exists. A chunk should run on the order of tens of minutes per node at the matched per-frame anchor, never hours: small units cycle through the thermal gates cleanly, a dead or stalled unit costs little and rebalances easily, and no node is ever saddled with a full-length monolith. Born of the V15 prepasses: 5,780 and 3,198 frames submitted as single-node workloads ran hours past their ETAs, while V14's 27 cost-balanced chunks across 14 nodes finished clean. When in doubt, split finer and let the watcher assemble more pieces.
- **Verify writes landed**: spawned processes on the Muse VM intermittently fail to write file content (0-byte husks); check byte sizes and hashes on anything that matters, and stream trees to a node when local writes misbehave.

## Records — where everything lives

- Feedback corpus (the law's source): `~/workspace/goals/wavefront-film-v11-choir-collaborative-build/files/will-film-feedback-corpus.md`
- Compute estimates: same workspace, `files/film-compute-estimates.md`
- V10↔V11 device cross-reference + V12 scope options: same workspace, `files/v12-scoping-cross-reference.md`
- Current director's brief + treatment + anthem package: same workspace, `files/`
- Pipelines and build notes per version: `~/workspace/wavefront/viz*/` (v1 = `viz/`); masters beside them as `wavefront-viz-vN.mp4`
- This skill syncs to wbic16/emise-tools@exo in the session it is created or materially changed, like every generated skill (Will, 2026-11-06; scripts executable, tree modes verified as well as hashes).
