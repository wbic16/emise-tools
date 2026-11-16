#!/usr/bin/env python3
"""github_archive.py — nightly full-snapshot archive of all wbic16
GitHub repositories, landing on aletheia-core (task 31.14.14/12.15.14/
9.9.11, stage 1).

Pipeline:
  1. Enumerate every repo wbic16 owns via the GitHub GraphQL API,
     using the custom.github connector helper as a library (its CLI
     truncates printed output at 4000 chars; the parsed response does
     not truncate). The collected count is asserted against the API's
     own totalCount.
  2. Ship hub_worker.py + a payload (date + repo names) to the hub and
     start the worker there, detached: bare mirror clones under
     ~/github-archive/mirrors/, updated in place, then a dated
     hardlink-delta snapshot under ~/github-archive/snapshots/ with a
     manifest.json. All bulk transfer happens hub<->GitHub over SSH.

Usage:
  github_archive.py            enumerate + start tonight's run on the hub
  github_archive.py --wait     ... and poll until the worker finishes
  github_archive.py --status   print the hub's last-run summary

Exit code mirrors the worker's when --wait is used (0 = all repos ok,
2 = some repo failed, snapshot still written).
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.expanduser(
    "~/workspace/custom-connectors/custom.github/bin/github_api.py")
FLEET_SSH = os.path.expanduser(
    "~/workspace/bickford-llama-ranch/deploy/fleet-ssh.sh")
HUB = "aletheia-core"
HUB_IP = "100.88.154.1"
SSH_BASE = ["ssh", "-i", os.path.expanduser("~/.ssh/id_ed25519"),
            "-o", "IdentitiesOnly=yes",
            "-o", "ProxyCommand=nc -X connect -x hatch-egress-proxy:3130 %h %p"]
SCP_BASE = ["scp", "-i", os.path.expanduser("~/.ssh/id_ed25519"),
            "-o", "IdentitiesOnly=yes",
            "-o", "ProxyCommand=nc -X connect -x hatch-egress-proxy:3130 %h %p"]
REMOTE_DIR = "/home/wbic16/github-archive-run"
OWNER = "wbic16"

QUERY = ("query($c:String){viewer{repositories(ownerAffiliations:OWNER,"
         "first:100,after:$c){totalCount pageInfo{hasNextPage endCursor} "
         "nodes{name}}}}")


def enumerate_repos():
    spec = importlib.util.spec_from_file_location("github_api", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    names, cursor, total = [], None, None
    while True:
        status, out = mod.call("POST", "/graphql",
                               {"query": QUERY, "variables": {"c": cursor}})
        if status != 200:
            raise RuntimeError(f"GraphQL HTTP {status}: {out}")
        repos = out["data"]["viewer"]["repositories"]
        total = repos["totalCount"]
        names += [n["name"] for n in repos["nodes"]]
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    if len(names) != total:
        raise RuntimeError(
            f"enumeration incomplete: collected {len(names)} of {total}")
    if len(set(names)) != len(names):
        raise RuntimeError("enumeration returned duplicate names")
    return sorted(names)


def hub_ssh(remote_cmd_argv, **kw):
    return subprocess.run([FLEET_SSH, HUB] + remote_cmd_argv, **kw)


def ship_and_start(date, names):
    payload = {"date": date, "repos": names}
    local_payload = os.path.join(HERE, "payload.json")
    with open(local_payload, "w") as f:
        json.dump(payload, f, indent=1)
    hub_ssh(["mkdir", "-p", REMOTE_DIR], check=True)
    for src, dst in ((os.path.join(HERE, "hub_worker.py"),
                      f"{REMOTE_DIR}/hub_worker.py"),
                     (local_payload, f"{REMOTE_DIR}/payload.json")):
        subprocess.run(SCP_BASE + [src, f"wbic16@{HUB_IP}:{dst}"], check=True)
    # Start detached; the worker logs to ~/github-archive/logs/run-<date>.log
    start = ("#!/bin/bash\n"
             "mkdir -p ~/github-archive/logs\n"
             f"nohup {REMOTE_DIR}/hub_worker.py "
             f"> ~/github-archive/logs/run-{date}.log 2>&1 &\n"
             "echo started\n")
    start_path = os.path.join(HERE, "start_run.sh")
    with open(start_path, "w") as f:
        f.write(start)
    os.chmod(start_path, 0o755)
    subprocess.run(SCP_BASE + [start_path,
                               f"wbic16@{HUB_IP}:{REMOTE_DIR}/start_run.sh"],
                   check=True)
    hub_ssh([f"{REMOTE_DIR}/start_run.sh"], check=True)


def hub_status():
    r = hub_ssh(["cat", "/home/wbic16/github-archive/last-run.json"],
                capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def worker_running():
    r = hub_ssh(["pgrep", "-f", "hub_worker.py"],
                capture_output=True, text=True)
    return r.returncode == 0


def main():
    date = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d")
    if "--status" in sys.argv:
        print(json.dumps(hub_status(), indent=1))
        return 0
    names = enumerate_repos()
    print(f"enumerated {len(names)} repos owned by {OWNER}")
    ship_and_start(date, names)
    print(f"worker started on {HUB} for snapshot {date}")
    if "--wait" not in sys.argv:
        return 0
    while worker_running():
        time.sleep(30)
    status = hub_status()
    print(json.dumps(status, indent=1))
    if status is None:
        return 3
    return 0 if not status["failures"] else 2


if __name__ == "__main__":
    sys.exit(main())
