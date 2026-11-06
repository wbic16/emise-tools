# Singular — One Person's Words

## What Singular is

- Up Goer Five holds you to the ten hundred words everyone uses most. Singular holds you to the words one person has in their archive — here, Will Bickford's Twitter archive, 2008–2025.
- Use this skill when Will asks for a Singular version of a text, asks to write using only his archive words, or asks whether a text stays inside them. Will's standing note (2026-11-05): Emise's own speech patterns stay within these words.

## The two lists

- `words.txt` — the archive list, 41,302 words: every word in his tweets (his own posts and the retweets he passed on) and in the tweets he liked. This is the "~40k words found in my Twitter archive" of his note, and the default list.
- `words-authored.txt` — the authored list, 19,094 words: only the words in tweets he wrote himself. The stricter list; pass `--words ~/workspace/custom-skills/singular/words-authored.txt` to the checker when "his speech" means only his own typing.
- Links and @-mentions are not in either list — they are addresses, not speech. Hashtag text is in, because he chose those words.
- Both lists hold the exact forms found, lowercased, contractions whole. Singular is strict: a changed form he never wrote is not on the list, and the checker flags it.

## Write and check

- Draft in his plain way: short lines, the words doing the work, no tower-of-complexity filler.
- Run the checker on every draft before showing it: `python3 ~/workspace/custom-skills/singular/scripts/check_singular.py <file>` or feed text on stdin.
- Rewrite each flagged word with a listed word, or go around it, then check again. `--suggest` prints close listed words as starting points.
- Names and new coinings of Will's own (phext, exocortex) are in the archive and pass. A word he never used — a name, a new thing — gets flagged honestly: keep it only if Will wants it, and say the text steps outside the list there.

## Rebuild the lists

- `python3 ~/workspace/custom-skills/singular/scripts/build_wordlist.py [ARCHIVE_DIR]` rebuilds both lists and `counts.tsv` from a Twitter archive export (tweets.json + like.js). Default archive: `~/workspace/twitter-archive`.
- Counts on the current archive: 29,539 tweets (4,414 of them retweets), 47,973 liked tweets, 347,242 words in his own tweets alone.
- Direct messages are not in either list yet — the archive's message files hold both sides of each talk, and v1 keeps to the public record. Adding only his sent messages is a known next step, not a silent gap.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.
