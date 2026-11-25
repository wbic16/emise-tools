#!/usr/bin/env python3
"""Build favorites-source.json — Will Bickford's X likes, addressed.

Source of truth for favorites.phext (this skill). Reads the merged
corpus at ~/workspace/twitter-archive-2026-11-21/like.js (the union of
59,562 likes built by the 2026-11-22 fold-in) and computes, for every
like, a holographic phext coordinate FROM THE ENTRY ALONE:

    coordinate = TIME . WORDS . DOMAIN   (three triples, 9 components)

TIME (components 1-3) — when the liked tweet was POSTED. The export
carries no like timestamps and no author field; the posting time is
derived from the tweet's snowflake id:
    ms = (tweetId >> 22) + 1288834974657   (UTC)
    TIME = (year - 2005, month, day)
Validated against the corpus's own tweets (tweets.json, created_at
known): for every one of the 32,979 own tweets posted 2011 or later
the derivation lands within 1 second. Pre-snowflake ids (tweets posted
before Twitter's Nov 2010 snowflake switch) do NOT derive — sequential
ids land within hours of the snowflake epoch — so a like whose derived
date falls before 2010-11-06 is flagged "ambiguous" and its TIME
triple is the sentinel (1, 1, 1), "time unknown". A time axis built
from this register is an axis of the liked tweets' posting times,
never of when Will liked them.

WORDS (components 4-6) — the text's Singular word profile: the first
triple of the holographic merge of the text's distinct words, computed
with the house machinery (scripts/task_coordinate.py: atlas positions
from atlas.tsv, component-wise average, round half up, never below 1;
words in neither CYOA nor the archive rest at the far corner
9.9.9/9.9.9/9.9.9). Tokenization is build_wordlist.tokens (URLs and
@-mentions stripped, lowercased) — the same tokens the word lists are
built from. A like with no mergeable words (placeholder text, absent
text, or link/emoji-only text) takes the far-corner triple (9, 9, 9),
"no word profile"; the scroll itself records why.

DOMAIN (components 7-9) — the expandedUrl's fingerprint:
    c7 = 2 + (int(sha256(domain)[:8], 16) % 97)     (1 if no URL)
    c8 = distinct word count of the text, clamped to 1..999
         (1 when there are no words; the WORDS sentinel says why)
    c9 = 1 + (token count % 98), then the COLLISION RULE below.

COLLISIONS: coordinates are unique addresses. Entries are assigned in
ascending tweetId order (canonical, independent of export order); the
register home scroll 1.1.1/1.1.1/1.1.1 is occupied from the start. If
an entry's coordinate is taken, c9 is nudged upward by 1 until free —
the artifacts.phext rule — and the nudge is recorded in the entry's
"nudge" field, never applied silently. The build prints the raw
collision count (entries whose base coordinate was already taken).

TEXTLESS: a like whose fullText contains "{learnmore}" is export
boilerplate for a post X can no longer show (suspended / unavailable /
hidden) — 1,640 entries. A further 258 entries carry no fullText at
all. Both classes are flagged in the register, excluded from every
text analysis, and given no word profile.

Usage:
    build_favorites_source.py [ARCHIVE_DIR]
Default ARCHIVE_DIR: ~/workspace/twitter-archive-2026-11-21
Output: favorites-source.json next to this script.
"""

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_wordlist import tokens as singular_tokens  # noqa: E402
from task_coordinate import load_atlas, round_half_up, fmt  # noqa: E402

SNOW_EPOCH = 1288834974657
AMBIGUOUS_BEFORE = datetime(2010, 11, 6, tzinfo=timezone.utc)
HOME = (1, 1, 1, 1, 1, 1, 1, 1, 1)
NO_WORDS = (9, 9, 9)


def load_js_json(path: Path):
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw[raw.index("["):])


def snow_datetime(tweet_id: str) -> datetime:
    ms = (int(tweet_id) >> 22) + SNOW_EPOCH
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def domain_of(url: str) -> str:
    if not url:
        return ""
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def word_triple(distinct_words, atlas):
    """First triple of the holographic merge of the distinct words."""
    if not distinct_words:
        return NO_WORDS
    totals = [0] * 9
    for word in distinct_words:
        entry = atlas.get(word)
        coord = entry[0] if entry is not None else (9,) * 9
        for k in range(9):
            totals[k] += coord[k]
    n = len(distinct_words)
    merged = tuple(round_half_up(totals[k], n) for k in range(9))
    return merged[:3]


