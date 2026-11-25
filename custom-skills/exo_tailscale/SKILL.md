# Tailscale — operate the tailnet from the docs, not from folklore

The knowledge base for this skill is **tailscale.phext**
(`~/workspace/phext/tailscale.phext`, source `tailscale-source.json`,
builder `build_tailscale_phext.py`). Read the relevant scroll before
answering or acting; the phext is distilled from Tailscale's official
documentation plus verified house experience. When the docs and a live
test disagree, the live test wins and the phext gets a dated correction.

## First principles

- The control plane distributes a **netmap**; a device can only reach
  what its netmap contains. DNS resolving a name proves nothing about
  reachability. Prove reachability with `tailscale ping` (a "no
  matching peer" answer = not in netmap) and `ip route get` (Linux
  tailscale routes live in table 52).
- Serve, Funnel, subnet routes, and Services are separate features
  with separate gates. One working says nothing about the others.
- Policy is allow-based: ACLs (legacy) and grants (modern) only ever
  allow. For Services, the grant's **destination must name the
  service** (`svc:<name>`) — generic device allows never reach it.

## Services (svc:) — work the gates in order

1. **Definition** — the service exists in the console with endpoints
   and a host tag. Auto-approval does not create it.
2. **Tag identity** — the host carries the service's tag
   (`Self.Tags` in `tailscale status --json`); untagged hosts get
   "service hosts must be tagged nodes". Hosts need Tailscale 1.86+.
3. **Serve config** — `tailscale serve --service=svc:<name> --bg
   <backend>` on the host; verify with `tailscale serve status` and
   the `service-host` capability map.
4. **Approval** — console approval per host, or
   `autoApprovers.services` in the policy mapping the service to the
   host tags allowed to advertise it. If a daemon stays stuck on
   "approval required" after approval: `tailscale serve clear
   svc:<name>`, pause, re-apply (known defect, issue 18821).
5. **Grant** — a `grants` entry with `dst: ["svc:<name>"]` and the
   exact `ip` (e.g. `tcp:443`). Without it the TailVIP never enters
   client netmaps.
6. **Client acceptance** — 1.94+ clients accept TailVIPs regardless
   of `--accept-routes`; older Linux clients need
   `tailscale set --accept-routes`. Verify per build; do not assume.

Full text, syntax, and the house case history: tailscale.phext
scrolls 1.1.1/1.3.1/1.1.1 (Services) and 1.1.1/1.3.1/2.1.1
(troubleshooting).

## House rules for this tailnet

- Never run DNS availability probes from the Muse VM (fake-IP
  resolver); resolve from a ranch node.
- Reach ranch nodes by Tailscale IP through the proxy, named by
  short hostname in all reporting (fleet-ssh.sh / TOOLS.md).
- Node-name Serve HTTPS is the proven production path; Services are
  adopted per-service as their gates are verified, not assumed.
- Anything learned the hard way on this tailnet goes into the
  tailscale.phext house scroll (1.1.1/1.9.1/1.1.1) the same session,
  dated, with the test that proved it.
