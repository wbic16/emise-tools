#!/bin/sh
# root-deploy.sh — full on-box install of Bickford Llama Ranch.
#
# Run ON the AWS box (44.248.235.76, same box as mirrorborn.us) AS ROOT,
# from a git clone of this repo:
#
#     git clone <clone-url-of-this-repo> bickford-llama-ranch
#     cd bickford-llama-ranch/deploy
#     sudo ./root-deploy.sh
#
# It performs the verified step list of deploy/STAGING-REPORT.md in order:
# §A dirs/secrets/auth/cron/permissions, file copies from this checkout
# (the report's §E — the from-VM re-run — is folded in here), §B SQ upgrade,
# §C certbot for admin ONLY, §D config install + services, §F verification.
# It does NOT depend on any /tmp staging from the from-VM deploy; the only
# /tmp file it uses is the optional staged SQ 0.6.0 binary (§B), and it
# stops with instructions if that binary is absent.
#
# There is no `sudo` in this script — it must already be root.
# Idempotent: re-running never regenerates an existing SQ key, never
# re-prompts for an existing htpasswd user or smtp.env, and never
# overwrites an existing ranch.phext (the herd data).
#
# Usage: ./root-deploy.sh [--dry-run]
#   --dry-run prints every step and changes nothing; it may be run as a
#   non-root user purely to review the step list (a warning is printed).
set -eu
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(dirname "$SCRIPT_DIR")

ETC=/etc/bickford-llama-ranch
SRV=/srv/bickford-llama-ranch
PUB=/sites/web/bickfordllamaranch.com
ADM=/sites/web/admin.bickfordllamaranch.com
SQBIN=/usr/local/bin/sq
SQBAK=/usr/local/bin/sq-0.5.6.bak

run() { echo "+ $*"; if [ "$DRY" = 0 ]; then "$@"; fi; }
say() { echo; echo "== $*"; }

# ---------------------------------------------------------------- preflight
# (id -u is the POSIX form of the EUID check.)
if [ "$(id -u)" != "0" ]; then
  if [ "$DRY" = 1 ]; then
    echo "WARNING: not running as root — dry-run only, nothing will be changed."
  else
    echo "ERROR: root-deploy.sh must be run as root (try: sudo $0)" >&2
    exit 1
  fi
fi
for d in site seed reminders deploy; do
  if [ ! -d "$ROOT/$d" ]; then
    echo "ERROR: $ROOT/$d not found — run this from a full repo checkout." >&2
    exit 1
  fi
done
echo "Repo root: $ROOT (dry-run=$DRY)"

# ------------------------------------------------------- A. dirs + secrets
say "A. Directories, SQ key, Basic Auth, SMTP env, cron, permissions"
run mkdir -p "$ETC" "$SRV/data" "$PUB" "$ADM"
run chown wbic16:wbic16 "$SRV" "$SRV/data"

# SQ key — server-side only, never in JS or this repo. Created once; an
# existing sq.env is always kept (rotating it would break the running SQ
# and the nginx proxy include at different times).
KEY=""
if [ -f "$ETC/sq.env" ]; then
  echo "sq.env already exists — keeping the existing SQ key."
  KEY=$(sed -n 's/^RANCH_SQ_KEY=//p' "$ETC/sq.env" | head -n 1)
  if [ ! -f "$ETC/sq-proxy.conf" ]; then
    if [ "$DRY" = 1 ]; then
      echo "+ write $ETC/sq-proxy.conf from the existing sq.env key (chmod 600)"
    else
      printf 'proxy_set_header Authorization "%s";\nproxy_set_header Host $host;\n' "$KEY" \
        > "$ETC/sq-proxy.conf"
      chmod 600 "$ETC/sq-proxy.conf"
      echo "sq-proxy.conf regenerated from existing sq.env."
    fi
  fi
