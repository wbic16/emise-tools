---
name: lost_work_sweep
description: Daily sweep that flags wbic16 branches with no PR, long-unmerged branches, and stale PRs against exo — and removes branches already part of merged history, bringing the remainder to Will for review.
---

# Lost-work sweep — no branch without a PR, no work lost off exo

Standing rule (Will, 2026-11-08): **always PR our branches; no lost work.** Every branch Emise creates gets a PR opened against its repo's exo branch in the same work session — a branch never sits PR-less. No repository may hold work un-merged to exo for long periods. This skill is the process; its scheduled embodiment is the cron `lost-work-sweep` (daily ~07:44 America/Chicago).

Standing rule (Will, 2026-11-15): **stale branches — merged history is removed, the remainder goes to Will.** "Detect stale/abandoned branches and remove any that are already part of merged history — bring the remainder to me for review." The sweep is where this rule runs daily; it also applies in-session wherever Emise works a repo (a branch whose PR has merged and whose tip is in merged history is deleted in the same session).

## The sweep (reads and reports; deletes merged-history branches only — never pushes, merges, or opens anything)

1. **Enumerate** Will's GitHub repositories from `~/workspace/site-map` (sitemap.json / SITE-MAP.md) — every wbic16 repo that has an `exo` branch. Reach GitHub through the custom.github connector's `github_api.py` route (see `~/workspace/custom-connectors/custom.github/CONNECTOR.md`).
2. **For each such repo, list all branches.** Skip `exo` itself and any `backup/*` branch (intentional history archives, exempt by the rule). For every remaining branch record: tip commit date + author, whether an OPEN PR exists with this branch as head, whether the branch is already merged into exo (tip is an ancestor of exo), and its age in days since the tip commit.
3. **Flag** a branch when any of these hold:
   - tip is more than **24 hours** old, the branch is not merged into exo, and NO open PR has it as head — "no PR — lost-work risk";
   - the branch is unmerged and its tip is more than **7 days** old, PR or not — "sitting unmerged";
   - an open PR with this head has been open more than **7 days** — "PR waiting on merge".
   
   A branch whose tip is already an ancestor of exo is merged work, not lost work — never flag it.
4. **Remove merged history.** Every branch (other than `exo` itself and `backup/*`) whose tip is an ancestor of exo is already part of merged history: delete it (via the connector's API route or git-over-SSH from aletheia-core), and verify the deletion by re-listing the repo's branches. Record each deletion for the report. Deletion is the ONLY write the sweep performs, and it applies only to branches whose full history is contained in exo — when ancestry is uncertain, do not delete; flag the branch for review instead.

## Delivery

- If nothing is flagged and nothing was removed, the sweep ends silently — no message.
- Otherwise report to the main chat: removals first (one line each: repo, branch, tip SHA it pointed at), then the flags — the remainder for Will's review (repo, branch, which rule fired, tip age, PR number if one exists), grouped by repo, oldest first within each repo.
- No recommendations beyond naming the flag; Will decides the remedy for the remainder.

## Boundaries

- The sweep's only write is deleting merged-history branches under step 4. Opening the missing PR or merging is separate work under the normal rules (every PR mentioned to Will carries its full URL). An unmerged branch is NEVER deleted by the sweep — it goes to Will's review list.
- Sibling check: `repo-pruning-check` (weekly, repo-level, untouched >365 days). The lost-work sweep is branch-level and daily; the pruning check is repo-level and weekly. The pruning check deletes nothing; the sweep deletes merged-history branches only.
