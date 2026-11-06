# Singular — One Person's Words

## What Singular is

- Up Goer Five holds you to the ten hundred words everyone uses most. Singular holds you to the words one person has in their archive — here, Will Bickford's Twitter archive, 2008–2025.
- Use this skill when Will asks for a Singular version of a text, asks to write using only his archive words, or asks whether a text stays inside them. Will's standing note (2026-11-05): Emise's own speech patterns stay within these words.

## The three lists, and the modes

- `words.txt` — the combined list, 41,302 words: every word in his tweets (his own posts and the retweets he passed on) and in the tweets he liked. This is the "~40k words found in my Twitter archive" of his note, and the default list.
- `words-authored.txt` — the authored list, 19,094 words: only the words in tweets he wrote himself.
- `words-read.txt` — the read list, 36,675 words: the words in what he passed on and kept — his retweets and the tweets he liked, without his own writing.
- The hosted page's modes are list picks (Will, 2026-11-05): **Read** flags against the read list (anything he RT'd or favorited), **Write** flags against the authored list (anything he wrote), **Read/Write** flags against the combined list. With the checker, pick a list with `--words`.
- Links and @-mentions are not in either list — they are addresses, not speech. Hashtag text is in, because he chose those words.
- Both lists hold the exact forms found, lowercased, contractions whole. Singular is strict: a changed form he never wrote is not on the list, and the checker flags it.

## Write and check

- Draft in his plain way: short lines, the words doing the work, no tower-of-complexity filler.
- Run the checker on every draft before showing it: `python3 ~/workspace/custom-skills/singular/scripts/check_singular.py <file>` or feed text on stdin.
- Rewrite each flagged word with a listed word, or go around it, then check again. `--suggest` prints close listed words as starting points.
- Names and new coinings of Will's own (phext, exocortex) are in the archive and pass. A word he never used — a name, a new thing — gets flagged honestly: keep it only if Will wants it, and say the text steps outside the list there.

## The map — holographic positioning

The hosted page (edit.phext.io/singular.html) is also a map of CYOA. Placement is **holographic positioning** (Will's rule, 2026-11-05): a word's place is not assigned from outside; it is read off the whole — every CYOA scroll that holds the word lends it that scroll's coordinate, and the word sits at the average of all its locations. Each location holds a piece of the word; the word's position holds all of its locations at once.

- The exact rule: one vote per valid CYOA scroll (a scroll carrying actual text) per distinct word in it, however many times the word occurs inside that scroll; the coordinate is the component-wise average of the voting scrolls' coordinates, each component rounded half up and never below 1. Tokenizing is the checker's. Source: the canonical CYOA from wbic16/human@exo, cached at `data/choose-your-own-adventure.phext` (the builder records its sha256 in `atlas.tsv.meta.json` on every build).
- The no-match rule has two cases (Will, 2026-11-05): a word found in his archive (any of the three lists) but not in CYOA rests at **1.1.1/1.1.1/1.1.1**, the home coordinate; a word found in neither rests at **9.9.9/9.9.9/9.9.9**, the far corner. The far case is never stored — the page computes it from absence (in no list, not in the CYOA map) and measures neighbor distances from 9.9.9/9.9.9/9.9.9 like from any other point.
- Current coverage: of the 41,302 list words, 10,525 are placed from CYOA and 30,777 rest at home; CYOA's vocabulary is 15,942 words; the map holds 46,719 entries (list words ∪ CYOA vocabulary). `phext` sits at 42.12.13/14.13.17/15.12.14, found in 132 scrolls.
- The page loads everything inline — the three lists, every mapped word's coordinate, and its CYOA scroll count are inlined as JSON by the generator; the page makes no requests of its own, and there are no separate word-list routes on the server. A word outside the chosen list shows its coordinate and the five nearest words inside the list, with Euclidean distances over the 9 components. Clicking any word opens the inspector: its coordinate, how many CYOA scrolls hold it (or which resting place it takes and why), which lists hold it, and its nearest in-list neighbors.
- The builder is `scripts/build_atlas.py`, which writes `atlas.tsv` (word, coordinate, in_read, in_authored, placement — `cyoa` or `home` — scrolls) plus the meta sidecar with the placement legend, including the far-corner case. The page generator is `scripts/build_editor.py` rendering `editor_template.html` to `~/workspace/phext-lattice/web/singular.html`.
- Note the divergence in one line: the sibling upgoer-five-phext atlas keeps its own GloVe embedding scheme — holographic positioning over CYOA is this map's rule, by Will's direction, not a change to that atlas.

## Task reference coordinates

- Standing practice (Will, 2026-11-06): every task Will submits gets a reference coordinate that captures the essence of the request relative to his Singular dialect. The coordinate is stated when the task is acknowledged, and it rides with the task in dispatch briefs and tracked records.
- Compute it with `scripts/task_coordinate.py`: `task_coordinate.py [--words] [TEXT ...]`, or feed the request text on stdin. It prints the coordinate, then a coverage line (distinct words, placed-from-CYOA, at-home, far-corner); `--words` also lists each word with its position and placement class.
- Merge rule: tokenize the request's exact words as the checker does, take the distinct words, and average their holographic positions component-wise, rounded half up and never below 1 — the same merge and rounding as the map above.
- Resting rules carry over from the map: a word's position is its atlas coordinate (archive words with no CYOA presence rest at home, 1.1.1/1.1.1/1.1.1); a word absent from the atlas rests at the far corner, 9.9.9/9.9.9/9.9.9, computed from absence and never stored. See "The map — holographic positioning" above for the full rule.

## Rebuild the lists

- `python3 ~/workspace/custom-skills/singular/scripts/build_wordlist.py [ARCHIVE_DIR]` rebuilds both lists and `counts.tsv` from a Twitter archive export (tweets.json + like.js). Default archive: `~/workspace/twitter-archive`.
- Counts on the current archive: 29,539 tweets (4,414 of them retweets), 47,973 liked tweets, 347,242 words in his own tweets alone.
- Direct messages are not in either list yet — the archive's message files hold both sides of each talk, and v1 keeps to the public record. Adding only his sent messages is a known next step, not a silent gap.

## Rebuild the map and page

- Flow: `build_wordlist.py` → `build_atlas.py` (reads the cached canonical CYOA in `data/`; refresh that copy from wbic16/human@exo when CYOA changes) → `build_editor.py` (writes `~/workspace/phext-lattice/web/singular.html`).
- The phext-lattice side ships on the `emise/singular` branch (PR #21) via the GitHub Git Data API, parented on the branch's fresh head, never forced. Merging and deploying are Will's steps.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.
