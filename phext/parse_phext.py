#!/usr/bin/env python3
"""Dead-reckoning phext parser: walk raw bytes, count delimiters, map scrolls to coordinates.

Delimiter hierarchy (highest -> lowest), per phext.io / libphext:
  0x01 Library, 0x1F Shelf, 0x1E Series, 0x1D Collection, 0x1C Volume,
  0x1A Book, 0x19 Chapter, 0x18 Section, 0x17 Scroll
Hitting a delimiter increments that level and resets all lower levels to 1.
Coordinates are 1-indexed; the first scroll sits at 1.1.1/1.1.1/1.1.1.
"""
import json, sys

LEVELS = [
    ("library", 0x01), ("shelf", 0x1F), ("series", 0x1E),
    ("collection", 0x1D), ("volume", 0x1C), ("book", 0x1A),
    ("chapter", 0x19), ("section", 0x18), ("scroll", 0x17),
]
DELIM_TO_LEVEL = {byte: i for i, (_, byte) in enumerate(LEVELS)}

def fmt(coord):
    return f"{coord[0]}.{coord[1]}.{coord[2]}/{coord[3]}.{coord[4]}.{coord[5]}/{coord[6]}.{coord[7]}.{coord[8]}"

def parse(path):
    data = open(path, "rb").read()
    coord = [1] * 9
    scrolls = []  # (coord_str, text)
    buf = bytearray()
    current = fmt(coord)
    for b in data:
        lvl = DELIM_TO_LEVEL.get(b)
        if lvl is None:
            buf.append(b)
        else:
            scrolls.append((current, bytes(buf).decode("utf-8", errors="replace")))
            buf = bytearray()
            coord[lvl] += 1
            for j in range(lvl + 1, 9):
                coord[j] = 1
            current = fmt(coord)
    scrolls.append((current, bytes(buf).decode("utf-8", errors="replace")))
    # Drop a trailing empty scroll produced by a final delimiter, keep interior empties
    if scrolls and scrolls[-1][1] == "":
        scrolls.pop()
    return scrolls

def title_of(text):
    for line in text.strip().splitlines():
        line = line.strip().strip("#").strip()
        if line:
            return line[:110]
    return "(empty)"

if __name__ == "__main__":
    for path in sys.argv[1:]:
        scrolls = parse(path)
        nonempty = [(c, t) for c, t in scrolls if t.strip()]
        out = path.rsplit(".", 1)[0] + ".index.json"
        with open(out, "w") as f:
            json.dump([{"coordinate": c, "chars": len(t), "title": title_of(t)} for c, t in nonempty], f, indent=1)
        coords = [c for c, _ in nonempty]
        print(f"{path}: {len(scrolls)} scroll slots, {len(nonempty)} non-empty")
        print(f"  first: {coords[0]}  last: {coords[-1]}")
        print(f"  max coordinate reached: {max(coords, key=lambda c: [int(x) for part in c.split('/') for x in part.split('.')])}")
        for c, t in nonempty[:6]:
            print(f"  {c}: {title_of(t)}")
        with open(out) as f:
            pass
        print(f"  index written: {out}")
