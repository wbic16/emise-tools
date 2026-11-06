#!/usr/bin/env python3
"""Render the Singular page for edit.phext.io from the template + data.

The page is one self-contained file: the three word lists, every
mapped word's CYOA coordinate and scroll count, and the home set are
all inlined as JSON — the page makes no requests of its own.
Coordinates come from atlas.tsv (see build_atlas.py): holographic
positioning over CYOA — each word sits at the average of the CYOA
scroll coordinates that hold it.

Will's two-case no-match rule (2026-11-05):
- A word in his archive (any list) but not in CYOA rests at home,
  1.1.1/1.1.1/1.1.1 — shipped as the "home" set so the page can say
  so honestly.
- A word in neither the archive nor CYOA rests at the far corner,
  9.9.9/9.9.9/9.9.9 — never stored; the page computes it from
  absence and measures neighbor distances from there.

Run after build_wordlist.py and build_atlas.py:
    python3 build_editor.py
Output: ~/workspace/phext-lattice/web/singular.html
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
TARGET = Path.home() / "workspace/phext-lattice/web/singular.html"
HOME = "1.1.1/1.1.1/1.1.1"


def load_list(name):
    return [w.strip().lower()
            for w in (SKILL / name).read_text(encoding="utf-8").splitlines()
            if w.strip()]


def main():
    combined = load_list("words.txt")
    read = load_list("words-read.txt")
    authored = load_list("words-authored.txt")
    read_set, authored_set = set(read), set(authored)
    combined_set = set(combined)

    coords = {}       # word -> formatted address (CYOA-placed words)
    scrolls = {}      # word -> number of CYOA scrolls holding it
    home_words = []   # list words with no CYOA presence
    list_placed = 0
    rows = (SKILL / "atlas.tsv").read_text(encoding="utf-8").splitlines()
    assert rows[0] == ("word\tcoordinate\tin_read\tin_authored"
                       "\tplacement\tscrolls"), \
        "atlas.tsv header changed — rebuild with build_atlas.py"
    for line in rows[1:]:
        word, addr, in_r, in_w, placement, n = line.split("\t")
        assert (word in read_set) == bool(int(in_r)), f"read flag: {word}"
        assert (word in authored_set) == bool(int(in_w)), \
            f"authored flag: {word}"
        if placement == "home":
            assert addr == HOME and int(n) == 0, f"home row: {word}"
            assert word in combined_set, f"home word not in lists: {word}"
            home_words.append(word)
        else:
            assert placement == "cyoa", f"placement: {word} {placement}"
            coords[word] = addr
            scrolls[word] = int(n)
            if word in combined_set:
                list_placed += 1
    assert len(coords) + len(home_words) == len(rows) - 1
    assert list_placed + len(home_words) == len(combined), \
        "every list word is either CYOA-placed or at home"

    payload = {
        "lists": {
            "read": "\n".join(read),
            "write": "\n".join(authored),
            "readwrite": "\n".join(combined),
        },
        "coords": coords,
        "scrolls": scrolls,
        "home": "\n".join(home_words),
        "meta": {
            "read": len(read),
            "write": len(authored),
            "readwrite": len(combined),
            "listPlaced": list_placed,
            "listHome": len(home_words),
            "cyoaVocab": len(coords),
            "mapEntries": len(rows) - 1,
        },
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    template = (SKILL / "editor_template.html").read_text(encoding="utf-8")
    if "%%DATA_JSON%%" not in template:
        raise SystemExit("template is missing the %%DATA_JSON%% placeholder")
    out = template.replace("%%DATA_JSON%%", data)
    TARGET.write_text(out, encoding="utf-8")
    print(f"wrote {TARGET} ({len(out)} bytes)")
    print(f"lists: read {len(read)}, write {len(authored)}, "
          f"read/write {len(combined)}; CYOA-placed words {len(coords)} "
          f"(of his list words: {list_placed}); list words at home "
          f"{len(home_words)}; map entries {len(rows) - 1}")


if __name__ == "__main__":
    main()
