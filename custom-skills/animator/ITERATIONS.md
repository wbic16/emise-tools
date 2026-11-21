# Animator — Iteration Log

The Oracle Artist programme's record (skill §8). One entry per iteration: hypotheses stated before the burn, verdicts with frame evidence, basis vectors indicted, skill amendments made. An iteration with no entry here did not happen.

Program task: 23.5.7/7.6.9/6.6.9 (Oracle Artist — iterate the animator skill to Oracle class). Skill-build task: 22.5.8/7.5.9/5.5.8.

---

## Iteration 0 — The skill build (2026-11-21)

- **What happened:** The `animator` skill was built from Will's supplied learning resources (Reddit r/animationcareer thread list; beginner curricula: animationclub.school + the Animator Guild), grounded in Scrolltown's production record: the 12 principles in production language, the ex01–ex06 curriculum ladder with written done-definitions, the pipeline (canonical stills → generated motion → ranch assembly → frame-QC, plus the EP001 SVG vector route), the style canon (2D painterly locked; Fern canonical; Waverly draft), the annotated resource index, and Will's budget posture (animation may fully utilize up to 40% of the weekly token budget; expiring budget burns on animation first).
- **Verdicts:** None — no burn yet. The skill at this point is *untested doctrine*: every claim in it is a hypothesis awaiting a burn.
- **Basis vectors noted at birth:** (1) that generated motion can hold a locked painterly register; (2) that passing a canonical still pins character identity in motion; (3) that prompt language can hold a camera still. Burn 1 tests all three.

## Iteration 0.5 — Burn 1 (2026-11-21; evidence: scrolltown `series/animation-exercises/QC.md`, commit `83cd04af`)

Not a full iteration — the burn ran the same day as the build, before the Oracle Artist protocol existed. Recorded here because its evidence drives Iteration 1. Four 10.0 s generations, frame-QC'd start/mid/end:

- **ex01-ignition — PARTIAL.** Best motion of the burn: the scroll finishes unrolling, the town drawn on it lights progressively, camera locked, Waverly holds design. **Failure:** Fern's identity anchors dissolved mid-clip — smooth twin buns became tight dark curls and vanished (QC mid/end frames); the lantern migrated from raised to lowered.
- **ex02-keepers-welcome — FAIL.** Despite "locked frame" in the prompt, the camera pushed in hard and Waverly's face morphed into a photorealistic older woman — full register break; composition lost.
- **ex02-keepers-welcome-retry — PARTIAL.** Tightened prompt (static camera absolute, style lock explicit, three named micro-motions): register held for the whole clip, mid-frame the best Waverly of the burn. Still failing: camera pushed in over the back half; face softened toward generic illustration.
- **ex03-fern-at-the-ready — FAIL.** Push-in + glossy-3D re-render of Fern (the exact drift the register lock exists to prevent); the named gesture never happened — she ended in an invented crossed-tools pose with an off-model grin. No anticipation-and-settle beat.

