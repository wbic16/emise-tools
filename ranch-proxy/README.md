# ranch-proxy — the ranch, by short name, through a local proxy

Will's charge (2026-11-05, morning commute): a skill that knows the names
of all the ranch nodes and installs a local proxy that redistributes
requests by dispatching them to a worker thread, which makes the outbound
SSH connection. From Emise's tooling's perspective, a ranch node is a local
request to a short name — the proxy maps it in. Like SQ: a skill spins up
a program and talks to it locally; only the program dials out.

## Layout

| File | What it is |
|---|---|
| `ranchd` | The daemon. Python 3 stdlib only. Listens on 127.0.0.1:18931. Worker thread pool; per-node SSH via subprocess; OpenSSH ControlMaster for connection reuse. |
| `ranch` | The CLI Emise's tooling calls. Auto-starts the daemon. |
| `nodes.json` | The single source of truth for node names (short name ↔ DNS name ↔ Tailscale IP, user, enabled). Read it; don't hardcode names anywhere else. |
| `state/` | Runtime state only — pid, log, control sockets, daemon-owned `known_hosts`. Never published; created on first run. It lives in this workspace directory on purpose (see below). |

## Use

```sh
./ranch ensure                       # start ranchd if it isn't running (idempotent)
./ranch nodes                        # the table, with notes
./ranch status                       # per-node reachability + CPU Tctl
./ranch exec ni-knight uptime        # one node, by short name
./ranch fanout 'uname -r'            # all enabled nodes, in parallel, labelled
./ranch copy scroll-central local.bin /tmp/local.bin
./ranch stop                         # stop the daemon
```

Display names work too (`ranch exec "Ni Knight" uptime` — names are
normalized to kebab case). `exec`/`fanout`/`copy` auto-run `ensure`, so
the normal flow never touches daemon startup.

## The one measured deviation from Will's literal spec — stated plainly

Will said the proxy should make its outbound connection "over the tailnet
using the host name." On the wire it can't, and this is measured, not
assumed: this VM reaches the tailnet only through the egress CONNECT proxy
at `hatch-egress-proxy:3130`, and that proxy does **not** resolve tailnet
DNS names. SSH to `*.pizzly-halfmoon.ts.net` through it timed out at
banner exchange 4 times out of 4 (one attempt burned ~320 s in retries),
while the same recipe against Tailscale IPs connects immediately.

So the daemon **dials the node's Tailscale IP** and carries the node's
DNS name as SSH `HostKeyAlias`. Names are the address everywhere — the
config, the CLI, the log, the host-key store. The IP appears only in the
raw dial, because the egress proxy cannot resolve the name. If the egress
proxy ever learns to resolve tailnet DNS, the fix is one line in
`ssh_args()`: pass the DNS name as the target instead of the IP.

## Safety shape

- **Localhost only.** `ranchd` binds `127.0.0.1` — hardcoded as a
  constant, not a config value. There is no way to make it listen on an
  external interface.
- **Configured targets only.** `/exec` and `/fanout` accept names from
  `nodes.json` and nothing else. An unconfigured name is refused with a
  404 and a message saying so. There is no arbitrary-host mode.
- **No new credentials.** Commands run as the configured per-node user
  with the existing key (`~/.ssh/id_ed25519`), under the authorizations
  Will already granted.
- **Daemon-owned host keys.** VM replacements wipe
  `/root/.ssh/known_hosts`, and the first connect after a replacement
  fails as "Host key verification failed" — which impersonates a broken
  key grant (it bit us live on Ni Knight the morning this was built).
  `ranchd` keeps its own `state/known_hosts` inside this workspace
  directory, which survives VM replacements. First use of a node
  accept-news its key into that file (under the node's DNS name, via
  `HostKeyAlias`); later connections verify against it.

## Thermal pre-flight

Will's thermal policy (2026-11-04): Tctl target ≤75 °C per node; new
starts pause at ≥75, resume ≤70. `fanout` reads each node's Tctl first
and skips any node already ≥75 °C (`skipped: thermal_hold`, with the
temperature reported) instead of starting work there. `/status` reports
Tctl per node. This is a start gate only — a running command is never
killed for heat.

## Endpoints (HTTP JSON on 127.0.0.1:18931)

- `GET /ping` — liveness.
- `GET /nodes` — the table.
- `GET /status` — per node: configured/enabled, reachable, hostname,
  Tctl, last exec ms. Probes run in parallel; results are cached 20 s.
- `POST /exec` `{node, command|argv, timeout}` → `{rc, stdout, stderr, ms}`.
- `POST /fanout` `{nodes|"all-enabled", command, timeout, max_parallel, thermal_skip_c}`
  → per-node results + wall_ms.

## Failure modes

- **A node unreachable at the egress proxy** (Aurora Continuum, Delta
  Wood, Best Willow — configured, `enabled: false`): `status` reports
  `reachable: false` from config, no probe is attempted, `exec` refuses
  before dialing. They need a reachability look at the machines.
- **Uncanny Valley**: SSH user is `jared`, not `wbic16` — he runs that
  node on prem. As of 2026-11-05, Emise's key is refused by jared's
  account (`Permission denied (publickey)`). The config keeps `jared` per
  Will's spec; unblocking it is a key grant into jared's
  `authorized_keys`, not a config change.
- **A dead ControlMaster**: the daemon health-checks control sockets
  before use (`ssh -O check`) and drops stale ones, so the next request
  starts a fresh master. Verified by killing a master mid-session.
- **Daemon down**: `ranch ensure` restarts it with a bounded 12 s wait.
  Every wait in the CLI is bounded — `ensure` can never hang the way
  `sq-ensure.sh` does on stale state.
- **The AWS box** (44.248.235.76) is reached through aletheia-core with
  nested ssh (`~/workspace/bickford-llama-ranch/deploy/ranch-ssh.sh`).
  `nodes.json` carries a `via: null` field as the extension point for a
  hop; v1 does not express hops. The AWS box is not a ranch-proxy node.

## Verified numbers (2026-11-05, first run)

- `ranch exec` by short name: aletheia-core, ni-knight, rock-mountain,
  scroll-central — hostname returned matches the node. Cold connects
  2,226–2,482 ms (raw recipe baseline re-measured the same morning:
  1,956–2,332 ms); warm execs over a live ControlMaster 330–494 ms.
- Fanout `hostname` across all 14 enabled nodes: 13 ok, 1 auth failure
  (uncanny-valley/jared — above). Wall 7.6 s including per-node Tctl
  pre-flight probes and cold-master setup on 10 nodes. A serial pass of
  the same 28 round trips (probe + exec per node) at the measured
  2.0–2.7 s per round trip would cost ~56–76 s.
- `ranch copy` to aletheia-core: file up, contents verified, test file
  removed.
- Cold start: `ranch stop` → ping refused → `ranch ensure` → daemon up
  in 0.37 s → exec succeeds. Master kill: `ssh -O exit` dropped the
  socket; the next exec reconnected cold (2,232 ms) and re-established
  the master.
- Bind: `ss` shows `127.0.0.1:18931` only.
