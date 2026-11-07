#!/usr/bin/env python3
"""Build tasks.phext: Will's task register.

Will's standing order (2026-11-06 18:22 CST): "for every task I issue,
record it in tasks.phext, keep notes and results in the coordinate
generated initially." Every task Will issues gets a reference coordinate
from the Singular task-coordinate tool (see the task-register skill);
that coordinate is the task's scroll address in this phext, and all
notes and results for the task accumulate in that scroll.

Source of truth: ~/workspace/phext/tasks-source.json — a list of task
records {coordinate, title, issued, request, verbatim, status, notes,
results}. Edit the JSON, never the .phext; rebuild after every edit.

Regenerate:  python3 ~/workspace/phext/build_tasks_phext.py
Check:       python3 ~/workspace/phext/build_tasks_phext.py --check
             (rebuilds to a temp file; prints CURRENT / DRIFT, exit 0/1)
Output:      ~/workspace/phext/tasks.phext (deterministic for a given
             source file). Conventions follow build_skills_phext.py:
             the 9 phext delimiters, coordinates 1-indexed, implode
             walks sorted coordinates.

The Home scroll (1.1.1/1.1.1/1.1.1) is generated: it carries Will's
order and an index of every task (coordinate — title — status).
"""
import hashlib
import json
import os
import sys
import tempfile

LEVEL_BYTES = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]  # library..scroll
DELIM_SET = set(LEVEL_BYTES)

SRC_PATH = os.path.expanduser("~/workspace/phext/tasks-source.json")
OUT_PATH = os.path.expanduser("~/workspace/phext/tasks.phext")
HOME_COORD = "1.1.1/1.1.1/1.1.1"


def parse_coord(s):
    parts = s.replace("/", ".").split(".")
    assert len(parts) == 9, f"coordinate must have 9 components: {s}"
    vals = tuple(int(p) for p in parts)
    assert all(v >= 1 for v in vals), f"no coordinate component below 1: {s}"
    return vals


def implode(scrolls):
    """scrolls: dict coord-string -> text. Same state machine as
    build_skills_phext.py / build_exocortex.py."""
    items = sorted(((parse_coord(k), v) for k, v in scrolls.items()))
    out = bytearray()
    state = [1] * 9
    for target, text in items:
        for lvl in range(9):
            while state[lvl] < target[lvl]:
                out.append(LEVEL_BYTES[lvl])
                state[lvl] += 1
                for j in range(lvl + 1, 9):
                    state[j] = 1
        assert tuple(state) == target, (state, target)
        out += text.encode()
    return bytes(out)


def render_task(t):
    lines = [f"# {t['title']}", ""]
    lines.append(f"Coordinate: {t['coordinate']}")
    lines.append(f"Issued: {t['issued']}")
    kind = "Request (verbatim)" if t.get("verbatim") else "Request (from session record)"
    lines.append(f"{kind}: {t['request']}")
    lines.append(f"Status: {t['status']}")
    if t.get("notes"):
        lines.append("")
        lines.append("Notes:")
        lines += [f"- {n}" for n in t["notes"]]
    if t.get("results"):
        lines.append("")
        lines.append("Results:")
        lines += [f"- {r}" for r in t["results"]]
    lines.append("")
    return "\n".join(lines)


def render_home(tasks):
    lines = [
        "# tasks.phext — Will's task register",
        "",
        "Will's standing order (2026-11-06 18:22 CST): \"for every task I",
        "issue, record it in tasks.phext, keep notes and results in the",
        "coordinate generated initially.\"",
        "",
        "Every task Will issues receives a reference coordinate from the",
        "Singular task-coordinate tool at the moment it is issued. That",
        "coordinate is the task's permanent address here: its scroll",
        "holds the request, its status, and all notes and results as",
        "they accumulate. Source of truth: tasks-source.json beside this",
        "builder (build_tasks_phext.py); never hand-edit the .phext.",
        "",
        f"Tasks recorded: {len(tasks)}",
        "",
        "Index (coordinate — title — status):",
    ]
    for t in sorted(tasks, key=lambda x: parse_coord(x["coordinate"])):
        lines.append(f"- {t['coordinate']} — {t['title']} — {t['status']}")
    lines.append("")
    return "\n".join(lines)


def build():
    with open(SRC_PATH) as f:
        tasks = json.load(f)["tasks"]
    coords = [t["coordinate"] for t in tasks]
    assert len(coords) == len(set(coords)), "duplicate task coordinates"
    assert HOME_COORD not in coords, "home coordinate is generated, not a task"
    scrolls = {HOME_COORD: render_home(tasks)}
    for t in tasks:
        scrolls[t["coordinate"]] = render_task(t)
    for coord, text in scrolls.items():
        bad = DELIM_SET & set(text.encode())
        assert not bad, f"raw delimiter bytes in scroll {coord}: {bad}"
    return implode(scrolls), tasks


def main():
    check = "--check" in sys.argv
    blob, tasks = build()
    digest = hashlib.sha256(blob).hexdigest()
    if check:
        if os.path.exists(OUT_PATH):
            with open(OUT_PATH, "rb") as f:
                current = hashlib.sha256(f.read()).hexdigest()
            if current == digest:
                print(f"CURRENT: tasks.phext matches tasks-source.json (sha256 {digest})")
                return 0
        print(f"DRIFT: tasks.phext does not match tasks-source.json (rebuilt sha256 {digest})")
        return 1
    with open(OUT_PATH, "wb") as f:
        f.write(blob)
    print(f"tasks.phext: {len(tasks)} tasks + home, {len(blob)} bytes, sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
