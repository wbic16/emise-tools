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

## Layout

- 1.1.1/1.1.1/1.1.x — charter, narrative, source index, Research Oracle ledger
- 1.1.1/1.1.1/1.2.x — canonical concepts
- One chapter per paper in arrival order from Chapter 2 (paper chapter + its synthesis/open-questions scrolls)