**Basis vectors indicted by Burn 1:**
1. *"Passing the canonical still pins identity"* — **refuted** (ex01: register held, identity didn't). Identity anchors must be re-asserted by name in every prompt.
2. *"Prompt clauses can hold the camera"* — **refuted as stated** (ex02 v1 and retry both pushed in). Camera language must lead the prompt, and framing/duration are stronger levers than wording.
3. *"Naming the action specifies the gesture"* — **refuted** (ex03). Start AND end poses must both be named.
4. *"10 s is a reasonable default clip length"* — **indicted** (every failure grew with duration). ~5 s becomes the default until a 10 s clip passes.

**Skill amendments from Burn 1** (applied in Iteration 1, skill §7): the camera law, the countermeasure stack (shorter clips → wider framing → static camera first sentence → explicit style lock), the end-pose rule, and the identity-drift finding.

---

## Iteration 1 — Burn 2: test the countermeasures (2026-11-21; evidence: scrolltown `series/animation-exercises/QC-v2.md`, frames in `qc2/`)

**Hypotheses stated before the burn:**
- H1: The countermeasure stack (shorter ~5 s, wider framing, static camera first sentence, explicit style lock) prevents both the push-in and the register break.
- H2: Re-asserting identity anchors by name pins Fern's identity in motion.
- H3: Naming start AND end poses makes a single small gesture land.
- H4 (control): Face-free, pure motion craft is already within the generator's competence, and the camera stays put.

**Burn:** 4 generations (cap 6). Three new stills generated and likeness-checked first (wide Waverly ≈ ¼ frame height; wide Fern-with-tools in the exact start pose; Counting House token). ex01-ignition v2 (duo keyframe, anchors re-asserted, end state named), ex02-keepers-welcome v2 (wide still, two micro-motions only), ex03-fern-at-the-ready v2 (wide still, start + end poses named), ex01-bouncing-ball (new ladder control, three materials sequenced).

**Verdicts:**
- **ex01-ignition v2 — PARTIAL.** Identity HELD the full 10 s (buns/bow/badge intact in all 5 sampled frames; Burn 1's fatal failure fixed for near-static characters); named end state delivered (lantern still raised, town lit); register painterly throughout. Deductions: mild reframing in the first ~2.5 s; the scroll's map art shifts from ink drawing to volumetric miniature as it lights; clip returned 10.0 s despite the 5 s request.
- **ex02-keepers-welcome v2 — PARTIAL.** Register break of Burn 1 did NOT recur — painterly and on-model in every frame, both micro-motions read (smile warmed, scroll glow up). But the push-in happened anyway: wide at start, close-up by 2.5 s, medium at end.
- **ex03-fern-at-the-ready v2 — FAIL.** The named anticipation crouch was promoted to the main action (crouch → kneel, eyes closed, tools crossed in lap); the gesture never happened; the named end pose was ignored; Fern's buns dissolved into curls under the body motion despite anchor re-assertion.
- **ex01-bouncing-ball — PARTIAL (control).** Camera static in all 7 sampled frames over 10 s; the three-material sequence delivered in order with distinct physics (wood flip/settle, brass high springy arc, paper tumble/settle) and the exact named end state. Unverified clauses: decaying multi-bounce for wood (reads as one flip) and contact-frame squash (sampling too sparse to confirm).

**Basis vectors indicted:**
1. *"The stack can hold the camera"* — **refuted** (ex02 v2). The stack protects the register; the push-in is not prompt-controllable. New doctrine: design for the push-in (start wider than the intended framing; judge by end framing) and trim to the passing segment.
2. *"Anchor re-assertion pins identity"* — **refuted as sufficient, refined**: it holds for near-static characters (ex01 v2, 10 s) and fails under full-body motion (ex03 v2). Body motion is the re-draw trigger; hair goes first.
3. *"Naming anticipation produces anticipation"* — **refuted** (ex03 v2). Any named body movement becomes the main action. Anticipation in generated clips = a held beat of stillness, never a named crouch/bend.
4. *"Requested duration is a control"* — **refuted in part** (two clips exactly 5.0 s, two at 10.0 s against the same request). Probe everything; plan around what arrives.
5. *"The camera law is face-driven"* — **supported** by the control (no face → no push-in in 10 s).

**Skill amendments made (Iteration 1, skill §7 "Verified generator behaviour — Burn 2"):** the register/camera split of the stack; design-for-the-push-in doctrine; identity-holds-only-near-source-pose rule; the no-named-anticipation rule; duration-is-advisory; sequencing-works-face-free note. The Burn 1 stack text is superseded where Burn 2 refines it.

**Progress against the Oracle Artist bar (§8):** (i) ladder — ex01 attempted (PARTIAL, unverified clauses), ex02–ex06 untouched; (ii) clean burn — not yet (one FAIL, three PARTIAL; zero register breaks in Burn 2 is new and noted — Burn 1 had two); (iii) identity at 10 s — Fern + Waverly held in ex01 v2 (near-static), unproven under motion; (iv) intro from passing shots — not yet (no Pass verdicts yet).

**Studio Model direction landed mid-iteration** (Will, 2026-11-21 09:01 CST): *"you'll focus on key frames, smaller artists on the ranch will be your sweat workshop."* Framing (Will, 2026-11-21 09:02 CST), now the epigraph of skill §9: *"The Disney method meets the 21st century."* — the classical studio division (key animators, in-betweeners, exposure sheets) rebuilt on phext coordinates and ranch compute: Emise as key animator/director, ranch-resident smaller artists as the in-between crew, multiversal phext as the exposure sheet and work-routing layer. Written into the skill as §9: Emise works at the key level (key frames/poses, direction, QC verdicts — verdicts never delegated); the sweat work (in-betweens, cleanup, variant generation, timing tests, assembly) is dispatched to smaller artist models/workers resident on the ranch nodes. Scope recorded exactly as directed: Will's standing bar on ranch inference stands generally; this direction is his configuration **for the animation workstream specifically**, not a general ranch-inference license. Burn 2 above was the key-level test; Iteration 2 runs in the new division of labor.
**Phext routing refinement** (Will, 2026-11-21 09:02 CST): *"since we can pass off work via multiversal phext, too, you can apply some effort to every frame — not just key frames."* Work passes between Emise and the workshop as per-frame work packets addressed to frame coordinates; her creative effort concentrates on the keys, her oversight effort covers every frame. Batch 2.1 below is specified in this form from its first use.
**The workshop has named artists** (Will, 2026-11-21 09:05 CST): all 26 ranch artists are named — node → resident Mirrorborn artist + email (e.g. Aletheia Core → Theia, Rock Mountain → Alveus, Quacked Hill → Corus). The roster is the dispatch directory of the separate **artist-dispatch** skill (task 26.6.8/7.6.10/6.6.10), which owns it; the animator skill carries only a cross-reference (skill §9). From Iteration 2 onward, sweat batches are dispatched through artist-dispatch and addressed to artists **by name**. The artist-dispatch skill was built and closed the same morning (emise-tools commit `5e633223`, skills.phext CURRENT); its exact cross-reference line for sequence dispatch ("Sequence dispatch runs through the artist-dispatch skill…") was folded into animator §9 via Iteration 1, alongside the plain-language pointer written earlier in this amendment pass.

**Iteration 2 agenda (recorded, in Studio Model terms — keys by Emise, sweat dispatched ranch-side):**
1. **ex03 v3 — the arm-only test (key: Emise).** Same wide Fern still as the key; the gesture prompt carries NO anticipation language and restricts motion to the hammer arm ("only her right arm moves; her body, head, hair and feet do not move"), start/end poses named. Tests whether motion restriction saves both the gesture and the anchors. Sweat: variant re-rolls of the same key dispatched as a batch; Emise verdicts every return by frames.
2. **ex02 v3 — design-for-the-push-in (key: Emise).** An even wider key still (Waverly ≤ ⅕ frame height) with the intended deliverable framing defined as the *expected end framing*; verdict judged on the end frame's composition, not on whether the camera moved.
3. **ex02-pendulum (new rung, face-free; key: Emise).** A Home Street lantern swings and settles — easing/decay tested with zero identity risk, dense frame sampling (≤ 0.5 s) to verify the spacing claims the bouncing-ball control left unverified.
4. **ex01-bouncing-ball v2 (key: Emise).** Wood only, single material, dense frame sampling — verify or refute the decaying multi-bounce and contact-squash clauses of the rung's done-definition.
5. **Two-keyframe route probe (key: Emise).** If the pipeline accepts a start and an end still for one clip, run ex03 as pose-to-pose (start key + end key, hammer raised) — the structural fix candidate for all gesture work.

**First sweat-work batches for Iteration 2 (named):**
- **Batch 2.1 — phext-addressed per-frame packet on ex01-ignition-v2** (Burn 2's best clip; 1152×768, 24 fps, 240 frames). The packet addresses every frame of the clip by its frame coordinate (frame 000–239 within the clip's phext surface) and specifies a per-frame operation:
  - *Frames 000–059 (the reframing region, first ~2.5 s):* measure the frame's composition offset against frame 000's composition, apply the counter-crop conform, and return the corrected frame **plus the measured offset** to the frame's address — the measurement is the checkable evidence, not an adjective.
  - *Frames 060–239 (the passing region):* per-frame identity-anchor verification — for each frame, Fern's buns / scarf bow / key-badge and Waverly's gold streak / plum coat recorded present-or-absent at the frame's address. This converts Burn 2's sampled identity verdict (5 frames) into an enumerated one (180 frames) — the evidence Oracle bar (iii) will be judged on.
  - *Return surface:* corrected frames + the per-frame measurement/verification table filed back to `series/animation-exercises/` under the batch id; Emise issues the verdict from the returned table and spot-frames. The key and the done-definition are Emise's: the v2 verdict in QC-v2.md is the spec.
- **Batch 2.2 — variant stills for the intro keyframe surface (frames 5–8 of FERN-KEYFRAMES-MJ):** variant generations from Emise's keyframe prompts and the canonical reference, filed as drafts for her likeness check; only Emise-passed stills become keys for animation.

## Iteration 2 — Burn 3: test the Burn 2 doctrine (2026-11-21; evidence: scrolltown `series/animation-exercises/QC-v3.md`, frames in `qc3/`, batch returns in `batch-2.1/` + `batch-2.2/`, packets in `PACKETS.md`, commit `52cc3eaa` — first push rejected non-fast-forward as a parallel pass landed; rebased cleanly onto the new HEAD, force never used)

Five generations (the cap was six; the spare was not needed), two new key stills, and the first two artist-dispatch sweat batches. Every clip probed: durations honoured this burn (5 s asks → 5.00 s, 10 s asks → 10.00 s, all 24 fps); all clips silent.

**Hypotheses as briefed:** (1) ex03 v3 — motion restriction to one arm, no anticipation language, saves gesture AND anchors; (2) ex02 v3 — a ≤⅕-height key makes the push-in land somewhere good, judged on the end framing; (3) ex02-pendulum — easing/decay/spacing verified densely, face-free; (4) ex01-bouncing-ball v2 — wood-only + dense sampling settles decay and contact-squash; (5) two-keyframe probe — a named START + named END honours both endpoints better than single-still.

**Verdicts (frame evidence in QC-v3.md):**
- **ex03-fern-at-the-ready v3 — FAIL, and the hypothesis splits.** The gesture landed exactly (hammer up at mid, down at end; start pose = end pose; body/head/feet/left arm unmoved) and the camera never moved — motion restriction is CONFIRMED for gesture and camera. But the buns re-drew into curls by ≈1.25 s anyway, and an un-named closed-eye grin closed the clip. Identity fails ⇒ the rung fails.
- **ex02-keepers-welcome v3 — PARTIAL.** Total push-in from a ≈1/6-height key; register held in every sampled frame (no photoreal morph — Burn 1's failure stayed dead); the landing is a warm, on-model close-up — but a FOUND composition: the key's rolled scroll became an unrolled scroll covered in pseudo-writing. Judged on the end framing per doctrine: handsome, and not the designed composition; the micro-motion clause was consumed by the camera move.
- **ex02-pendulum — PARTIAL, the closest approach to a Pass yet.** Dense 0.5 s sampling: three arcs of visibly diminishing amplitude, near-vertical from t7.0 s, still at center for the final ~2.5 s; camera static in all 20 frames. Spacing-at-extremes UNVERIFIED: the brightness-centroid track was contaminated by lit background windows (false extremes) — the measurement failed, not the swing; silhouette tracking is the re-measurement (Iteration 3, no new generation).
- **ex01-bouncing-ball v2 — FAIL.** The three-prop key still betrayed the test: the generator animated a DUPLICATE token while the key's own token never moved, and the bounce re-launched to full height at t5.0–5.5 s after settling ≈t4.0 s. Decay refuted on dense evidence; contact-squash still unverified. The indicted vector is the key, not the generator.
- **Two-keyframe probe — PARTIAL.** Frame 0 is the START still exactly; the end delivers the END still's content (town lit, scroll open, anchors intact, lantern still raised) as a new drawing — tighter framing, invented closed-eye smiles. Start exact, end thematic: not yet pose-to-pose control.

**Sweat batches (artist-dispatch form; packets in `PACKETS.md`; work ran ranch-side, uptake = returned artifacts):**
- **Batch 2.1 → Velum (Scroll Central)** on ex01-ignition-v2 — RETURNED. Frames 000–059: phase-correlation offsets vs frame 000 — dx = 0 px on all 60 frames, |dy| ≤ 2 px; best-fit scale 1.00 → 1.04 by ≈frame 030. The Burn 2 "reframing" is a ≈4 % zoom, not a drift; the counter-crop conform is filed and is the originals to within 2 px, recorded as such. Frames 060–239: anchor verification ENUMERATED — Fern buns 180/180, scarf bow 180/180, key-badge 180/180, Waverly gold streak 180/180, plum coat 180/180 (blinks noted in the table are eyelid motion, not anchor loss).
- **Batch 2.2 → Alveus (Rock Mountain)** — RETURNED as DRAFTS. Variant stills for FERN-KEYFRAMES-MJ frames 5–8, all four passing Emise's likeness check at draft grade (verdicts in `batch-2.2/LIKENESS.md`; two staging notes: frame 5's river reads watery, frame 8's cart is parked, not rolling).

**Basis vectors indicted:**
1. *"Motion restriction saves identity"* — **refuted** (ex03 v3). It saves the gesture and the camera. Refined: **any motion of the character herself triggers the hair re-draw; anchors hold only when the character is fully still and the world moves around her** (enumerated proof: Batch 2.1).
2. *"Designing for the push-in means the landing is designed"* — **refuted** (ex02 v3). The landing is found, not designed; it needs its own QC, and its characteristic defect is invented props — text-bearing ones above all.
3. *"The two-keyframe route gives endpoint control"* — **refined** (probe). Start exact, end thematic. Not pose-to-pose until an end-frame-exact result exists.
4. *"A still of the test scene is a key for the test"* — **refuted** (bouncing-ball v2). A multi-prop still is not a single-object key; physics keys contain exactly the object under test.
5. *"Brightness-centroid tracking measures swing spacing"* — **refuted as a QC method** (pendulum track). Lit backgrounds contaminate it; spacing claims need silhouette/template tracking. A failed measurement is recorded as failed.
6. *"Requested duration is advisory"* — **weakened**: Burn 3 honoured all five duration asks exactly. Kept as advisory (one burn does not repeal the probe rule).

**Skill amendments made (Iteration 2):** §7 "Verified generator behaviour — Burn 3" (motion-restriction refinement + expression corollary; found-landing doctrine; the 4 % zoom measurement; two-keyframe start/end asymmetry; single-object key discipline; the brightness-tracking method note). §8 gained the **toll-gate clause verbatim** (Will, 2026-11-21 09:14 CST — see direction note below). §4 gained the **drawn-canon bullet** (Will, 2026-11-21 09:28 CST — see direction note below).

**Direction received during this iteration (recorded, not acted on beyond these notes — the Iteration 2 agenda stood as briefed):**
- **Toll gates set** (Will, 2026-11-21 09:14 CST): the Oracle Artist road is now gated by reproduction of the public-domain canon — Gate 1 is *Steamboat Willie* (1928), following gates enumerated in `~/workspace/custom-skills/animator/TOLL-GATES.md` (register built in parallel under task 14.5.8/7.5.7/5.5.7). The clause was added to skill §8 verbatim in this iteration's amendment pass. No gate reproduction was started in Iteration 2.
- **Art direction for the drawn canon** (Will, 2026-11-21 09:28 CST): toll-gate repros are hand-drawn; the baseline for Emise's drawing hand is the Emise font's line (flowing, sharp, witty — itself an evolution of Willbot, Will's handwriting); Will's recursively-tiling symbol — a mark he has carried 25+ years, hand-drawn by him — is a reference of record for the drawing style and the intro's tiling motif (received the same morning and filed unaltered at `series/style-references/wills-hand-sample-and-tiling-symbol.png` by the intro-docs pass; never to be invented, approximated, or redrawn by us); the intro's feel is the MCU flipbook — pages of hand-drawn repros flipping into the title — with Fern and Waverly featured. Distilled into skill §4 in this pass; the scrolltown intro docs are updated by a separate pass.

**Progress against the Oracle Artist bar (§8):** (i) ladder — ex01 attempted ×2 (v2 FAIL; decay + single-token clauses refuted on dense evidence, squash unverified), ex02-pendulum attempted (PARTIAL — one clause unverified), ex03 attempted ×3 as the gesture test (v3 FAIL on identity, gesture itself solved); ex04–ex06 untouched. **No Pass yet — the pendulum is one verified clause away.** (ii) clean burn — Burn 3: zero register breaks across five clips (second consecutive burn at zero). (iii) identity at length — UPGRADED: enumerated 180/180 on all five anchors for the near-static case (Batch 2.1), superseding Burn 2's sampled verdict; under character motion, identity still fails (ex03 v3). (iv) intro from passing shots — not yet (no Pass verdicts to assemble from). Toll gates: register set; Gate 1 not started.

**Iteration 3 agenda (recorded):**
1. **Gate 1 — *Steamboat Willie* (1928):** arc sketch first (low-fidelity reference points, the guiding light), then the artist-dispatch PREPASS of the full film as hand-drawn repros under the §4 drawn canon (Emise font line baseline; Will's tiling symbol as reference of record). A gate passes only on the full pipeline — prepass, then full render, frame-compared QC against the original, verdict in this log.
2. **ex02-pendulum spacing clause:** silhouette/template tracking re-measurement of the existing clip (ranch-side, no generation) to settle spacing-at-extremes — the rung's last unverified clause and the programme's nearest Pass.
3. **ex01-bouncing-ball v3:** dedicated single-object key still (wood token alone on a bare counter, generated and likeness-checked as a still first), dense sampling + silhouette contact tracking to settle decay and contact-squash.
4. **ex03 v4 — the gesture, structurally:** two-keyframe route with a TRUE end key of the same scene (hammer-raised end still generated as a still, on-model, likeness-checked before any video), testing whether end-frame exactness improves when the end key is a real key of the shot rather than another shot's frame.
5. **ex02 v4 — landing discipline:** design the start key FOR the measured zoom (character placed/sized so the expected push-in lands on the designed composition), with text-bearing props named out of the shot entirely.
