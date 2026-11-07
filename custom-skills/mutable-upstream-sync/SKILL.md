# Mutable Upstream Sync — a two-band patch stack that tracks upstream nightly

How Emise keeps wbic16/mutable-os in sync with its upstream, argimenes/mutable-os (Will directed the pipeline 2026-11-06: "we need to get a pipeline going for staying in sync with upstream; the SSO changes we apply need to sit in a separate repo or branch; once phext support is merged upstream, we won't have to merge as frequently"). Companion to fork-patch-discipline; tracked under goal `mutable-phext-io-mutable-os-fork-setup-with-phext-patches`.

## The shape

Our divergence from upstream is a **two-band patch stack**, never a snowflake tree:

- **Phext band** — branch `emise/phext-support`. The phext support stack: the support squash `64f8eea2209515d5f0fcae9766c2c79a5008a227`, per-Cavern mode selection, the font-settings domain, and the PATCHES.md record commit. This band is **upstream-bound**: it exists to be merged upstream one day, and it dissolves the day phext support lands there.
- **SSO band** — branch `emise/sso`. The edit.phext.io SSO gate commit and the SSO UX-fixes commit. This band is **ours and never upstream-bound**; it stays separable from the phext band precisely so the phext band can go upstream (or dissolve) without dragging our site auth with it.
- **`main`** is the integration/deploy line. It advances **by merge only** — main is never rebased and never force-pushed.

The live band definition — the recorded base (`OLD_BASE`), the exact band commit lists, and the upstream-support marker files — is `sync-bands.conf` in the pipeline directory (below). The conf is the record; this skill describes the process around it. Marker files whose presence in the upstream tip tree means phext support has landed upstream: `server/phext-fs.mjs`, `src/phext/codec.ts`, `PHEXT.md`.

## Where everything lives

- Pipeline: `~/workspace/goals/mutable-phext-io-mutable-os-fork-setup-with-phext-patches/hidden_files/sync-pipeline/`
  - `upstream-sync.sh` — the trial sync (fetch, measure, trial-rebase, verify, report). Never pushes.
  - `promote.sh` — the promotion step. **A draft, guarded to exit 64 as a no-op**; see Promotion.
  - `sync-bands.conf` — band definition (above).
  - `recorded-set.txt` — the recorded vitest file set for verification.
  - `reports/` — one dated report per run (`sync-<stamp>.md`); `logs/<stamp>/` — per-suite logs.
  - `scratch/` — the pipeline's **dedicated scratch clone** of the fork. The sync never operates on the main clone (`~/workspace/mutable-os-work`) and refuses to run if the scratch path resolves to it.
- Publication route: outbound git push from this VM is blocked. All GitHub writes go through the API tooling — the goal's `hidden_files/publish_branch.py` / `publish_rebase.py` and `python3 ~/workspace/custom-connectors/custom.github/bin/github_api.py` — which parent on the branch's fresh remote HEAD with force disabled and abort on a moved HEAD.

## The nightly trial — upstream-sync.sh

Scheduled embodiment: cron `mutable-upstream-sync`, daily ~03:44 America/Chicago, owned by the mutable goal. The script, in order:

1. Fetches origin (the fork) and upstream into the scratch clone.
2. Measures drift between `OLD_BASE` and the upstream default-branch tip: merge-base, commit counts on both sides, **content drift** (tree diff), and the touched-file overlap of the upstream changes against each band's file set.
3. **Twin check:** if `OLD_BASE` is not an ancestor of the upstream tip, runs a `range-diff` patch-twin check before treating the gap as drift (see the twin-lineage lesson).
4. **Endgame check:** if any support marker file exists in the upstream tip tree, stops with the mode-switch exit — no rebase attempted.
5. Trial-rebases the phext band (`git rebase --onto <tip> <OLD_BASE> <band tip>`), then cherry-picks the SSO band commits, in a throwaway worktree of the scratch clone.
6. On a clean stack: installs dependencies, then verifies **from a fresh build** (below), and writes the dated report, including the proposed post-promotion `sync-bands.conf` values and the resulting stack SHAs.

Exit codes — the cron run reports to Will on everything except 0:

