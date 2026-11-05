# Ranch Proxy — reach the ranch by short name

## Use the proxy, not raw ssh recipes

- Use this skill whenever you need to run a command, copy a file, or check state on a ranch node (aletheia-core, Rock Mountain, Ni Knight, and the rest of the fleet).

- Run everything through `~/workspace/ranch-proxy/ranch` instead of hand-built `ssh` commands. The CLI is a local request to the short name; the `ranchd` daemon behind it makes the outbound SSH connection through the tailnet egress proxy with the key and authorizations already in place.

- The node table lives in one place: `~/workspace/ranch-proxy/nodes.json`. Read it when you need a name, an address, or a note; never hardcode node names or IPs in scripts or prose. Report nodes by their short names, per Will's naming rule.

## Commands

- `~/workspace/ranch-proxy/ranch exec <short-name> <command...>` runs a command on one node and exits with the remote exit code. Display names work too ("Ni Knight"); names are normalized to kebab case.

- `~/workspace/ranch-proxy/ranch fanout <command...>` runs a command on all enabled nodes in parallel and labels every result by short name. Use fanout for fleet questions (versions, disk, load, service state) instead of looping ssh yourself.

- `~/workspace/ranch-proxy/ranch status` shows reachability and CPU Tctl per node; `ranch nodes` prints the configured table with its notes (occupied nodes, infrastructure, known breakage).

- `~/workspace/ranch-proxy/ranch copy <short-name> <local> <remote>` copies one file to a node over the same transport, reusing the daemon's control connection.

- `ranch exec`, `fanout` and `copy` auto-start the daemon, so you rarely call `ranch ensure` yourself. If a call reports the daemon down and ensure fails, read `~/workspace/ranch-proxy/state/ranchd.log` before retrying — every wait in the CLI is bounded, so a failure is a real error, not a hang.

## Respect the fleet while you use it

- Check `ranch status` before heavy fan-out. Fanout already enforces Will's thermal pre-flight: a node at or above 75 °C Tctl is skipped (`thermal_hold`) and its temperature reported. Never route around the skip by sshing to the node directly; bursts are fine for directed one-off work on a named node, with off-time after, per the thermal policy.

- Read a node's note before running heavy work on it. Orchid Flow is the fleet NFS server (heavy jobs slow everyone), Quacked Hill is Corus's occupied home, aletheia-core is Theia's home and infrastructure, and Plain View has no usable Ollama models until its store is repaired.

- Keep test and probe traffic in the hostname / uptime / sensors class unless the task itself calls for more. Ranch-first placement still applies: full test suites, builds, and bulk jobs go to ranch nodes (aletheia-core first) rather than the Muse VM — now through `ranch exec` / `ranch fanout`.

## Failure modes, and what they mean

- **"unconfigured node"** — the name is not in `nodes.json`. The daemon can only ever reach configured nodes; that restriction is the design, not a bug. If a node is genuinely missing, add it to `nodes.json` from a verified source (never from memory of an IP) and restart the daemon with `ranch stop` then `ranch ensure`.

- **Uncanny Valley refuses auth** — its SSH user is `jared`, not `wbic16`, and Emise's key is not granted in jared's account (verified 2026-11-05). Do not switch the configured user to work around it; the unblock is Will's key grant into jared's `authorized_keys`.

- **Aurora Continuum, Delta Wood, Best Willow are unreachable** at the egress proxy (no SSH banner). They are configured with `enabled: false`. Don't chase them with retries; they need a reachability look at the physical machines.

- **Latency expectations** — a cold connection costs about 2.0–2.7 s; a warm one through the daemon's control master costs about 0.3–0.5 s. If every call suddenly costs cold latency, a master died; the daemon drops stale sockets and re-establishes them on its own, so just re-run.

- **The AWS box is not a ranch node.** Reach 44.248.235.76 through aletheia-core with `~/workspace/bickford-llama-ranch/deploy/ranch-ssh.sh`, as before. `nodes.json` has a `via` field reserved for expressing that hop later.

## Why it is shaped this way

- The egress proxy at hatch-egress-proxy:3130 cannot resolve tailnet DNS names (measured: banner timeouts 4/4; IPs connect immediately), so the daemon dials the Tailscale IP and carries the DNS name as `HostKeyAlias`. Names are the address in the interface and config; the IP is only the raw dial. The full reasoning is in `~/workspace/ranch-proxy/README.md`.

- Host keys live in `~/workspace/ranch-proxy/state/known_hosts`, inside the persistent workspace, because VM replacements wipe `/root/.ssh/known_hosts` and the loss impersonates a broken key grant. Do not point ranch tooling at the VM's own known_hosts.

## Available connectors

- [Github](~/workspace/custom-connectors/custom.github/CONNECTOR.md) for the emise-tools publish route; the program, README, and this skill are published to wbic16/emise-tools@exo under `ranch-proxy/` and `custom-skills/ranch-proxy/` in the session they change.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.
