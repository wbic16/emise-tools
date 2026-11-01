#!/usr/bin/env python3
"""Check text against the Up Goer Five (ten hundred word) list.

Reads text from a file argument or from stdin, splits it into words on
non-letters (keeping contractions such as "can't" together), and reports
every word that is not in words.txt.

A word also passes when it is a common changed form of a listed word,
such as "uses" from "use" or "going" from "go", because the Splasho
editor treats word forms of a listed word as fine. Pass --strict to
turn that off and require the exact listed form.

Usage:
    check_ug5.py [FILE] [--words WORDS_FILE] [--suggest] [--strict]

Exit code is 0 when the text is clean, 1 when any word is flagged,
and 2 on a usage or file error.
"""

import argparse
import difflib
import re
import sys
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
DEFAULT_WORDS = Path(__file__).resolve().parent.parent / "words.txt"


def normalize(word):
    """Lowercase a word and drop apostrophes and other non-letters."""
    return re.sub(r"[^a-z]", "", word.lower())


def load_words(path):
    words = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        word = normalize(line)
        if word:
            words.add(word)
    return words


def stems(word):
    """Yield shorter forms of a word made by common English endings."""
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


def is_allowed(word, allowed, strict):
    if word in allowed:
        return True
    if strict:
        return False
    return any(stem in allowed for stem in stems(word))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check text against the Up Goer Five word list."
    )
    parser.add_argument("file", nargs="?", help="Text file to check (default: stdin)")
    parser.add_argument(
        "--words",
        type=Path,
        default=DEFAULT_WORDS,
        help="Word list file (default: words.txt beside this skill)",
    )
    parser.add_argument(
        "--suggest",
        action="store_true",
        help="Print close listed words for each flagged word",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require the exact listed form, with no changed forms allowed",
    )
    args = parser.parse_args(argv)

    try:
        allowed = load_words(args.words)
    except OSError as exc:
        print(f"error: cannot read word list {args.words}: {exc}", file=sys.stderr)
        return 2

    try:
        if args.file:
            text = Path(args.file).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()
    except OSError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 2

    tokens = [normalize(match) for match in WORD_RE.findall(text)]
    counts = Counter(
        token for token in tokens if token and not is_allowed(token, allowed, args.strict)
    )

    if not counts:
        print("OK: every word is on the ten hundred word list.")
        return 0

    total = sum(counts.values())
    print(f"Flagged {total} word use(s), {len(counts)} different word(s):")
    for word in sorted(counts):
        print(f"  {word} x{counts[word]}")
        if args.suggest:
            close = difflib.get_close_matches(word, sorted(allowed), n=3, cutoff=0.6)
            if close:
                print(f"    close listed words: {', '.join(close)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