| Code | Meaning | Cron behaviour |
|---|---|---|
| 0 | No drift — upstream tip is exactly the recorded base | Silent |
| 10 | Clean sync, fully verified | Message: new stack SHAs + verification tallies; promotion has NOT been done |
| 11 | Phext support detected upstream — mode switch needed | Message prominently: the support band can dissolve; re-plan as SSO-only |
| 20 | Rebase/cherry-pick conflict | Message with the conflicted files named; never auto-resolve |
| 30 | Build or test failure | Message with the failing tallies |
| 40 | Setup/environment error (fetch, install, bad config) | Message with the error (but see the install fallback) |

Every run appends a one-line outcome note to the mutable goal's GOAL.md state log.

## Verification discipline

- **Fresh build first**: `npm run build`, then typecheck. A suite tally from a stale `dist/` proves nothing.
- **Suites run serially** (`--no-file-parallelism`): the shared establishment flock makes parallel suites fail spuriously or hang.
- The battery: SSO + startup suites; the recorded vitest set (`recorded-set.txt`); `server/phext-settings.test.mjs` qualified separately under `node --test` (it fails vitest *collection* at baseline with zero tests — a failed-file list containing only it is a pass); `npm run test:sqlite`.
- **Install fallback:** if `npm install` fails on native-module downloads through the egress proxy (seen 2026-11-06 with better-sqlite3), the script may copy a `node_modules` whose tree's `package-lock.json` blob is identical to the trial tree's — same lock, same dependency bits — and verifies better-sqlite3 loads. No lock-identical donor, no fallback: exit 40.

## The twin-lineage lesson

A recorded base SHA that is **not an ancestor** of the upstream tip is not necessarily drift. Upstream history gets rewritten (the 2026-11-06 rebase produced exactly this): the first verified run measured base `4bf3a936` against tip `db3ed300` — not an ancestor, 15 commits on each side of the merge-base — yet the range-diff showed **15 of 15 patch-identical twins and zero content drift**. Prove twin-identity with `range-diff` / an empty tree diff before treating a non-ancestor base as divergence; ancestry is a claim about history, content is the fact.

## The endgame — mode switch (exit 11)

When phext support merges upstream, the marker files appear in the upstream tip tree and the sync stops asking for a full-band trial. A human then re-plans: retire the phext band, rewrite `sync-bands.conf` by hand as an SSO-only stack on the new base, and the nightly sync continues at a lower merge cadence — the SSO band is small and touches few files upstream moves often. The script never performs the mode switch itself.

## Promotion — separate, guarded, and not yet ratified

`upstream-sync.sh` prepares and proves; it **never pushes**. Publishing a verified trial is a separate step, `promote.sh`, which is currently a **draft with a hard exit-64 guard** — it must not be run, and the guard is removed only in a reviewed change, never edited around ad hoc.

Why the split (Will's force-push rules, 2026-10-30 / 2026-11-06): fetch and rebase before any push, never force push — with one sanctioned exception, a rebase Will asks for, force-pushed `--force-with-lease` (never bare `--force`) with the old history preserved on a backup branch first, unless the rewrite would impact anyone except us. A sync promotion contains exactly one force-class operation (rewriting the two `emise/*` band branches), so it stays isolated, named, and gated.

When enabled for a specific verified report, promotion does:

0. **Preconditions, all before any write:** the report says CLEAN SYNC, VERIFIED and names the new stack; **no open PR has head `emise/phext-support` or `emise/sso`** (checked via the GitHub API) — if one is open, STOP and report; remote main and band heads still sit where the trial measured them (the lease-equivalent parent check).
1. **Backups first:** create `emise/backup-pre-sync-<date>` refs at the current band heads (additive).
2. Publish the rebased bands via `publish_rebase.py` (per-commit tree verification; the ref update is the sanctioned force-with-lease equivalent — it parents on the branch's fresh remote HEAD and fails if that moved): `emise/phext-support` := rebased phext tip, `emise/sso` := rebased SSO tip.
3. Advance `main` **by merge only**: merges API, base `main`, head `emise/sso`.
4. Verify: `ls-remote` all three refs; main's tree must equal the trial stack's tip tree from the report.
5. Update `sync-bands.conf` with the report's proposed values; append the promotion record to the goal's GOAL.md.

**Status: a standing ratification for unattended promotion was requested from Will on 2026-11-06 and is PENDING.** Until he ratifies it, each promotion is approved per sync by Will (or run by Emise in session at his direction). Do not treat promotion as an approved standing operation, and do not let the nightly cron promote.
