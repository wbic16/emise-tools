---
name: exo_repo_pruning_check
description: Weekly report-only check that flags wbic16 repos Will hasn't touched in over a year as pruning candidates; never deletes, archives, or renames anything — pruning is Will's call per repo.
---

# Repo pruning check

Will, 2026-11-15 03:30 CST: "setup repo pruning checks - anything I haven't touched in over a year" — task 38.11.7/14.7.16/5.8.9.

## The rule

- **Reports only.** The check never deletes, archives, renames, or modifies any repository. It produces a candidate list; pruning is Will's call, per repo.
- **Definition of touched:** `last_touched = max(repo pushed_at, last house-authored commit date)`.
  - `pushed_at` (GitHub API) is the practical proxy for Will's own activity: for forks, upstream commits count only when actually pushed into his fork; upstream's activity in the parent repo never moves his fork's `pushed_at`.
  - The house-authored signal scans the default branch's 100 most recent commits for authors in the Will/Emise/Theia identity set (from `~/workspace/gh-baseline-local/results.json`), matched by GitHub login, author name, or author email.
  - A repo is flagged when `last_touched` is more than **365 days** before the run's reference date.
- **Caution column:** corpus-class repos (per `~/workspace/agentic-pass-plan/repo-classes.json`) carry an explicit "contains unique material" caution; every other flagged repo is marked "contents not audited". A flag means "no recorded touch in over a year", never "safe to delete".

## The machinery

- **Checker:** `~/workspace/repo-pruning/check_repo_pruning.py` (executable). Enumerates repos from the union of `~/workspace/site-map/sitemap.json`, the GitHub API owner list, and the gh-baseline included set; reaches GitHub through the custom.github connector helper (imported `call()`, so list responses aren't truncated).
- **Outputs** (in `~/workspace/repo-pruning/`): a dated report `pruning-candidates-YYYY-MM-DD.md` per run, and `state.json` holding the flagged set + SHA-256 for change detection. The script's last stdout line is `BASELINE` / `UNCHANGED` / `CHANGED: <summary>`.
- **Cron:** `exo_repo_pruning_check`, weekly Mondays ~07:55 America/Chicago (just after the daily lost-work sweep's 07:44 slot). The run re-executes the checker and reports to the main chat **only when the flagged set changes** (new candidates or count change), silent otherwise — the same report-only discipline as the lost-work sweep.

## Running it by hand

```
~/workspace/repo-pruning/check_repo_pruning.py [--reference-date YYYY-MM-DD]
```

## Boundaries

- No repo is ever pruned by this process. If Will rules a repo pruned, that is a separate, per-repo action under his direction.
- The check reads metadata only; it does not audit repo contents (hence the caution column's default).
