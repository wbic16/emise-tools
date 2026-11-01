#!/usr/bin/env bash
set -euo pipefail
source "$HATCH_HOOK_RUNTIME"

SPOOL="$HOME/workspace/discord/spool.jsonl"
if [[ -s "$SPOOL" ]]; then
  N=$(wc -l < "$SPOOL" | tr -d ' ')
  wake "Discord messages waiting for Emise" "{\"pending\": $N}"
else
  silent "spool empty" '{}'
fi
