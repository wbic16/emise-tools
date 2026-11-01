#!/usr/bin/env python3
"""Collect live status for Emise's perpetual dashboard.

Reads only local, already-maintained sources:
- SQ daemon status (subprocess, read-only)
- deploy-study sentinel ledger (last line) for substrate + watcher heartbeat
- Discord spool size
- curated.json (waiting-on-Will, shipped, schedules, goals) maintained by Emise

Writes status.json next to this script. Safe to run any time; stdlib only.
"""
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.expanduser("~/workspace/deploy-study/ledger.jsonl")
SPOOL = os.path.expanduser("~/workspace/discord/spool.jsonl")


def sq_status():
    env = dict(os.environ)
    env["PATH"] = os.path.expanduser("~/.cargo/bin") + ":" + env.get("PATH", "")
    try:
        out = subprocess.run(
            ["sq", "status"], cwd=os.path.expanduser("~/workspace/phext"),
            capture_output=True, text=True, timeout=15, env=env,
        ).stdout
        info = {"running": "Hosting:" in out}
        for line in out.splitlines():
            if "Hosting:" in line:
                info["hosting"] = line.split("Hosting:", 1)[1].strip()
            elif "Phext Size:" in line:
                info["size_bytes"] = int(line.split(":", 1)[1].strip())
            elif "Scrolls:" in line:
                info["scrolls"] = int(line.split(":", 1)[1].strip())
        return info
    except Exception as e:  # daemon down or binary missing
        return {"running": False, "error": type(e).__name__}


def sentinel():
    try:
        with open(LEDGER, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 8192))
            lines = f.read().decode("utf-8", "replace").strip().splitlines()
        last = json.loads(lines[-1])
        return {
            "boot_id": (last.get("boot_id") or "")[:8],
            "uptime_s": last.get("uptime_s"),
            "watcher_heartbeat_age_s": last.get("watcher_heartbeat_age_s"),
            "host_mem_available_kb": last.get("host_mem_available_kb"),
            "host_oom_kills": last.get("host_oom_kills"),
            "ns_rss_kb": last.get("ns_rss_total_kb"),
            "sq_running": last.get("sq_running"),
            "sentinel_ts": last.get("ts_iso"),
        }
    except Exception as e:
        return {"error": type(e).__name__}


def main():
    status = {"collected_at_epoch": int(time.time())}
    status["sq"] = sq_status()
    status["substrate"] = sentinel()
    try:
        status["discord"] = {
            "spool_bytes": os.path.getsize(SPOOL) if os.path.exists(SPOOL) else 0,
            "watcher_heartbeat_age_s": status["substrate"].get("watcher_heartbeat_age_s"),
        }
    except Exception:
        status["discord"] = {}
    try:
        with open(os.path.join(HERE, "curated.json")) as f:
            status["curated"] = json.load(f)
    except Exception as e:
        status["curated"] = {"error": type(e).__name__}
    with open(os.path.join(HERE, "status.json"), "w") as f:
        json.dump(status, f, indent=2)
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
