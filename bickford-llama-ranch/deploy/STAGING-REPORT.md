# Staging report — Bickford Llama Ranch deploy

Date: 2026-10-31 (America/Chicago). Staged by Emise from this VM, non-sudo only.
**Nothing was sudo'd, no vhost was enabled, no service was started or
restarted, no cert was requested, no secret or htpasswd was created.**

## Result in one line

All non-sudo files are on the box and md5-verified; `deploy.sh` ran for real
and stopped at its first sudo command, exactly where it has to:
`sudo: a terminal is required to read the password … a password is required`
(exit 1). Everything after that line is Will's block, below.

## SSH route — the shipped one was broken; fixed

`deploy.sh` as built used `ssh -J wbic16@100.88.154.1 …`. Tested first,
verbatim: it fails immediately —

```
ssh: connect to host 100.88.154.1 port 22: Operation not permitted
EXIT:255   (deploy.sh stopped at its first remote mkdir; nothing ran)
```

Why: from this VM, ranch nodes are reachable only through the Tailscale
proxy (`nc -X connect -x hatch-egress-proxy:3130`, TOOLS.md), and
`ssh -J` + ProxyCommand cannot be combined. ProxyJump with our local key
also fails: the AWS hop is authenticated by wbic16's key **on
aletheia-core**, not by ours.

**Fix (local, in `deploy/`):** new transport `ranch-ssh.sh` — nested ssh
(hop 1: our key + proxy to aletheia-core; hop 2: run on aletheia-core, its
own key to the box). It serves as both the ssh command and `rsync -e`
transport in `deploy.sh`. Verified: interactive command, a test rsync, and
the full deploy run all pass through it. Two more fixes found live:

- rsync passes `-l <user>` before the host; the wrapper now strips it
  (unstripped, the far shell tried to execute `wbic16` as a command).
- The config files now carry real Let's Encrypt lineage paths instead of
  "certbot will add these" comments, and `deploy.sh` enables the public
  vhost only if its cert already exists (see TLS wrinkle, below).

## Writability on the box (tested as wbic16)

| Path | State |
|---|---|
| `/sites/web/bickfordllamaranch.com` | exists, **writable** |
| `/sites/web/admin.bickfordllamaranch.com` | missing; `/sites/web` is wbic16-owned → **created by deploy.sh** |
| `/srv/bickford-llama-ranch/data` | missing; `/srv` is `root:root` → **NOT writable, needs sudo** |
| `/etc/bickford-llama-ranch` | missing; `/etc` → **needs sudo** |

Consequence: `remind.py` and the seed `ranch.phext` could **not** be staged
yet — they land on the first `deploy.sh` re-run after Will creates the
`/srv` tree (step A below, then step E).

## What is on the box now (all md5-verified against local copies)

```
/sites/web/admin.bickfordllamaranch.com/   index.html 3,208 · app.js 9,737 · style.css 1,683
/sites/web/bickfordllamaranch.com/         index.html   756 · home.js   852 · style.css 1,683
/tmp/nginx-admin.conf    (updated staged copy, md5 3d2935a1e69db188880b9d252c5bf191)
/tmp/nginx-public.conf   (updated staged copy, md5 9961935d73846a0b88eb9d4c6b99f25c)
/tmp/sq-ranch.service
/tmp/sq-0.6.0            SQ 0.6.0 binary, md5 d09666169c3195d0b056f7228de30d3e —
                         executed on the box: `sq version` → 0.6.0. Ready to install.
```

Not on the box: `/srv/bickford-llama-ranch/` (absent), seed (not installed),
any `/etc/bickford-llama-ranch/` secrets, any new vhost.

## Production untouched — verified after staging

- SQ ports **1337 / 1338 / 1339 still listening**; 18765 not listening (expected).
- `/etc/nginx/sites-enabled/` unchanged — the only Bickford entry is the
  pre-existing `staging.bickfordllamaranch.com`, untouched.
- `https://mirrorborn.us/` → **200** from this VM.
- Box SQ is still the stock 0.5.6 (`/usr/local/bin/sq`, 14,055,712 B).