else
  if [ "$DRY" = 1 ]; then
    echo "+ generate SQ key; write $ETC/sq.env and $ETC/sq-proxy.conf (chmod 600)"
    KEY="<generated-at-runtime>"
  else
    KEY=$(head -c32 /dev/urandom | base64 | tr -d /+= | head -c32)
    printf 'RANCH_SQ_KEY=%s\n' "$KEY" > "$ETC/sq.env"
    printf 'proxy_set_header Authorization "%s";\nproxy_set_header Host $host;\n' "$KEY" \
      > "$ETC/sq-proxy.conf"
    chmod 600 "$ETC/sq.env" "$ETC/sq-proxy.conf"
    echo "SQ key generated into sq.env + sq-proxy.conf (chmod 600)."
  fi
fi

# Basic-auth users (box has NO htpasswd binary — `openssl passwd -apr1`
# prompts interactively without echo and needs no install). Users already
# in the file are skipped, so a re-run never clobbers a set password.
HTP="$ETC/htpasswd"
for user in libby will; do
  if [ -f "$HTP" ] && grep -q "^$user:" "$HTP"; then
    echo "htpasswd: user '$user' already present — skipped."
  elif [ "$DRY" = 1 ]; then
    echo "+ prompt for '$user' Basic Auth password (openssl passwd -apr1) and append to $HTP"
  else
    echo "Set the Basic Auth password for user '$user':"
    HASH=$(openssl passwd -apr1)
    printf '%s:%s\n' "$user" "$HASH" >> "$HTP"
  fi
done
if [ "$DRY" = 0 ] && [ -f "$HTP" ]; then chmod 640 "$HTP"; fi

# SMTP env for reminders (AgentMail or Amazon SES — the box has no mail
# stack of its own). Prompted interactively, once; the password is read
# with echo off and is never printed. Empty answers keep the report's
# <placeholder> tokens — edit the file by hand later to fill them in.
# Values are single-quoted in the file so placeholders/odd characters
# survive being sourced by cron. Recipients are NOT here — they live in
# the settings scroll and are edited from the admin page.
ask() { # $1 = label, $2 = value-if-empty; prints the answer on stdout
  printf '%s: ' "$1" >&2
  read -r _ans || _ans=""
  [ -z "$_ans" ] && _ans="$2"
  printf '%s' "$_ans" | tr -d "'"
}
SMTPF="$ETC/smtp.env"
if [ -f "$SMTPF" ]; then
  echo "smtp.env already exists — skipped (edit $SMTPF by hand to change it)."
elif [ "$DRY" = 1 ]; then
  echo "+ prompt for RANCH_SMTP_HOST/PORT/USER/PASS (no echo)/FROM and write $SMTPF (chmod 600, RANCH_SQ_KEY from sq.env)"
else
  echo "SMTP settings for the reminder digest (press Enter to keep a <placeholder>):"
  SMTP_HOST=$(ask "SMTP host" "<host>")
  SMTP_PORT=$(ask "SMTP port" "<port>")
  SMTP_USER=$(ask "SMTP user" "<user>")
  printf 'SMTP password (not echoed): ' >&2
  if [ -t 0 ]; then stty -echo; fi
  read -r SMTP_PASS || SMTP_PASS=""
  if [ -t 0 ]; then stty echo; fi
  printf '\n' >&2
  [ -z "$SMTP_PASS" ] && SMTP_PASS="<pass>"
  SMTP_PASS=$(printf '%s' "$SMTP_PASS" | tr -d "'")
  SMTP_FROM=$(ask "SMTP from address" "<from-address>")
  {
    printf "RANCH_SMTP_HOST='%s'\n" "$SMTP_HOST"
    printf "RANCH_SMTP_PORT='%s'\n" "$SMTP_PORT"
    printf "RANCH_SMTP_USER='%s'\n" "$SMTP_USER"
    printf "RANCH_SMTP_PASS='%s'\n" "$SMTP_PASS"
    printf "RANCH_SMTP_FROM='%s'\n" "$SMTP_FROM"
    printf "RANCH_SMTP_TLS='1'\n"
    printf "RANCH_SQ_URL='http://127.0.0.1:18765'\n"
    printf "RANCH_SQ_KEY='%s'\n" "$KEY"
  } > "$SMTPF"
  chmod 600 "$SMTPF"
  echo "smtp.env written (chmod 600)."
