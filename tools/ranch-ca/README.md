# ranch-ca — the Ranch Root CA and fake-TLS generator

Our own certificate authority for ranch-internal names and end-to-end test
rigs (Will's directive, 2026-11-22: full e2e validation before anything
publishes to prod, without doubling the AWS bill). This CA is the trust root
for the ranch-side awsbox replica/tests and internal service names.

It is deliberately a *separate* trust domain from the Ranch Choir Squid CA
(/etc/squid/ssl/ on aletheia-core): that CA exists to ssl-bump proxy traffic,
its distribution to the fleet is known-broken, and an interception root must
never double as a service-identity root.

## The root

- Subject: `C=US, ST=Nebraska, L=Ranch, O=RanchChoir, CN=Ranch Root CA`
- Algorithm: EC P-384, SHA-384 — small, fast, supported by every TLS stack
  on the fleet and on Will's devices; the root signs rarely, so the
  stronger curve costs nothing.
- Validity: 2026-11-22 → 2036-11-19 (~10 years)
- Extensions: CA:TRUE (pathlen 1), key usage = certificate signing only
- SHA-256 fingerprint:
  `46:F3:AB:32:51:4D:34:EF:60:C2:2E:DC:D4:77:81:77:5B:13:20:B3:64:6D:6C:58:BC:4C:AA:21:33:E9:28:81`
- Created: EE 112 (2026-11-22)

## Where things live

The CA itself lives **only** on aletheia-core, in `~/ranch-ca/` (dir 700):

- `root-ca.key.pem` — the root private key, mode 600. It never leaves the
  hub: never in git, never in chat, never copied to another node.
- `root-ca.crt` — the root certificate (public; the copy in this repo is
  the same file).
- `issue.sh` — the leaf issuer (below).
- `ledger.txt` — append-only issuance ledger: serial, hostname, SANs,
  issued UTC + Exocortical Epoch, expiry, leaf SHA-256 fingerprint.
- `issued/<hostname>/` — per-leaf `key.pem` (600), `cert.pem`,
  `fullchain.pem`.

This repo directory carries the tooling only: `issue.sh`, `install-root.sh`,
`README.md`, and the public `root-ca.crt`. No private keys, ever.

## Issuing a leaf

On aletheia-core:

```
~/ranch-ca/issue.sh <hostname> [extra-san ...]
```

Extra SANs are DNS names; prefix an IP as `IP:1.2.3.4`. Leaves are EC P-256,
serverAuth, ~1 year, signed by the root, ledgered, and the tool prints the
leaf's SHA-256 fingerprint. Example: `~/ranch-ca/issue.sh e2e.test.ranch`.

## Trusting the root

- Ranch Linux nodes: `sudo bash install-root.sh` (installs into
  /usr/local/share/ca-certificates, runs update-ca-certificates, verifies
  against the rebuilt bundle). Installed and verified 2026-11-22 on
  aletheia-core, rock-mountain, scroll-central, quacked-hill, orchid-flow,
  ni-knight, ashfall-haven, lighthouse-omen, halycon-vector, elven-path,
  free-fall, logos-prime, yeet-max, kaleidoscope-one, moon-beam,
  west-lincoln, jacked-kite, plain-view, and the Muse VM.
  Not installed: great-white (box returns I/O errors; key grant outstanding),
  delta-wood / best-willow (dark), trust-fall / victory-galleon /
  aurora-continuum (unlocated).
- Will's own devices (Android, Windows on lilly, browsers): see
  `~/workspace/your_files/ranch-root-ca-install.md` — the fingerprint above
  is the check that the cert being installed is this one.

## Verification (EE 112)

Leaf `e2e.test.ranch` (serial 1000) served by a throwaway `openssl s_server`
on aletheia-core:18443; from rock-mountain, `curl --noproxy '*'` with no
`-k` returned HTTP 200 with `ssl_verify=0`, and `openssl s_client
-verify_return_error` reported `Verify return code: 0 (ok)`. Test server
torn down after the check.
