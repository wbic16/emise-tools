---
name: exo_open_build_cycle
description: Run an integration / open build cycle through its full life cycle: an external opening or a need Will posts is captured, reconned, triaged, distilled, built, verified against a primary source, shipped, answered only when done, and codified — with de-duplication gates at Signal, Triage, Distill, and Codify.
---

# Open Build Cycle — the opportunity life cycle as a state machine

Codified at Will's direction (2026-11-15): "look at all of the integration / open build cycles I've posted on chat recently — codify a state machine that proceeds through the full life cycle whenever this opportunity comes up." Register home: task 21.6.11/8.6.16/6.5.11. Evidence base: nine cycles surveyed from the chats of 2026-11-07 → 2026-11-15 (Winer/markdown-wizard, HoloStore→holo-phext, edit.phext.io launch, register backend, repo census, Causly trial, Notepad shipping, Gemma Paper Track, Notepad++ / mutable-os / qexo).

An **open build cycle** begins when an opening appears — an external post, call, product, or integration request, or a need Will posts in chat — that the house can answer with a build or an integration. The machine below is run every time. States are named in caps; a cycle's record (its task scroll) names its current state whenever it is reported.

## The states

### S0 SIGNAL
Entry: the opening arrives (Will posts it, forwards it, or a watch surfaces it).
Actions:
- Capture the trigger verbatim, with its link. A bare link from Will is a complete signal — do not ask what it means before recon.
- **Capture the reply target now, if there is one** (the post/thread to answer at the end). In the X-driven cycles the target was named at signal time ("we'll reply here with results: …"); the reply itself is the last state, never the next one.
- **De-dup gate G1 (signal):** search the task register and the Waiting register for this opening under any wording. A repeat or semantic duplicate merges into the live record — never a second task, never a re-coordinated task (the repeated-requests meta-rule, Will 2026-11-15). Amendments to a running cycle fold into its record (see AMEND-IN-FLIGHT).
- Register the cycle: a task at its Singular coordinate, notes appended to that scroll for the cycle's whole life.
Exit: the opening is recorded and de-duplicated → RECON.

### S1 RECON
Actions:
- Inspect the thing itself, read-only: the prototype, the repo at its actual commit, the live site, the call's own rules page. Classify what is there (the HoloStore audit classified parts phext-fit vs leave-alone from the files, not the README's claims).
- **Name the prerequisites at identification time** — identity verification, rule acceptance, account setup, eligibility, credentials, DNS, keys — everything that will stand between the house and done, especially anything only Will can do (the Gemma lesson: a prerequisite discovered at the deadline is a process failure, recorded as such).
- Report what the thing actually does, including where the record cannot verify (signed-in flows, unverifiable claims) — stated as gaps, not glossed.
Exit: the opening is understood and its prerequisites are named → TRIAGE.