fi
unset KEY

# Reminder cron (daily 07:00 box-local). Fixed content — rewritten as-is.
CRON_LINE='0 7 * * * wbic16 . /etc/bickford-llama-ranch/smtp.env; /usr/bin/python3 /srv/bickford-llama-ranch/remind.py >>/srv/bickford-llama-ranch/remind.log 2>&1'
if [ "$DRY" = 1 ]; then
  echo "+ write /etc/cron.d/ranch-reminders: $CRON_LINE"
else
  printf '%s\n' "$CRON_LINE" > /etc/cron.d/ranch-reminders
  chmod 644 /etc/cron.d/ranch-reminders
fi

# nginx must be able to read the docroots (files staged 660 caused a 403
# on this box before — mirrorborn blog deploy, 2026-10-30).
run chmod -R a+rX "$ADM" "$PUB"

# Sanity: port 18765 must NOT be publicly reachable (SQ binds 0.0.0.0;
# the --key + nginx are the defences — confirm the firewall agrees).
if [ "$DRY" = 1 ]; then
  echo "+ check ufw / AWS security group: port 18765 must not be public"
elif command -v ufw >/dev/null 2>&1; then
  ufw status 2>/dev/null | grep 18765 \
    || echo "NOTE: ufw shows no 18765 rule — also check the AWS security group for 18765."
else
  echo "NOTE: no ufw on this box — check the AWS security group for 18765."
fi

# ------------------------------------------------- file copies (§E folded)
say "Files from this checkout (public + admin docroots, remind.py, seed)"
run cp -a "$ROOT/site/public/." "$PUB/"
run cp -a "$ROOT/site/style.css" "$PUB/style.css"
run cp -a "$ROOT/site/admin/." "$ADM/"
run cp -a "$ROOT/site/style.css" "$ADM/style.css"
run install -m644 "$ROOT/reminders/remind.py" "$SRV/remind.py"
# Seed data only if the ranch has no data yet — never overwrite the herd.
if [ "$DRY" = 1 ]; then
  echo "+ install seed/ranch.phext to $SRV/data/ranch.phext ONLY if absent (never overwrite)"
else
  if [ -f "$SRV/data/ranch.phext" ]; then
    echo "ranch.phext already on server — seed NOT copied."
  else
    install -m644 -o wbic16 -g wbic16 "$ROOT/seed/ranch.phext" "$SRV/data/ranch.phext"
    echo "Seed ranch.phext installed."
  fi
fi
# Files just copied may land unreadable by nginx — repeat the §A chmod.
run chmod -R a+rX "$ADM" "$PUB"

# ------------------------------------------------------------ B. SQ upgrade
say "B. SQ upgrade 0.5.6 -> 0.6.0 (approved by Will 2026-10-31)"
if [ "$DRY" = 1 ]; then
  echo "+ current=\$($SQBIN version); if it already reports 0.6.0, skip this section"
  echo "+ cp $SQBIN $SQBAK (backup kept if one already exists)"
  echo "+ install -m755 /tmp/sq-0.6.0 $SQBIN — if /tmp/sq-0.6.0 is missing, print the cargo-install instruction and STOP before restarting anything"
  echo "+ systemctl restart sq-router sq-backend-wbic16 sq-backend-demo"
  echo "+ verify ports 1337 1338 1339 answer; on failure print the rollback command and exit"
