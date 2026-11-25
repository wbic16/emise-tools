#!/usr/bin/env python3
"""Place every Singular word by holographic positioning (Will's rule).

A word's place is not assigned from outside; it is read off the whole.
Every CYOA scroll that holds the word lends it that scroll's
coordinate, and the word sits at the average of all its locations.
Each location holds a piece of the word; the word's position holds all
of its locations at once. This is the first tier of the map: CYOA
places the words it holds, and any word with no CYOA presence rests
at the home coordinate, 1.1.1/1.1.1/1.1.1 (Will's origin ruling,
2026-11-05).

The no-match rule has two cases (Will, 2026-11-05):
- In the archive (any of the three lists) but not in CYOA -> home,
  1.1.1/1.1.1/1.1.1. Stored here with placement "home".
- In neither the archive nor CYOA -> the far corner,
  9.9.9/9.9.9/9.9.9. Such a word never appears in this file at all;
  absence from atlas.tsv IS the far-corner record. The page computes
  it at runtime from that absence and measures neighbor distances
  from 9.9.9/9.9.9/9.9.9 like from any other point.

The exact rule (Will, 2026-11-05):
- Source: CYOA, canonical from wbic16/human@exo (a cached copy lives
  at data/choose-your-own-adventure.phext; its sha256 is recorded in
  atlas.tsv.meta.json on every build). Parsed with
  ~/workspace/phext/parse_phext.py. A valid scroll is a scroll
  carrying actual text.
- For each valid scroll at coordinate C, every distinct word in its
  text gets one vote for C — one vote per scroll, however many times
  the word occurs inside that scroll. Tokenizing is the checker's:
  letter runs with internal apostrophes, lowercased
  (check_singular.py's WORD_RE).
- A word's coordinate is the component-wise average of its scroll
  coordinates, each component rounded to the nearest whole step,
  half up, and never below 1.

Output: atlas.tsv next to the word lists, one row per word in the
union of the three lists and the whole CYOA vocabulary:
    word <TAB> coordinate <TAB> in_read <TAB> in_authored <TAB>
    placement <TAB> scrolls
where placement is "cyoa" (averaged from its scrolls) or "home"
(1.1.1/1.1.1/1.1.1). Plus atlas.tsv.meta.json with the source,
counts, and the placement legend including the far-corner case.

Usage:
    build_atlas.py [--cyoa PATH]   build atlas.tsv, print coverage
    build_atlas.py --address W...  address ad-hoc words by the same
                                   rule (prints word, coordinate,
                                   placement, scroll count; a word in
                                   neither the archive nor CYOA prints
                                   the far corner, placement "far")
"""

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(Path.home() / "workspace/phext"))
sys.path.insert(0, str(HERE))

import parse_phext  # noqa: E402  (Will's dead-reckoning parser)
from check_singular import WORD_RE  # noqa: E402  (the checker's tokenizer)

ORIGIN = (1, 1, 1, 1, 1, 1, 1, 1, 1)
DEFAULT_CYOA = SKILL / "data" / "choose-your-own-adventure.phext"


def fmt(c):
    return (f"{c[0]}.{c[1]}.{c[2]}/{c[3]}.{c[4]}.{c[5]}"
            f"/{c[6]}.{c[7]}.{c[8]}")


def parse_coord(s):
    parts = s.replace("/", ".").split(".")
    return tuple(int(p) for p in parts)


