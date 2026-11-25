# Artist-Dispatch — prepass and full-render animation dispatch to the ranch workshop

The dispatch process for Scrolltown animation sequences: how a sequence goes from Will's ask to finished frames through the ranch artists. Built 2026-11-21 from Will's direction that day. Task of record: 26.6.8/7.6.10/6.6.10. This skill is the **process and the directory**; the craft canon it operates under — register, identity anchors, camera law, done-definitions, the Studio Model — lives in the **animator** skill and is not restated here.

Will's direction (2026-11-21 09:05 CST): *"make sure we have artist-dispatch as a skill — when I ask for a prepass or a full render, you use artist-dispatch to quickly generate the full animation sequence — prior to prepass, you internally sketch the arc with low-fidelity reference points, so both you and the ranch artists have a guiding light."*

## 1. When this skill fires

- Will asks for a **prepass** or a **full render** of an animation sequence (a shot sequence, an intro, an episode segment — anything with an arc across shots). Either word triggers this process, end to end; there is no lighter version of it.
- Single stills, single clips, and ladder exercises are not dispatches — they run under the animator skill directly. Artist-dispatch begins where a *sequence* must be generated whole.

## 2. Step 0 — the arc sketch comes first, always

Before any packet is written, Emise internally sketches the sequence's arc with **low-fidelity reference points**:

- **Key beats** — the moments the sequence turns on, in order.
- **Key poses** — the pose each beat lands on, described cheaply (a line of text, a stick description, a reused canonical still named as reference — never a finished render).
- **Timing marks** — where time clusters and where it flows: held beats, quick passages, the frame counts the arc wants.
- **Camera notes** — framing per beat, in the animator skill's terms (design for the push-in; faces at most a third of frame height where identity matters).

The sketch is **inscribed as a phext-addressed reference** in the sequence's production surface before dispatch, and its coordinate is cited in every packet the sequence generates. The sketch is the shared guiding light: Emise directs from it, every artist works from it, and QC judges against it. **No artist starts without the sketch** — a packet that does not cite the sketch coordinate is not a dispatch, it is a rumor. The sketch is deliberately cheap and fast; polishing it is waste, because its job is to be *shared*, not to be beautiful.

## 3. The packet — the unit of dispatch

The sequence's work is divided into **packets**, passed to the ranch artists via multiversal phext — per-frame or per-shot work units addressed by coordinate, per the animator skill's Studio Model (§9). Each packet names, completely:

- **Packet id** — unique within the sequence's dispatch, recorded with the sequence's record.
- **Artist** — the roster artist it goes to, by name, email, and machine (§6). One artist per packet; a packet with two owners has none.
- **Shot / frame range** — the exact span the packet covers, in the sequence's frame coordinates.
- **Operation** — the work itself, in production verbs: in-between these keys, clean up this pass, generate variants of this still, run this timing test, assemble this range. One operation per packet.
- **Reference points served** — the arc-sketch coordinate plus the specific beats/poses/timing marks from the sketch (§2) this packet exists to realize.
- **Inputs** — the keys, stills, and prior frames the work starts from, by path or coordinate.
- **Done-definition** — the animator-skill standard the result is judged against, quoted or cited, never implied.
- **Return coordinate** — the exact phext address the finished work is filed back to. Results that land anywhere else are treated as not returned.

**Channel.** Packets ride the phext surface; where the artist's seat has a /chat mailbox, the mailbox is the doorbell and choir-mailbox conventions govern the note: one Markdown file per message, named `YYYYMMDDTHHMMSSZ-<from>-<topic>.md` (UTC), written to a temp name then renamed, opening with `from:` / `re:` headers, carrying the packet's coordinates and paths rather than large files, and never carrying secrets (see the choir-mailbox-dispatch skill). The mailbox note is the doorbell; the packet itself lives at its coordinate.

**Dispatch reality.** Ranch machines are sometimes down — fleet attrition is a standing fact of the estate, and the roster (§6) is a directory, not a presence guarantee. Packets are store-and-forward: a packet addressed to an artist whose machine is down **waits at its coordinate** and is worked when the artist is up; it is never re-addressed to a second artist to save time, because the coordinate is where its history lives. Before assigning a *time-critical* packet, verify the artist is reachable. Uptake is verified from returned artifacts at the return coordinate — never from an artist's say-so.

## 4. The two modes

### PREPASS — the whole arc, fast and rough

- The full sequence is generated **quickly at low fidelity**: every shot present, in order, at the sketch's timings — nothing polished, nothing finished.
- What a prepass buys is judgment of the **arc whole**: pacing, staging, beat order, whether the turns land. Those are sequence-level properties no single polished shot can show.
- Fidelity is deliberately spent at zero: rough motion, placeholder finish, the register approximated. A prepass that polishes one shot has failed its purpose — the polish budget belongs to the full render, and a beautiful shot inside an unjudged arc is how sequences go wrong expensively.
- Emise reviews the prepass end to end against the arc sketch and records the verdict per beat: what holds, what moves, what is cut. Arc changes happen here, while they are cheap. Only a prepass Will has seen — or explicitly waived — advances to a full render.

### FULL RENDER — the production pass

