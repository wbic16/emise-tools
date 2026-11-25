#!/usr/bin/env python3
"""Inventory a project's persistent/structured parts for a phext upgrade.

Usage: phext_audit.py PROJECT_DIR [--json]

Walks the tree (skipping .git, venvs, caches, node_modules), groups files by
extension with sizes, and flags candidate artifacts for classification:
structured text stores, databases, custom binary formats, docs corpora,
config, and media/weights that are usually Class D. Prints a worksheet the
agent fills in from reading the code -- this script classifies nothing by
itself, on purpose: classification must be distilled from the project's own
invariants, not from file extensions.
"""
import json
import os
import sys
from collections import defaultdict

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".tox", "dist", "build"}
FLAG_RULES = [
    ("structured-text store candidate (Class A/B test)", {".json", ".jsonl", ".csv", ".tsv", ".yaml", ".yml", ".toml", ".xml", ".phext"}),
    ("database candidate (unravel: authored vs derived)", {".db", ".sqlite", ".sqlite3"}),
    ("docs / knowledge corpus candidate (Class A/B test)", {".md", ".rst", ".txt"}),
    ("config candidate (usually bridge or leave)", {".ini", ".cfg", ".env"}),
    ("binary / weights / media (Class D test first)", {".bin", ".safetensors", ".gguf", ".npy", ".npz", ".pt", ".pth", ".onnx", ".png", ".jpg", ".gif", ".mp4", ".wav", ".mp3"}),
]


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if len(args) != 1:
        print(__doc__.strip().splitlines()[3], file=sys.stderr)
        return 2
    root = args[0]
    by_ext = defaultdict(lambda: [0, 0])  # ext -> [count, bytes]
    flagged = defaultdict(list)
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            total_files += 1
            ext = os.path.splitext(name)[1].lower() or "(none)"
            by_ext[ext][0] += 1
            by_ext[ext][1] += size
            rel = os.path.relpath(path, root)
            for label, exts in FLAG_RULES:
                if ext in exts:
                    flagged[label].append((rel, size))
    if as_json:
        print(json.dumps({
            "root": root, "total_files": total_files,
            "by_extension": {e: {"count": c, "bytes": b} for e, (c, b) in sorted(by_ext.items())},
            "flagged": {k: v for k, v in flagged.items()},
        }, indent=1))
        return 0
    print(f"phext audit: {root}  ({total_files} files)")
    print("\nby extension (count, bytes):")
    for ext, (count, size) in sorted(by_ext.items(), key=lambda kv: -kv[1][1]):
        print(f"  {ext:14s} {count:5d}  {size:10d}")
    for label, items in flagged.items():
        print(f"\n{label}: {len(items)}")
        for rel, size in sorted(items, key=lambda t: -t[1])[:20]:
            print(f"  {size:10d}  {rel}")
    print("\nworksheet: for each flagged artifact and each custom format in code,")
    print("record in PHEXT.md: native invariants / class A-D / coordinate axis it would supply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