else
  CUR=$("$SQBIN" version 2>/dev/null || true)
  echo "Current SQ version: ${CUR:-unknown}"
  case "$CUR" in
    *0.6.0*)
      echo "SQ is already 0.6.0 — upgrade skipped."
      ;;
    *)
      if [ ! -f /tmp/sq-0.6.0 ]; then
        echo "ERROR: /tmp/sq-0.6.0 is not present — cannot upgrade SQ here." >&2
        echo "Build or stage the 0.6.0 binary first, e.g.:" >&2
        echo "  cargo install sq --version 0.6.0 --root /tmp/sq060 && cp /tmp/sq060/bin/sq /tmp/sq-0.6.0" >&2
        echo "Stopping BEFORE restarting anything. Nothing else was changed by this section; re-run $0 once /tmp/sq-0.6.0 exists." >&2
        exit 1
      fi
      NEWVER=$(/tmp/sq-0.6.0 version 2>/dev/null || true)
      case "$NEWVER" in
        *0.6.0*) : ;;
        *)
          echo "ERROR: /tmp/sq-0.6.0 reports '${NEWVER:-unknown}', not 0.6.0 — refusing to install it." >&2
          exit 1
          ;;
      esac
      if [ -f "$SQBAK" ]; then
        echo "Backup $SQBAK already exists — keeping the original backup."
      else
        cp "$SQBIN" "$SQBAK"
        echo "Backed up the current binary to $SQBAK."
      fi
      install -m755 /tmp/sq-0.6.0 "$SQBIN"
      echo "Installed SQ: $("$SQBIN" version 2>/dev/null || echo unknown)"
      if ! systemctl restart sq-router sq-backend-wbic16 sq-backend-demo; then
        echo "ERROR: restarting the SQ tenants failed. Roll back with:" >&2
        echo "  install -m755 $SQBAK $SQBIN && systemctl restart sq-router sq-backend-wbic16 sq-backend-demo" >&2
        exit 1
      fi
      sleep 2
      FAIL=0
      for p in 1337 1338 1339; do
        CODE=$(curl -s -o /dev/null -w '%{http_code}' -m 5 "http://127.0.0.1:$p/api/v2/version?p=" || true)
        if ss -ltn | grep -q ":$p " && [ "$CODE" != "000" ]; then
          echo "port $p: answering (HTTP $CODE)"
        else
          echo "port $p: NOT answering"
          FAIL=1
        fi
      done
      if [ "$FAIL" = 1 ]; then
        echo "ERROR: one or more SQ tenants did not come back after the upgrade. Roll back with:" >&2
        echo "  install -m755 $SQBAK $SQBIN && systemctl restart sq-router sq-backend-wbic16 sq-backend-demo" >&2
        exit 1
      fi
      echo "SQ tenants verified on 0.6.0 (sq-ranch starts in section D)."
      ;;
  esac
fi

# ------------------------------------------------------------- C. TLS admin
say "C. TLS for admin.bickfordllamaranch.com ONLY (root/www DNS is not on this box yet)"
ADMIN_CERT=/etc/letsencrypt/live/admin.bickfordllamaranch.com/fullchain.pem
if [ -f "$ADMIN_CERT" ]; then
  echo "Admin certificate already exists — certbot skipped."
elif [ "$DRY" = 1 ]; then
  echo "+ write temporary port-80-only vhost /etc/nginx/sites-available/admin-temp and enable it"
  echo "+ nginx -t && systemctl reload nginx"
  echo "+ certbot --nginx -d admin.bickfordllamaranch.com"
  echo "+ rm /etc/nginx/sites-enabled/admin-temp"
else
  # The real admin vhost references its cert paths, so it cannot pass
  # nginx -t until a cert exists; certbot needs a live port-80 vhost to
  # answer the challenge. Temporary vhost first (STAGING-REPORT §C).
  cat > /etc/nginx/sites-available/admin-temp <<'EOF'
server {
    listen 80;
    server_name admin.bickfordllamaranch.com;
    root /sites/web/admin.bickfordllamaranch.com;
    index index.html;
}
EOF
  ln -sf /etc/nginx/sites-available/admin-temp /etc/nginx/sites-enabled/
  nginx -t && systemctl reload nginx
  certbot --nginx -d admin.bickfordllamaranch.com
  rm -f /etc/nginx/sites-enabled/admin-temp
  echo "Admin certificate issued; temporary vhost disabled."
fi

