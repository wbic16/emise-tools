#!/usr/bin/env python3
"""Ranch state sampler: one 5-minute cycle of the state.phext distillation.

Pipeline (Will's design, 2026-11-06):
  1. Probe the ranch fleet through the ranch proxy (`ranch fanout`) — one
     parallel pass over every enabled node collecting load, core count,
     the top processes, ollama / render / gateway markers, and GPU edge
     temperature. CPU Tctl comes from the fanout footers, which the proxy
     measures itself (and reports even for thermally skipped nodes).
  2. Compose a one-or-two-line plain-language summary of the cluster —
     deterministic template, no LLM in the loop.
  3. Compute the summary's holographic coordinate by Will's Singular
     method, reusing the singular skill's own machinery (check_singular's
     WORD_RE tokenizer + task_coordinate's atlas load and merge) — never
     reimplemented here.
  4. Append the summary, prefixed with its timestamp, as a line inside the
     scroll at that coordinate in ~/workspace/phext/state.phext. A
     coordinate already occupied gains a line; nothing is overwritten,
     nothing is dropped. The phext holds ONLY distilled summaries — raw
     pulls live in the working-state dir below, never in the phext.

Working state (outside the phext): ~/workspace/state-sampler/hidden_files/
  last-pull.json  — the most recent raw pull (overwritten each cycle)
  pulls.jsonl     — raw pull log, size-capped (rotated, newest kept)

Usage: state_sampler.py [--dry-run]   (--dry-run probes + prints, writes nothing)
Exit code: 0 on success (including a lock-skip), 1 on a hard failure.
"""

import fcntl
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HOME_DIR = Path.home()
RANCH = HOME_DIR / "workspace/ranch-proxy/ranch"
NODES_JSON = HOME_DIR / "workspace/ranch-proxy/nodes.json"
PHEXT_DIR = HOME_DIR / "workspace/phext"
STATE_PHEXT = PHEXT_DIR / "state.phext"
WORK_DIR = HOME_DIR / "workspace/state-sampler/hidden_files"
SINGULAR_SCRIPTS = HOME_DIR / "workspace/custom-skills/singular/scripts"
TZ = ZoneInfo("America/Chicago")
HOME_COORD = (1, 1, 1, 1, 1, 1, 1, 1, 1)
THERMAL_CAP_C = 75  # Will's sustained Tctl target; flag crossings in the summary

sys.path.insert(0, str(SINGULAR_SCRIPTS))
sys.path.insert(0, str(PHEXT_DIR))
from check_singular import WORD_RE          # noqa: E402  (the Singular tokenizer)
from task_coordinate import load_atlas, round_half_up, fmt  # noqa: E402
from parse_phext import parse as parse_phext  # noqa: E402
from build_skills_phext import implode  # noqa: E402

DELIM_BYTES = {0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17}

PROBE = (
    "load=$(cut -d' ' -f1 /proc/loadavg); echo load=$load; "
    "echo ncpu=$(nproc); "
    "ps -eo pcpu=,comm= --sort=-pcpu | head -3 | "
    "awk '{s=s $2 \":\" int($1+0.5) \" \"} END {print \"top=\" s}'; "
    "pgrep -x ollama >/dev/null && echo ollama=up || echo ollama=off; "
    "pgrep -f 'chunk_rende[r]|ffmpe[g]|blende[r]' >/dev/null && echo render=on || echo render=off; "
    "pgrep -f 'opencla[w]' >/dev/null && echo gateway=on || echo gateway=off; "
    "for d in /sys/class/hwmon/hwmon*; do "
    "if grep -qx amdgpu $d/name 2>/dev/null; then "
    "for f in $d/temp*_label; do "
    "if grep -qx edge $f 2>/dev/null; then ti=${f%_label}_input; "
    "echo gpu=$(( $(cat $ti 2>/dev/null) / 1000 )); fi; done; fi; done; true"
)

