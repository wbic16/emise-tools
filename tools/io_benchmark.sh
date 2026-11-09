#!/usr/bin/env bash
# io_benchmark.sh — 1 GiB sequential disk I/O probe for a ranch node.
#
# Runs ON the node (no network, no orchestration): writes a 1 GiB probe
# file with direct I/O, reads it back with direct I/O, prints one result
# block, and always cleans up after itself (trap on exit).
#
# Usage: ./io_benchmark.sh [target-dir] [size-mib]
#   target-dir  where the probe file lives (default: $HOME)
#   size-mib    probe size in MiB (default: 1024)
#
# Built for Will's fleet spot-checks, 2026-11-08 — companion to the
# daily disk-usage report. Reference numbers from the Muse VM the
# same evening: write ~60 MB/s, read ~225 MB/s (throttled virtual disk).
# Ranch nodes carry dedicated NVMe and should beat both by a lot.
set -u

TARGET_DIR="${1:-$HOME}"
SIZE_MIB="${2:-1024}"

if [ ! -d "$TARGET_DIR" ]; then
  echo "io_benchmark: target dir '$TARGET_DIR' does not exist" >&2
  exit 1
fi

WORK="$(mktemp -d "$TARGET_DIR/io-probe.XXXXXX")" || exit 1
PROBE="$WORK/probe"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT INT TERM

rate() { # extract "X MB/s" (or GB/s) from dd's summary line on stderr
  grep -o '[0-9.]* [MG]B/s' | tail -1
}

echo "node:      $(hostname)"
echo "target:    $TARGET_DIR (probe: ${SIZE_MIB} MiB, direct I/O)"
DEV="$(df --output=source "$TARGET_DIR" 2>/dev/null | tail -1)"
FS="$(df --output=fstype "$TARGET_DIR" 2>/dev/null | tail -1)"
echo "device:    ${DEV:-unknown} (${FS:-unknown})"
MODEL="$(lsblk -dn -o MODEL "$DEV" 2>/dev/null | sed 's/^ *//;s/ *$//')"
[ -n "$MODEL" ] && echo "model:     $MODEL"

WRITE_OUT="$(dd if=/dev/zero of="$PROBE" bs=1M count="$SIZE_MIB" oflag=direct 2>&1)"
WRITE_RATE="$(printf '%s' "$WRITE_OUT" | rate)"
echo "write:     ${WRITE_RATE:-FAILED}"

READ_OUT="$(dd if="$PROBE" of=/dev/null bs=1M iflag=direct 2>&1)"
READ_RATE="$(printf '%s' "$READ_OUT" | rate)"
echo "read:      ${READ_RATE:-FAILED}"

[ -n "$WRITE_RATE" ] && [ -n "$READ_RATE" ]
