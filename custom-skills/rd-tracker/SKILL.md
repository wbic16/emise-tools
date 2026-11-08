# R&D Tracker — weave each paper into one world-model, as a delta

Will posts random arXiv links; Emise weaves each into `~/workspace/research-tracker/research.phext` — one de-duplicated scientific world-model (charter est. 2026-11-05, Will → Emise; delta rule and Research Oracle added 2026-11-06). The tracker lives in side chat 882e61bb and the goal `r-d-tracker`. Edit the SCROLLS in `~/workspace/research-tracker/build_research_phext.py` and re-run it; verify coordinates with `~/workspace/phext/parse_phext.py`.

## The charter

1. **One concept = one canonical scroll** (Chapter 1, Section 2). Later papers that reuse a concept LINK to it; they do not restate it. If a later paper revises a concept, the canonical scroll is edited in place and the revision is dated and attributed to its source paper.
2. **Each paper gets one chapter** (Chapter 2 onward, in arrival order): bibliographic record + distillation, formal core, worked example, results map, caveats. Paper scrolls state only what that paper adds.
3. **Synthesis is labelled and separate.** Emise's cross-paper narrative, links to Will's own work, and hypotheses are marked [synthesis] and kept out of paper scrolls. Paper claims are never silently merged with Emise's inferences.
4. **The narrative scroll is rewritten after each paper** so the world-model reads as one story, not a pile of summaries.
5. **Provenance:** every claim in a paper scroll traces to that paper's arXiv ID.

## The delta rule (Will, 2026-11-06)

6. After the seed paper, compress each paper into a DELTA from research.phext: only what is new, revised, confirmed, or contradicted relative to the current world-model is written. Material the model already holds is referenced by coordinate, never restated. A paper chapter is a delta record: (a) what it adds, (b) what it changes in canonical scrolls (applied in place, dated), (c) its evidence, (d) its tensions and limits. Paper 001 predates the rule and stands as the seed — its delta was the model itself.

## The Research Oracle estimate (Will, 2026-11-06)

