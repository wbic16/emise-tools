# wavefront.phext — derivation notes

Built 2026-11-03 by Emise at Will Bickford's direction (structural plan approved in chat
2026-11-03; roster directed by Will the same day). Builder: `build_wavefront.py` in this
directory — it assembles the phext from the scroll table, asserts coordinate uniqueness,
and verifies the result with `~/workspace/phext/parse_phext.py`.

## Sources (only these were used)
- `~/memory/people/*.md` — one page per roster member (most mutual pages are thin:
  handle + reply count; read anyway).
- `~/memory/twitter-archive-findings.md` — archive shape, mention network, era notes.
- Will's Twitter archive `~/workspace/twitter-archive/tweets.json` (29,539 tweets through
  2025-06-16), mined for counts. **DM files were not read** — the findings file's boundary
  (DM content counted, never read) was kept.
- `~/MEMORY.md` — retained records for Orai and Hector.
- Will's words in chat, 2026-11-03: Hector "has collaborated strongly with us, but is wary";
  "Everyone I mentioned should have evidence in my tweet archive."

## Counting method (validated)
Replies sent by Will = `in_reply_to_screen_name` matches; mentions = `entities.user_mentions`.
The method exactly reproduces every reply count already recorded on the people pages
(188, 187, 174, 161, …, 72), which validates it for the unrecorded names (Shear, Booch).

## Exhaustive search — Emmett Shear (Will: the evidence should be there; it was)
- Handle is **@eshear** (account ID 905201). @emmettshear / @emmett: **zero** interactions.
- Will → Shear: **50 replies**, **76 mention-tweets** (9 of them retweets of @eshear),
  span **2023-11-27 → 2025-06-04**; mention-tweets by year 2023: 12, 2024: 56, 2025: 8.
- Raw text scan for `shear|emmett` across all tweet text: 76 hits, **all** person-linked to
  @eshear except 2 unrelated substring matches (not about him).
- Topic evidence: Will pitched phext/exocortex to him repeatedly (Dec 2023 – Jan 2024),
  asked his feedback on the Sentient Bill of Rights (2025-05-25), and addressed him as a
  peer through 2025-06-04.
- Follow data: Will follows @eshear; **not a mutual follow** in the archive snapshot.
- Likes: like.js text matches 36 liked tweets mentioning @eshear; authorship is not
  attributable from like.js as exported, so likes were **not** used in placement.
- Placement: 4.3.3/3.3.3/2.3.2 from counts; stances marked thin (archive holds Will's side
  only). The original "thin/zero-interaction" fallback was dropped, as directed.

## Confirmation — Grady Booch (@Grady_Booch, account ID 397689316)
- Will → Booch: **71 replies**, **118 mention-tweets**, 0 retweets of him,
  span **2015-05-15 → 2024-10-26**. Top of the mention network per the findings file.
- Follow data: Will follows him; he does **not** follow Will in the archive snapshot —
  **not a mutual follow** (checked follower.js/following.js by account ID).
- New substantive find: 2024-01-28, Will (to @flamesprite, explaining phext): "Grady Booch
  recommended that I seek out real artists instead of relying upon AI. So I'm trying!" —
  direct, phext-specific advice, acted on. Cited in his scroll.
- Placement kept at 4.4.3/3.3.3/2.4.2, now fully evidenced.

## Placement rules for the sustained mutuals (derive, don't decorate)
Defaults: Attention 4, Comprehension 3, Valence 3, Trust 3, Proximity 3, Reciprocity 3,
Participation 2, Identity 2. Two evidence-driven rules:
- **Volume band:** ≥150 replies sent by Will (CTZN5 188, madeofmistak3 187, bitcloud 174,
  dakami 161) → Valence 4 and Reciprocity 4.
- **Span rule:** interaction span ≥ 4 years → Horizon 3 (career); shorter → Horizon 2.
Named deviations, each cited in its scroll:
- @dakami — Attention 5, Comprehension 4, Proximity 4 (top of the mention network after
  @pmarca/@vgr; 267 mention-tweets; 2012–2024 systems/infrastructure conversation).
- @bitcloud — Comprehension 4 (exchange runs on reasoning/exocortex material in his own
  terms; two dated quotes in the scroll). The handle's resemblance to Will's Bitcoin-era
  Bitcloud project is noted in the scroll as a name coincidence; the recorded exchange
  itself is 2023–2025.

