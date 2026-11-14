#!/usr/bin/env python3
"""Build life.phext: every message in Discord #life, tracked holographically.

Will's order (2026-11-13 19:25 CST): "track every message in #life
holographically, uploaded to life.phext and published to human.git"

Each message is inscribed at the holographic coordinate computed from
its OWN words by the Singular holographic merge (the
task_coordinate.py machinery: tokenize as the Singular checker does,
average each distinct word's atlas position component-wise, round
half up, never below 1; archive-only words rest at home
1.1.1/1.1.1/1.1.1, words in neither at the far corner
9.9.9/9.9.9/9.9.9). A message with no words at all (attachment-only
or blank) rests at the far corner, recorded in the source with
coordinate_basis "far-corner (no words)".

Source of truth: ~/workspace/phext/life-source.json — message records
{id, timestamp, author, author_id, bot, content, attachments,
coordinate, coordinate_basis} plus a fetch watermark. Edit the JSON
(through life_track.py), never the .phext; rebuild after every edit.

Regenerate:  python3 ~/workspace/phext/build_life_phext.py
Check:       python3 ~/workspace/phext/build_life_phext.py --check
Output:      ~/workspace/phext/life.phext (deterministic for a given
             source file). Serialization follows build_tasks_phext.py:
             the 9 phext delimiters, coordinates 1-indexed, implode
             walks sorted coordinates.

Scrolls: one per distinct coordinate, holding every message that
merged there, in timestamp order. Each message entry is a provenance
header (author, timestamp, Discord message id) followed by the
message content. Content is verbatim except that phext delimiter
bytes and the chain bytes 0x02/0x03 are replaced with spaces — a chat
message must never be able to break the lattice or the chain framing.
The Home scroll (1.1.1/1.1.1/1.1.1) carries Will's order and an index:
one line per coordinate (coordinate — message count — time span).
"""
import json
import os
import sys

LEVEL_BYTES = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]  # library..scroll
DELIM_SET = set(LEVEL_BYTES) | {0x02, 0x03}  # + chain break / chain close

SRC_PATH = os.path.expanduser("~/workspace/phext/life-source.json")
OUT_PATH = os.path.expanduser("~/workspace/phext/life.phext")
HOME_COORD = "1.1.1/1.1.1/1.1.1"
CHANNEL_ID = "1477162982210273291"


def parse_coord(s):
    parts = s.replace("/", ".").split(".")
    assert len(parts) == 9, f"coordinate must have 9 components: {s}"
    vals = tuple(int(p) for p in parts)
    assert all(v >= 1 for v in vals), f"no coordinate component below 1: {s}"
    return vals


def implode(scrolls):
    """scrolls: dict coord-string -> text. Same state machine as
    build_tasks_phext.py / build_artifacts_phext.py."""
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


def sanitize(text):
    raw = text.encode()
    if DELIM_SET & set(raw):
        text = "".join(c if ord(c) > 0x1F or c in "\n\t" else " " for c in text)
        # the loop above keeps ordinary control whitespace; also strip
        # any of the exact delimiter/chain codepoints if present as text
        for b in (0x01, 0x02, 0x03, 0x17, 0x18, 0x19, 0x1A, 0x1C, 0x1D, 0x1E, 0x1F):
            text = text.replace(chr(b), " ")
    return text


def message_entry(m):
    head = (f"— {m['timestamp']} · {m['author']} · message {m['id']}")
    if m.get("attachments"):
        head += f" · attachments: {', '.join(m['attachments'])}"
    body = sanitize(m.get("content") or "")
    return head + "\n" + body + "\n"


def build(source):
    messages = sorted(source["messages"], key=lambda m: (m["timestamp"], m["id"]))
    by_coord = {}
    for m in messages:
        by_coord.setdefault(m["coordinate"], []).append(m)

    scrolls = {}
    index_lines = []
    for coord in sorted(by_coord, key=parse_coord):
        if coord == HOME_COORD:
            continue  # home is generated below; messages merging home share it under the index
        msgs = by_coord[coord]
        scrolls[coord] = "".join(message_entry(m) for m in msgs).rstrip("\n") + "\n"
        index_lines.append(
            f"{coord} — {len(msgs)} message(s) — {msgs[0]['timestamp']} .. {msgs[-1]['timestamp']}")

    home_msgs = by_coord.get(HOME_COORD, [])
    home = (
        "life.phext — every message in #life, tracked holographically\n"
        "\n"
        "Will's order (2026-11-13 19:25 CST): \"track every message in #life "
        "holographically, uploaded to life.phext and published to human.git\"\n"
        "\n"
        f"Channel: #life (Discord channel {CHANNEL_ID}, guild Tessera — "
        "\"Phext, The Exocortex, and Phextura\"). Each message rests at the "
        "holographic coordinate computed from its own words (Singular merge: "
        "tokenize as the Singular checker does, average each distinct word's "
        "atlas position, round half up, never below 1). Messages with no "
        "words rest at the far corner 9.9.9/9.9.9/9.9.9. One scroll per "
        "coordinate; a scroll holds every message that merged there, in "
        "timestamp order, each with its author, timestamp, and Discord "
        "message id. Content is verbatim except phext delimiter and chain "
        "bytes are replaced with spaces.\n"
        "\n"
        f"Messages tracked: {len(messages)} across {len(by_coord)} coordinates.\n"
        "\n"
        "Index (coordinate — messages — span):\n"
        + "\n".join(index_lines)
        + "\n"
    )
    if home_msgs:
        home += ("\nMessages that merged to Home itself:\n"
                 + "".join(message_entry(m) for m in home_msgs))
    scrolls[HOME_COORD] = home
    return implode(scrolls)


def main():
    check = "--check" in sys.argv
    with open(SRC_PATH, encoding="utf-8") as f:
        source = json.load(f)
    data = build(source)
    import hashlib
    sha = hashlib.sha256(data).hexdigest()
    if check:
        try:
            with open(OUT_PATH, "rb") as f:
                current = f.read()
        except FileNotFoundError:
            print("DRIFT: life.phext does not exist")
            return 1
        if current == data:
            print(f"CURRENT: life.phext matches life-source.json (sha256 {sha})")
            return 0
        print(f"DRIFT: life.phext does not match life-source.json (rebuilt sha256 {sha})")
        return 1
    with open(OUT_PATH, "wb") as f:
        f.write(data)
    print(f"life.phext: {len(source['messages'])} messages, {len(data)} bytes, sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
