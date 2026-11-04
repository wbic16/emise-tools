# github-publish

Git Data API publishers used to ship branches from this VM (outbound SSH git is blocked here). Both parent new commits on the branch's fresh remote HEAD and update refs with force disabled, per the standing publish rule; both are authored as Emise and replay local commits blob-by-blob, asserting each replayed tree matches the local tree.

- `publish_branch.py <owner/repo> <local-repo-dir> <branch>` — create/replay a whole branch off remote main.
- `publish_incremental.py <owner/repo> <local-repo-dir> <branch>` — replay only the commits after the one whose tree matches the existing remote branch head.

Provenance: built 2026-11-03 for the wbic16/mutable-os phext work (branches emise/phext-support, emise/vault-title-defaults; remote read-backs matched 3,215/3,219 files, scripts at mode 100755).
