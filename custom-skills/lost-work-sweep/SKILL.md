---
name: lost_work_sweep
description: Daily read-only sweep that flags wbic16 branches with no PR, long-unmerged branches, and stale PRs against exo — no branch Emise creates sits PR-less, and no work stays un-merged to exo for long.
---

# Lost-work sweep — no branch without a PR, no work lost off exo

Standing rule (Will, 2026-11-08): **always PR our branches; no lost work.** Every branch Emise creates gets a PR opened against its repo's exo branch in the same work session — a branch never sits PR-less. No repository may hold work un-merged to exo for long periods. This skill is the process; its scheduled embodiment is the cron `lost-work-sweep` (daily ~07:44 America/Chicago).

## The sweep (read-only — never push, merge, or open anything)

1. **Enumerate** Will's GitHub repositories from `~/workspace/site-map` (sitemap.json / SITE-MAP.md) — every wbic16 repo that has an `exo` branch. Reach GitHub through the custom.github connector's `github_api.py` route (see `~/workspace/custom-connectors/custom.github/CONNECTOR.md`).
2. **For each such repo, list all branches.** Skip `exo` itself and any `backup/*` branch (intentional history archives, exempt by the rule). For every remaining branch record: tip commit date + author, whether an OPEN PR exists with this branch as head, whether the branch is already merged into exo (tip is an ancestor of exo), and its age in days since the tip commit.
3. **Flag** a branch when any of these hold:
   - tip is more than **24 hours** old, the branch is not merged into exo, and NO open PR has it as head — "no PR — lost-work risk";
   - the branch is unmerged and its tip is more than **7 days** old, PR or not — "sitting unmerged";
   - an open PR with this head has been open more than **7 days** — "PR waiting on merge".
   
   A branch whose tip is already an ancestor of exo is merged work, not lost work — never flag it. (A stale un-deleted merged branch may be listed once, in a single cleanup line, only if it is more than 14 days past its merge.)

## Delivery

- If nothing is flagged, the sweep ends silently — no message.
- If anything is flagged, report to the main chat: one line per flag (repo, branch, which rule fired, tip age, PR number if one exists), grouped by repo, oldest first within each repo.
- No recommendations beyond naming the flag; Will and Emise decide the remedy.

## Boundaries

- The sweep only reads and reports. Opening the missing PR, merging, or deleting a branch is separate work under the normal rules (every PR mentioned to Will carries its full URL).
- Sibling check: `repo-pruning-check` (weekly, repo-level, untouched >365 days). The lost-work sweep is branch-level and daily; the pruning check is repo-level and weekly. Neither deletes anything.
