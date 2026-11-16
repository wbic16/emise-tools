#!/usr/bin/env python3
"""verify_restore.py — prove a dated snapshot restores.

Runs ON aletheia-core. Usage: verify_restore.py <date> <repo> [repo...]

For each repo: clone from ~/github-archive/snapshots/<date>/mirrors/
<repo>.git into a scratch dir, check the clone's HEAD equals the
manifest's recorded HEAD, and run git fsck --strict in the clone.
Prints one verdict line per repo; exit 0 only if all pass.
"""
import json
import os
import subprocess
import sys

BASE = os.path.expanduser("~/github-archive")


def check(date, name):
    snap = os.path.join(BASE, "snapshots", date)
    with open(os.path.join(snap, "manifest.json")) as f:
        manifest = json.load(f)
    want = manifest["repos"][name]["head"]
    scratch = os.path.join(BASE, "verify-" + date, name)
    os.makedirs(os.path.dirname(scratch), exist_ok=True)
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    r = subprocess.run(["git", "clone", "--quiet",
                        os.path.join(snap, "mirrors", name + ".git"),
                        scratch], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return f"{name}: CLONE FAILED {r.stderr.strip()[-200:]}"
    head = subprocess.run(["git", "-C", scratch, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    fsck = subprocess.run(["git", "-C", scratch, "fsck", "--strict"],
                          capture_output=True, text=True)
    ok = head == want and fsck.returncode == 0
    return (f"{name}: head={'MATCH' if head == want else 'MISMATCH'} "
            f"({head[:12]}) fsck={'PASS' if fsck.returncode == 0 else 'FAIL'} "
            f"-> {'OK' if ok else 'BAD'}")


if __name__ == "__main__":
    date, names = sys.argv[1], sys.argv[2:]
    verdicts = [check(date, n) for n in names]
    for v in verdicts:
        print(v, flush=True)
    sys.exit(0 if all(v.endswith("OK") for v in verdicts) else 1)