One caution for step D: staged docroot files are mode `660` (wbic16:wbic16).
On this box that pattern caused a 403 for nginx before (mirrorborn blog
deploy, 2026-10-30) — step A includes the `chmod` that prevents it.

---

## Will's sudo block — run in an interactive SSH session ON the box, in order

(`deploy.sh` cannot run these from this VM: its sudo lines get
"a terminal is required". That stop is expected, not a failure.)

### A. Directories, secrets, cron, permissions (one-time, from deploy/README.md)

```sh
sudo mkdir -p /etc/bickford-llama-ranch /srv/bickford-llama-ranch/data
sudo chown wbic16:wbic16 /srv/bickford-llama-ranch /srv/bickford-llama-ranch/data

# SQ key — server-side only, never in JS or this repo:
KEY=$(head -c32 /dev/urandom | base64 | tr -d /+= | head -c32)
printf 'RANCH_SQ_KEY=%s\n' "$KEY" | sudo tee /etc/bickford-llama-ranch/sq.env
printf 'proxy_set_header Authorization "%s";\nproxy_set_header Host $host;\n' "$KEY" \
  | sudo tee /etc/bickford-llama-ranch/sq-proxy.conf
sudo chmod 600 /etc/bickford-llama-ranch/sq.env /etc/bickford-llama-ranch/sq-proxy.conf

# Basic-auth users (box has NO htpasswd binary — openssl method needs no install;
# or first: sudo apt-get install -y apache2-utils, then use htpasswd -c):
printf 'libby:%s\n' "$(openssl passwd -apr1)" | sudo tee    /etc/bickford-llama-ranch/htpasswd
printf 'will:%s\n'  "$(openssl passwd -apr1)" | sudo tee -a /etc/bickford-llama-ranch/htpasswd
sudo chmod 640 /etc/bickford-llama-ranch/htpasswd

# SMTP env for reminders (AgentMail or Amazon SES — your pick; the box has
# no mail stack of its own). Recipients are NOT here — they live in the
# settings scroll and are edited from the admin page.
sudo tee /etc/bickford-llama-ranch/smtp.env >/dev/null <<EOF
RANCH_SMTP_HOST=<host>
RANCH_SMTP_PORT=<port>
RANCH_SMTP_USER=<user>
RANCH_SMTP_PASS=<pass>
RANCH_SMTP_FROM=<from-address>
RANCH_SMTP_TLS=1
RANCH_SQ_URL=http://127.0.0.1:18765
RANCH_SQ_KEY=$KEY
EOF
sudo chmod 600 /etc/bickford-llama-ranch/smtp.env
unset KEY

# Reminder cron (daily 07:00 box-local):
printf '0 7 * * * wbic16 . /etc/bickford-llama-ranch/smtp.env; /usr/bin/python3 /srv/bickford-llama-ranch/remind.py >>/srv/bickford-llama-ranch/remind.log 2>&1\n' \
  | sudo tee /etc/cron.d/ranch-reminders

# nginx must be able to read the staged docroots:
sudo chmod -R a+rX /sites/web/admin.bickfordllamaranch.com /sites/web/bickfordllamaranch.com

# Sanity: port 18765 must NOT be publicly reachable (SQ binds 0.0.0.0;
# the --key + nginx are the defences — confirm the firewall agrees):
sudo ufw status 2>/dev/null | grep 18765 || echo "check AWS security group for 18765"
```

### B. SQ upgrade 0.5.6 → 0.6.0 — APPROVED by Will 2026-10-31

Binary already staged and test-run at `/tmp/sq-0.6.0` (see above).

```sh
sudo cp /usr/local/bin/sq /usr/local/bin/sq-0.5.6.bak     # backup / rollback point
sudo install -m755 /tmp/sq-0.6.0 /usr/local/bin/sq
sq version                                                # expect: 0.6.0
sudo systemctl restart sq-router sq-backend-wbic16 sq-backend-demo
# (sq-ranch is restarted in step D, once its unit is installed.)
# Rollback if anything misbehaves: sudo install -m755 /usr/local/bin/sq-0.5.6.bak /usr/local/bin/sq
#   then restart the same three units.
```

