# favorites.phext — Will's X favorites, holographically addressed

Part of Singular. Where `words-authored.phext` keeps the words Will
wrote, `favorites.phext` keeps what he *kept*: every like in the merged
X corpus (59,562 entries, corpus `~/workspace/twitter-archive-2026-11-21/`),
one scroll per like, each at a coordinate computed from the like itself.

## Files

- `favorites-source.json` — the source of truth (edit this, never the .phext):
  every like's record — tweetId, derived posting time, status, text,
  expandedUrl, word counts, its coordinate, and its collision nudge.
- `build_favorites_source.py` — corpus → source. Reads `like.js` from the
  merged archive, validates the date derivation, computes coordinates,
  resolves collisions. Deterministic: same corpus in, same source out.
- `build_favorites_phext.py` — source → `favorites.phext`, through the
  reference phext implementation. `--check` prints CURRENT iff the .phext
  on disk is byte-identical to a fresh build from the source. Every build
  round-trips through the reference parser (scroll count + tweet-id set).

## The coordinate — TIME . WORDS . DOMAIN

Nine components in three triples, each in 1..999, computed **from the
entry alone** (plus the collision rule below, which is a function of the
register, applied in canonical order and recorded per entry).

**TIME (1–3) — when the liked tweet was posted.** The export carries no
like timestamps, so the posting time is derived from the tweet's
snowflake id: `ms = (tweetId >> 22) + 1288834974657` (UTC), then
`(year − 2005, month, day)`. Validation against the corpus's own tweets
(created_at known): all 32,979 own tweets posted 2011+ derive within 2 s
(max 1 s). Ids from before Twitter's Nov 2010 snowflake switch are
sequential and do not derive — a like whose derived date falls before
2010-11-06 (4 entries) is flagged `ambiguous`, its TIME triple is the
sentinel (1, 1, 1), and it is excluded from every time axis. **Every date
in this register is a posting time, never a liking time.**

**WORDS (4–6) — the text's Singular word profile.** The first triple of
the holographic merge of the text's distinct words, using the house
machinery (`scripts/task_coordinate.py`: atlas positions from
`atlas.tsv`, component-wise average, round half up, never below 1;
unplaced words rest at the far corner 9.9.9/9.9.9/9.9.9). Tokenization
is `build_wordlist.tokens` — the same tokens the word lists are built
from. A like with no mergeable words takes (9, 9, 9); the scroll records
why (placeholder / absent / wordless).

**DOMAIN (7–9) — the expandedUrl's fingerprint.**
`c7 = 2 + (int(sha256(domain)[:8], 16) % 97)` (1 if no URL);
`c8` = distinct word count (1..999; 1 when wordless);
`c9 = 1 + (token count % 98)`, before collisions.
In this corpus every expandedUrl is an in-platform `twitter.com` link,
so c7 is the constant 24 — the component carries no discriminating
information here and is kept because the scheme is defined over the
entry; a future export with external URLs would use it.

**Collisions.** Coordinates are unique addresses. Entries are assigned
in ascending tweetId order; the home scroll (1.1.1/1.1.1/1.1.1, the
register header) is occupied from the start. If an entry's coordinate is
taken, c9 nudges upward by 1 until free — the artifacts.phext rule — and
the nudge is stored in the entry's `nudge` field and printed on its
scroll. This corpus: 2,787 raw collisions, 12,758 total nudges, worst
single nudge 32; 95.3% of likes sit at their pure content address.

## Textless entries

- **placeholder** (1,640): fullText contains `{learnmore}` — X's
  boilerplate for a post that can no longer be shown (suspended,
  unavailable, hidden). The boilerplate is kept verbatim on the scroll,
  flagged; it is not the post's words and enters no text analysis.
- **absent** (258): the export carries no fullText at all.
- **wordless** (2,190): real text, but no words after tokenization
  (link-only or emoji-only posts). Kept in full; no word profile.
- **text** (55,474): the rest.

Total: 59,562 = 55,474 + 2,190 + 1,640 + 258.

## The word landscape, corrected (2026-11-22, EE 6)

The delivery of this register carried a word-landscape claim: that
95.5% of the words in the liked texts are words from Will's authored
vocabulary — framed as an *echo*, Will mostly liking what is written in
his own tongue. Will challenged it the same morning ("really? I just
like singular posts?"), a control check was run, and **the echo framing
is withdrawn**. The register's texts and coordinates were never in
question; the inference was.

**The control.** Direct messages from *other* senders in the merged
corpus (`direct-messages.js`, senderId ≠ Will's; 3,247 messages) —
everyday conversation, nothing curated — scored against the same
20,189-word authored list:

| corpus | tokenizer | tokens | covered | coverage |
|---|---|---|---|---|
| liked texts (55,474) | register's (`build_wordlist.tokens`) | 1,120,242 | 1,069,673 | 95.5% |
| others' DMs | register's | 68,014 | 64,831 | 95.3% |
| liked texts | alpha (`[a-z]+` on lowercase) | 1,283,816 | 1,187,985 | 92.5% |
| others' DMs | alpha | 71,134 | 67,542 | 95.0% |

(The main chat's quick recount — 92.1% over ~1.30M alpha tokens for the
likes, 94.8% over ~70K for the control — sits between the alpha rows
above; the spread is tokenization and inclusion choices, and every
variant tells the same story.) A 20,189-word authored vocabulary covers
roughly 92–95% of *any* ordinary English. The coverage number measured
the size of the vocabulary, not the character of the likes.

**What survives, with the control beside it** (alpha tokenization,
occurrences per 10,000 tokens, liked posts vs others' DMs):

| word | likes | DMs |
|---|---|---|
| agi | 4.23 | 1.69 |
| singularity | 1.76 | 0.28 |
| phext | 0.80 | 24.46 |
| exocortex | 1.01 | 6.75 |
| consciousness | 1.87 | 3.09 |
| llama | 0.52 | 0.98 |

The defensible claim: liked posts skew toward AGI/singularity themes
versus everyday conversation (~2.5× on *agi*, ~6× on *singularity*);
his coinages live in his inner-circle DMs, not his public likes.
Unaffected by the correction: the time findings (44% of liked posts
were posted in 2024; peak month October 2024) and the distinct-word
counts (39,631 distinct words in the liked texts, 15,441 of them
authored).

## What the data does not hold

No like-action timestamps. No author field — leading @handles in reply
texts are mentions, not authors, and are never presented as authors.
No external URLs: expandedUrl is uniformly `twitter.com/i/web/status/…`,
and the t.co shortlinks inside texts are unexpanded in the export.
