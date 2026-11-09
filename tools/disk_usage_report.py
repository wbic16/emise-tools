#!/usr/bin/env python3
"""Daily disk-usage report for Emise's home volume (Will, 2026-11-08).

Born of the 2026-11-08 EDQUOT incident: writes began failing with
"Disk quota exceeded" at ~106 GB home usage while df still showed
45 GB free — a quota below the filesystem size, tripped by bytes
and/or file count. This report watches both, plus a live write probe
(the true canary: creating a new file is what failed first).

State (last run's numbers + history) lives beside this script in
~/workspace/disk-watch/. Prints a compact plain-text report.
Exit code: 0 = report produced (any level), 2 = probe failed (RED).
"""
import json, os, subprocess, sys, time
from pathlib import Path

HOME = Path.home()
WORKSPACE = HOME / "workspace"
STATE_DIR = HOME / "workspace" / "disk-watch"
STATE_FILE = STATE_DIR / "state.json"
HISTORY_FILE = STATE_DIR / "history.tsv"
GB = 1024 ** 3

# Thresholds anchored to the observed 2026-11-08 failure at ~106 GB used.
RED_USED_GB = 102.0
AMBER_USED_GB = 95.0
GROWTH_ALERT_GB = 5.0      # a top-level dir growing this much in a day
BIG_FILE_GB = 1.0          # single files at least this large are listed
NEW_BIG_FILE_GB = 5.0      # a new single file this large is an AMBER flag


def df_home():
    out = subprocess.run(["df", "-B1", str(HOME)], capture_output=True, text=True).stdout.splitlines()
    parts = out[1].split()
    total, used, avail = (int(parts[i]) / GB for i in (1, 2, 3))
    return total, used, avail, parts[4]


def write_probe():
    probe = WORKSPACE / ".disk-watch-probe"
    try:
        probe.write_bytes(b"ok")
        probe.unlink()
        return True
    except OSError:
        return False


def top_dirs():
    """Top-level workspace dirs by size (bytes), largest first."""
    sizes = {}
    entries = [e for e in WORKSPACE.iterdir() if e.is_dir() and not e.is_symlink()]
    for e in entries:
        try:
            out = subprocess.run(["du", "-s", "-B1", str(e)], capture_output=True, text=True, timeout=600)
            sizes[e.name] = int(out.stdout.split()[0])
        except Exception:
            pass
    return dict(sorted(sizes.items(), key=lambda kv: -kv[1])[:10])


def scan_files():
    """One find pass over home: total file count + files >= BIG_FILE_GB."""
    count = 0
    big = []
    proc = subprocess.run(
        ["find", str(HOME), "-xdev", "-type", "f", "-printf", "%s\t%p\n"],
        capture_output=True, text=True, timeout=900)
    for line in proc.stdout.splitlines():
        count += 1
        try:
            size, path = line.split("\t", 1)
            size = int(size)
            if size >= BIG_FILE_GB * GB:
                big.append((size, path))
        except ValueError:
            pass
    big.sort(reverse=True)
    return count, big[:8]


def trash_size():
    trash = HOME / ".local" / "share" / "Trash"
    if not trash.exists():
        return 0
    out = subprocess.run(["du", "-s", "-B1", str(trash)], capture_output=True, text=True)
    try:
        return int(out.stdout.split()[0])
    except Exception:
        return 0


def fmt(gb):
    return f"{gb:.1f} GB" if gb >= 10 else f"{gb:.2f} GB"


def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    prev = {}
    if STATE_FILE.exists():
        try:
            prev = json.loads(STATE_FILE.read_text())
        except Exception:
            prev = {}

    total, used, avail, pct = df_home()
    probe_ok = write_probe()
    tops = top_dirs()
    files, big = scan_files()
    trash = trash_size() / GB

    flags = []
    if not probe_ok or used >= RED_USED_GB:
        level = "RED"
        if not probe_ok:
            flags.append("write probe FAILED — new-file creation is blocked (the 2026-11-08 failure mode)")
        if used >= RED_USED_GB:
            flags.append(f"usage {fmt(used)} is in the red zone (failures observed at ~106 GB)")
    elif used >= AMBER_USED_GB:
        level = "AMBER"
        flags.append(f"usage {fmt(used)} is in the amber zone")
    else:
        level = "GREEN"

    prev_tops = prev.get("top", {})
    for name, size in tops.items():
        grew = size / GB - prev_tops.get(name, 0)
        if prev_tops and grew >= GROWTH_ALERT_GB:
            flags.append(f"{name} grew {fmt(grew)} since yesterday (now {fmt(size / GB)})")
            if level == "GREEN":
                level = "AMBER"
    prev_big = {p for _, p in prev.get("big", [])}
    for size, path in big:
        if path not in prev_big and size >= NEW_BIG_FILE_GB * GB:
            flags.append(f"new large file: {path} ({fmt(size / GB)})")
            if level == "GREEN":
                level = "AMBER"

    delta = used - prev.get("used_gb", used)
    lines = [f"Disk usage — {time.strftime('%Y-%m-%d %H:%M %Z')} — {level}"]
    lines.append(f"Home: {fmt(used)} used of {fmt(total)} ({pct}), {fmt(avail)} free"
                 + (f", {delta:+.1f} GB since yesterday" if prev else " (first report — baseline)"))
    lines.append(f"Write probe: {'OK' if probe_ok else 'FAILED'} · files under home: {files:,}"
                 f" · trash holds {fmt(trash)} (still on disk until purged/expired)")
    lines.append("Largest workspace directories:")
    for name, size in tops.items():
        lines.append(f"  {name}: {fmt(size / GB)}")
    if big:
        lines.append("Largest single files (≥1 GB):")
        for size, path in big:
            lines.append(f"  {fmt(size / GB)}  {path.replace(str(HOME), '~')}")
    if flags:
        lines.append("Flags:")
        for f in flags:
            lines.append(f"  ⚠ {f}")
    else:
        lines.append("No flags. Nothing within sight of the quota that failed at ~106 GB on 2026-11-08.")

    state = {"date": time.strftime("%Y-%m-%d"), "used_gb": used, "files": files,
             "top": {k: v / GB for k, v in tops.items()}, "big": big, "level": level}
    STATE_FILE.write_text(json.dumps(state, indent=1))
    with HISTORY_FILE.open("a") as fh:
        fh.write(f"{state['date']}\t{used:.2f}\t{avail:.2f}\t{files}\t{int(probe_ok)}\t{level}\n")

    print("\n".join(lines))
    return 0 if probe_ok else 2


if __name__ == "__main__":
    sys.exit(main())
