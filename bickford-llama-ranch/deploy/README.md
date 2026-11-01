# Deploy notes — Bickford Llama Ranch

Target: the same AWS box as mirrorborn.us (44.248.235.76), reached by hopping
through aletheia-core. Files go straight into the docroots — the box's GitHub
deploy key is broken, so do not build deploy on `git pull`.

## Run as root on the box (full install, one script)

The preferred path: clone this repo onto the box and run the on-box
installer as root. `root-deploy.sh` performs the whole verified sequence
from `STAGING-REPORT.md` (§A–§F) in order — directories, SQ key, Basic
Auth users, SMTP env, cron, file copies from the checkout, the SQ 0.6.0
upgrade (backup-first, with the rollback command printed on failure),
certbot for admin only, config install, service start, and the
verification checks. It needs no `/tmp` staging from the from-VM deploy,
and it is idempotent: re-running never regenerates the SQ key, an
existing htpasswd user or smtp.env, or the herd's `ranch.phext`.

```sh
git clone https://github.com/wbic16/emise-tools.git
cd emise-tools/bickford-llama-ranch/deploy
sudo ./root-deploy.sh --dry-run   # review every step first (works non-root too)
sudo ./root-deploy.sh             # interactive: htpasswd + SMTP prompts, no echo
```

`deploy.sh` remains the from-VM path (Emise's machine → aletheia-core →
box, non-sudo staging); the manual steps below are the same one-time
setup `root-deploy.sh` automates.

## One-time server setup (by hand, once — automated by root-deploy.sh above)

```sh
sudo mkdir -p /etc/bickford-llama-ranch /srv/bickford-llama-ranch/data

# 1. SQ key — generate one, store it ONLY in these two server files:
KEY=$(head -c32 /dev/urandom | base64 | tr -d /+= | head -c32)
printf 'RANCH_SQ_KEY=%s\n' "$KEY" | sudo tee /etc/bickford-llama-ranch/sq.env        # chmod 600
printf 'proxy_set_header Authorization "%s";\nproxy_set_header Host $host;\n' "$KEY" \
  | sudo tee /etc/bickford-llama-ranch/sq-proxy.conf                                 # chmod 600
sudo chmod 600 /etc/bickford-llama-ranch/sq.env /etc/bickford-llama-ranch/sq-proxy.conf
unset KEY

# 2. Basic-auth users for the admin vhost (Libby + Will):
sudo apt-get install -y apache2-utils   # provides htpasswd, if missing
sudo htpasswd -c /etc/bickford-llama-ranch/htpasswd libby
sudo htpasswd    /etc/bickford-llama-ranch/htpasswd will

# 3. SQ binary: the box's /usr/local/bin/sq v0.5.6 is verified compatible
#    with this app (research/sq-056-compat.md, 2026-10-31). Will approved
#    upgrading it to 0.6.0 on 2026-10-31 — the staged, backup-first upgrade
#    sequence (with router/tenant restarts and verification) is step B of
#    deploy/STAGING-REPORT.md. Never replace the binary without that
#    sequence: it is shared with the production SQ router/tenants on
#    ports 1337-1339.

# 4. Firewall: port 18765 must NOT be public. SQ binds 0.0.0.0 in host mode;
#    the --key is the second line of defence, nginx the first.
```

## Every deploy

```sh
./deploy.sh --dry-run   # prints every step, touches nothing
./deploy.sh             # rsync site + reminders, install configs, restart SQ, nginx -t + reload
```

`deploy.sh` never overwrites an existing server `ranch.phext` — the herd data
only moves server → backups, never laptop → server after day one.

## TLS (one-time)

DNS for `admin.bickfordllamaranch.com` (and the apex/www) must point at the box
first, then:

```sh
sudo certbot --nginx -d bickfordllamaranch.com -d www.bickfordllamaranch.com \
                     -d admin.bickfordllamaranch.com
```

mirrorborn.us on the same box uses Let's Encrypt + HSTS; these vhosts match it.

## Reminder cron (one-time)

```sh
# /etc/cron.d/ranch-reminders — daily 07:00 local, digest via the ranch SMTP env
0 7 * * * wbic16 . /etc/bickford-llama-ranch/smtp.env; /usr/bin/python3 /srv/bickford-llama-ranch/remind.py >>/srv/bickford-llama-ranch/remind.log 2>&1
```

`/etc/bickford-llama-ranch/smtp.env` (chmod 600) holds `RANCH_SMTP_HOST`,
`RANCH_SMTP_PORT`, `RANCH_SMTP_USER`, `RANCH_SMTP_PASS`, `RANCH_SMTP_FROM`,
optionally `RANCH_SMTP_TLS=1`, plus `RANCH_SQ_URL=http://127.0.0.1:18765` and
`RANCH_SQ_KEY` (same value as sq.env). Recipients are NOT here — they live in
the settings scroll (1.1.1/1.1.2/1.1.1) and are edited from the admin page.

## Backup

The whole database is one file: `/srv/bickford-llama-ranch/data/ranch.phext`.
Copy it anywhere to back up the ranch. SQ rewrites it on every edit, so copy
it while SQ is stopped or accept a last-write snapshot.