def round_half_up(total, n):
    """Round total/n to the nearest whole step, half up, min 1."""
    return max(1, (2 * total + n) // (2 * n))


def load_list(name):
    return [w.strip().lower()
            for w in (SKILL / name).read_text(encoding="utf-8").splitlines()
            if w.strip()]


def cyoa_votes(cyoa_path):
    """word -> (component sums, scroll count), from valid CYOA scrolls."""
    scrolls = parse_phext.parse(str(cyoa_path))
    valid = [(c, t) for c, t in scrolls if t.strip()]
    sums = defaultdict(lambda: [0] * 9)
    counts = defaultdict(int)
    for coord_str, text in valid:
        coord = parse_coord(coord_str)
        for word in {w.lower() for w in WORD_RE.findall(text)}:
            counts[word] += 1
            acc = sums[word]
            for k in range(9):
                acc[k] += coord[k]
    return sums, counts, len(scrolls), len(valid)


def place(sums, counts, word):
    """(coordinate tuple, placement, scroll count) for one word.

    Placement is "cyoa" when at least one CYOA scroll holds the word,
    else "home" (the word rests at 1.1.1/1.1.1/1.1.1). Words in
    neither the archive nor CYOA get no call here and no row: the
    page rests them at the far corner, 9.9.9/9.9.9/9.9.9.
    """
    n = counts.get(word, 0)
    if n == 0:
        return ORIGIN, "home", 0
    acc = sums[word]
    return tuple(round_half_up(acc[k], n) for k in range(9)), "cyoa", n


def main():
    args = sys.argv[1:]
    cyoa_path = DEFAULT_CYOA
    if "--cyoa" in args:
        i = args.index("--cyoa")
        cyoa_path = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    if not cyoa_path.exists():
        print(f"CYOA not found at {cyoa_path}", file=sys.stderr)
        return 2

    sums, counts, n_slots, n_valid = cyoa_votes(cyoa_path)

    if args and args[0] == "--address":
        combined_set = set(load_list("words.txt"))
        for w in args[1:]:
            wl = w.lower()
            coord, placement, n = place(sums, counts, wl)
            if placement == "home" and wl not in combined_set:
                # In neither the archive nor CYOA: the far corner.
                coord, placement = (9,) * 9, "far"
            print(f"{w}\t{fmt(coord)}\t{placement}\t{n}")
        return 0

    combined = load_list("words.txt")
    read_set = set(load_list("words-read.txt"))
    authored_set = set(load_list("words-authored.txt"))
    vocab = set(counts)
    words = combined + sorted(vocab - set(combined))

    combined_set = set(combined)
    rows = []
    list_placed = list_home = 0
    for w in words:
        coord, placement, n = place(sums, counts, w)
        in_r, in_w = w in read_set, w in authored_set
        if w in combined_set:
            if placement == "home":
                list_home += 1
            else:
                list_placed += 1
        rows.append((w, fmt(coord), int(in_r), int(in_w), placement, n))

    out = SKILL / "atlas.tsv"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("word\tcoordinate\tin_read\tin_authored\tplacement\tscrolls\n")
        for w, addr, r, a, p, n in rows:
            fh.write(f"{w}\t{addr}\t{r}\t{a}\t{p}\t{n}\n")

    raw = cyoa_path.read_bytes()
    meta = {
        "source": "CYOA from wbic16/human@exo (cached copy), "
                  f"file {cyoa_path}",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "scroll_slots": n_slots,
        "valid_scrolls": n_valid,
        "cyoa_vocabulary": len(vocab),
        "list_words": len(combined),
        "list_words_cyoa_placed": list_placed,
        "list_words_at_home": list_home,
        "map_entries": len(rows),
        "rule": "holographic positioning: one vote per valid CYOA "
                "scroll holding the word; coordinate = component-wise "
                "average, rounded half up, min 1",
        "placement_legend": {
            "cyoa": "averaged from the CYOA scrolls holding the word",
            "home": "1.1.1/1.1.1/1.1.1 — in the archive, not in CYOA",
            "far": "9.9.9/9.9.9/9.9.9 — in neither the archive nor "
                   "CYOA; no row is stored, absence from atlas.tsv "
                   "is the record, and the page rests such words at "
                   "the far corner at runtime",
        },
    }
    (SKILL / "atlas.tsv.meta.json").write_text(json.dumps(meta, indent=1))

    print(f"CYOA: {cyoa_path}")
    print(f"  sha256 {meta['sha256']}")
    print(f"  {n_slots} scroll slots, {n_valid} valid (text-carrying)")
    print(f"  CYOA vocabulary: {len(vocab)} words")
    print(f"list words: {len(combined)}")
    print(f"  placed from CYOA: {list_placed}")
    print(f"  resting at home (1.1.1/1.1.1/1.1.1): {list_home}")
    print(f"map entries total: {len(rows)}")
    for probe in ("phext", "exocortex"):
        coord, placement, n = place(sums, counts, probe)
        print(f"  {probe}: {fmt(coord)} (placement={placement}, scrolls={n})")
    print(f"wrote {out} and atlas.tsv.meta.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
