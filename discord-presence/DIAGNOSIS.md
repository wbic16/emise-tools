# Discord watcher: diagnosis and re-architecture

Date: 2026-10-31. Trigger: the discord-presence backstop cron restarted the
watcher six times in one day (~00:17, 02:22, 04:19, 06:18, 08:18, 10:18 CDT,
roughly every 2 hours), each time finding the heartbeat ~6–7 min stale, the
systemd unit sometimes missing, and SSL EOF errors at the tail of watch.log.
William's hypothesis: "I assume your backend is serverless" — essentially
correct, and confirmed below.

## Root cause (confirmed unless marked inferred)

The watcher does not crash. The machine underneath it is replaced.

1. **The unit lived in ephemeral storage.** `discord-ensure.sh` copies the
   canonical unit from `~/workspace/discord/` to
   `/etc/systemd/system/discord-watch.service`. `/etc` does not survive VM
   replacement. Evidence: after the current boot (15:11 UTC), the unit file's
   mtime was 15:17:53 UTC — the moment the backstop's ensure run reinstalled
   it — and at several restarts the backstop found the unit missing entirely.
2. **Deployments are frequent and regular.** The current VM booted at
   15:11 UTC with `uptime` showing 9 minutes when the 10:18 CDT (15:18 UTC)
   backstop restart landed. `journalctl --list-boots` shows only the current
   boot (the journal is wiped too). The six detection times are spaced
   ~2h00–2h05 apart (05:17, 07:22, 09:19, 11:18, 13:18, 15:18 UTC), matching a
   roughly 2-hour replacement cadence (inferred: cadence inferred from
   detection times; each individual replacement directly observed only for
   the 15:11 UTC boot).
3. **Nothing on the box could restart the watcher after a replacement.**
   The only trigger was the runtime-managed 5-minute backstop cron noticing
   a heartbeat stale >3 min — hence outages of ~6–10 min each.
4. **Process crashes were already covered, and were never the problem.** The
   unit already had `Restart=always` / `RestartSec=5`: a crashed process
   would return in ~5 s and the heartbeat would never reach 6–7 min stale.
   Verified empirically after the fix (kill -9 test below).
5. **The watcher loop does not exit on network errors.** The entire poll
   body sits in `try/except Exception`, which logs and retries after 5 s.
   The SSL EOF / "Remote end closed" lines in watch.log are that catch
   firing, not crashes. (Inferred: the errors cluster near replacements
   because the egress path is being torn down; the log alone cannot prove
   the timing correlation.) Verified empirically after the fix (dead-proxy
   test below).
6. **Latent bug, independent of deployments:** the unit's `[Install]` said
   `WantedBy=multi-user.target`, but this guest boots a minimal
   `default.target` only (`systemctl get-default` → `default.target`,
   "Hatch runtime-cell minimal boot target"; `multi-user.target` is not
   among the active targets). So even on a plain reboot with `/etc` intact,
   the enabled unit would never have autostarted.
7. **systemd user services are unavailable here** (verified):
   `systemctl --user` → "Failed to connect to bus"; no `XDG_RUNTIME_DIR`,
   no `/run/user`, no user manager process, no lingering. The
   `~/.config/systemd/user` route is dead in this runtime.

## Alternatives evaluated

- **(i) Hardened systemd user unit** — impossible per (7). The system-unit
  half of (i) was adopted (see below) but cannot self-restore after a
  replacement because its unit file lives in wiped `/etc`.
- **(ii) Cron-primary polling** — rejected. Runtime crons are agent runs;
  the cron interval format bottoms out at 1-minute granularity for a full
  agent execution, which is far heavier (tokens, latency) than a 15 s
  script poll and still 4× slower. It would also duplicate the spool/hook
  machinery for no gain.
- **(iii) Hook-based recovery trigger** — adopted as the recovery layer.
  Hooks are runtime-managed (they survive deployments — the discord-spool
  hook kept firing all day), run scripts through the same shell executor as
  ordinary commands, and need no connector credentials for this job: the
  health signal is a local file and the repair is a local idempotent
  script. Note the boundary: hooks have no connector credentials, so the
  hook does *not* poll Discord itself; it only restores the watcher.
- **(iv) Discord Gateway websocket** — rejected. It is the same long-lived
  process on the same replaceable VM, strictly worse: it adds connection
  state and reconnect logic, and per the connector doc the vault credential
  cannot be held by a long-lived gateway process.

## Chosen design (layered, fewest new parts)

1. **Watcher (unchanged behavior):** `discord_watch.py` still polls every
   15 s, spools addressed messages to `spool.jsonl`, keeps watermarks in
   `state.json`, writes the heartbeat every loop. Only change: log lines
   now carry UTC timestamps (the old log was undated, which hampered this
   very diagnosis).