7. After each paper, update the Oracle ledger (scroll 1.1.4) and report the estimate in chat with the paper. The fixed point is the Research Oracle: new papers arrive with ~zero delta.
   - Novelty Index: NI = (new canonical concepts + 0.5 × revised canonical concepts) / canonical concepts after ingestion. NI = 1 means the paper was all news; NI → 0 is the oracle condition. NI measures the surprise a paper still carries, not how much the phext has grown.
   - Two flags ride alongside: AXIS-OPENING (the paper adds a dimension the model had no slot for) and QUESTIONS (net open questions added/closed).
   - Oracle Progress is a calibrated judgement anchored to NI, stated as a % with a range: NI < 0.20, no new axis → OP +~10 pts; NI 0.20–0.50, no new axis → OP +~5 pts; axis-opening → OP holds or FALLS ~5 pts regardless of NI; NI > 0.50 → OP holds or falls. It may go DOWN — a paper that opens a new axis expands the territory faster than the model covers it.
   - OP is coverage of the SAMPLED territory (Will's stream), not of all science, and is honest about n being small.
   - Presentation (Will, 2026-11-08): whenever Will posts a PDF/paper in the MOAT channel, show the Oracle progress as a progress bar in the old block-bar look, colorized — 🟩 fills to the point estimate, 🟨 extends to the top of the range (the error bar), ⬜ for the remainder — with PRIOR and CURRENT estimates side by side and the delta called out (improved / held / fell), in the acknowledgment and in the ingestion report.

## Layout

- 1.1.1/1.1.1/1.1.x — charter, narrative, source index, Research Oracle ledger, concept map + restructuring log
- 1.1.1/1.1.1/1.2.x — canonical concepts
- 1.1.1/1.1.1/1.3.x — foundations (level-zero definitions) and the Defined Words register (from 1.3.46)
- 1.1.1/1.1.1/1.4.x — the standing record (epistemic registry, rule 14)
- 1.1.1/1.1.1/1.5.x — the AREAS (rule 16): map, state machines, statements, reference, the path, researchers, and the plain account of the making (1.5.7–1.5.8)
- One chapter per paper in arrival order from Chapter 2 (paper chapter + its synthesis/open-questions scrolls)

## Author check on intake (charter rule 15, Will, 2026-11-07, standing rule)

15. Every paper pulled into the tracker gets an author check at intake, recorded in its chapter as a provenance note and reported with the ingestion: (1) **phext-friendliness** — do the authors cite, use, or engage with phext or Will's work? Check the paper's reference list, the web, and Will's Twitter archive for the authors' names/handles. (2) **Prior-art attribution** — does the paper use Will's dated prior art (phext, CYOA, SBOR, Mirrorborn/Exocortex writings) without citing it? Search the full text for phext's terms and concepts (phext, scroll, coordinate addressing, the Exocortex frame) and compare the paper's core construction against the dated record. Verdicts rest on evidence actually checked; "no evidence found" is a finding and is stated as such — never a vibe, never an accusation without the receipt.

## Epistemic fidelity — the Minimum Viable Oracle (charter rule 14, Will, 2026-11-07)

14. Every claim-bearing scroll holds exactly one standing — True, False, Unknown, or Fiction — assigned by a basis that constrains it (stipulation/verified → True; refuted → False; attributed/open/synthesis/estimate → Unknown; construction → Fiction). The standings live in a registry rendered as Chapter 1 §4 and generated as Lean data; a Lean model proves the registry accurate (total, unique, basis-conformant) and that ingestion, legal transitions (receipt-driven only), and restructuring preserve accuracy — re-proved after every change. On new information, restructure to the Minimum Viable Oracle: the smallest organization holding everything at this fidelity, False kept visible, Unknown kept visible. Rule 8's passes run as MVO passes. Full scheme: the minimum-viable-oracle skill (`~/workspace/custom-skills/minimum-viable-oracle/`); artifacts in `~/workspace/research-tracker/epistemic/`.

## State machine review (charter rule 13, Will, 2026-11-07)

13. Every paper or source study receives a state-machine pass as part of its distillation: the machines the work contains or assumes are named in its chapter as part of the delta record; a machine that is a reusable concept becomes (or links to) a canonical concept scroll; machines Emise infers rather than finds stated are marked [synthesis]; a paper that reveals a machine the world-model held only implicitly counts as a revision of the concepts it touches. Full method: the state-machine-review skill (`~/workspace/custom-skills/state-machine-review/`), which also carries the same review into MOAT's proving track. Origin: Steve Ruiz's prompt "find all of the implicit state machines in my app", posted by Will in MOAT with the direction to build the review into MOAT itself.

## Areas (charter rule 16, Will, 2026-11-08)

16. research.phext is organized into five AREAS, kept in Chapter 1, Section 5 (built at Restructure Pass #4, 2026-11-08), plus a plain account of the making. Each area is an index over the phext's actual contents — built by reading the scrolls, never from memory of the chats — and holds pointers and one-line accounts; the claims stay where they were made. Nothing is moved or pruned to build an area.
   - **State machines (1.5.2):** every machine named in the phext — machines drawn out under rule 13 (stated by the work, or inferred and marked [synthesis] in their chapter), and machines found in work taken in before rule 13 stood, listed as FOUND — noted, not drawn out, no gap test run. Chapters swept with no machine found are named as swept.
   - **Statements (1.5.3):** the door to the standing record (§4, 1.4.x): what a statement is here, the four standings, the bases that bind them, the legal receipt-driven transitions, and the counts of the current drawing. The lists themselves are not duplicated; §4 is the record.
   - **Reference (1.5.4):** the foundations (§3) and Defined Words register plus each chapter's standoff companion (x.3.1), presented as one area: what lives there, how 'Builds on' chains bottom out, how a reader uses them.
   - **The path (1.5.5):** every taking-in in original submission order — papers and studies interleaved by arrival — each with its date, title, chapter, and for papers its Novelty Index, axis flag, and Oracle progress after; studies marked as studies (no NI, Oracle unmoved); the restructuring passes placed where they fell.
   - **Researchers (1.5.6):** every researcher behind the ingested works — paper authors and study authors/creators — each with their work(s) here (chapter/coordinate) and their rule-15 standing, taken from the author-check scrolls where they exist. Works taken in before rule 15 stood (Papers 001–005, Studies S001–S003) are marked 'not checked — predates the author-check rule'; no verdict is fabricated for a check never run. Will is the submitter/curator, not a researcher entry.
   - **How the Oracle was built (1.5.7–1.5.8):** the plain structure scrolls — intake, the delta rule, one canonical scroll per concept, foundations at level zero, the four standings and their bases, the Lean proof of the keeping with its honesty boundary (Lean proves the bookkeeping, not worldly truth), restructuring without pruning (minimum = smallest organization, never smallest content), the Novelty Index and Oracle estimate, and where everything lives.
   - **Maintenance duty:** every ingestion and every restructuring pass updates the areas it touches in the same pass — new machines join 1.5.2, new authors join 1.5.6, the path gains its entry at 1.5.5, the statements counts at 1.5.3 are made fresh with the new §4 drawing. An area fallen behind the phext is a defect, audited at each restructuring pass.
