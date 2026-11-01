#!/usr/bin/env python3
"""Fetch one file's raw bytes from a repo ref via the Contents API.

Writes bytes to the output path (never stdout, so large files survive).
Usage: fetch_file.py <owner/repo> <ref> <repo-path> <out-file>
"""
import base64, sys
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin"); sys.path.insert(0, ".")
from github_api import call  # same directory

if __name__ == "__main__":
    repo, ref, path, out = sys.argv[1:5]
    status, resp = call("GET", f"/repos/{repo}/contents/{path}?ref={ref}")
    if status >= 300:
        print(f"FAILED: HTTP {status} {resp}")
        sys.exit(1)
    data = base64.b64decode(resp["content"])
    open(out, "wb").write(data)
    print(f"{path}@{ref}: {len(data)} bytes -> {out} (blob {resp['sha']})")
