# commit-rollup — rolled-up GitHub commit tracking for Discord

Ian (argimenes) has the GitHub app post one Discord embed per commit in his
channel. Will's operation makes 100–200 commits/day across 200+ repos, so
per-commit posts would flood. This tool posts **one embed per session**
instead (Will's design, 2026-11-16): a session is a burst of commits; when
the newest commit across all of wbic16's repos is older than the dormancy
threshold (config `dormancy_minutes`, default **5**), the session is over
and one rollup covering exactly that session posts to the configured
channel — Tessera **#git** (`1571768026397941771`).

## How it works

- **Collector** — GitHub commit search, `user:wbic16` scope: every commit
  that lands in Will's repos, any author (Will, Emise, Theia, … — the
  Exocortex's output, not just one identity). Imported from the
  custom.github connector helper, so no 4000-char CLI truncation.
  Measured 2026-11-15 (America/Chicago): user: scope **212** commits;
  author:wbic16 alone only 61; the speedup meter's 196-repo clone universe
  counted 127 (126 of the 212 are in that universe — the rest are the repos
  created after the meter's clone set froze: register, markdown-wizard,
  jenkins, doctor, …).
- **Formatter** — one embed per session, GitHub-app look: session span and
  duration (America/Chicago), PR merges called out first with full PR
  URLs, then one field per repo sorted by commits descending. Each repo
  carries an ascii effort bar — the repo's **share of the session total**,
  10 blocks (`█`/`░`), minimum 1 filled block — plus up to 5 recent subject
  lines with short SHAs linked to the commit, and a `+K more` tail.
  Discord limits are enforced while building (≤25 fields, ≤1024 chars per
  field value, ≤6000 total): overflow repos fold into a summary field.
- **Poller** — cron `commit-rollup-poller`, every 2 minutes. Each run:
  load the watermark, collect commits since (watermark − 15 min lookback),
  drop already-posted SHAs; if none, exit silently; if the newest is
  younger than the dormancy threshold, the session is live — wait; if
  older, build the embed, post it, advance the watermark.
- **State** — `state/watermark.json`: watermark (committer time of the
  newest posted commit), a ring of posted SHAs (absorbs search-index lag
  and the lookback overlap), and the last posted message id. Seeded by
  `--init-state`, which marks everything already in the lookback window
  as posted so going live never dumps history into the channel.

## Config (`config.json`, env `COMMIT_ROLLUP_CHANNEL_ID` overrides)

| key | meaning |
|---|---|
| `channel_id` | Discord channel to post into (null = dry-run only) |
| `dormancy_minutes` | quiet gap that ends a session (default 5) |
| `owner` | GitHub owner scope (`wbic16`) |
| `timezone` | display zone (`America/Chicago`) |
| `bar_width` | effort bar width in blocks (10) |
| `max_subjects_per_repo` | subject lines per repo field (5) |

## Usage

```
rollup.py                    poll once (post if a session has closed)
rollup.py --dry-run          force-close any pending session, print the
                             embed JSON, change nothing
rollup.py --init-state       seed the watermark at now (idempotent)
rollup.py --day 2026-11-15   session-segmentation report for a Chicago day
rollup.py --window A B       render one embed for an explicit ISO window
```

Status line protocol: `INIT` / `NOOP` / `WAITING` / `POSTED` / `DRYRUN` /
`ERROR` — the cron reports only `ERROR` (or a nonzero exit).

## Known edges

- Commit search indexes with a lag of a minute or so; the 5-minute
  dormancy threshold plus the posted-SHA ring absorb it.
- A post that times out after Discord stored it could double-post on the
  next poll (state only advances on a confirmed response). Rare; the
  window is one HTTP call.
- Sessions are computed on committer dates in `user:` scope; a force-push
  that rewrites committer dates can re-show a commit whose SHA changed —
  by design, since it is a new commit.

Live since 2026-11-16 00:07 CST (watermark seeded at enable time; first
rollup posts at the first genuine session end after that).
