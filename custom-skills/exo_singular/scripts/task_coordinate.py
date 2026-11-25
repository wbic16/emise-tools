#!/usr/bin/env python3
"""Compute a task reference coordinate by holographic merge (Will's rule).

For every task Will submits, a reference coordinate captures the
essence of the request relative to his Singular dialect: tokenize the
request's exact words exactly as the Singular checker does, take the
distinct words, and merge their holographic positions into one
coordinate.

A word's position comes from atlas.tsv: CYOA-placed words carry the
average of the CYOA scrolls holding them; archive words with no CYOA
presence rest at home, 1.1.1/1.1.1/1.1.1 (stored in the atlas with
placement "home"). A word absent from the atlas is in neither the
archive lists nor CYOA, so it rests at the far corner,
9.9.9/9.9.9/9.9.9 — never stored, computed from absence.

The merge is the component-wise average of the distinct words'
9-component positions, each component rounded half up and never
below 1 — the same rounding the atlas builder uses
(build_atlas.py's round_half_up).

Usage:
    task_coordinate.py [--words] [TEXT ...]
    echo "some request text" | task_coordinate.py [--words]

Text is taken from the argument remainder, or from stdin when no
text arguments are given. Output is the coordinate on its own line,
then a coverage line (distinct words, placed-from-CYOA, at-home,
far-corner counts). With --words, each distinct word is also listed
with its position and placement class, in order of first appearance.

Exit code is 0 on success, 2 on a usage error (no text, or no words
in the text).
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))

from check_singular import WORD_RE  # noqa: E402  (the checker's tokenizer)

FAR = (9,) * 9
ATLAS = SKILL / "atlas.tsv"


def fmt(c):
    return (f"{c[0]}.{c[1]}.{c[2]}/{c[3]}.{c[4]}.{c[5]}"
            f"/{c[6]}.{c[7]}.{c[8]}")


def parse_coord(s):
    parts = s.replace("/", ".").split(".")
    return tuple(int(p) for p in parts)


def round_half_up(total, n):
    """Round total/n to the nearest whole step, half up, min 1."""
    return max(1, (2 * total + n) // (2 * n))


def load_atlas(path=ATLAS):
    """word -> (coordinate tuple, placement) from atlas.tsv."""
    atlas = {}
    with open(path, encoding="utf-8") as fh:
        header = fh.readline()
        if not header.startswith("word\t"):
            raise ValueError(f"unexpected atlas header in {path}: {header!r}")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 6:
                continue
            word, coord, _in_read, _in_authored, placement, _scrolls = parts
            atlas[word] = (parse_coord(coord), placement)
    return atlas


def main(argv):
    show_words = False
    text_parts = []
    for arg in argv:
        if arg == "--words":
            show_words = True
        else:
            text_parts.append(arg)
    if text_parts:
        text = " ".join(text_parts)
    else:
        text = sys.stdin.read()

    tokens = [w.lower() for w in WORD_RE.findall(text)]
    distinct = list(dict.fromkeys(tokens))
    if not distinct:
        print("no words in the request text", file=sys.stderr)
        return 2

    atlas = load_atlas()

    totals = [0] * 9
    n_cyoa = n_home = n_far = 0
    details = []
    for word in distinct:
        entry = atlas.get(word)
        if entry is None:
            coord, placement = FAR, "far"
            n_far += 1
        else:
            coord, placement = entry
            if placement == "cyoa":
                n_cyoa += 1
            else:
                n_home += 1
        for k in range(9):
            totals[k] += coord[k]
        details.append((word, coord, placement))

    n = len(distinct)
    merged = tuple(round_half_up(totals[k], n) for k in range(9))

    print(fmt(merged))
    print(f"coverage: distinct words {n}, placed-from-CYOA {n_cyoa}, "
          f"at-home {n_home}, far-corner {n_far}")
    if show_words:
        for word, coord, placement in details:
            print(f"{word}\t{fmt(coord)}\t{placement}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