# ------------------------------------------------------ D. configs + services
say "D. Install nginx configs + sq-ranch unit, start services"
run install -m644 "$ROOT/deploy/nginx-public.conf" /etc/nginx/sites-available/bickfordllamaranch.com
run install -m644 "$ROOT/deploy/nginx-admin.conf" /etc/nginx/sites-available/admin.bickfordllamaranch.com
run ln -sf /etc/nginx/sites-available/admin.bickfordllamaranch.com /etc/nginx/sites-enabled/
# Public vhost is enabled only once its cert exists (its DNS moves here later).
if [ "$DRY" = 1 ]; then
  echo "+ ln -sf /etc/nginx/sites-available/bickfordllamaranch.com /etc/nginx/sites-enabled/ ONLY if /etc/letsencrypt/live/bickfordllamaranch.com/fullchain.pem exists"
elif [ -f /etc/letsencrypt/live/bickfordllamaranch.com/fullchain.pem ]; then
  ln -sf /etc/nginx/sites-available/bickfordllamaranch.com /etc/nginx/sites-enabled/
  echo "Public vhost enabled (cert exists)."
else
  echo "Public vhost installed but NOT enabled — no cert yet (root DNS not on this box)."
fi
run install -m644 "$ROOT/deploy/sq-ranch.service" /etc/systemd/system/sq-ranch.service
run systemctl daemon-reload
run systemctl enable --now sq-ranch
run systemctl restart sq-ranch
if [ "$DRY" = 1 ]; then
  echo "+ nginx -t && systemctl reload nginx"
else
  nginx -t
  systemctl reload nginx
fi

# ------------------------------------------------------------ F. verification
say "F. Verification"
if [ "$DRY" = 1 ]; then
  echo "+ ss -ltn | grep -E '1337|1338|1339|18765'   (all four SQ ports listening)"
  echo "+ curl http://127.0.0.1:18765/api/v2/version?p=ranch with the sq.env key (SQ answers)"
  echo "+ curl -s -o /dev/null -w '%{http_code}' https://admin.bickfordllamaranch.com/   (expect 401 = Basic Auth gate up)"
  echo "+ curl -s -o /dev/null -w '%{http_code}' https://mirrorborn.us/   (expect 200, production untouched)"
  echo "+ python3 $SRV/remind.py --dry-run with smtp.env sourced (digest prints, nothing sent)"
else
  echo "-- SQ ports (expect 1337, 1338, 1339, 18765):"
  ss -ltn | grep -E '1337|1338|1339|18765' || echo "  WARNING: some SQ ports are not listening."
  SQKEY=$(sed -n 's/^RANCH_SQ_KEY=//p' "$ETC/sq.env" 2>/dev/null | head -n 1)
  printf '%s' "-- ranch SQ version: "
  curl -s -m 5 -H "Authorization: $SQKEY" "http://127.0.0.1:18765/api/v2/version?p=ranch" || echo "(no answer)"
  echo
  printf '%s' "-- https://admin.bickfordllamaranch.com/ HTTP code (expect 401): "
  curl -s -o /dev/null -w '%{http_code}\n' -m 10 https://admin.bickfordllamaranch.com/ || echo "(unreachable)"
  printf '%s' "-- https://mirrorborn.us/ HTTP code (expect 200): "
  curl -s -o /dev/null -w '%{http_code}\n' -m 10 https://mirrorborn.us/ || echo "(unreachable)"
  echo "-- remind.py --dry-run:"
  if [ -f "$ETC/smtp.env" ]; then
    ( set -a; . "$ETC/smtp.env"; set +a; /usr/bin/python3 "$SRV/remind.py" --dry-run ) \
      || echo "  (remind.py dry-run failed — check smtp.env values and that sq-ranch is up)"
  else
    echo "  skipped: $ETC/smtp.env does not exist."
  fi
fi

say "Done"
echo "Still manual, by design:"
echo "  - If smtp.env holds <placeholder> values, edit $ETC/smtp.env (chmod 600) with the real AgentMail/SES settings."
echo "  - Reminder recipients live in the settings scroll (1.1.1/1.1.2/1.1.1) — set them from the admin page."
echo "  - Later, once admin is verified: point bickfordllamaranch.com + www DNS at this box, extend the cert, and re-run this script to enable the public vhost."
