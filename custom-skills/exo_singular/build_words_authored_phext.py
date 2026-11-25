#!/usr/bin/env python3
"""Build words-authored.phext - Will's authored Singular words, by cohort.

The corpus Iam learns from, kept as phext: one scroll per cohort.
A cohort is a set of words admitted together under one ruling, kept
together as one scroll. Cohort 1 is the archive itself; later cohorts
are admissions. The whole corpus is every cohort's words, in order.

Cohort 1's source of truth is words-authored.txt (this skill's list).
Admissions are recorded in COHORTS below, each with its ruling.

All phext writing goes through the reference implementation
(PyPI `phext`, Will's Python port of libphext).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace/tlm-proto/.venv/lib/python3.12/site-packages"))
from phext.phext import Phext
from phext.coordinate import Coordinate

HERE = Path(__file__).resolve().parent
HOME = Coordinate(1, 1, 1, 1, 1, 1, 1, 1, 1)

# Admissions after the archive: (cohort name, ruling, words in order).
# Cohorts are eras (Will, 2026-11-14): cohort 1 is 2008-2025, cohort 2 is
# 2026-2033. An admission lands in the cohort of its era; the ruling that
# admitted it is recorded in the cohort scroll.
COHORTS = [
    ("2026 - 2033",
     "era cohort, open 2026-2033. First admission: Will's ruling, "
     "2026-11-14: \"phcc, qexo, phccbox - these are all Will words. "
     "Iam must learn how to spell them.\" Admitted by cohort at "
     "Will's suggestion, 2026-11-14.",
     ["phcc", "phccbox", "qexo"]),
]

def coord_for(idx):
    i = idx + 1
    return Coordinate(1, 1, 1, 1, 1, 1, i // 10000 + 1, (i // 100) % 100 + 1, i % 100 + 1)

def cohort_scroll(name, ruling, words):
    lines = [f"cohort: {name}", f"admitted: {ruling}", f"words: {len(words)}"]
    lines += words
    return "\n".join(lines)

def main():
    archive = [w.strip() for w in (HERE / "words-authored.txt").read_text(encoding="utf-8").splitlines() if w.strip()]
    cohorts = [("2008 - 2025", "the authored archive, 2008-2025 (words-authored.txt)", archive)] + COHORTS
    seen = set()
    for name, _ruling, words in cohorts:
        for w in words:
            assert w not in seen, f"word in two cohorts: {w}"
            seen.add(w)
    total = sum(len(w) for _n, _r, w in cohorts)
    home_lines = [
        "words-authored.phext - Will Bickford's authored Singular words, by cohort.",
        "The corpus Iam learns from. One scroll per cohort: words admitted",
        "together, under one ruling, kept together. The corpus is every",
        "cohort's words, in cohort order.",
    ]
    for i, (name, _r, words) in enumerate(cohorts, 1):
        home_lines.append(f"cohort {i}: {name} - {len(words)} words")
    home_lines.append(f"total: {total} words")
    table = {HOME: "\n".join(home_lines)}
    for idx, (name, ruling, words) in enumerate(cohorts):
        table[coord_for(idx)] = cohort_scroll(name, ruling, words)
    table = dict(sorted(table.items(), key=lambda kv: kv[0].as_tuple()))
    buf = Phext().implode(table)
    out = HERE / "words-authored.phext"
    out.write_text(buf, encoding="utf-8")
    print(f"wrote {out}: {len(buf.encode('utf-8'))} bytes, {len(cohorts)} cohorts, {total} words")
    # round-trip: read it back and reassemble the corpus
    back = Phext().explode(out.read_text(encoding="utf-8"))
    words = []
    for coord in sorted(back, key=lambda c: c.as_tuple()):
        lines = back[coord].split("\n")
        if lines and lines[0].startswith("cohort: "):
            start = next(i for i, ln in enumerate(lines) if ln.startswith("words: ")) + 1
            words += [ln for ln in lines[start:] if ln]
    expect = [w for _n, _r, ws in cohorts for w in ws]
    assert words == expect, "round-trip corpus differs"
    print(f"round-trip via reference phext parser: OK ({len(words)} words, order preserved)")

if __name__ == "__main__":
    main()
