#!/usr/bin/env python3
"""Build favorites.phext — Will Bickford's X likes, holographically addressed.

One scroll per like, at the coordinate computed from the like itself
(scheme: build_favorites_source.py's docstring, and FAVORITES.md).
Source of truth: favorites-source.json (this skill). Edit the source,
never the .phext.

    build_favorites_phext.py           rebuild favorites.phext + verify
    build_favorites_phext.py --check   print CURRENT iff the .phext on
                                       disk is byte-identical to a fresh
                                       build from the source

All phext writing goes through the reference implementation
(PyPI `phext`, Will's Python port of libphext).
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace/tlm-proto/.venv/lib/python3.12/site-packages"))
from phext.phext import Phext
from phext.coordinate import Coordinate

HERE = Path(__file__).resolve().parent
HOME = Coordinate(1, 1, 1, 1, 1, 1, 1, 1, 1)


def parse_coord(s: str) -> Coordinate:
    nums = [int(p) for part in s.split("/") for p in part.split(".")]
    assert len(nums) == 9
    return Coordinate(*nums)


def scroll_for(rec: dict) -> str:
    lines = [f"tweet: {rec['tweetId']}"]
    if rec["posted"]:
        lines.append(f"posted: {rec['posted']} (derived from tweet id — snowflake)")
    else:
        lines.append("posted: unknown (pre-snowflake-transition id; date not derivable)")
    lines.append(f"status: {rec['status']}")
    lines.append(f"url: {rec['url']}")
    lines.append(f"domain: {rec['domain'] or '(none)'}")
    lines.append(f"words: {rec['distinctWords']} distinct / {rec['tokens']} tokens")
    if rec["nudge"]:
        lines.append(f"nudge: {rec['nudge']} (collision rule — see FAVORITES.md)")
    lines.append("text:")
    if rec["status"] == "absent":
        lines.append("[no text in export]")
    else:
        lines.append(rec["text"] or "")
    return "\n".join(lines)


def home_scroll(source: dict) -> str:
    v = source["snowflake_validation"]
    s = source["statuses"]
    return "\n".join([
        "favorites.phext — Will Bickford's X favorites, holographically addressed.",
        "Part of Singular: what he kept, placed by what it is.",
        "",
        f"likes: {source['total']} (one scroll each, plus this home scroll)",
        f"  with text: {s.get('text', 0)}",
        f"  wordless (link/emoji only): {s.get('wordless', 0)}",
        f"  placeholder (export boilerplate, post unviewable): {s.get('placeholder', 0)}",
        f"  absent (no text in export): {s.get('absent', 0)}",
        f"ambiguous dates (pre-snowflake-transition ids): {source['ambiguous_dates']}",
        f"raw coordinate collisions: {source['raw_collisions']}; "
        f"nudges applied: {source['total_nudges']} (recorded per scroll)",
        "",
        "Coordinates are computed from each entry alone — TIME (the liked",
        "tweet's posting time, derived from its snowflake id) . WORDS (the",
        "Singular holographic merge of its text) . DOMAIN (its expandedUrl",
        "fingerprint). Full scheme: FAVORITES.md; builder:",
        "build_favorites_source.py -> favorites-source.json -> this file.",
        "",
        "Honesty of the data: the export holds no like timestamps and no",
        "author field. Every date here is the liked tweet's POSTING time,",
        "never the moment of liking. Snowflake derivation validated on the",
        f"corpus's own tweets: {v['within_2s']}/{v['own_tweets_2011_plus']} "
        f"posted 2011+ derive within 2s (max {v['max_diff_s']:.0f}s).",
        "In this corpus every expandedUrl is an in-platform twitter.com",
        "link, so the DOMAIN fingerprint (component 7) is the constant 24",
        "for every entry; the scheme keeps it because it is defined over",
        "the entry, and a future export carrying external URLs would",
        "use it.",
        "",
        "Correction (2026-11-22, EE 6): this register's delivery carried a",
        "word-landscape claim — 95.5% of the words in liked texts come from",
        "Will's authored vocabulary, framed as an echo. A control refuted",
        "it: direct messages from other people score the same or higher",
        "against the same list (alpha tokenization — likes 92.5% of",
        "1,283,816 tokens; others' DMs 95.0% of 71,134). A 20,189-word",
        "vocabulary covers ~92-95% of ordinary English; the figure measured",
        "the vocabulary, not the likes. What survives the control is",
        "thematic (per 10k tokens, likes vs others' DMs): agi 4.23 vs",
        "1.69; singularity 1.76 vs 0.28; phext 0.80 vs 24.46; exocortex",
        "1.01 vs 6.75. The echo framing is withdrawn. Full record:",
        "FAVORITES.md, 'The word landscape, corrected'.",
    ])


def build_table(source: dict) -> dict:
    table = {HOME: home_scroll(source)}
    for rec in source["records"]:
        coord = parse_coord(rec["coordinate"])
        assert coord not in table, f"duplicate coordinate {rec['coordinate']}"
        table[coord] = scroll_for(rec)
    return dict(sorted(table.items(), key=lambda kv: kv[0].as_tuple()))


def render(source: dict) -> bytes:
    return Phext().implode(build_table(source)).encode("utf-8")


def main() -> int:
    check_only = "--check" in sys.argv
    source = json.loads((HERE / "favorites-source.json").read_text(encoding="utf-8"))
    buf = render(source)
    out = HERE / "favorites.phext"
    digest = hashlib.sha256(buf).hexdigest()
    if check_only:
        if out.exists() and hashlib.sha256(out.read_bytes()).hexdigest() == digest:
            print(f"CURRENT: favorites.phext matches favorites-source.json (sha256 {digest})")
            return 0
        print("STALE: favorites.phext differs from a fresh build of favorites-source.json")
        return 1
    out.write_bytes(buf)
    print(f"wrote {out}: {len(buf):,} bytes, sha256 {digest}")
    # round-trip through the reference parser: every scroll must come back
    back = Phext().explode(out.read_text(encoding="utf-8"))
    expect = source["total"] + 1
    assert len(back) == expect, f"round-trip scroll count {len(back)} != {expect}"
    ids = set()
    for coord, text in back.items():
        if coord == HOME:
            continue
        first = text.split("\n", 1)[0]
        assert first.startswith("tweet: "), f"scroll at {coord} lacks tweet line"
        ids.add(first[7:])
    assert len(ids) == source["total"], "round-trip tweet id set incomplete"
    print(f"round-trip via reference phext parser: OK ({len(back)} scrolls, "
          f"{len(ids)} unique tweet ids)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