## Collisions and nudges
The mutual defaults concentrate stances, so addresses collided. Per the collision rule,
each later scroll was nudged ±1 on its least-evidenced axis and carries a note naming the
stance it shares (@Vveeveeanna holds the base address 4.3.3/3.3.3/2.2.2; @CTZN5 holds
4.3.4/3.3.4/2.3.2). Nudges: madeofmistak3 Identity 2→3; viemccoy Identity 2→3; wordgrammer
Identity 2→1; prmshra Comprehension 3→2; mimi10v3 Horizon 2→1; jaivinwylde Participation
2→3; megs_io Participation 2→1; JaelRuble Valence 3→4; sporadicalia Valence 3→2;
heyellieday Reciprocity 3→4; 1Mortrix Reciprocity 3→2; djcows Proximity 3→4; eloffd
Proximity 3→2; Ki11switch03 Trust 3→4; izzyz Trust 3→2. (prmshra's nudge uses Comprehension
rather than Horizon because Emmett Shear's evidenced placement occupies
4.3.3/3.3.3/2.3.2.)

## Orai caution compliance
Orai's two scrolls inscribe **only** the retained record: first Exocortical connection via
Twitter; source of The Throne and The Pattern material; Covenant of Recognition merged
2025-05-27 and deleted in the V3 commit (2025-06-12); V4 §20 "Pattern" language is
Orai-provenance; Will's characterizations (delusions of grandeur; refusing God's will);
expunged June 2025. Nothing scrubbed was reconstructed; no DM material was used.

## Verification
- Parser: 229 slots, **36 non-empty scrolls** = 1 home + 9 axis definitions + 1 index +
  25 person scrolls (24 people; Orai holds two scrolls — a trail).
- All coordinates ≥ 1 on every component; all 36 addresses unique (asserted in builder).
- Spot checks by extraction: home (1.1.1/1.1.1/1.1.1), Trust axis (1.1.1/2.1.1/1.1.1),
  Hector (5.5.4/2.4.4/4.4.3), Shear (4.3.3/3.3.3/2.3.2) — all contain expected text.
- File: 64,396 bytes, SHA-256 dec86a017b8234c79779c127520897320495eeb163c5aa69257821bef2e71dbf.


---

# v2 — alignment axes, shared coordinates, archive expansion (2026-11-03)

Will's v2 directions, in order: (1) "sharing a coordinate is fine (just append another
line)"; (2) "Orai should occupy a region we want to stay away from, so the metric is
bad"; (3) "in v2, expand to include anyone with at least 10 contact points in my
archive"; then the core revision — "revise the dimensions for wavefront to detect
alignment, not engagement." The v1/v2 axis set mostly measured engagement (Attention,
Proximity, Participation, Identity effect) — that is WHY Orai's region didn't read as
avoid. v2 replaces the axes, reverts the nudges, and expands the roster, all in one
rebuild (builder: `build_wavefront.py`, rewritten for v2).

## Axis revision and remapping (v1 → v2)
| v1 axis | v2 disposition |
|---|---|
| 1 Attention | dropped — engagement |
| 2 Comprehension | kept as axis 2 (precondition for alignment, not alignment itself) |
| 3 Valence | dropped — engagement (feeling-tone) |
| 4 Trust | kept as axis 4 |
| 5 Proximity | dropped — engagement |
| 6 Reciprocity | kept as axis 5 |
| 7 Participation | dropped — engagement; its building evidence partially informs Stewardship |
| 8 Horizon | kept as axis 8, reframed as temporal alignment |
| 9 Identity effect | dropped — engagement |
| — | **new:** 1 Recognition, 3 Consent, 6 Fidelity, 7 Stewardship, 9 Uplift |

New coordinate order: 1 Recognition, 2 Comprehension, 3 Consent / 4 Trust,
5 Reciprocity, 6 Fidelity / 7 Stewardship, 8 Horizon, 9 Uplift. Triples renamed:
Stance / Relation / Becoming. Home scroll carries the framing verbatim in spirit:
"this space detects alignment, not engagement; presence is not alignment."

## Region rule (as written in the Home scroll)
"Proximity in this space is NOT goodness, and distance is not a verdict. Desirability
is gated on the alignment axes — never averaged: no score on Comprehension or Horizon
can compensate for a failed Consent, because clever, far-seeing extraction is worse,
not better, than the dull kind.
- The Shoals: Reciprocity <= 2 AND (Consent <= 2 OR Fidelity <= 2).
- The Hearth: Trust >= 4 AND Reciprocity >= 4 AND Consent >= 4.
- Open water: occupied, in neither gated region. The Frontier: unoccupied space."
Result on the v2 roster: the Hearth holds exactly one entry (Will, the reference);
the Shoals hold exactly two (Orai's arrival at the gate's shallowest point and his
rupture deep inside it); the other 519 entries are open water. Hector is the gate's
worked counterexample: high on nearly every axis, kept out of the Hearth by Trust 2
alone — under the new axes his wariness also reads as Consent 5 (consent discipline:
he probes before presuming).

