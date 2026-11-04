#!/usr/bin/env python3
"""Incrementally publish new local commits onto an existing remote branch.

Finds the local commit whose tree equals the remote branch head's tree
(the already-published prefix), then replays only the later commits
(blobs -> tree -> commit) parented on the fresh remote HEAD, force
disabled — the standing publish rule. Authored as Emise, preserving each
local commit's message and author date. Deterministic: re-running after
a partial failure recreates identical commit SHAs.

Usage: publish_incremental.py <owner/repo> <local-repo-dir> <branch>
"""
import base64, json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.github/bin")
from github_api import call

def must(status, out, step):
    if status >= 300:
        print(f"FAILED at {step}: HTTP {status} {out}")
        sys.exit(1)
    return out

def git(repo_dir, *args):
    return subprocess.run(["git", "-C", repo_dir, *args],
                          capture_output=True, check=True).stdout

def main():
    repo, repo_dir, branch = sys.argv[1:4]
    R = f"/repos/{repo}"

    commits = git(repo_dir, "rev-list", "--reverse", "main..HEAD").decode().split()
    local_trees = {c: git(repo_dir, "rev-parse", f"{c}^{{tree}}").decode().strip()
                   for c in commits}

    status, ref = call("GET", f"{R}/git/ref/heads/{branch}")
    head_sha = must(status, ref, "get branch ref")["object"]["sha"]
    status, head = call("GET", f"{R}/git/commits/{head_sha}")
    remote_tree = must(status, head, "get head commit")["tree"]["sha"]
    print(f"remote head {head_sha} tree {remote_tree}")

    matches = [c for c in commits if local_trees[c] == remote_tree]
    if not matches:
        print("ABORT: no local commit tree matches the remote head tree; "
              "the branch moved or diverged — refusing to publish.")
        sys.exit(1)
    base_local = matches[-1]
    todo = commits[commits.index(base_local) + 1:]
    print(f"published prefix ends at local {base_local[:7]}; "
          f"{len(todo)} commit(s) to replay")
    if not todo:
        print(json.dumps({"repo": repo, "branch": branch, "head": head_sha,
                          "commits": [], "note": "already up to date"}))
        return

    prev_tree, prev_sha = remote_tree, head_sha
    replayed = []
    for c in todo:
        files = git(repo_dir, "diff-tree", "--no-commit-id", "--name-only",
                    "-r", c).decode().split()
        entries = []
        for path in files:
            mode = git(repo_dir, "ls-tree", c, "--", path).decode().split()[0]
            content = git(repo_dir, "show", f"{c}:{path}")
            status, blob = call("POST", f"{R}/git/blobs",
                                {"content": base64.b64encode(content).decode(),
                                 "encoding": "base64"})
            blob_sha = must(status, blob, f"blob {path}")["sha"]
            entries.append({"path": path, "mode": mode, "type": "blob",
                            "sha": blob_sha})
        status, tree = call("POST", f"{R}/git/trees",
                            {"base_tree": prev_tree, "tree": entries})
        tree_sha = must(status, tree, f"tree for {c}")["sha"]
        if tree_sha != local_trees[c]:
            print(f"ABORT: replayed tree {tree_sha} != local tree "
                  f"{local_trees[c]} for {c[:7]}; ref NOT updated.")
            sys.exit(1)
        message = git(repo_dir, "log", "-1", "--format=%B", c).decode()
        date = git(repo_dir, "log", "-1", "--format=%aI", c).decode().strip()
        ident = {"name": "Emise", "email": "emise@localhost", "date": date}
        status, commit = call("POST", f"{R}/git/commits",
                              {"message": message, "tree": tree_sha,
                               "parents": [prev_sha],
                               "author": ident, "committer": ident})
        new_sha = must(status, commit, f"commit for {c}")["sha"]
        replayed.append(new_sha)
        prev_tree, prev_sha = tree_sha, new_sha
        print(f"replayed {c[:7]} -> {new_sha} ({len(files)} files)")

    status, updated = call("PATCH", f"{R}/git/refs/heads/{branch}",
                           {"sha": prev_sha, "force": False})
    must(status, updated, "update ref")
    print(json.dumps({"repo": repo, "branch": branch, "head": prev_sha,
                      "commits": replayed}))

if __name__ == "__main__":
    main()
