#!/bin/sh
# discord-ensure.sh — install and start the discord-watch service if needed.
# Idempotent. The canonical unit lives in ~/workspace/discord/ because
# /etc/systemd/system does not survive VM replacement; the backstop cron
# runs this whenever the watcher heartbeat is stale.
set -e
UNIT=/etc/systemd/system/discord-watch.service
SRC="$HOME/workspace/discord/discord-watch.service"
if [ ! -f "$UNIT" ] || ! cmp -s "$SRC" "$UNIT"; then
  cp "$SRC" "$UNIT"
  systemctl daemon-reload
  systemctl enable discord-watch.service >/dev/null 2>&1 || true
  echo "unit installed"
fi
if ! systemctl is-active --quiet discord-watch.service; then
  systemctl start discord-watch.service
  echo "service started"
else
  echo "already running"
fi
