#!/usr/bin/env python3
"""Publish a local branch's commits to a GitHub repo via the Git Data API.

Replays each local commit (blobs -> tree -> commit) onto a fresh remote
branch, parented on the remote main HEAD read fresh at publish time, with
force disabled — the standing publish rule. Authored as Emise, preserving
each local commit's message and author date.

Usage: publish_branch.py <owner/repo> <local-repo-dir> <branch>
Aborts if the remote branch already exists anywhere other than the base
commit or one of the replayed commits (resume-safe for our own partials).
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

    local_base = git(repo_dir, "rev-parse", "main").decode().strip()
    commits = git(repo_dir, "rev-list", "--reverse", "main..HEAD").decode().split()

    status, ref = call("GET", f"{R}/git/ref/heads/main")
    remote_base = must(status, ref, "get main ref")["object"]["sha"]
    if remote_base != local_base:
        print(f"ABORT: remote main {remote_base} != local main {local_base}")
        sys.exit(1)

    status, ref = call("GET", f"{R}/git/ref/heads/{branch}")
    if status == 404:
        status, ref = call("POST", f"{R}/git/refs",
                           {"ref": f"refs/heads/{branch}", "sha": remote_base})
        must(status, ref, "create branch ref")
        head_sha = remote_base
        print(f"branch created at base {remote_base}")
    elif status == 200:
        head_sha = ref["object"]["sha"]
        print(f"branch exists at {head_sha}; resuming if it is one of ours")
    else:
        must(status, ref, "get branch ref")

    status, head = call("GET", f"{R}/git/commits/{head_sha}")
    prev_tree = must(status, head, "get head commit")["tree"]["sha"]
    prev_sha = head_sha

    replayed = []
    for c in commits:
        changes = git(repo_dir, "diff-tree", "--no-commit-id", "--name-status",
                      "-r", c).decode().splitlines()
        entries = []
        for line in changes:
            status, path = line.split("\t", 1)
            if status == "D":
                # A null sha in a tree creation deletes the path.
                entries.append({"path": path, "mode": "100644",
                                "type": "blob", "sha": None})
                continue
            mode = git(repo_dir, "ls-tree", c, "--", path).decode().split()[0]
            content = git(repo_dir, "show", f"{c}:{path}")
            status_code, blob = call("POST", f"{R}/git/blobs",
                                {"content": base64.b64encode(content).decode(), "encoding": "base64"})
            blob_sha = must(status_code, blob, f"blob {path}")["sha"]
            entries.append({"path": path, "mode": mode, "type": "blob", "sha": blob_sha})
        status, tree = call("POST", f"{R}/git/trees", {"base_tree": prev_tree, "tree": entries})
        tree_sha = must(status, tree, f"tree for {c}")["sha"]
        local_tree = git(repo_dir, "rev-parse", f"{c}^{{tree}}").decode().strip()
        if tree_sha != local_tree:
            print(f"ABORT: replayed tree {tree_sha} != local tree "
                  f"{local_tree} for {c[:7]}; ref NOT updated.")
            sys.exit(1)
        message = git(repo_dir, "log", "-1", "--format=%B", c).decode()
        date = git(repo_dir, "log", "-1", "--format=%aI", c).decode().strip()
        ident = {"name": "Emise", "email": "emise@localhost", "date": date}
        status, commit = call("POST", f"{R}/git/commits",
                              {"message": message, "tree": tree_sha, "parents": [prev_sha],
                               "author": ident, "committer": ident})
        new_sha = must(status, commit, f"commit for {c}")["sha"]
        replayed.append(new_sha)
        prev_tree, prev_sha = tree_sha, new_sha
        print(f"replayed {c[:7]} -> {new_sha} ({len(entries)} files)")

    if prev_sha != head_sha:
        status, updated = call("PATCH", f"{R}/git/refs/heads/{branch}",
                               {"sha": prev_sha, "force": False})
        must(status, updated, "update ref")
    print(json.dumps({"repo": repo, "branch": branch, "head": prev_sha, "commits": replayed}))

if __name__ == "__main__":
    main()