2. **Systemd unit (hardened):** `WantedBy=default.target` (the target this
   guest actually reaches), `Restart=always`, `RestartSec=5`,
   `StartLimitIntervalSec=0`, `TimeoutStopSec=10`,
   `KillMode=control-group`. Covers in-VM process death in ~5 s, and makes
   enablement correct if `/etc` ever persists across a boot.
3. **NEW `discord-watchdog` hook (the deployment-survival layer):**
   script-only, polls every 30 s. Heartbeat fresh (≤120 s) → silent. Stale
   → run `discord-ensure.sh` once (2-min cooldown between attempts; output
   logged to `~/hooks/state/discord-watchdog-ensure.log`), re-check after
   8 s: recovered → log + silent (no agent, no user noise). Still stale →
   wake an agent **once per outage** to investigate and, if needed, do a
   manual presence pass. This is what converts a VM replacement from a
   6–10 min outage noticed by a 5-min agent cron into a ~2.5 min outage
   repaired by a shell script.
4. **Backstop cron (unchanged, not edited):** `discord-presence` every
   5 min remains the final net — drains a stuck spool >10 min, restarts a
   watcher the other layers somehow missed, escalates persistent API
   errors.

Recovery behavior now:
- Watcher process dies → systemd restarts it in ~5 s.
- Network/API flakes → the loop logs and retries forever; never exits.
- VM replaced → watchdog hook notices the stale heartbeat within
  ~2–2.5 min and reinstalls/restarts the watcher silently; worst case the
  5-min backstop cron catches it as before.
- Watchdog's repair fails → one agent wake per outage investigates.

## Verification (2026-10-31, all after the change)

- **Kill test:** `kill -9` on the watcher PID → systemd restarted it (new
  PID) within the 12 s observation window; heartbeat fresh.
- **Deployment simulation:** stopped the service, deleted the unit and its
  enablement symlinks from `/etc`, `daemon-reload` (the exact
  post-replacement state). Untouched from there: the watchdog hook's log
  shows heartbeat ages climbing 1 s → 105 s, then at 135 s stale it ran
  ensure ("unit installed / service started" in its log), the watcher
  logged "starting" at 15:27:36 UTC — **2 min 15 s after the last
  heartbeat** — and the hook closed the incident *silent*, no agent wake.
- **Network-failure test:** sandboxed copy of the watcher (temp HOME) with
  the proxy env pointed at a dead address: three consecutive poll cycles
  logged "Connection refused", the heartbeat kept advancing, and the
  process was still alive when a 50 s timeout killed it. Retry-not-exit
  confirmed.
- **Spool/hook path:** a synthetic entry appended to `spool.jsonl` made
  the `discord-spool` hook's dry run return a wake decision
  (`pending: 1`); no agent was launched and nothing was posted. Spool then
  truncated back to empty. A read-only `GET /users/@me/guilds` with the
  connector helper returned 200 (Tessera). State intact: 13 channels
  watermarked, inaccessible-channel record unchanged.

## Residual risks / unverified

- **An actual runtime deployment has not yet occurred since the change.**
  The simulation reproduces its observable state (no unit, no process,
  stale heartbeat), but end-to-end proof arrives with the next real
  replacement (~2 h cadence): success looks like a "watcher recovered via
  discord-ensure.sh" entry in the discord-watchdog hook log with no
  backstop-cron restart that cycle.
- Hook polling itself depends on the runtime's hook scheduler surviving
  deployments, which it did all day today for discord-spool (observed),
  but it is the same trust assumption the backstop cron already relies on.
- If a deployment ever lands while the egress proxy/authd is still
  warming up, the watcher's first polls will fail; by design it retries
  forever, and the watchdog only cares about the heartbeat, which the
  watcher writes before its first API call each loop — so no false
  escalation results.

## Files changed

- `~/workspace/discord/discord-watch.service` — default.target + hardening.
- `~/workspace/discord/DIAGNOSIS.md` — this file.
- `~/workspace/custom-connectors/custom.discord/bin/discord_watch.py` —
  timestamped log lines only; behavior unchanged.
- `~/hooks/scripts/discord-watchdog.sh` — new watchdog script.
- Hook `discord-watchdog` — new, enabled, 30 s poll, delivery main.
- `~/workspace/custom-connectors/custom.discord/CONNECTOR.md` — Limits
  paragraph updated to describe the layered recovery.
- Not changed: `discord-ensure.sh` (already idempotent; installs whatever
  unit is canonical), the `discord-spool` hook, `state.json` handling, the
  reply policy, and the `discord-presence` cron.
