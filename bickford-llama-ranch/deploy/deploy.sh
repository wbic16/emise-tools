#!/bin/sh
# Deploy Bickford Llama Ranch to the mirrorborn.us box.
# Route: this machine -> aletheia-core (tailnet, via the hatch-egress-proxy
# Tailscale proxy) -> wbic16@44.248.235.76, as nested ssh — see ranch-ssh.sh
# for why plain `ssh -J` cannot work from this VM (verified 2026-10-31).
# (The AWS box's git-pull deploy key is broken, so files are placed
# directly — same as mirrorborn.us.)
# Idempotent: re-running only re-copies files, re-installs configs, restarts SQ
# (SQ must be restarted, not hot-swapped — replacing a hosted .phext under a
# running SQ wedges it), and reloads nginx after `nginx -t`.
# The seed ranch.phext is installed ONLY if no ranch.phext exists on the server.
#
# Usage: ./deploy.sh [--dry-run]
# Env:   RANCH_HOST (default wbic16@44.248.235.76), RANCH_JUMP (default wbic16@100.88.154.1)
#        SSH_IDENTITY (default ~/.ssh/id_ed25519)
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(dirname "$HERE")
HOST=${RANCH_HOST:-wbic16@44.248.235.76}
JUMP=${RANCH_JUMP:-wbic16@100.88.154.1}
SSH="$HERE/ranch-ssh.sh"
RSYNC_RSH="$HERE/ranch-ssh.sh"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1

run() { echo "+ $*"; if [ "$DRY" = 0 ]; then "$@"; fi; }
remote() { echo "+ ssh $HOST: $*"; if [ "$DRY" = 0 ]; then $SSH "$HOST" "$*"; fi; }

echo "Target: $HOST via jump $JUMP (dry-run=$DRY)"
# Docroots: /sites/web is wbic16-writable. /srv and /etc are root-owned —
# they are created by the one-time sudo setup (deploy/README.md), NOT here,
# so a non-sudo staging run can place everything else first.
remote "mkdir -p /sites/web/bickfordllamaranch.com /sites/web/admin.bickfordllamaranch.com"
remote "mkdir -p /srv/bickford-llama-ranch/data 2>/dev/null || echo 'NOTE: /srv/bickford-llama-ranch not writable yet — sudo setup pending; skipping /srv files this run'"

# Static files (public docroot gets style.css alongside; admin likewise)
run rsync -a -e "$RSYNC_RSH" "$ROOT/site/public/"  "$HOST:/sites/web/bickfordllamaranch.com/"
run rsync -a -e "$RSYNC_RSH" "$ROOT/site/style.css" "$HOST:/sites/web/bickfordllamaranch.com/style.css"
run rsync -a -e "$RSYNC_RSH" "$ROOT/site/admin/"   "$HOST:/sites/web/admin.bickfordllamaranch.com/"
run rsync -a -e "$RSYNC_RSH" "$ROOT/site/style.css" "$HOST:/sites/web/admin.bickfordllamaranch.com/style.css"

# /srv files (remind.py + seed) only once the sudo setup has created the tree.
if [ "$DRY" = 0 ]; then
  if $SSH "$HOST" "test -d /srv/bickford-llama-ranch/data"; then
    rsync -a -e "$RSYNC_RSH" "$ROOT/reminders/remind.py" "$HOST:/srv/bickford-llama-ranch/remind.py"
    # Seed data only if the ranch has no data yet — never overwrite the herd.
    if $SSH "$HOST" "test -f /srv/bickford-llama-ranch/data/ranch.phext"; then
      echo "ranch.phext already on server — seed NOT copied."
    else
      rsync -a -e "$RSYNC_RSH" "$ROOT/seed/ranch.phext" "$HOST:/srv/bickford-llama-ranch/data/ranch.phext"
      echo "Seed ranch.phext installed."
    fi
  else
    echo "Skipping remind.py + seed: /srv/bickford-llama-ranch/data does not exist yet (sudo setup first, then re-run deploy.sh)."
  fi
fi

# Server config
run rsync -a -e "$RSYNC_RSH" "$HERE/nginx-public.conf" "$HOST:/tmp/nginx-public.conf"
run rsync -a -e "$RSYNC_RSH" "$HERE/nginx-admin.conf"  "$HOST:/tmp/nginx-admin.conf"
run rsync -a -e "$RSYNC_RSH" "$HERE/sq-ranch.service"  "$HOST:/tmp/sq-ranch.service"
remote "sudo mkdir -p /etc/bickford-llama-ranch && \
        sudo install -m644 /tmp/nginx-public.conf /etc/nginx/sites-available/bickfordllamaranch.com && \
        sudo install -m644 /tmp/nginx-admin.conf /etc/nginx/sites-available/admin.bickfordllamaranch.com && \
        (test -f /etc/letsencrypt/live/bickfordllamaranch.com/fullchain.pem && sudo ln -sf /etc/nginx/sites-available/bickfordllamaranch.com /etc/nginx/sites-enabled/ || echo 'public vhost installed but NOT enabled — no cert yet (root DNS not on this box)') && \
        sudo ln -sf /etc/nginx/sites-available/admin.bickfordllamaranch.com /etc/nginx/sites-enabled/ && \
        sudo install -m644 /tmp/sq-ranch.service /etc/systemd/system/sq-ranch.service && \
        sudo systemctl daemon-reload"
# One-time server secrets (SQ key + htpasswd + proxy include) are created by hand
# once — see deploy/README.md. deploy.sh refuses to invent or overwrite them.
remote "test -f /etc/bickford-llama-ranch/sq.env && test -f /etc/bickford-llama-ranch/htpasswd && test -f /etc/bickford-llama-ranch/sq-proxy.conf || echo 'MISSING one-time secrets — see deploy/README.md'"

remote "sudo systemctl restart sq-ranch && sudo nginx -t && sudo systemctl reload nginx"
# Reminder cron (daily 07:00 America/Chicago on the box): installed once by hand, see README.
echo "Done. First-time TLS (admin only — the root/www DNS does not point at this box yet): sudo certbot --nginx -d admin.bickfordllamaranch.com"