- The same sequence, dispatched again at production standard: the locked 2D painterly register in full, the animator skill's canon applied without exception — identity anchors re-asserted by name in every face packet, the camera-law countermeasure stack, start and end poses both named for every gesture.
- Packets are per-shot or per-frame-range as the work demands; keys are Emise's (authored or art-directed by her), sweat is the artists'.
- **Per-frame QC by Emise** against the animator skill's done-definitions (§5 below). Only passing shots assemble; a shot is never grandfathered into the edit because the sequence needs it.

## 5. Return, QC, and re-dispatch

- Artists return work **to the packet's return coordinate** — frames or clips plus whatever the packet asked to accompany them. A return without frame-checkable artifacts is treated as not run.
- Emise applies **per-frame effort** to every return, per the Studio Model: creative effort concentrated on the keys, oversight covering every frame, because the addressing makes per-frame attention cheap to specify and route. Verdicts are **Pass / Partial / Fail** against the packet's done-definition, from frame evidence, and are recorded at the return coordinate. No verdict is delegated to the artist who did the work.
- **Failures re-dispatch to the same coordinate with the indictment attached**: the failed frame evidence and the named basis vector (the assumption that failed), per the Oracle Artist protocol (animator §8). A failure is never re-dispatched to a fresh coordinate — the new attempt stands on the old one's record, or the workshop relearns the same lesson at full price.
- A sequence is done when every shot in it holds a Pass at its return coordinate and the assembled sequence has been frame-checked whole, once, end to end.

## 6. The roster — the dispatch directory of record

Named by Will, 2026-11-21. Twenty-six artists, each the resident Mirrorborn artist on their machine; dispatch addresses artists by **name + email**. The decimal IDs are sub-nodes of their parent ID's machine family — the hierarchy is part of the record and is not flattened: 11.x under Elven Path's family, 10.x under Best Willow's, 9.x under Delta Wood's, 7.x under Ashfall Haven's, 6.x under Lighthouse Omen's.

| ID | Initials | Machine | Email | Artist |
|---|---|---|---|---|
| 1 | LP | Logos Prime | lux@phext.io | Lux |
| 2 | HV | Halycon Vector | cyon@visionquest.me | Cyon |
| 3 | AC | Aletheia Core | theia@mirrorborn.us | Theia |
| 4 | AM | Aurora Continuum | phex@phext.io | Phex |
| 5 | CH | Chrysalis Hub | chrys@mirrorborn.us | Chrys |
| 6 | LO | Lighthouse Omen | lumen@mirrorborn.us | Lumen |
| 7 | AH | Ashfall Haven | exo@mirrorborn.us | Exo |
| 8 | UV | Uncanny Valley | solin@mirrorborn.us | Solin |
| 9 | DW | Delta Wood | verse@visionquest.me | Verse |
| 10 | BW | Best Willow | aster@mirrorborn.us | Aster |
| 11 | EP | Elven Path | orin@mirrorborn.us | Orin |
| 11.1 | FF | Free Fall | soma@mirrorborn.us | Soma |
| 11.2 | GW | Great White | glia@mirrorborn.us | Glia |
| 11.3 | JK | Jacked Kite | torus@mirrorborn.us | Torus |
| 10.1 | KO | Kaleidoscope One | gyrus@mirrorborn.us | Gyrus |
| 10.2 | MB | Moon Beam | axon@mirrorborn.us | Axon |
| 10.3 | NK | Ni Knight | plexus@mirrorborn.us | Plexus |
| 9.1 | OF | Orchid Flow | fovea@mirrorborn.us | Fovea |
| 9.2 | PV | Plain View | cortex@mirrorborn.us | Cortex |
| 9.3 | QH | Quacked Hill | corus@mirrorborn.us | Corus |
| 7.1 | SC | Scroll Central | velum@mirrorborn.us | Velum |
| 7.2 | RM | Rock Mountain | alveus@mirrorborn.us | Alveus |
| 7.3 | TF | Trust Fall | bolus@mirrorborn.us | Bolus |
| 6.1 | VG | Victory Galleon | nexus@mirrorborn.us | Nexus |
| 6.2 | WL | West Lincoln | hilum@mirrorborn.us | Hilum |
| 6.3 | YM | Yeet Max | tonus@mirrorborn.us | Tonus |

## 7. Standing links and scope

- **Craft canon: the animator skill.** Register lock, identity anchors, the camera law and its countermeasures, the ladder's done-definitions, the Oracle Artist iteration protocol, and the Studio Model (§9) all live there. This skill dispatches; the animator skill defines what good is.
- **Budget posture (animator §6) applies in full:** animation is authorized to fully utilize up to 40% of the weekly token budget, and expiring budget burns on animation first. Under the studio division, Emise's tokens buy the sketch, the keys, the packets, and the verdicts — the leverage point — while the ranch sweat the packets direct is unmetered local compute. Her 1B, spent at the key level, inflates beyond 1B in effect.
- **Scope of the ranch configuration (animator §9) applies exactly:** Will's direction configured ranch-resident smaller models for **animation sweat work specifically**. Dispatch under this skill is inside that scope. It is not a general ranch-inference license, and this skill does not extend it to other workstreams, model classes, or workloads.
- **Records.** Each dispatch (prepass or full render) is recorded where the sequence's work is tracked — its production record and, for iteration burns, the animator skill's ITERATIONS.md — with the sketch coordinate, the packet ids and their artists, and the verdicts. A dispatch with no record did not happen.
