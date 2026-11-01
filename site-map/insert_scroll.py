#!/usr/bin/env python3
"""Insert a new scroll into a phext at an exact coordinate, without moving any
existing scroll. Works only when the target coordinate falls inside a
traversal gap (between two consecutive visited slots in stream order) and is
reachable from the preceding slot's coordinate by delimiter increments alone
(each delimiter increments one level and resets all lower levels to 1).
The byte that originally terminated the preceding slot is left in place and
becomes the new scroll's terminator; if that byte resynchronizes the counters
to the following slot's original coordinate (true when it is a break at or
above every level the insertion advanced), all downstream coordinates are
unchanged.

Usage: insert_scroll.py <in.phext> <out.phext> <coordinate> <text-file>
Refuses to write anything if the target is already visited or unreachable.
"""
import sys

LEVELS = [
    ("library", 0x01), ("shelf", 0x1F), ("series", 0x1E),
    ("collection", 0x1D), ("volume", 0x1C), ("book", 0x1A),
    ("chapter", 0x19), ("section", 0x18), ("scroll", 0x17),
]
DELIM_TO_LEVEL = {byte: i for i, (_, byte) in enumerate(LEVELS)}
DELIMS = {byte for _, byte in LEVELS}

def fmt(c):
    return f"{c[0]}.{c[1]}.{c[2]}/{c[3]}.{c[4]}.{c[5]}/{c[6]}.{c[7]}.{c[8]}"

def key_of(c):
    return tuple(c)

def parse_slots(data):
    """Return [(coord_tuple, text_start, text_end, terminator_byte_or_None)]."""
    coord = [1] * 9
    slots = []
    start = 0
    for i, b in enumerate(data):
        lvl = DELIM_TO_LEVEL.get(b)
        if lvl is not None:
            slots.append((tuple(coord), start, i, b))
            coord[lvl] += 1
            for j in range(lvl + 1, 9):
                coord[j] = 1
            start = i + 1
    slots.append((tuple(coord), start, len(data), None))
    # drop trailing empty slot left by a final delimiter
    if slots and slots[-1][1] == slots[-1][2]:
        slots.pop()
    return slots

def parse_target(s):
    parts = [int(x) for part in s.split("/") for x in part.split(".")]
    assert len(parts) == 9, "coordinate must have 9 components"
    return tuple(parts)

def main():
    src, dst, target_s, text_path = sys.argv[1:5]
    target = parse_target(target_s)
    text = open(text_path, "rb").read()
    bad = [b for b in text if b in DELIMS]
    assert not bad, f"scroll text contains phext delimiter bytes: {bad}"

    data = open(src, "rb").read()
    slots = parse_slots(data)
    coords = [s[0] for s in slots]
    assert len(set(coords)) == len(coords), "duplicate coordinates in source"
    assert all(coords[i] < coords[i + 1] for i in range(len(coords) - 1)), \
        "source coordinates are not strictly increasing in stream order"
    if target in coords:
        sys.exit(f"ABORT: target {target_s} is already a visited slot")

    # crossing: first visited slot greater than target; insertion happens at
    # the end of the previous slot's text (the offset of its terminator).
    cross = next(i for i, c in enumerate(coords) if c > target)
    prev_coord, _, prev_end, prev_term = slots[cross - 1]
    insert_at = prev_end

    # derive the delimiter run from prev_coord to target by increments only
    coord = list(prev_coord)
    run = bytearray()
    for lvl in range(9):
        while coord[lvl] < target[lvl]:
            run.append(LEVELS[lvl][1])
            coord[lvl] += 1
            for j in range(lvl + 1, 9):
                coord[j] = 1
    if tuple(coord) != target:
        sys.exit(f"ABORT: target unreachable by increments from {fmt(prev_coord)} "
                 f"(got {fmt(coord)})")

    # the original terminator of the previous slot must, applied to the
    # target, reproduce the following slot's coordinate exactly
    lvl = DELIM_TO_LEVEL[prev_term]
    after = list(target)
    after[lvl] += 1
    for j in range(lvl + 1, 9):
        after[j] = 1
    if tuple(after) != coords[cross]:
        sys.exit(f"ABORT: resync fails: terminator {prev_term:#x} after target "
                 f"gives {fmt(after)}, next slot is {fmt(coords[cross])}")

    out = data[:insert_at] + bytes(run) + text + data[insert_at:]
    open(dst, "wb").write(out)
    print(f"inserted {len(run)} delimiter bytes + {len(text)} text bytes "
          f"at offset {insert_at} (before original terminator {prev_term:#x})")
    print(f"previous slot: {fmt(prev_coord)}  target: {target_s}  "
          f"next slot: {fmt(coords[cross])}")
    print(f"file size: {len(data)} -> {len(out)} (+{len(out) - len(data)})")

if __name__ == "__main__":
    main()
