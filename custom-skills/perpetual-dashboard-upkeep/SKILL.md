# Perpetual Dashboard Upkeep — one current surface for the whole operation

The perpetual dashboard (goal `perpetual-dashboard`) is a self-updating web artifact showing live systems, armed schedules, shipped work, and threads waiting on Will. Scheduled embodiment: cron `perpetual-dashboard-refresh` (every 5 minutes), which invokes the artifact's published `refreshDashboard` action and retains its run history; the artifact also offers on-demand refresh.

## What "current" means

- The dashboard re-checks SQ, the scheduler, and host state on every refresh — its panels are only as good as their last successful run, so a stale or failing refresh is a defect to repair, not a fact to accept.
- Currency includes, alongside ranch utilization: provider token headroom and reset timing (see substrate-steering), armed schedules, shipped work, and the Waiting-on-Will queue.
- When a refresh fails, check the run history first, repair within the dashboard's own scope, and verify the next run lands before calling it fixed.

## Keeping it truthful

- The dashboard reads live surfaces; it never becomes a second register. Waits shown there still live in `~/workspace/your_files/waiting-on-will.md`, schedules in the scheduler, and node state on the nodes — correct the source, and the dashboard follows on its next refresh.
- New panels or endpoints ship discoverable from the dashboard's main UI in the same change (Will's discoverability rule, 2026-11-02).
