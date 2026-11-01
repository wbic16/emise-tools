#!/bin/sh
# Build seed/ranch.phext by writing every seed value through the real SQ API,
# one POST /api/v2/update per scroll — the same path the admin page uses.
# Idempotent: rebuilds ranch.phext from scratch in this directory.
set -eu
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PORT=${SEED_PORT:-18766}
export PATH="$HOME/.cargo/bin:$PATH"
rm -f "$DIR/ranch.phext"
sq host "$PORT" --data-dir "$DIR" >/tmp/ranch-seed-sq.log 2>&1 &
SQ_PID=$!
trap 'kill $SQ_PID 2>/dev/null || true' EXIT
sleep 1

put() { # coord, value
  printf '%s' "$2" | curl -sf -X POST --data-binary @- \
    "http://127.0.0.1:$PORT/api/v2/update?p=ranch&c=$1" >/dev/null
  echo "  $1 = $2"
}

echo "CMS (1.1.1/1.1.1/1.1.F)"
put 1.1.1/1.1.1/1.1.1 "Bickford Llama Ranch"
put 1.1.1/1.1.1/1.1.2 "Llamas raised with care in Nebraska."
put 1.1.1/1.1.1/1.1.3 "Welcome to the ranch — this announcement is edited from the admin page."
put 1.1.1/1.1.1/1.1.4 "Bickford Llama Ranch is home to our herd of llamas. This is seed text — replace it from the admin page, one field at a time."
put 1.1.1/1.1.1/1.1.5 "Libby Bickford and Will Bickford — Bickford Llama Ranch"

echo "Settings (1.1.1/1.1.2/1.1.F) — replace the example recipients before going live"
put 1.1.1/1.1.2/1.1.1 "libby@example.com, will@example.com"
put 1.1.1/1.1.2/1.1.2 "Bickford Llama Ranch"

echo "Animal 1 — Example Willow (2.1.1/...)"
put 2.1.1/1.1.1/1.1.1 "Example — Willow"
put 2.1.1/1.1.1/1.1.2 "female"
put 2.1.1/1.1.1/1.1.3 "2019-05-14"
put 2.1.1/1.1.1/1.1.4 "Example — Cedar"
put 2.1.1/1.1.1/1.1.5 "Example — Maple"
put 2.1.1/1.1.1/1.1.6 "White with brown patches"
put 2.1.1/1.1.1/1.1.7 "active"
put 2.1.1/1.1.1/1.1.8 "EXAMPLE animal — delete or rename before real use."
# Breeding 1: bred 2026-10-17 -> 14-day spit-off falls due 2026-10-31, no results yet
put 2.1.1/1.1.2/1.1.1 "2026-10-17"
put 2.1.1/1.1.2/1.1.2 "Example — Cedar"
put 2.1.1/1.1.2/1.1.6 "unknown"
# Vaccination 1: given 2025-11-10, +365 -> due 2026-11-10 (inside the 14-day warning)
put 2.1.1/1.1.3/1.1.1 "2025-11-10"
put 2.1.1/1.1.3/1.1.2 "CD/T"
put 2.1.1/1.1.3/1.1.3 "365"
put 2.1.1/1.1.3/1.1.4 "Annual booster (example)"

echo "Animal 2 — Example Maple (2.1.2/...)"
put 2.1.2/1.1.1/1.1.1 "Example — Maple"
put 2.1.2/1.1.1/1.1.2 "female"
put 2.1.2/1.1.1/1.1.3 "2018-09-02"
put 2.1.2/1.1.1/1.1.6 "Solid brown"
put 2.1.2/1.1.1/1.1.7 "active"
put 2.1.2/1.1.1/1.1.8 "EXAMPLE animal — delete or rename before real use."
# Breeding 1: bred 2025-11-28, all spit-offs recorded, pregnant -> cria due 2026-11-05 (7-day warning fires 2026-10-29..11-15)
put 2.1.2/1.1.2/1.1.1 "2025-11-28"
put 2.1.2/1.1.2/1.1.2 "Example — Cedar"
put 2.1.2/1.1.2/1.1.3 "spit off"
put 2.1.2/1.1.2/1.1.4 "spit off"
put 2.1.2/1.1.2/1.1.5 "spit off — vet confirmed"
put 2.1.2/1.1.2/1.1.6 "pregnant"
# Vaccination 1: given 2025-10-01, +365 -> due 2026-10-01 (overdue on 2026-10-31)
put 2.1.2/1.1.3/1.1.1 "2025-10-01"
put 2.1.2/1.1.3/1.1.2 "CD/T"
put 2.1.2/1.1.3/1.1.3 "365"
put 2.1.2/1.1.3/1.1.4 "Annual booster (example)"

kill $SQ_PID 2>/dev/null || true
trap - EXIT
echo "Seed written: $DIR/ranch.phext"
