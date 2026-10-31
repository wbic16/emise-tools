#!/usr/bin/env python3
"""Push a whole local directory tree to a branch of any repo via the Git Data API.

Generalization of push_file.py: reads the branch's current HEAD fresh, parents
the new commit on it, and updates the ref with force disabled, per the standing
rule (fetch and rebase before pushing; never force push). Commits are authored
as Emise <emise@localhost>; the API actor is the token owner.

Usage: push_tree.py <owner/repo> <branch> <local-dir> <commit-message>
All files under <local-dir> (excluding .git) become blobs at their relative
paths. Prints the new commit sha. Exits non-zero without touching the ref on
any failure before the ref update.
"""
import base64, json, sys, os, datetime
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin"); sys.path.insert(0, ".")
from github_api import call  # same directory

def must(status, out, step):
    if status >= 300:
        print(f"FAILED at {step}: HTTP {status} {out}")
        sys.exit(1)
    return out

if __name__ == "__main__":
    repo, branch, local_dir, message = sys.argv[1:5]
    REPO = f"/repos/{repo}"

    status, ref = call("GET", f"{REPO}/git/ref/heads/{branch}")
    head_sha = must(status, ref, "get ref")["object"]["sha"]
    status, head = call("GET", f"{REPO}/git/commits/{head_sha}")
    base_tree = must(status, head, "get head commit")["tree"]["sha"]

    entries = []
    for root, dirs, files in os.walk(local_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in sorted(files):
            full = os.path.join(root, name)
            rel = os.path.relpath(full, local_dir)
            content = open(full, "rb").read()
            status, blob = call("POST", f"{REPO}/git/blobs",
                                {"content": base64.b64encode(content).decode(), "encoding": "base64"})
            blob_sha = must(status, blob, f"create blob {rel}")["sha"]
            entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob_sha})
    print(f"{len(entries)} blobs created", file=sys.stderr)

    status, tree = call("POST", f"{REPO}/git/trees",
                        {"base_tree": base_tree, "tree": entries})
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
    print(json.dumps({"repo": repo, "branch": branch, "files": len(entries),
                      "parent": head_sha, "commit": commit_sha}))
