#!/usr/bin/env python3
"""Check text against the Singular word list (one person's words).

Reads text from a file argument or from stdin, splits it into words
(keeping contractions such as "don't" together), and reports every
word that is not in words.txt.

Matching is strict: the list holds the exact forms the person used,
so a changed form that was never written is flagged. The list is
lowercase; case in the text does not matter.

Usage:
    check_singular.py [FILE] [--words WORDS_FILE] [--suggest]

Exit code is 0 when the text is clean, 1 when any word is flagged,
and 2 on a usage or file error.
"""

import argparse
import difflib
import re
import sys
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.UNICODE)
DEFAULT_WORDS = Path(__file__).resolve().parent.parent / "words.txt"


def load_words(path: Path) -> set:
    return {w.strip().lower() for w in path.read_text(encoding="utf-8").splitlines() if w.strip()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="file to check (default: stdin)")
    ap.add_argument("--words", default=str(DEFAULT_WORDS))
    ap.add_argument("--suggest", action="store_true", help="print close listed words for each flagged word")
    args = ap.parse_args()

    words_path = Path(args.words)
    if not words_path.exists():
        print(f"word list not found: {words_path}", file=sys.stderr)
        return 2
    allowed = load_words(words_path)

    if args.file:
        try:
            text = Path(args.file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"cannot read {args.file}: {exc}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()

    tokens = [w.lower() for w in WORD_RE.findall(text)]
    flagged = Counter(w for w in tokens if w not in allowed)

    if not flagged:
        print(f"clean: {len(tokens)} words, all in the Singular list ({len(allowed)} words)")
        return 0
    print(f"flagged {sum(flagged.values())} word(s), {len(flagged)} distinct, not in the Singular list:")
    for word, n in flagged.most_common():
        line = f"  {word} x{n}" if n > 1 else f"  {word}"
        if args.suggest:
            close = difflib.get_close_matches(word, allowed, n=3, cutoff=0.6)
            if close:
                line += f"  (close: {', '.join(close)})"
        print(line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
