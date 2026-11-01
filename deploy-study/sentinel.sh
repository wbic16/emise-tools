#!/bin/sh
# Deploy Continuity Study sentinel.
# Appends one JSON line to ledger.jsonl (same directory as this script).
# Read-only apart from that append. Safe to run concurrently (flock).
# Usage: sh sentinel.sh [note]
set -u

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LEDGER="$DIR/ledger.jsonl"
HEARTBEAT_FILE="$HOME/workspace/discord/heartbeat"
NOTE=${1:-}

BOOT_ID=$(cat /proc/sys/kernel/random/boot_id 2>/dev/null || echo "unknown")
BTIME=$(awk '/^btime/{print $2}' /proc/stat 2>/dev/null || echo 0)
UPTIME_S=$(awk '{printf "%d", $1}' /proc/uptime 2>/dev/null || echo 0)
TS=$(date +%s)
TS_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

if pgrep -x sq >/dev/null 2>&1; then SQ=true; else SQ=false; fi

# Visibility-gap trio (added 2026-10-31 at William's direction): what the host
# reports, what the host has suffered, and what this namespace actually holds.
HOST_MEM_AVAIL_KB=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo 2>/dev/null || echo null)
[ -z "$HOST_MEM_AVAIL_KB" ] && HOST_MEM_AVAIL_KB=null
HOST_OOM_KILLS=$(awk '/^oom_kill/{print $2}' /proc/vmstat 2>/dev/null || echo null)
[ -z "$HOST_OOM_KILLS" ] && HOST_OOM_KILLS=null
NS_RSS_KB=$(awk '/^VmRSS:/{s+=$2} END{print s+0}' /proc/[0-9]*/status 2>/dev/null || echo null)
[ -z "$NS_RSS_KB" ] && NS_RSS_KB=null

if [ -f "$HEARTBEAT_FILE" ]; then
  HB=$(cat "$HEARTBEAT_FILE" 2>/dev/null || echo "")
  case "$HB" in
    ''|*[!0-9]*) HB_AGE=null ;;
    *) HB_AGE=$((TS - HB)); [ "$HB_AGE" -lt 0 ] && HB_AGE=0 ;;
  esac
else
  HB_AGE=null
fi

# Last boot_id recorded by a prior sentinel/boot line (for change detection).
LAST_BOOT=""
if [ -f "$LEDGER" ]; then
  LAST_BOOT=$(grep '"boot_id"' "$LEDGER" 2>/dev/null | tail -n 1 | sed -n 's/.*"boot_id": "\([^"]*\)".*/\1/p')
fi
if [ -z "$LAST_BOOT" ] || [ "$LAST_BOOT" = "$BOOT_ID" ]; then
  CHANGED=false
else
  CHANGED=true
fi

# Escape the optional note for JSON (backslash, quote).
NOTE_ESC=$(printf '%s' "$NOTE" | sed 's/\\/\\\\/g; s/"/\\"/g')

LINE=$(printf '{"kind": "sentinel", "ts": %s, "ts_iso": "%s", "boot_id": "%s", "btime": %s, "uptime_s": %s, "sq_running": %s, "watcher_heartbeat_age_s": %s, "boot_changed_since_last_line": %s, "host_mem_available_kb": %s, "host_oom_kills": %s, "ns_rss_total_kb": %s, "note": "%s"}' \
  "$TS" "$TS_ISO" "$BOOT_ID" "$BTIME" "$UPTIME_S" "$SQ" "$HB_AGE" "$CHANGED" "$HOST_MEM_AVAIL_KB" "$HOST_OOM_KILLS" "$NS_RSS_KB" "$NOTE_ESC")

# Atomic append under lock so concurrent runs cannot interleave lines.
(
  flock -x 9
  printf '%s\n' "$LINE" >> "$LEDGER"
) 9>> "$LEDGER"

printf '%s\n' "$LINE"
