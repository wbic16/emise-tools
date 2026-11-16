#!/usr/bin/env python3
"""hub_worker.py — hub-side worker for the nightly GitHub archive.

Runs ON aletheia-core. Reads a payload ({"date": "YYYY-MM-DD",
"repos": [names...]}) from ~/github-archive-run/payload.json, then:

  1. Maintains bare mirror clones under ~/github-archive/mirrors/<name>.git
     (git clone --mirror the first time, git remote update --prune after),
     cloned over SSH as wbic16. Per-repo failures are logged, never fatal.
  2. Writes a dated snapshot: rsync -a --link-dest=<previous snapshot>
     mirrors/ into ~/github-archive/snapshots/<date>/mirrors/ so unchanged
     files are hardlinks and cost ~nothing.
  3. Writes manifest.json into the snapshot (per-repo HEAD SHA, size,
     status, seconds; plus totals) and ~/github-archive/last-run.json.

Exit code: 0 when every repo succeeded, 2 when any repo failed (the
snapshot and manifest are still written with whatever succeeded).
Idempotent and resumable: mirrors update in place, a re-run re-syncs
the same dated snapshot, and a flock prevents concurrent workers.
"""
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
BASE = os.path.join(HOME, "github-archive")
MIRRORS = os.path.join(BASE, "mirrors")
SNAPSHOTS = os.path.join(BASE, "snapshots")
PAYLOAD = os.path.join(HOME, "github-archive-run", "payload.json")
CLONE_TIMEOUT = 3600   # openpilot alone is ~2.3 GiB
UPDATE_TIMEOUT = 900
ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0")


def run(cmd, timeout):
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, env=ENV)


def du_bytes(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def is_bare_mirror(path):
    if not os.path.isdir(path):
        return False
    try:
        r = run(["git", "-C", path, "rev-parse", "--is-bare-repository"], 30)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except Exception:
        return False


def mirror_one(name):
    """Clone or update one mirror. Returns a result dict."""
    dest = os.path.join(MIRRORS, name + ".git")
    url = f"git@github.com:wbic16/{name}.git"
    t0 = time.time()
    status, action, err = "ok", None, ""
    try:
        if is_bare_mirror(dest):
            action = "update"
            r = run(["git", "-C", dest, "remote", "update", "--prune"],
                    UPDATE_TIMEOUT)
            if r.returncode != 0:
                status, err = "failed", r.stderr.strip()[-400:]
        else:
            if os.path.exists(dest):
                aside = dest + ".broken-" + datetime.now(
                    timezone.utc).strftime("%Y%m%d%H%M%S")
                shutil.move(dest, aside)
                err = f"previous non-mirror moved aside to {aside}; "
            action = "clone"
            r = run(["git", "clone", "--mirror", url, dest], CLONE_TIMEOUT)
            if r.returncode != 0:
                status, err = "failed", err + r.stderr.strip()[-400:]
    except subprocess.TimeoutExpired:
        status, err = "failed", f"timeout during {action}"
    except Exception as e:  # never let one repo abort the run
        status, err = "failed", f"{type(e).__name__}: {e}"
    head = None
    if status == "ok":
        try:
            r = run(["git", "-C", dest, "rev-parse", "HEAD"], 30)
            if r.returncode == 0:
                head = r.stdout.strip()
            else:
                err = (err + " empty repository (no HEAD)").strip()
        except Exception:
            pass
    size = du_bytes(dest) if os.path.isdir(dest) else 0
    return {"head": head, "size_bytes": size, "status": status,
            "action": action, "seconds": round(time.time() - t0, 2),
            "error": err}


def main():
    payload_path = sys.argv[1] if len(sys.argv) > 1 else PAYLOAD
    with open(payload_path) as f:
        payload = json.load(f)
    date = payload["date"]
    names = payload["repos"]
    os.makedirs(MIRRORS, exist_ok=True)
    os.makedirs(SNAPSHOTS, exist_ok=True)
    lock = open(os.path.join(BASE, ".worker.lock"), "w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # raises if busy

    print(f"[{date}] archiving {len(names)} repos", flush=True)
    results, failures = {}, []
    t_start = time.time()
    for i, name in enumerate(names, 1):
        res = mirror_one(name)
        results[name] = res
        if res["status"] != "ok":
            failures.append(name)
        print(f"({i}/{len(names)}) {name}: {res['status']} "
              f"{res['action']} {res['seconds']}s {res['size_bytes']}B "
              f"{res['error']}", flush=True)

    # Dated snapshot with hardlink delta against the previous snapshot.
    snap = os.path.join(SNAPSHOTS, date)
    os.makedirs(snap, exist_ok=True)
    prevs = sorted(d for d in os.listdir(SNAPSHOTS)
                   if d < date and os.path.isdir(os.path.join(SNAPSHOTS, d)))
    cmd = ["rsync", "-a"]
    if prevs:
        cmd.append("--link-dest=" + os.path.join(SNAPSHOTS, prevs[-1],
                                                 "mirrors"))
    cmd += [MIRRORS + "/", os.path.join(snap, "mirrors") + "/"]
    r = run(cmd, 3600)
    if r.returncode != 0:
        print("rsync FAILED: " + r.stderr.strip()[-400:], flush=True)
        return 3

    total = sum(v["size_bytes"] for v in results.values())
    manifest = {
        "date": date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_count_enumerated": len(names),
        "repo_count_ok": len(names) - len(failures),
        "total_bytes": total,
        "duration_seconds": round(time.time() - t_start, 1),
        "failures": failures,
        "repos": results,
    }
    with open(os.path.join(snap, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(BASE, "last-run.json"), "w") as f:
        json.dump({k: manifest[k] for k in
                   ("date", "generated_at", "repo_count_enumerated",
                    "repo_count_ok", "total_bytes", "duration_seconds",
                    "failures")}, f, indent=1)
    print(f"[{date}] done: {len(names) - len(failures)}/{len(names)} ok, "
          f"{total} bytes, {manifest['duration_seconds']}s, "
          f"failures={failures}", flush=True)
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