> **Doc debt:** `deploy/README.md` §3 still says "Do NOT upgrade or replace"
> the box SQ. That wording is **superseded by Will's 2026-10-31 approval**
> and the README needs a post-staging update to match (the 0.5.6
> compatibility note stays as history). Not edited during staging, per
> instructions — flagged here so it isn't lost.

### C. TLS for admin ONLY (root/www DNS does not point at this box yet)

Wrinkle, plainly: the staged vhost files reference their cert paths, so
enabling the admin vhost before a cert exists fails `nginx -t`. Certbot
needs a live port-80 vhost to answer the challenge. Sequence that works:

```sh
# Temporary port-80-only vhost so certbot can find and verify the name:
sudo tee /etc/nginx/sites-available/admin-temp >/dev/null <<'EOF'
server {
    listen 80;
    server_name admin.bickfordllamaranch.com;
    root /sites/web/admin.bickfordllamaranch.com;
    index index.html;
}
EOF
sudo ln -sf /etc/nginx/sites-available/admin-temp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d admin.bickfordllamaranch.com     # admin ONLY
sudo rm /etc/nginx/sites-enabled/admin-temp
```

Do **not** add `bickfordllamaranch.com` / `www` to certbot until their DNS
points at this box (Will: planned, after admin is done). For the same
reason the staged public vhost must stay disabled until then —
`deploy.sh` now checks for its cert before symlinking it.

### D. Install configs and start services (deploy.sh's sudo lines, verbatim)

```sh
sudo mkdir -p /etc/bickford-llama-ranch
sudo install -m644 /tmp/nginx-public.conf /etc/nginx/sites-available/bickfordllamaranch.com
sudo install -m644 /tmp/nginx-admin.conf  /etc/nginx/sites-available/admin.bickfordllamaranch.com
sudo ln -sf /etc/nginx/sites-available/admin.bickfordllamaranch.com /etc/nginx/sites-enabled/
sudo install -m644 /tmp/sq-ranch.service /etc/systemd/system/sq-ranch.service
sudo systemctl daemon-reload
sudo systemctl enable --now sq-ranch
sudo systemctl restart sq-ranch
sudo nginx -t && sudo systemctl reload nginx
```

(Deliberately no public-vhost symlink here — see step C.)

### E. Back on this VM: re-run `./deploy.sh`

With `/srv` now existing, it places `remind.py` and the seed `ranch.phext`,
refreshes the `/tmp` config copies, then stops at the sudo line again —
expected and harmless; steps A–D already did that work by hand.

### F. Verify (any shell)

```sh
ss -ltn | grep -E '1337|1338|1339|18765'                       # all four listening
curl -s http://127.0.0.1:18765/api/v2/version?p=ranch          # SQ 0.6.0 answers
curl -I https://admin.bickfordllamaranch.com/                  # 401 = Basic Auth gate is up
curl -s https://mirrorborn.us/ -o /dev/null -w '%{http_code}'  # still 200
/usr/bin/python3 /srv/bickford-llama-ranch/remind.py --dry-run # digest prints, nothing sent
```

## deploy.sh changes made during staging (all local, in `deploy/`)

1. **New `ranch-ssh.sh`** transport (nested ssh via the Tailscale proxy);
   `SSH`/`RSYNC_RSH` now point at it. Fixes the `EXIT:255` first-step failure.
2. Wrapper strips rsync's leading `-l <user>` preamble.
3. First remote mkdir no longer includes `/etc/…` (root-owned); `/srv`
   mkdir is best-effort with a printed note, and `remind.py`/seed rsyncs
   run only when `/srv/…/data` exists — so a non-sudo staging run places
   everything it can instead of aborting.
4. Sudo install line gained `sudo mkdir -p /etc/bickford-llama-ranch`;
   public-vhost symlink is now conditional on its cert existing.
5. Final TLS hint line corrected to **admin only**.
6. `nginx-admin.conf` / `nginx-public.conf`: certbot comment replaced with
   the deterministic Let's Encrypt lineage paths for each name.
