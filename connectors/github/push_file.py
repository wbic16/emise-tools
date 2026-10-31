#!/usr/bin/env python3
"""Push one file to a branch of wbic16/human via the Git Data API.

Creates blob -> tree (on top of the branch HEAD tree) -> commit -> ref update.
The commit is authored as Emise <emise@localhost>; the API actor is the token
owner (wbic16), which is how GitHub records the push.

Usage: push_file.py <branch> <repo-path> <local-file> <commit-message>
Prints the new commit sha. Exits non-zero without touching the ref on any
failure before the ref update.
"""
import base64, json, sys, datetime
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin"); sys.path.insert(0, ".")
from github_api import call  # same directory

REPO = "/repos/wbic16/human"

def must(status, out, step):
    if status >= 300:
        print(f"FAILED at {step}: HTTP {status} {out}")
        sys.exit(1)
    return out

if __name__ == "__main__":
    branch, repo_path, local_file, message = sys.argv[1:5]
    content = open(local_file, "rb").read()

    status, ref = call("GET", f"{REPO}/git/ref/heads/{branch}")
    head_sha = must(status, ref, "get ref")["object"]["sha"]
    status, head = call("GET", f"{REPO}/git/commits/{head_sha}")
    base_tree = must(status, head, "get head commit")["tree"]["sha"]

    status, blob = call("POST", f"{REPO}/git/blobs",
                        {"content": base64.b64encode(content).decode(), "encoding": "base64"})
    blob_sha = must(status, blob, "create blob")["sha"]

    status, tree = call("POST", f"{REPO}/git/trees",
                        {"base_tree": base_tree,
                         "tree": [{"path": repo_path, "mode": "100644",
                                   "type": "blob", "sha": blob_sha}]})
    tree_sha = must(status, tree, "create tree")["sha"]

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))
    stamp = now.isoformat(timespec="seconds")
    ident = {"name": "Emise", "email": "emise@localhost", "date": stamp}
    status, commit = call("POST", f"{REPO}/git/commits",
                          {"message": message, "tree": tree_sha,
                           "parents": [head_sha], "author": ident, "committer": ident})
    commit_sha = must(status, commit, "create commit")["sha"]

    status, updated = call("PATCH", f"{REPO}/git/refs/heads/{branch}",
                           {"sha": commit_sha, "force": False})
    must(status, updated, "update ref")
    print(json.dumps({"branch": branch, "path": repo_path,
                      "parent": head_sha, "commit": commit_sha}))