HOME_TEXT = """Home — state.phext: the ranch, distilled
kind: observed | origin: Muse (this agent) | maintained by: the state-phext-sampler cron (every 5 minutes) running ~/workspace/custom-skills/ranch-state-distillation/scripts/state_sampler.py
source of truth: this file. Raw pulls are working state only, kept outside the phext at ~/workspace/state-sampler/hidden_files/ — never inscribed here.

What this is: every 5 minutes the sampler probes the ranch fleet (17 nodes) through the ranch proxy, writes a one-or-two-line plain-language summary of the cluster (nodes up and down, what is running where, average CPU Tctl, the hotspot), computes the summary's holographic coordinate by Will's Singular method, and stores ONLY the distilled summary as a scroll at that coordinate. No raw telemetry lives in this phext; it stays small and reviewable long-term.

Layout: this Home scroll sits at 1.1.1/1.1.1/1.1.1. Every other scroll is one distilled state of the ranch. Its coordinate is the holographic merge of the summary's words — Singular tokenization (letters only; digits carry no words), the component-wise average of each distinct word's atlas position, rounded half up and never below 1, exactly the task-coordinate method — computed over the summary text WITHOUT its timestamp, so a state that reads the same distills to the same coordinate whenever it recurs.

Entry format: one line per pull — "YYYY-MM-DD HH:MM TZ | summary". When a new summary computes to a coordinate already occupied, its line is appended inside that scroll with its own timestamp; scrolls are never overwritten and lines are never dropped. Numbers (temperatures, counts) ride inside the line text; the coordinate merges words only, so states differing only in a degree or a count share a scroll, while a changed hotspot or a changed busy set moves the coordinate. If a state ever computed to the Home coordinate itself, it would be stored one scroll past it, at 1.1.1/1.1.1/1.1.2, with its true coordinate noted in the line — the meta line is reserved.

Reading it: scrolls cluster by resemblance — near-identical states sit at near-identical coordinates, so the phext reads as a map of the shapes the ranch takes over time.
"""


def probe_fleet():
    """One ranch fanout pass. Returns {node_name: result-dict} for every
    roster node (enabled or not)."""
    roster = json.loads(NODES_JSON.read_text(encoding="utf-8"))["nodes"]
    results = {}
    for node in roster:
        results[node["name"]] = {
            "name": node["name"], "enabled": bool(node.get("enabled")),
            "status": "down" if not node.get("enabled") else "unreachable",
            "tctl": None, "load": None, "ncpu": None, "top": "",
            "ollama": None, "render": None, "gateway": None, "gpu": None,
        }
    proc = subprocess.run(
        [str(RANCH), "fanout", PROBE],
        capture_output=True, text=True, timeout=240,
    )
    out = proc.stdout or ""
    blocks = re.split(r"^===== (.+?) =====$", out, flags=re.M)
    # blocks: [prelude, name, body, name, body, ...]
    for i in range(1, len(blocks) - 1, 2):
        name, body = blocks[i].strip(), blocks[i + 1]
        if name not in results:
            continue
        r = results[name]
        m = re.search(r"^----- rc=(-?\d+) \d+ms Tctl=([0-9.]+|None|-)$", body, flags=re.M)
        skipped = re.search(r"^SKIPPED \(([^)]*?)(?:, Tctl ([0-9.]+)C)?\)$", body, flags=re.M)
        if skipped:
            r["status"] = "thermal-hold"
            if skipped.group(2):
                r["tctl"] = float(skipped.group(2))
            continue
        if m:
            if m.group(2) not in ("-", "None"):
                r["tctl"] = float(m.group(2))
            if int(m.group(1)) != 0:
                r["status"] = "no-access" if "Permission denied" in body else "unreachable"
                continue
            r["status"] = "up"
        else:
            r["status"] = "unreachable"
            continue
        kv = dict(re.findall(r"^(\w+)=(\S.*)$", body, flags=re.M))
        if "load" in kv:
            try:
                r["load"] = float(kv["load"])
            except ValueError:
                pass
        if "ncpu" in kv:
            try:
                r["ncpu"] = int(kv["ncpu"])
            except ValueError:
                pass
        r["top"] = kv.get("top", "").strip()
        r["ollama"] = kv.get("ollama")
        r["render"] = kv.get("render")
        r["gateway"] = kv.get("gateway")
        if "gpu" in kv:
            try:
                r["gpu"] = int(kv["gpu"])
            except ValueError:
                pass
    return results


def classify(r):
    """(busy?, activity-label) for one probed node."""
    if r["status"] == "thermal-hold":
        return (False, "thermal-hold")
    if r["status"] != "up":
        return (False, r["status"])
    load = r["load"] or 0.0
    if r["render"] == "on":
        return (True, "render")
    if r["ollama"] == "up" and load >= 0.5:
        return (True, "inference")
    if r["ncpu"] and load >= 0.75 * r["ncpu"]:
        return (True, "compute")
    if load >= 2.0:
        return (True, "busy")
    return (False, "idle")


