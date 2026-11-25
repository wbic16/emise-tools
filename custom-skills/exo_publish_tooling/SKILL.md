# Publish Tooling — every tool ships to emise-tools the session it is built

Standing order (Will, 2026-10-31): when you build or materially update a tool or skill, sync it to wbic16/emise-tools@exo in the same work session. Exclusions: live state files, logs, secrets, large data artifacts, and deliberately unpublished material (orai-dm). Skills sync under `custom-skills/<name>/`, mirroring `~/workspace/custom-skills/`.

## Before choosing where work lives

- Scan the site map for an existing repo before choosing a home (Will, 2026-10-31): check ~/workspace/site-map (SITE-MAP.md / sitemap.json) for a wbic16 repository that already covers the domain. If a fitting repo exists but the GitHub token can't reach it, ask Will for access instead of defaulting to emise-tools or a new repo.

## The publish itself

- Tooling: `~/workspace/custom-connectors/custom.github/bin/push_tree.py <owner/repo> <branch> <local-dir> <message>` (Git Data API; read the connector doc at ~/workspace/custom-connectors/custom.github/CONNECTOR.md). It reads the branch's current remote HEAD fresh, parents the new commit on it, and updates the ref with force disabled.
- Fetch and rebase before any push; NEVER force push (Will, 2026-10-30). For the API route the same rule means: parent on the branch's current remote HEAD, read fresh at publish time, force disabled — a moved HEAD fails instead of being overwritten. (A force update happens only under Will's explicit in-chat direction for a specific case; never generalize an exception.)
- Stage only what ships: build a staging tree containing exactly the files being published at their repo-relative paths. push_tree preserves everything else on the branch via base_tree.

## Execute bits and checksums — verify both

- Every script file (shebang-bearing, .sh or otherwise) is created/chmodded executable locally and published with git tree mode 100755. Git stores executability as the tree mode, not in blob content, so a content-hash check does NOT catch a lost bit — publish verification checks modes as well as blob SHAs. (push_tree.py carries the local exec bit into the tree mode.)
- Always use SHA-256 for file-integrity verification — never MD5 or SHA-1. (Git's own object IDs are identifiers git chooses, not checksums.)
- After publishing, re-read the remote tree and confirm each published file's blob SHA matches the local `git hash-object`, and each script's mode is 100755.
