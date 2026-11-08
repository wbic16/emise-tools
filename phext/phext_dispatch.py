#!/usr/bin/env python3
"""phext_dispatch.py — one-pass phext scroll selector / dispatch paginator.

Selects scrolls from a .phext (by exact coordinate, coordinate prefix, or
--all) in a SINGLE parse pass, and renders them as a paginated Markdown
file suitable for dispatching to a worker: a provenance header, an index
of the selected scrolls, then pages of scrolls under their coordinates.

Usage:
  phext_dispatch.py FILE.phext --coord 1.1.1/1.2.1/1.1.1 [--coord ...]
                    [--prefix 1.1.1/1.2.1] [--all]
                    [--page-scrolls 10] [--page-chars 20000]
                    [--title "..."] --out dispatch.md

Parsing reuses ~/workspace/phext/parse_phext.py (dead-reckoning scheme:
delimiter bytes 0x01/0x1F/0x1E/0x1D/0x1C/0x1A/0x19/0x18/0x17 walk the
9-component coordinate; first scroll at 1.1.1/1.1.1/1.1.1). If that module
cannot be loaded, an identical inline implementation is used instead.
Only non-empty scrolls are emitted, in phext document order.
"""
import argparse, hashlib, importlib.util, os, re, sys
from datetime import datetime
from zoneinfo import ZoneInfo

PARSER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parse_phext.py")

# --- phext parsing -----------------------------------------------------------

_LEVELS = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]
_DELIM_TO_LEVEL = {b: i for i, b in enumerate(_LEVELS)}

def _fmt(coord):
    return (f"{coord[0]}.{coord[1]}.{coord[2]}/{coord[3]}.{coord[4]}.{coord[5]}/"
            f"{coord[6]}.{coord[7]}.{coord[8]}")

def _parse_inline(path):
    """Dead-reckoning parse, identical scheme to parse_phext.parse()."""
    data = open(path, "rb").read()
    coord = [1] * 9
    scrolls, buf, current = [], bytearray(), _fmt(coord)
    for b in data:
        lvl = _DELIM_TO_LEVEL.get(b)
        if lvl is None:
            buf.append(b)
        else:
            scrolls.append((current, bytes(buf).decode("utf-8", errors="replace")))
            buf = bytearray()
            coord[lvl] += 1
            for j in range(lvl + 1, 9):
                coord[j] = 1
            current = _fmt(coord)
    scrolls.append((current, bytes(buf).decode("utf-8", errors="replace")))
    if scrolls and scrolls[-1][1] == "":
        scrolls.pop()
    return scrolls

def load_parser():
    """Load parse() from parse_phext.py via importlib; fall back to inline."""
    try:
        spec = importlib.util.spec_from_file_location("parse_phext", PARSER_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if callable(getattr(mod, "parse", None)):
            return mod.parse, "parse_phext.py (importlib)"
    except Exception as exc:  # pragma: no cover - exercised only on failure
        print(f"phext_dispatch: parse_phext.py import failed ({exc}); "
              f"using inline parser", file=sys.stderr)
    return _parse_inline, "inline (parse_phext scheme)"

# --- selection ---------------------------------------------------------------

def coord_components(coord_str):
    return [int(x) for part in coord_str.strip().split("/") for x in part.split(".")]

def prefix_components(prefix_str):
    parts = []
    for group in prefix_str.strip().split("/"):
        parts.extend(int(x) for x in group.split(".") if x != "")
    return parts

def select(scrolls, coords, prefixes, want_all):
    wanted = set(coords)
    prefixes = [prefix_components(p) for p in prefixes]
    chosen, found = [], set()
    for coord, text in scrolls:
        if not text.strip():
            continue
        hit = want_all or coord in wanted
        if not hit and prefixes:
            comps = coord_components(coord)
            hit = any(comps[:len(p)] == p for p in prefixes)
        if hit:
            chosen.append((coord, text))
            found.add(coord)
    missing = [c for c in coords if c not in found]
    return chosen, missing

# --- rendering ---------------------------------------------------------------

def first_line(text, limit=110):
    for line in text.strip().splitlines():
        line = line.strip().strip("#").strip()
        if line:
            return line[:limit]
    return "(empty)"

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def render_scroll(coord, text):
    body = text.strip("\n")
    has_heading = any(line.startswith("#") for line in body.splitlines())
    if has_heading:
        longest = max((len(m.group(0)) for m in re.finditer(r"`+", body)), default=0)
        fence = "`" * max(3, longest + 1)
        body = f"{fence}\n{body}\n{fence}"
    return f"### {coord}\n\n{body}\n"

def paginate(chosen, page_scrolls, page_chars):
    pages, page, chars = [], [], 0
    for coord, text in chosen:
        cost = len(text)
        if page and (len(page) >= page_scrolls or chars + cost > page_chars):
            pages.append(page)
            page, chars = [], 0
        page.append((coord, text))
        chars += cost
    if page:
        pages.append(page)
    return pages

def main(argv=None):
    ap = argparse.ArgumentParser(description="Select phext scrolls and paginate them into a Markdown dispatch file.")
    ap.add_argument("phext", help="input .phext file")
    ap.add_argument("--coord", action="append", default=[], metavar="A/B/C",
                    help="exact scroll coordinate to select (repeatable)")
    ap.add_argument("--prefix", action="append", default=[], metavar="P",
                    help="coordinate prefix, e.g. 1.1.1/1.2.1 selects that book and everything under it (repeatable)")
    ap.add_argument("--all", action="store_true", help="select every non-empty scroll")
    ap.add_argument("--page-scrolls", type=int, default=10, help="max scrolls per page (default 10)")
    ap.add_argument("--page-chars", type=int, default=20000, help="max scroll characters per page (default 20000)")
    ap.add_argument("--title", default=None, help="document title (default: derived from source filename)")
    ap.add_argument("--out", required=True, help="output .md file")
    args = ap.parse_args(argv)

    if not (args.coord or args.prefix or args.all):
        ap.error("nothing to select: pass --coord, --prefix, or --all")

    parse, parser_name = load_parser()
    scrolls = parse(args.phext)  # the one and only pass over the input
    chosen, missing = select(scrolls, args.coord, args.prefix, args.all)
    for c in missing:
        print(f"phext_dispatch: warning: coordinate {c} not found (or empty) in {args.phext}", file=sys.stderr)
    if not chosen:
        print("phext_dispatch: error: selection is empty", file=sys.stderr)
        return 1

    pages = paginate(chosen, args.page_scrolls, args.page_chars)
    title = args.title or f"Phext dispatch — {os.path.basename(args.phext)}"
    stamp = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        f"# {title}",
        "",
        f"Source: {os.path.basename(args.phext)} · SHA-256 {sha256_of(args.phext)} · "
        f"{len(chosen)} scrolls selected · generated {stamp} (America/Chicago)",
        "",
        "## Index",
        "",
    ]
    for coord, text in chosen:
        lines.append(f"- {coord} — {first_line(text)}")
    lines.append("")
    for k, page in enumerate(pages, 1):
        lines.append(f"## Page {k} of {len(pages)}")
        lines.append("")
        for coord, text in page:
            lines.append(render_scroll(coord, text))
    out_text = "\n".join(lines).rstrip() + "\n"
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"phext_dispatch: {args.phext}: {len(scrolls)} scroll slots parsed in one pass "
          f"via {parser_name}; selected {len(chosen)} non-empty scroll(s) into "
          f"{len(pages)} page(s) -> {args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