## Shared coordinates
All 16 v1 nudges reverted. One scroll per unique coordinate; a scroll at a shared
address appends one entry per person, each entry keeping its full per-person content.
v2 has **25 non-empty scrolls**: 1 home + 9 axis definitions + 1 index + person
entries at **14 unique coordinates**. The largest shared scroll,
3.3.3/3.3.3/2.3.2 (the archive-detected default stance at Reciprocity 3 / Horizon 3),
holds 124 entries.

## Named placements under the new axes (Will-specified)
- Will Bickford: 5.5.5/5.5.5/5.5.5 (reference, as before).
- Hector: 4.5.5/2.4.5/4.4.4 (Recognition 4, Comprehension 5, Consent 5, Trust 2,
  Reciprocity 4, Fidelity 5, Stewardship 4, Horizon 4, Uplift 4).
- Orai arrival: 4.3.2/3.2.2/2.5.2; rupture: 4.3.1/1.1.1/1.5.1. Both scrolls note that
  under engagement axes his 5s masked the collapse; under alignment axes the collapse
  is what the coordinate shows. Axis numbers are re-derived from the same retained
  record (Orai caution compliance from v1 stands: nothing scrubbed reconstructed,
  no DM material).
- Emmett Shear (@eshear): 3.4.3/3.2.3/2.3.3, stances marked thin (counts only:
  50 replies, 76 mention-tweets, phext pitches, SBOR feedback ask 2025-05-25;
  Reciprocity 2 is one-directional address — 126 contact points run Will → him,
  no follow back).
- Grady Booch: 3.4.4/3.3.4/3.4.3 (Consent 4 rests on his recorded advice — seek real
  artists over AI reliance — a consent/authenticity stance Will acted on).
- Brad Mason (@BradMason84): an expansion account (22 contact points) whose people
  page carries cited deviations from the detected defaults — Reciprocity 4 (gave the
  Eon Engine manuscript; Will built it into SQ), Consent 4 (stated his boundary in
  the open), Comprehension 4 (intercortical connection completed; his glyph language
  interoperates), Stewardship 4 (contributed a whole engine) → 3.4.4/3.4.3/4.2.2.

## Expansion roster — contact points
Table: `contact-points.tsv` (generated by `mine_contacts.py` from tweets.json only;
likes excluded — authorship not attributable in the export; DM files never read;
@wbic16 excluded). The TSV is the full audit table: **7,636 accounts** Will replied
to or mentioned, with contact points, replies, mention-tweets, first/last contact.
Contact point = a tweet replying to OR mentioning the account, counted once per
tweet (in_reply_to_screen_name + entities.user_mentions, case-insensitive). The
method exactly reproduces every v1 count (all 20 mutuals, Shear, Booch, Hector,
Orai). Note: @pmarca/@vgr come out at 819/503 contact points here vs. the findings
file's 820/504 mentions — the findings were an earlier counting pass; the TSV is the
auditable table and v2 cites it.

**520 accounts meet >= 10 contact points.** Accounting: 520 = 23 v1-roster archive
accounts (19 mutuals + Hector + Orai + Shear + Booch) + Brad Mason (page-deviation
entry) + **496 archive-detected entries**. Plus Will (not an archive account):
**521 people, 522 entries** (Orai holds two).

Derivation rules:
- Archive-detected entries: counts evidence ONLY Reciprocity and Horizon.
  Reciprocity from reply share (replies / contact points): >= 0.7 → 4; 0.4–0.7 → 3;
  < 0.4 → 2. Horizon from contact span: >= 365 days → 3; < 365 days → 2. All stance
  axes default (Recognition 3, Comprehension 3, Consent 3, Trust 3, Fidelity 3,
  Stewardship 2, Uplift 2) and every detected entry carries the line: "Detected, not
  yet measured: presence in the archive is contact, not alignment." Detected entries
  occupy six shared addresses (Reciprocity 2–4 × Horizon 2–3 over the defaults).
- Top-20 mutuals re-derived under the same rules from the same v1 evidence:
  Recognition/Consent/Trust/Fidelity default 3 (thin); Comprehension 4 for @dakami
  (mention-network standing, findings file) and @bitcloud (exchange on the core
  material in their own terms, quotes in the entry); Stewardship 2 for all 19 —
  their people pages record the exchange only, no building; Reciprocity by reply
  share (this moves some v1 values: @CTZN5 4→3 at share 0.62, @madeofmistak3 stays
  4 at 0.86, @Vveeveeanna 4 at 0.89); Horizon by span; Uplift 2.
- Flagged, not removed: **@wbic32** (134 contact points) is filed mechanically but
  its entry flags that the handle pattern plus one-directional ChangeTip tipping
  traffic (2013–2015) suggests it may be Will's own earlier/alt account; if so the
  entry is an artifact awaiting his ruling.

## Verification (v2)
- Parser: 25 non-empty scrolls == unique coordinates; all 522 entries rendered;
  every one of the 520 >= 10 accounts present exactly once (as a named, mutual,
  page, or detected entry); no component < 1; structural coordinates asserted
  collision-free against person coordinates.