def validate_snowflake(archive: Path) -> dict:
    """Derive posting times for the corpus's own tweets and compare."""
    tweets = json.loads((archive / "tweets.json").read_text(encoding="utf-8"))
    fmt_in = "%a %b %d %H:%M:%S %z %Y"
    n_ok = n_bad = n_pre = 0
    max_diff = 0.0
    for item in tweets:
        t = item.get("tweet", item)
        created = datetime.strptime(t["created_at"], fmt_in)
        diff = abs((snow_datetime(t["id_str"]) - created).total_seconds())
        if created.year >= 2011:
            if diff <= 2:
                n_ok += 1
            else:
                n_bad += 1
            max_diff = max(max_diff, diff)
        else:
            n_pre += 1
    return {"own_tweets_2011_plus": n_ok + n_bad, "within_2s": n_ok,
            "beyond_2s": n_bad, "max_diff_s": max_diff,
            "own_tweets_pre_2011_not_derivable": n_pre}


def main() -> int:
    archive = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path.home() / "workspace/twitter-archive-2026-11-21"
    likes_path = archive / "like.js"
    if not likes_path.exists():
        print(f"no like.js at {likes_path}", file=sys.stderr)
        return 2

    validation = validate_snowflake(archive)
    print(f"snowflake validation: {validation['within_2s']}/"
          f"{validation['own_tweets_2011_plus']} own tweets (2011+) derive "
          f"within 2s (max diff {validation['max_diff_s']:.0f}s); "
          f"{validation['own_tweets_pre_2011_not_derivable']} pre-2011 own "
          f"tweets not derivable (sequential ids)")

    atlas = load_atlas()
    likes = load_js_json(likes_path)
    print(f"likes in corpus: {len(likes)}")

    records = []
    status_counts = Counter()
    for item in likes:
        like = item.get("like", item)
        tid = str(like["tweetId"])
        text = like.get("fullText")
        url = like.get("expandedUrl") or ""

        if text is None:
            status, words, toks = "absent", [], []
        elif "{learnmore}" in text:
            status, words, toks = "placeholder", [], []
        else:
            toks = singular_tokens(text)
            words = list(dict.fromkeys(toks))
            status = "text" if words else "wordless"

        posted = snow_datetime(tid)
        ambiguous = posted < AMBIGUOUS_BEFORE
        if ambiguous:
            time_triple, posted_iso = (1, 1, 1), None
        else:
            time_triple = (posted.year - 2005, posted.month, posted.day)
            posted_iso = posted.strftime("%Y-%m-%dT%H:%M:%SZ")

        dom = domain_of(url)
        if dom:
            c7 = 2 + (int(hashlib.sha256(dom.encode()).hexdigest()[:8], 16) % 97)
        else:
            c7 = 1
        c8 = max(1, min(len(words), 999))
        c9 = 1 + (len(toks) % 98)

        coord = time_triple + word_triple(words, atlas) + (c7, c8, c9)
        status_counts[status] += 1
        records.append({
            "tweetId": tid,
            "posted": posted_iso,
            "ambiguous": ambiguous,
            "status": status,
            "text": text,
            "url": url,
            "domain": dom,
            "distinctWords": len(words),
            "tokens": len(toks),
            "coordinate": fmt(coord),
            "nudge": 0,
        })

    # collision pass — canonical order, home occupied, nudge c9 upward
    records.sort(key=lambda r: int(r["tweetId"]))
    occupied = {HOME}
    raw_collisions = 0
    total_nudge = 0
    for rec in records:
        base = rec["coordinate"]
        if tuple(int(p) for part in base.split("/") for p in part.split(".")) in occupied:
            raw_collisions += 1
        coord = [int(p) for part in base.split("/") for p in part.split(".")]
        nudge = 0
        while tuple(coord) in occupied:
            coord[8] += 1
            nudge += 1
            assert coord[8] <= 999, f"scroll component overflow at {base}"
        occupied.add(tuple(coord))
        rec["coordinate"] = fmt(tuple(coord))
        rec["nudge"] = nudge
        total_nudge += nudge

    n_amb = sum(1 for r in records if r["ambiguous"])
    print(f"statuses: {dict(status_counts)}")
    print(f"ambiguous (pre-snowflake-transition) dates: {n_amb}")
    print(f"raw collisions: {raw_collisions}; total nudges applied: {total_nudge}")
    assert len(occupied) == len(records) + 1, "coordinate uniqueness failed"

    source = {
        "register": "favorites — Will Bickford's X likes, holographically addressed",
        "built_from": str(likes_path),
        "total": len(records),
        "statuses": dict(status_counts),
        "ambiguous_dates": n_amb,
        "raw_collisions": raw_collisions,
        "total_nudges": total_nudge,
        "snowflake_validation": validation,
        "records": records,
    }
    out = HERE / "favorites-source.json"
    out.write_text(json.dumps(source, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out}: {out.stat().st_size:,} bytes, {len(records)} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
