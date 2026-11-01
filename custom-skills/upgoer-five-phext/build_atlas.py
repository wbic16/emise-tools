#!/usr/bin/env python3
"""Build the UG5 phext word atlas (natural 9D positions, v2).

Every word gets its phext coordinate from one natural mapping: GloVe 6B
50d embeddings are projected onto the top 9 principal components fitted
over a broad 60,000-word vocabulary sample, and each projection is
quantized to a phext component. There are no bins and no cell origins.
UG5 words land wherever their meaning puts them.

Outputs:
  coordinates.json     the 1,000 UG5 words with coordinate and address
  data/model.json      PCA mean/components and quantization parameters
  data/editor_vocab.json  coordinates for 5,000 frequent non-UG5 words
                       (used by the interactive editor for suggestions)
  atlas.phext          index scroll at 1.1.1/1.1.1/1.1.1 plus one scroll
                       per inscribed coordinate, in phext delimiter form

See SCHEME.md for the full specification.
Usage: python3 build_atlas.py [--words PATH] [--glove PATH]
Only numpy is required beyond the standard library.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_WORDS = HERE.parent / "upgoer-five" / "words.txt"
DEFAULT_GLOVE = HERE / "data" / "glove.6B.50d.txt"

# Quantization (see SCHEME.md): component = clamp(CENTER + round(p/SCALE)).
SCALE = 0.04        # GloVe units per coordinate step, same for all 9 axes
CENTER = 150        # coordinate value of projection 0 (the sample mean)
QMIN, QMAX = 1, 999

SAMPLE_N = 60000    # broad vocabulary sample the PCA axes are fitted on
EXTRA_N = 5000      # frequent non-UG5 words shipped to the editor
SEED = 20261031

# Phext delimiter bytes by level, from parse_phext.py (libphext order):
# library, shelf, series, collection, volume, book, chapter, section, scroll
DELIMS = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]


def fmt(coord):
    c = [int(x) for x in coord]
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


def embed(word, glove):
    """GloVe vector with the contraction fallback chain, else None."""
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


def write_phext(path, scrolls):
    """Write {coord_tuple: text} as a phext file, dead-reckoning style.

    Scrolls are emitted in coordinate order. A delimiter byte increments
    its level and resets all lower levels to 1, so reaching a sparse
    coordinate walks through empty scroll slots, exactly as libphext
    files do. Returns the number of delimiter bytes written.
    """
    out = bytearray()
    cur = [1] * 9
    ndelim = 0
    for coord in sorted(scrolls):
        target = list(coord)
        while cur != target:
            k = next(i for i in range(9) if cur[i] != target[i])
            if target[k] < cur[k]:
                raise ValueError(f"coordinates out of order at {coord}")
            out.append(DELIMS[k])
            ndelim += 1
            cur[k] += 1
            for j in range(k + 1, 9):
                cur[j] = 1
        out += scrolls[coord].encode("utf-8")
    Path(path).write_bytes(bytes(out))
    return ndelim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", default=str(DEFAULT_WORDS))
    ap.add_argument("--glove", default=str(DEFAULT_GLOVE))
    args = ap.parse_args()

    words = [w.lower() for w in
             Path(args.words).read_text(encoding="utf-8").split()]
    if len(words) != 1000 or len(set(words)) != 1000:
        sys.exit(f"word list must hold exactly 1000 unique words, "
                 f"got {len(words)}")
    ug5_set = set(words)
    wanted = wanted_tokens(words)

    # One streaming pass over GloVe: PCA sample (first SAMPLE_N parsed
    # lines, the file is frequency ordered), UG5 tokens, and the editor's
    # extra vocabulary (frequent plain alphabetic non-UG5 words).
    sample, glove, extra = [], {}, {}
    with open(args.glove, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.rstrip("\n").split(" ")
            if len(parts) != 51:
                continue
            tok = parts[0]
            vec = np.array(parts[1:], dtype=np.float64)
            if len(sample) < SAMPLE_N:
                sample.append(vec)
            if tok in wanted:
                glove[tok] = vec
            if (len(extra) < EXTRA_N and tok.isalpha() and tok.islower()
                    and len(tok) >= 3 and tok not in ug5_set):
                extra[tok] = vec
            if (len(sample) >= SAMPLE_N and len(extra) >= EXTRA_N
                    and wanted.issubset(glove.keys())):
                break
    S = np.stack(sample)
    print(f"PCA sample: {len(S)} vectors; editor extra vocab: {len(extra)}")

    mean = S.mean(axis=0)
    _, _, vt = np.linalg.svd(S - mean, full_matrices=False)
    pcs = vt[:9].copy()
    for k in range(9):
        j = int(np.argmax(np.abs(pcs[k])))
        if pcs[k][j] < 0:
            pcs[k] = -pcs[k]

    def coord_of(vec):
        proj = (vec - mean) @ pcs.T
        q = CENTER + np.round(proj / SCALE)
        return tuple(int(x) for x in np.clip(q, QMIN, QMAX)), proj

    ug5_vecs, missing = {}, []
    for w in words:
        v = embed(w, glove)
        if v is None:
            missing.append(w)
        else:
            ug5_vecs[w] = v
    if missing:
        sys.exit(f"anchors with no GloVe route: {missing}")
    ug5_coord = {w: coord_of(ug5_vecs[w])[0] for w in words}
    extra_coord = {w: coord_of(v)[0] for w, v in extra.items()}

    by_coord = {}
    for w in words:
        by_coord.setdefault(ug5_coord[w], []).append(w)
    shared = {c: ws for c, ws in by_coord.items() if len(ws) > 1}
    print(f"UG5 coordinates: {len(by_coord)} unique for 1000 words; "
          f"{len(shared)} shared coordinates")
    for c, ws in shared.items():
        print(f"  shared {fmt(c)}: {ws}")
    allq = np.array([ug5_coord[w] for w in words])
    print(f"UG5 coordinate ranges per axis: "
          f"{list(zip(allq.min(axis=0).tolist(), allq.max(axis=0).tolist()))}")

    model = {"scale": SCALE, "center": CENTER, "qmin": QMIN, "qmax": QMAX,
             "pca_sample_size": len(S), "mean": mean.tolist(),
             "pcs": pcs.tolist()}
    (HERE / "data" / "model.json").write_text(json.dumps(model))
    coords_doc = {w: {"address": fmt(ug5_coord[w]),
                      "coord": list(ug5_coord[w])} for w in words}
    (HERE / "coordinates.json").write_text(json.dumps(coords_doc, indent=1))
    (HERE / "data" / "editor_vocab.json").write_text(
        json.dumps({w: list(c) for w, c in extra_coord.items()}))
    print("wrote data/model.json, coordinates.json, data/editor_vocab.json")

    # ---- validation: address distance vs semantic distance ------------
    pool_words = words + list(extra)
    pool_vecs = np.stack([ug5_vecs[w] if w in ug5_vecs else extra[w]
                          for w in pool_words])
    pool_coord = np.array([ug5_coord[w] if w in ug5_coord
                           else extra_coord[w] for w in pool_words],
                          dtype=np.float64)
    Vn = pool_vecs / np.linalg.norm(pool_vecs, axis=1, keepdims=True)
    rng = np.random.default_rng(SEED)
    pairs = rng.integers(0, len(pool_words), size=(4000, 2))
    cos_d, addr_d = [], []
    for i, j in pairs:
        if i == j:
            continue
        cos_d.append(1.0 - float(Vn[i] @ Vn[j]))
        addr_d.append(float(np.linalg.norm(pool_coord[i] - pool_coord[j])))
    cos_d, addr_d = np.array(cos_d), np.array(addr_d)
    pearson = float(np.corrcoef(addr_d, cos_d)[0, 1])
    spearman = float(np.corrcoef(np.argsort(np.argsort(addr_d)),
                                 np.argsort(np.argsort(cos_d)))[0, 1])
    print(f"distance validation over {len(cos_d)} pairs: "
          f"Pearson r = {pearson:.3f}, Spearman rho = {spearman:.3f}")

    # ---- validation: UG5 neighbors in address space --------------------
    C = np.array([ug5_coord[w] for w in words], dtype=np.float64)
    print("UG5 nearest neighbors in address space (top 5):")
    nn_map = {}
    for probe in words:
        i = words.index(probe)
        d = np.linalg.norm(C - C[i], axis=1)
        near = np.argsort(d)[1:6]
        nn_map[probe] = [(words[j], float(d[j])) for j in near]
    for probe in ("fire", "water", "happy", "love", "dog", "money",
                  "time", "song"):
        if probe in nn_map:
            print(f"  {probe}: " + ", ".join(
                f"{w} ({dist:.0f})" for w, dist in nn_map[probe]))

    # ---- atlas.phext ----------------------------------------------------
    scrolls = {}
    index_lines = [
        "UG5 Phext Atlas - Index",
        "The ten hundred Up Goer Five words at their natural 9D "
        "coordinates.",
        "Each word also has its own scroll at its own coordinate.",
        "Scheme: upgoer-five-phext skill, SCHEME.md.",
        "",
    ]
    for w in words:
        index_lines.append(f"{w}  {fmt(ug5_coord[w])}")
    scrolls[(1, 1, 1, 1, 1, 1, 1, 1, 1)] = "\n".join(index_lines) + "\n"
    for coord, ws in by_coord.items():
        sections = []
        for w in sorted(ws):
            lines = [w, f"coordinate: {fmt(coord)}", "",
                     "nearest UG5 neighbors by address distance:"]
            for nw, dist in nn_map[w]:
                lines.append(f"  {nw}  {fmt(ug5_coord[nw])}  {dist:.1f}")
            sections.append("\n".join(lines))
        scrolls[coord] = "\n\n".join(sections) + "\n"
    ndelim = write_phext(HERE / "atlas.phext", scrolls)
    size = (HERE / "atlas.phext").stat().st_size
    print(f"atlas.phext: {len(scrolls)} inscribed scrolls, "
          f"{ndelim} delimiter bytes, {size} bytes total")


if __name__ == "__main__":
    main()