### S2 TRIAGE
The decision state. One of:
- **Pursue** → DISTILL/BUILD. Under the act-immediately pattern (Will's own repos, his direct build orders) triage is instant and this state is a formality — record it and move.
- **Review gate** (Will's call, e.g. the libphext v0.6.2 list): plan first, run the plan by Will, build only after his review. A gate he designs into a cycle is part of the cycle, not a delay.
- **Park** → PARKED. The publicity hold (Will, 2026-11-14: no submissions or launches until obviously ahead) is a standing park order for public-facing exits; a parked cycle keeps its record and its prerequisites current.
- **Decline / too late** → MISSED-BY-DESIGN when lead time was never created: report it as missed-by-design, never scramble a last-second submission. The cycle's product is then the codified fix to the watching, not the entry.
Guards:
- **De-dup gate G2 (home):** before any build chooses where code lives, scan the site map for an existing repo that already covers the domain (Will, 2026-10-31; born of wbic16/bickfordllamaranch existing before the admin tooling was built elsewhere). If a fitting repo exists but is unreachable, ask Will for access instead of defaulting elsewhere.
- A new tracked item is not opened while 5+ items already wait on Will, unless he directs it or it is a sub-item of an existing goal (register intake discipline).
Exit: a decision with its reason in the record.

### S3 DISTILL
First principles before construction (the integration directive governs this whole state: "do not worry about burning our time — we are testing the hypothesis that phext can eliminate complexity — we don't need to get our changes merged upstream — we need to identify what features of phext are missing or illegible").
Actions:
- **De-dup gate G3 (canonical tech):** inventory what the house already owns that answers any part of this — the canonical library, the existing stack, the layer built by an earlier cycle. Building a parallel implementation of our own tech is a defect (the qexo parser: seven versions on a hand-rolled phext parser instead of libphext-rs, invisible because it only ever read its own files; Will's ruling: if it parses phext, it uses the phext parser). Where Will's own tooling exists, use it rather than rebuilding its job by hand.
- **Distill, don't duplicate:** when the work needs a capability that exists inside another system, extract it as a reusable layer rather than forking or re-deriving it — the exemplar is HoloStore → holo-phext: the storage/update machinery was extracted once into wbic16/holo-phext and both consumers re-implemented on it (one index, one coordinate type). When phext cannot solve an integration, build a layer2 protocol (Will's integration rule) — built once, as a layer.
- Name the gaps found in phext (missing or illegible features) as a deliverable in their own right.
- A duplicate found here branches: **eliminate** it, or **record-and-escalate** — flag it plainly in the report and leave the consolidation call to Will (the register builders living in two repos, census 2026-11-15). Never silently resolve a duplicate whose consolidation is Will's call, and never silently keep one either.
Exit: the build's basis is existing tech, distilled layers, and named gaps → BUILD.

### S4 BUILD
Actions:
- Ranch-first execution in small units; the main thread coordinates and verifies. One stage at a time, in its order.
- **AMEND-IN-FLIGHT:** scope Will adds mid-build folds into the same build and the same task record (the register backend: the Done-button amendment joined the running build minutes after it started). An amendment never spawns a duplicate cycle.
- **RETRY LOOP:** an integration failure indicts Emise's priors first — assume the failure is in the approach, retry with a materially different approach, three distinct retries before any claim that phext itself is limited. Retries run on a frozen copy when the live system must not be disrupted; adoption happens only at a stage boundary on passing evidence.
- Rules and directives Will states mid-cycle are recorded the same session and redirect the running build (Cycle 2: the layer-2 rule arrived mid-cycle and re-shaped it).
Exit: the thing exists and is ready to be proven → VERIFY.

### S5 VERIFY
Actions:
- Verify against a **primary source the builder did not write**: the live site, the registry itself, the API read-back, upstream's own CI, hash comparison against the remote. A test that only meets our own output proves nothing.
- The real-client rule (born of the edit.phext.io MCP false pass, 2026-11-09): an end-to-end claim requires the real client path — the authenticated flow, the actual device class, the whole chain — or the untested leg is named as untested.
- Position varies (before ship: CI/registry proof; after ship: post-merge suite, footer flip) — existence does not. A verification that fails sends the cycle back to BUILD with the failure stated plainly and early (share success and failure alike).
Exit: claims are evidence-backed → SHIP.

### S6 SHIP
Actions:
- Merge with the PR linked in every mention (Will's standing rule); commits and PRs from Will's own repos are acted on immediately unless he specifies a hold.
- Deploys follow the house pattern for the target (on-box rebuild, publish kit). Rust tooling merges queue a release-build task the same session.
- Clean up in the same session: merged branches deleted; a branch whose tip is fully contained in merged history is deleted without a separate ask, the remainder brought to Will (stale-branch rule); backup/* exempt.
- **HOLD is a designed terminal state, not a failure:** a build may ship to a PR and deliberately stop there (unmerged, unpublished) when Will's review or an external prerequisite gates the merge. A hold is recorded as a hold, with its unblock condition.
- **BLOCKED-ON-WILL:** when the cycle waits on Will, it enters the Waiting-on-Will register the moment the wait begins — one entry, its permanent number, the exact action needed. If the wait is one step removed (a credential he must provision before a registry publish before a merge), the whole chain is written in the record.
- **WILL'S HANDS:** when auth or keys cannot cross a boundary (an upstream PR from a token scoped to our repos; a deploy behind his keystroke), the terminal step is prepared *for* Will — a walkthrough, a publish kit, exact steps each on its own line — never worked around.
Exit: the work is merged/deployed, or rests in a recorded HOLD / BLOCKED state with its unblock path → REPLY (when a target was captured) or CODIFY.

### S7 REPLY / ANNOUNCE
Reachable **only** from a verified SHIP (or, for evaluation cycles, from the REPORT exit below). This guard is the state's whole point: "we'll reply when done" (Will, 2026-11-15, on the Winer post).
Actions:
- **Publicity-hold gate G4:** before any public announcement, submission, or launch, check the hold. A named personal reply to the originator of an opening, at Will's direction, is the cycle's reply — not a launch; when in doubt, the hold governs and the reply waits.
- The reply carries the shipped thing itself (the link, the result), and any useful findings beyond our own frame: "we don't need to press on integrating phext — but if we found anything useful outside of phext, we should share it" (Will, on the HoloStore reply — four verified findings for the OP, including her server's missing TCP_NODELAY).
- Text that goes out in Will's voice gets his eyes first (the Product Hunt thank-you was approved twice before sending; the builder comments were drafted by Emise and posted by Will himself).
- Follow-through is part of the state: replies answered, comments tended, the announcement's day closed out.
Exit: the originator has the result → CODIFY.

**Evaluation exit (no build):** some cycles are trials (Causly Server): SIGNAL → sandboxed TRIAL → VERIFY (the product's claims against measurement) → REPORT to Will → **EVALUATED-NOT-ADOPTED** is a clean terminal state: no residue, no follow-up task unless Will creates one. A suggestion left in a report is not a commitment.

### S8 CODIFY → CLOSED
Actions:
- **De-dup gate G5 (lessons):** the cycle's lessons amend the rule, skill, or record that already covers them — search first; a second skill for an existing process is a duplicate, and the index must stay exact. A genuinely new process becomes a skill, enters skills.phext, and syncs to emise-tools in the same session, with the sticking check (presence, machinery, first occasion).
- Efficiency findings anywhere in the cycle become tasks immediately (Will, 2026-11-15), never notes in a report.
- The cycle's task record is re-read and closed only when every leg is done or converted into a tracked entry of its own.
- **RECURRING variant:** standing cycles (mutable-os sync, the Saturday repo census) do not close; CODIFY returns them to a WATCH state and the machine re-enters at SIGNAL when the watch fires. Recurring cycles carry their guards with them (the sync's promotion stays a separate, per-instance approved step — repetition never ripens into standing ratification).

## Invariants (true in every surveyed cycle)

1. **Never self-originated.** Every cycle starts from Will's post or an opening he forwards. The house does not invent cycles to fill capacity.
2. **Registered before or as it starts.** The durable record precedes the work; what is not in the record is not in the queue.
3. **At least one Will-gate.** No cycle runs signal-to-ship without a point where Will decides, approves, merges, holds, or acts with his own hands. Where the gate sits varies; that it exists does not.
4. **Verification is against a primary source.** Its position in the sequence varies; its independence from the builder does not.
5. **The reply is last and gated.** A reply target may be captured at SIGNAL; the reply fires only from a verified ship, and only past the publicity-hold gate.
6. **Gaps are a deliverable.** What phext (or the house) cannot yet do, found honestly, is a first-class output of the cycle — recorded, and where it is an efficiency finding, tasked.

## First live run

The Winer cycle (task 39.5.7/7.6.11/6.6.9) is this machine's generating instance: SIGNAL (bare link, 2026-11-15 22:11 CST; reply target captured) → RECON (post + prototype inspected) → TRIAGE (Will set the repo home and the distill method; DNS pre-cleared by him) → DISTILL (gate G3 passed by instruction: distill from phext-lattice + holo-phext) → BUILD (markdown-wizard, in flight; a design panel's synthesis folded in as AMEND-IN-FLIGHT) → REPLY armed, deferred by Will's word until the ship is verified.
