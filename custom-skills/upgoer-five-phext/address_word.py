#!/usr/bin/env python3
"""Address words in the UG5 phext atlas, decode coordinates, validate text.

Every word, UG5 or not, has one natural 9D phext address: its GloVe
embedding projected onto the atlas's nine principal components and
quantized (see SCHEME.md).

Usage:
  python3 address_word.py WORD [WORD ...]
      Print each word's natural address. UG5 words also print their
      nearest UG5 neighbors in address space. Words with no GloVe route
      are reported as unembeddable and never silently placed.
  python3 address_word.py --decode a.b.c/d.e.f/g.h.i
      Print the inscribed (UG5) words nearest to the coordinate.
  python3 address_word.py --validate FILE
      Flag the non-UG5 words in a text (same word-form rules as the
      sibling upgoer-five checker) and suggest the nearest UG5 words by
      address distance for each one. Use --validate - for stdin.

Requires coordinates.json and data/model.json from build_atlas.py, plus
the GloVe file cached in data/. Only numpy beyond the standard library.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
GLOVE = HERE / "data" / "glove.6B.50d.txt"
CACHE = HERE / "data" / "query_cache.json"
WORDS_TXT = HERE.parent / "upgoer-five" / "words.txt"

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
ADDR_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)/(\d+)\.(\d+)\.(\d+)"
                     r"/(\d+)\.(\d+)\.(\d+)$")


def fmt(c):
    return (f"{c[0]}.{c[1]}.{c[2]}/{c[3]}.{c[4]}.{c[5]}"
            f"/{c[6]}.{c[7]}.{c[8]}")


def split_parts(w):
    if w.endswith("n't"):
        return [w[:-3], "n't"]
    head, _, tail = w.partition("'")
    return [head, "'" + tail]


def wanted_tokens(words):
    wanted = set()
    for w in words:
        wanted.add(w)
        if "'" in w:
            wanted.add(w.replace("'", ""))
            wanted.update(split_parts(w))
    return wanted


def scan_glove(wanted):
    found = {}
    with open(GLOVE, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            tok = line.split(" ", 1)[0]
            if tok in wanted:
                found[tok] = np.array(line.rstrip("\n").split(" ")[1:],
                                      dtype=np.float64)
                if len(found) == len(wanted):
                    break
    return found


def embed(word, glove):
    w = word.lower()
    if w in glove:
        return glove[w]
    if "'" in w:
        squashed = w.replace("'", "")
        if squashed in glove:
            return glove[squashed]
        vecs = [glove[p] for p in split_parts(w) if p in glove]
        if vecs:
            return np.mean(vecs, axis=0)
    return None


# --- sibling checker word rules (kept in step with check_ug5.py) --------

def normalize(word):
    return re.sub(r"[^a-z]", "", word.lower())


def stems(word):
    if word.endswith("'s"):
        yield word[:-2]
    if word.endswith("ies") and len(word) > 3:
        yield word[:-3] + "y"
    if word.endswith("ing") and len(word) > 4:
        yield word[:-3]
        yield word[:-3] + "e"
    if word.endswith("ed") and len(word) > 3:
        yield word[:-2]
        yield word[:-1]
    if word.endswith("es") and len(word) > 2:
        yield word[:-2]
        yield word[:-1]
    if word.endswith("s") and len(word) > 1:
        yield word[:-1]
    if word.endswith("er") and len(word) > 3:
        yield word[:-2]
        yield word[:-2] + "e"
    if word.endswith("est") and len(word) > 4:
        yield word[:-3]
        yield word[:-3] + "e"


def is_allowed(word, allowed):
    w = word.lower()
    if normalize(w) in allowed:
        return True
    return any(normalize(s) in allowed for s in stems(w))


class Atlas:
    def __init__(self):
        coords = json.loads((HERE / "coordinates.json").read_text())
        self.words = list(coords)
        self.coord = {w: coords[w]["coord"] for w in self.words}
        self.C = np.array([self.coord[w] for w in self.words],
                          dtype=np.float64)
        model = json.loads((HERE / "data" / "model.json").read_text())
        self.mean = np.array(model["mean"])
        self.pcs = np.array(model["pcs"])
        self.scale = model["scale"]
        self.center = model["center"]
        self.qmin, self.qmax = model["qmin"], model["qmax"]

    def coord_of_vec(self, vec):
        proj = (vec - self.mean) @ self.pcs.T
        q = self.center + np.round(proj / self.scale)
        return tuple(int(x) for x in np.clip(q, self.qmin, self.qmax))

    def nearest_ug5(self, coord, k=5, exclude=None):
        d = np.linalg.norm(self.C - np.array(coord, dtype=np.float64),
                           axis=1)
        out = []
        for j in np.argsort(d):
            w = self.words[j]
            if w == exclude:
                continue
            out.append((w, self.coord[w], float(d[j])))
            if len(out) == k:
                break
        return out


def load_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {"vectors": {}, "unembeddable": []}


def embed_words(atlas, words):
    """Embed a list of words, using and updating the query cache."""
    cache = load_cache()
    vectors, missing = {}, []
    todo = []
    for w in words:
        lw = w.lower()
        if lw in cache["vectors"]:
            vectors[w] = np.array(cache["vectors"][lw])
        elif lw in cache["unembeddable"]:
            missing.append(w)
        else:
            todo.append(w)
    if todo:
        glove = scan_glove(wanted_tokens([w.lower() for w in todo]))
        for w in todo:
            vec = embed(w, glove)
            if vec is None:
                cache["unembeddable"].append(w.lower())
                missing.append(w)
            else:
                cache["vectors"][w.lower()] = vec.tolist()
                vectors[w] = vec
        CACHE.write_text(json.dumps(cache))
    return vectors, missing


def cmd_address(atlas, words):
    vectors, missing = embed_words(
        atlas, [w for w in words if w.lower() not in atlas.coord])
    status = 0
    for word in words:
        lw = word.lower()
        if lw in atlas.coord:
            near = atlas.nearest_ug5(atlas.coord[lw], exclude=lw)
            print(f"{word}: {fmt(atlas.coord[lw])} (UG5 word; nearest "
                  f"UG5 neighbors: " +
                  ", ".join(f"{w} at {d:.0f}" for w, _, d in near[:3]) +
                  ")")
        elif word in vectors:
            coord = atlas.coord_of_vec(vectors[word])
            near = atlas.nearest_ug5(coord)
            print(f"{word}: {fmt(coord)} (not UG5; nearest UG5: " +
                  ", ".join(f"{w} at {d:.0f}" for w, _, d in near[:3]) +
                  ")")
        else:
            print(f"{word}: UNEMBEDDABLE (no GloVe vector; not placed)")
            status = 1
    return status


def cmd_decode(atlas, address):
    m = ADDR_RE.match(address.strip())
    if not m:
        print(f"{address}: not a phext address")
        return 1
    coord = tuple(int(g) for g in m.groups())
    near = atlas.nearest_ug5(coord, k=5)
    exact = [w for w, _, d in near if d == 0]
    if exact:
        print(f"{address}: inscribed word(s): {', '.join(exact)}")
    for w, c, d in near:
        print(f"  {w}  {fmt(c)}  address distance {d:.1f}")
    return 0


def cmd_validate(atlas, path, k):
    text = (sys.stdin.read() if path == "-"
            else Path(path).read_text(encoding="utf-8"))
    allowed = {normalize(w) for w in
               WORDS_TXT.read_text(encoding="utf-8").split()}
    flagged = []
    for m in WORD_RE.finditer(text):
        if not is_allowed(m.group(0), allowed) \
                and m.group(0).lower() not in [f.lower() for f in flagged]:
            flagged.append(m.group(0))
    if not flagged:
        print("clean: every word is a UG5 word or a form of one")
        return 0
    vectors, missing = embed_words(atlas, flagged)
    for word in flagged:
        if word in vectors:
            coord = atlas.coord_of_vec(vectors[word])
            near = atlas.nearest_ug5(coord, k=k)
            print(f"{word}  (at {fmt(coord)}):")
            for w, c, d in near:
                print(f"    {w}  {fmt(c)}  distance {d:.1f}")
        else:
            print(f"{word}: no embedding; no neighbors to suggest")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words", nargs="*", help="words to address")
    ap.add_argument("--decode", metavar="ADDRESS",
                    help="nearest inscribed words to a coordinate")
    ap.add_argument("--validate", metavar="FILE",
                    help="flag non-UG5 words in a text file (- for stdin)")
    ap.add_argument("--neighbors", type=int, default=5,
                    help="suggestions per flagged word in validate mode")
    args = ap.parse_args()
    atlas = Atlas()
    if args.decode:
        return cmd_decode(atlas, args.decode)
    if args.validate:
        return cmd_validate(atlas, args.validate, args.neighbors)
    if not args.words:
        ap.print_usage()
        return 2
    return cmd_address(atlas, args.words)


if __name__ == "__main__":
    sys.exit(main())