def summarize(results, total):
    ups = [r for r in results.values() if r["status"] in ("up", "thermal-hold")]
    downs = sorted(r["name"] for r in results.values() if r["status"] == "down")
    noacc = sorted(r["name"] for r in results.values()
                   if r["status"] in ("no-access", "unreachable"))
    busy = []
    for r in sorted(ups, key=lambda x: x["name"]):
        is_busy, label = classify(r)
        if is_busy:
            busy.append((label, r["name"]))
    temps = {r["name"]: r["tctl"] for r in ups if r["tctl"] is not None}
    clauses = [f"{len(ups)}/{total} nodes up"]
    if busy:
        shown = busy[:3]
        clause = "busy: " + ", ".join(f"{label} on {name}" for label, name in shown)
        if len(busy) > 3:
            clause += f", +{len(busy) - 3} more"
        clauses.append(clause)
    else:
        clauses.append("fleet idle")
    if temps:
        avg = round(sum(temps.values()) / len(temps))
        clauses.append(f"avg Tctl {avg}C across {len(temps)} reporting")
        hot_name, hot_t = max(temps.items(), key=lambda kv: kv[1])
        hot_clause = f"hotspot {hot_name} {round(hot_t)}C"
        if hot_t >= THERMAL_CAP_C:
            hot_clause += f" (over the {THERMAL_CAP_C}C cap)"
        clauses.append(hot_clause)
    gpus = {r["name"]: r["gpu"] for r in ups if r.get("gpu") is not None}
    if gpus:
        g_name, g_t = max(gpus.items(), key=lambda kv: kv[1])
        if g_t >= 65:
            clauses.append(f"gpu hotspot {g_name} {g_t}C")
    if downs:
        clauses.append("down: " + ", ".join(downs))
    if noacc:
        clauses.append("no-access: " + ", ".join(noacc))
    return "; ".join(clauses) + "."


def coordinate_of(text, atlas):
    tokens = [w.lower() for w in WORD_RE.findall(text)]
    distinct = list(dict.fromkeys(tokens))
    if not distinct:
        raise ValueError("summary produced no words")
    totals = [0] * 9
    for word in distinct:
        entry = atlas.get(word)
        coord = entry[0] if entry is not None else (9,) * 9
        for k in range(9):
            totals[k] += coord[k]
    n = len(distinct)
    return tuple(round_half_up(totals[k], n) for k in range(9))


def clean(text):
    return "".join(ch for ch in text if ord(ch) not in DELIM_BYTES)


def append_entry(summary, coord, timestamp):
    """Insert the timestamped summary line into state.phext at coord.
    Returns the coordinate actually used."""
    if STATE_PHEXT.exists():
        scrolls = {coord_str: t for coord_str, t in parse_phext(str(STATE_PHEXT))}
    else:
        scrolls = {}
    scrolls.setdefault(fmt(HOME_COORD), HOME_TEXT)
    used = coord
    if coord == HOME_COORD:
        used = (1, 1, 1, 1, 1, 1, 1, 1, 2)
    key = fmt(used)
    line = f"{timestamp} | {summary}"
    if key in scrolls and scrolls[key].strip():
        scrolls[key] = scrolls[key].rstrip("\n") + "\n" + line
    else:
        scrolls[key] = line
    blob = implode({k: clean(v) for k, v in scrolls.items()})
    tmp = STATE_PHEXT.with_suffix(".phext.tmp")
    tmp.write_bytes(blob)
    os.replace(tmp, STATE_PHEXT)
    return used


def save_raw(pull, keep_bytes=2_000_000):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    (WORK_DIR / "last-pull.json").write_text(
        json.dumps(pull, indent=1), encoding="utf-8")
    log = WORK_DIR / "pulls.jsonl"
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(pull) + "\n")
    if log.stat().st_size > keep_bytes:
        lines = log.read_text(encoding="utf-8").splitlines()
        log.write_text("\n".join(lines[-1000:]) + "\n", encoding="utf-8")


def main(argv):
    dry = "--dry-run" in argv
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    lock = open(WORK_DIR / "sampler.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("skipped: previous cycle still running")
        return 0
    now = datetime.now(TZ)
    results = probe_fleet()
    total = len(results)
    summary = summarize(results, total)
    atlas = load_atlas()
    coord = coordinate_of(summary, atlas)
    timestamp = now.strftime("%Y-%m-%d %H:%M %Z")
    pull = {"ts": now.isoformat(), "summary": summary,
            "coordinate": fmt(coord),
            "nodes": sorted(results.values(), key=lambda r: r["name"])}
    if dry:
        print(json.dumps(pull, indent=1))
        return 0
    used = append_entry(summary, coord, timestamp)
    save_raw(pull)
    print(f"{fmt(used)} | {timestamp} | {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
