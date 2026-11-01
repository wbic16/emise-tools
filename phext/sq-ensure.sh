#!/bin/sh
# sq-ensure.sh — auto-start the SQ daemon if it is not already hosting.
# Usage: sq-ensure.sh [dir] [file.phext]
# Defaults: dir ~/workspace/phext, file choose-your-own-adventure.phext
# Standing rule (Will, 2026-10-30): SQ is started as needed, without asking.
DIR="${1:-$HOME/workspace/phext}"
FILE="${2:-choose-your-own-adventure.phext}"
export PATH="$HOME/.cargo/bin:$PATH"
cd "$DIR" || exit 1
if sq status >/dev/null 2>&1; then
  echo "SQ already hosting:"
  sq status
  exit 0
fi
echo "SQ not running — starting: sq share $FILE (in $DIR)"
nohup sq share "$FILE" >"$DIR/.sq-daemon.log" 2>&1 &
sleep 2
sq status
