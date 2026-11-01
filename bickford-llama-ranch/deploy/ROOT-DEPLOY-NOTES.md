# Root deploy path — notes (2026-10-31)

Added `deploy/root-deploy.sh`: a POSIX sh, `set -eu` script Will can run
**on the AWS box as root** from a git clone of this repo, answering his
"can I just run deploy.sh as root?" — deploy.sh itself can't (its
transport is nested ssh from Emise's VM and its remote lines call sudo).
The new script is independent of all `/tmp` staging from the from-VM
deploy; the only `/tmp` file it touches is the optional SQ 0.6.0 binary.

## What it does (STAGING-REPORT order)

- **Preflight:** refuses unless root (`id -u`, the POSIX form of an EUID
  check); repo root is resolved from the script's own location and
  verified to contain `site/ seed/ reminders/ deploy/`, so it works as
  `./deploy/root-deploy.sh` or from inside `deploy/`. No `sudo` anywhere
  inside — it already is root.
- **§A:** mkdir `/etc/bickford-llama-ranch` + `/srv/bickford-llama-ranch/data`
  (chown wbic16), docroot mkdirs; SQ key generated **only if sq.env is
  absent** (an existing key is never regenerated; a missing sq-proxy.conf
  is rebuilt from it); htpasswd users `libby`/`will` via interactive
  `openssl passwd -apr1` (no htpasswd binary on the box), each skipped if
  already present; smtp.env written **only from interactive prompts**
  (password via `stty -echo`, never printed; empty answers keep the
  report's `<placeholder>` tokens; values single-quoted in the file so
  placeholders survive being sourced by cron), skipped if the file
  exists; reminder cron file; `chmod -R a+rX` on both docroots; ufw /
  AWS-security-group sanity note for port 18765.
- **Copies (the report's §E, folded in):** site files from the checkout
  into both docroots, `remind.py` into `/srv`, seed `ranch.phext` only if
  absent — never over herd data. Docroot chmod repeated after the copy.
- **§B:** SQ upgrade backup-first: skips if already 0.6.0; keeps an
  existing `sq-0.5.6.bak`; installs `/tmp/sq-0.6.0` only after verifying
  the staged binary itself reports 0.6.0; if the binary is missing it
  prints a `cargo install` instruction and **exits before restarting
  anything**; restarts `sq-router sq-backend-wbic16 sq-backend-demo`,
  then verifies 1337/1338/1339 are listening and answering (any HTTP
  code, since the tenants may 401 without a key) — on any failure it
  prints the rollback command and exits 1.
- **§C:** certbot for `admin.bickfordllamaranch.com` only, via the
  report's temporary port-80 vhost sequence; skipped if the cert exists.
- **§D:** installs nginx confs + `sq-ranch.service` from the checkout,
  symlinks admin always, public only if its cert exists, daemon-reload,
  `enable --now` + restart sq-ranch, `nginx -t` then reload.
- **§F:** prints verification results: four SQ ports, ranch SQ version
  (with the sq.env key), admin HTTPS code (expect 401), mirrorborn.us
  code (expect 200), `remind.py --dry-run` with smtp.env sourced.

`--dry-run` prints every step, changes nothing, and bypasses the root
refusal with a warning so the step list can be reviewed by non-root;
interactive prompts are printed as descriptions instead of being read.

## Verification (local, this VM)

- `sh -n` passes (sh is dash here, so this is a real POSIX parse).
- shellcheck is not installed on this VM — not run.
- Full `--dry-run` as root from the repo root and from `deploy/`:
  complete §A–§F step list, exit 0.
- As uid 65534 (in a `/tmp` skeleton checkout, since the VM workspace is
  not readable by other uids): real run refuses with exit 1; `--dry-run`
  prints the warning and the full list, exit 0.
- Script copied alone outside a checkout: repo check refuses, exit 1.
- Not run for real anywhere — the box run is Will's.

## README

`deploy/README.md` gained a "Run as root on the box (full install, one
script)" section above the manual one-time setup, noting `deploy.sh`
remains the from-VM path. The clone URL is left as `<clone-url-of-this-repo>`
— this repo's published remote is Will's to name when he pushes it.
