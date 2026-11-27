#!/usr/bin/env python3
"""Build policy/audits.phext from the scroll sources in policy/scrolls/.

The scroll sources are the editable record — one file per crate audit,
plus 00-home.md (the policy home scroll). The built phext is what
phext-dep-lint reads. Never edit audits.phext by hand; edit a scroll
source and rebuild.

    python3 tools/build_audits.py           # rebuild policy/audits.phext
    python3 tools/build_audits.py --check   # exit 1 if the built file drifts

Coordinate scheme (recorded in the home scroll):
  library.shelf.series / collection.volume.book / chapter.section.scroll
  = 1.1.1 / 1.<volume>.1 / 1.1.1
  volume 1 = home scroll; volumes 2.. = one audit scroll per crate,
  in sorted filename order.
"""
import os
import sys

LEVEL_BYTES = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCROLLS = os.path.join(ROOT, "policy", "scrolls")
OUT = os.path.join(ROOT, "policy", "audits.phext")


def implode(scrolls):
    """scrolls: dict coord-tuple -> text. Same state machine as the
    estate's build_skills_phext.py."""
    items = sorted(scrolls.items())
    out = bytearray()
    state = [1] * 9
    for target, text in items:
        for lvl in range(9):
            while state[lvl] < target[lvl]:
                out.append(LEVEL_BYTES[lvl])
                state[lvl] += 1
                for j in range(lvl + 1, 9):
                    state[j] = 1
        assert tuple(state) == tuple(target), (state, target)
        out += text.encode()
    return bytes(out)


def build():
    files = sorted(f for f in os.listdir(SCROLLS) if f.endswith(".md"))
    if not files or files[0] != "00-home.md":
        sys.exit("policy/scrolls must start with 00-home.md")
    scrolls = {}
    for i, fn in enumerate(files):
        volume = i + 1
        coord = (1, 1, 1, 1, volume, 1, 1, 1, 1)
        with open(os.path.join(SCROLLS, fn), "r", encoding="utf-8") as fh:
            scrolls[coord] = fh.read()
    return implode(scrolls)


def main():
    blob = build()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print("DRIFT: policy/audits.phext missing")
            return 1
        with open(OUT, "rb") as fh:
            current = fh.read()
        if current == blob:
            print("CURRENT: policy/audits.phext matches policy/scrolls/")
            return 0
        print("DRIFT: policy/audits.phext does not match policy/scrolls/")
        return 1
    with open(OUT, "wb") as fh:
        fh.write(blob)
    import hashlib

    print(f"wrote {OUT} ({len(blob)} bytes, sha256 {hashlib.sha256(blob).hexdigest()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
