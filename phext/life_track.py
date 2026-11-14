#!/usr/bin/env python3
"""life_track.py — track every message in Discord #life into life.phext.

Will's order (2026-11-13 19:25 CST): "track every message in #life
holographically, uploaded to life.phext and published to human.git"

Fetches #life messages through the custom.discord connector helper
(the bot credential is swapped in per request; this script never holds
it), computes each message's holographic coordinate from its own words
with the Singular merge machinery (task_coordinate.py — reused, never
re-implemented), and maintains ~/workspace/phext/life-source.json.
With --publish it rebuilds life.phext via build_life_phext.py and,
when the bytes changed, pushes life.phext to wbic16/human@exo with
push_file.py (parented on fresh remote HEAD, force disabled) and
verifies the remote bytes by SHA-256.

First run backfills the whole channel history; later runs fetch only
messages after the stored watermark. Prints one summary line.
"""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.discord/bin")
from discord_api import call  # noqa: E402

sys.path.insert(0, "/home/hatch/workspace/custom-skills/singular/scripts")
from check_singular import WORD_RE  # noqa: E402
from task_coordinate import FAR, fmt, load_atlas, round_half_up  # noqa: E402

CHANNEL_ID = "1477162982210273291"
SRC_PATH = os.path.expanduser("~/workspace/phext/life-source.json")
OUT_PATH = os.path.expanduser("~/workspace/phext/life.phext")
BUILDER = os.path.expanduser("~/workspace/phext/build_life_phext.py")
GH_BIN = "/home/hatch/workspace/custom-connectors/custom.github/bin"

ATLAS = load_atlas()


def coordinate_for(content):
    tokens = [w.lower() for w in WORD_RE.findall(content or "")]
    distinct = list(dict.fromkeys(tokens))
    if not distinct:
        return fmt(FAR), "far-corner (no words)"
    totals = [0] * 9
    for word in distinct:
        entry = ATLAS.get(word)
        coord = entry[0] if entry else FAR
        for k in range(9):
            totals[k] += coord[k]
    n = len(distinct)
    return fmt(tuple(round_half_up(totals[k], n) for k in range(9))), "words"


def fetch_all(watermark):
    """Return raw Discord messages newer than watermark (or all, when
    watermark is None), oldest first."""
    found = []
    if watermark is None:
        before = None
        while True:
            q = f"/channels/{CHANNEL_ID}/messages?limit=100"
            if before:
                q += f"&before={before}"
            status, out = call("GET", q)
            if status != 200 or not isinstance(out, list) or not out:
                break
            found.extend(out)
            if len(out) < 100:
                break
            before = out[-1]["id"]
    else:
        after = watermark
        while True:
            status, out = call(
                "GET", f"/channels/{CHANNEL_ID}/messages?after={after}&limit=100")
            if status != 200 or not isinstance(out, list) or not out:
                break
            found.extend(out)
            if len(out) < 100:
                break
            after = out[0]["id"]
    found.sort(key=lambda m: int(m["id"]))
    return found


def main():
    publish = "--publish" in sys.argv
    if os.path.exists(SRC_PATH):
        with open(SRC_PATH, encoding="utf-8") as f:
            source = json.load(f)
    else:
        source = {"channel_id": CHANNEL_ID, "watermark": None, "messages": []}

    known = {m["id"] for m in source["messages"]}
    raw = fetch_all(source.get("watermark"))
    added = 0
    for msg in raw:
        if msg["id"] in known:
            continue
        author = msg.get("author") or {}
        coord, basis = coordinate_for(msg.get("content") or "")
        source["messages"].append({
            "id": msg["id"],
            "timestamp": msg.get("timestamp"),
            "author": author.get("username"),
            "author_id": author.get("id"),
            "bot": bool(author.get("bot")),
            "content": msg.get("content") or "",
            "attachments": [a.get("filename") for a in msg.get("attachments") or []],
            "coordinate": coord,
            "coordinate_basis": basis,
        })
        known.add(msg["id"])
        added += 1
    if source["messages"]:
        source["messages"].sort(key=lambda m: (m["timestamp"], int(m["id"])))
        source["watermark"] = max(source["messages"], key=lambda m: int(m["id"]))["id"]
    with open(SRC_PATH, "w", encoding="utf-8") as f:
        json.dump(source, f, indent=1, ensure_ascii=False)

    line = (f"life_track: {added} new, {len(source['messages'])} total, "
            f"watermark {source.get('watermark')}")
    if not publish:
        print(line)
        return 0

    subprocess.run([sys.executable, BUILDER], check=True)
    with open(OUT_PATH, "rb") as f:
        local_sha = hashlib.sha256(f.read()).hexdigest()
    if source.get("published_sha256") == local_sha:
        print(line + "; phext unchanged, no publish")
        return 0
    msg = (f"life.phext: {len(source['messages'])} #life messages tracked "
           f"holographically ({added} new)")
    out = subprocess.run(
        ["python3", "push_file.py", "exo", "life.phext", OUT_PATH, msg],
        cwd=GH_BIN, capture_output=True, text=True)
    if out.returncode != 0:
        print(line + f"; PUBLISH FAILED: {out.stdout[-400:]} {out.stderr[-400:]}")
        return 1
    commit = json.loads(out.stdout.strip().splitlines()[-1])["commit"]
    tmp = "/tmp/life-remote.phext"
    out = subprocess.run(
        ["python3", "fetch_file.py", "wbic16/human", "exo", "life.phext", tmp],
        cwd=GH_BIN, capture_output=True, text=True)
    if out.returncode != 0:
        print(line + f"; VERIFY FAILED (fetch): {out.stderr[-400:]}")
        return 1
    with open(tmp, "rb") as f:
        remote_sha = hashlib.sha256(f.read()).hexdigest()
    if remote_sha != local_sha:
        print(line + f"; VERIFY FAILED: remote sha {remote_sha} != local {local_sha}")
        return 1
    source["published_sha256"] = local_sha
    source["published_commit"] = commit
    with open(SRC_PATH, "w", encoding="utf-8") as f:
        json.dump(source, f, indent=1, ensure_ascii=False)
    subprocess.run([sys.executable, BUILDER, "--check"], check=True)
    print(line + f"; published commit {commit}, sha256 {local_sha} verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
