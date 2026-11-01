#!/usr/bin/env python3
"""Render up-goer-five.html from editor_template.html plus the atlas data.

Reads coordinates.json (UG5 words) and data/editor_vocab.json (frequent
non-UG5 words) and inlines both as JSON, so the page is one self-contained
file that works from file:// with no external assets.

Run after build_atlas.py:  python3 build_editor.py
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    coords = json.loads((HERE / "coordinates.json").read_text())
    ug5 = {w: v["coord"] for w, v in coords.items()}
    extra = json.loads((HERE / "data" / "editor_vocab.json").read_text())
    data = json.dumps({"ug5": ug5, "extra": extra}, separators=(",", ":"))
    template = (HERE / "editor_template.html").read_text(encoding="utf-8")
    if "%%DATA_JSON%%" not in template:
        raise SystemExit("template is missing the %%DATA_JSON%% placeholder")
    out = template.replace("%%DATA_JSON%%", data)
    target = HERE / "up-goer-five.html"
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target} ({len(out)} bytes, {len(ug5)} UG5 words, "
          f"{len(extra)} extra words)")


if __name__ == "__main__":
    main()
