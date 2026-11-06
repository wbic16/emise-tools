#!/usr/bin/env python3
"""Build the Singular word lists from one person's Twitter archive.

Singular is an Up Goer Five variant: instead of the ten hundred words
everyone uses most, the allowed list is the words found in one person's
archive. This builder reads a Twitter archive export and writes two
lists:

- words.txt — the ARCHIVE list: every word in the person's tweets
  (their own posts and the retweets they passed on) plus every word in
  the tweets they liked. For Will Bickford's archive this is 41,302
  words — the "~40k" of his note. It is the words his account holds:
  what he wrote, what he amplified, what he kept.
- words-authored.txt — the AUTHORED list: only the words in tweets he
  wrote himself (retweets skipped). 19,094 words. The stricter list,
  for when "his speech" means only his own typing.

Both lists: links and @-mentions are stripped first (addresses, not
speech); hashtag text is kept (chosen words); words are lowercased;
contractions stay whole ("don't"); every distinct form is kept as
found — Singular is strict, a form never written is not on the list.

Usage:
    build_wordlist.py [ARCHIVE_DIR]
Default ARCHIVE_DIR: ~/workspace/twitter-archive
Outputs land next to this script's parent folder: words.txt,
words-authored.txt, counts.tsv (archive counts).
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
WORD_RE = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.UNICODE)

HERE = Path(__file__).resolve().parent


def tokens(text: str):
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    return [w.lower() for w in WORD_RE.findall(text)]


def load_js_json(path: Path):
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw[raw.index("["):])


def main() -> int:
    archive = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "workspace/twitter-archive"
    tweets_path = archive / "tweets.json"
    if not tweets_path.exists():
        print(f"no tweets.json at {tweets_path}", file=sys.stderr)
        return 2

    archive_counts: Counter = Counter()
    authored_counts: Counter = Counter()

    tweets = json.loads(tweets_path.read_text(encoding="utf-8"))
    n_tweets = n_rt = 0
    for item in tweets:
        text = item.get("tweet", item).get("full_text") or ""
        n_tweets += 1
        archive_counts.update(tokens(text))
        if text.startswith("RT @"):
            n_rt += 1
        else:
            authored_counts.update(tokens(text))

    likes_path = archive / "like.js"
    n_likes = 0
    if likes_path.exists():
        for item in load_js_json(likes_path):
            archive_counts.update(tokens(item.get("like", {}).get("fullText") or ""))
            n_likes += 1

    out_dir = HERE.parent
    (out_dir / "words.txt").write_text("\n".join(sorted(archive_counts)) + "\n", encoding="utf-8")
    (out_dir / "words-authored.txt").write_text("\n".join(sorted(authored_counts)) + "\n", encoding="utf-8")
    with open(out_dir / "counts.tsv", "w", encoding="utf-8") as fh:
        for word, n in archive_counts.most_common():
            fh.write(f"{word}\t{n}\n")

    print(f"tweets: {n_tweets} (retweets among them: {n_rt}), liked tweets: {n_likes}")
    print(f"archive list: {len(archive_counts)} distinct words -> words.txt")
    print(f"authored list: {len(authored_counts)} distinct words -> words-authored.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