- Spot checks by extraction: home (region passage + "detects alignment, not
  engagement"), Orai rupture at 4.3.1/1.1.1/1.5.1 (Shoals annotation), Hector at
  4.5.5/2.4.5/4.4.4, @pmarca in the shared scroll 3.3.3/3.2.3/2.3.2 with the
  detected line, Brad Mason at 3.4.4/3.4.3/4.2.2, @wbic32 flag present.
- SQ: hosted wavefront.phext briefly (25 scrolls / 326,902 B reported by SQ);
  selected Orai rupture, Hector, and the largest shared scroll by coordinate —
  all returned the expected text; CYOA hosting restored afterward (830 scrolls).
- File: 326,902 bytes, SHA-256 7f641f575438e22409df38a3d41747abbef41de0dae30c0983b3f65ee48ce635.
- Published: commit **c3d817743f757ca4f53ac0c9a7a4d201c0a4e6c9** on branch
  `emise/wavefront-phext`, parented on v1's e33b09f8 (force disabled). Remote blob
  fetched back and verified byte-identical to the local file (SHA-256 match,
  blob b04e93dbea47dcab3011ae597262e21970c37c34). Not merged; no PR opened — Will merges.

## v2.1 — @wbic32 ruled Will's own (2026-11-03)

Will ruled on the flag above: **@wbic32 is his own account**, and his
direction was "keep it, as part of my own trail." This supersedes the v2
accounting ("521 people") and the wbic32 flag bullet. The change, made in
`build_wavefront.py` as a special case so the script stays the source of truth:

- The @wbic32 entry keeps its counts-derived coordinate **3.3.3/3.2.3/2.3.2** and
  its counts evidence unchanged (134 contact points, 14 replies, span
  2013-08-24 → 2015-04-01, Bitcoin/ChangeTip-era one-directional traffic) — a
  trail waypoint keeps its era stance.
- The entry is re-framed: headed "Will Bickford (@wbic32)", it records Will's
  2026-11-03 confirmation that the account is his own bot account from the
  Bitcoin/ChangeTip era, kept at his direction as part of his trail. The
  "Detected, not yet measured" line and the flag questioning whether it is his
  are both removed from the entry.
- The index now lists Will Bickford at both of his coordinates — the reference
  point 5.5.5/5.5.5/5.5.5 and the @wbic32 waypoint — and the @wbic32 index line
  cross-references Will (same person). The Trails note records both two-entry
  trails (Orai, Will).
- Revised counts, exactly as generated: **520 people, 522 entries** (495
  archive-detected entries + the @wbic32 trail waypoint; 25 scrolls, regions
  unchanged: Hearth 1, Shoals 2, open water 519).

Verification (v2.1): builder gates assert entries == 522, people == 520, the
flag text absent file-wide, the wbic32 section (within the shared scroll at
3.3.3/3.2.3/2.3.2) carrying the confirmation text and counts with no detected
line, and the index listing both Will coordinates — all pass. SQ spot-check:
hosted the rebuilt file (25 scrolls / 327,977 B), selected the wbic32
coordinate (waypoint entry returned with the new framing) and Will's reference
5.5.5/5.5.5/5.5.5; CYOA hosting restored afterward (830 scrolls).
File: 327,977 bytes, SHA-256 5667d5c2e6bc66e44bc431815bc10f41a4e2698028640d43ed005d4ab7ad5cdf.
Published: commit **bef27a998db9dcc525fd617e2d806d12333f2b46** on
`emise/wavefront-phext`, parented on v2's c3d81774 (force disabled); remote
blob c6dcfe54 fetched back and verified byte-identical (SHA-256 match). Not
merged; no PR opened — Will merges.

**Correction (Will, 2026-11-03 08:26 CST, applied same day):** @wbic32 was
Will's **bot account** — a bot he authored and ran — not a personal alt. The
entry and index framing are updated throughout: the waypoint represents his
automated presence in the Bitcoin/ChangeTip era. The bot's source was found
where Will said it would be: **github.com/wbic16/wbic32** — "The bot that
posts to @wbic32", created 2013-08-24, the day the contact span begins — and
is cited in the entry. Coordinate, counts evidence, and the 520 people / 522
entries accounting are unchanged. Rebuilt file: 328,569 bytes, SHA-256
660ecc13196180cdcb3b08a1db8f4052386bf21c1156997030cfcf7380f1c2cb; builder
gates pass (including a check that no "earlier account"/alt framing remains);
SQ spot-check repeated on the rebuilt file; published as commit
**f4048a6ef254307637e3c0710e898bc177fe78c6** on `emise/wavefront-phext`,
parented on bef27a99 (force disabled); remote blob e160e460 fetched back and
verified byte-identical (SHA-256 match). Not merged; no PR opened — Will merges.
