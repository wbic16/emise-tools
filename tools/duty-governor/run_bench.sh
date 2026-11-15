#!/bin/bash
# run_bench.sh <instances> <duration_s> <outdir>
# Launches N soak_worker.py instances (the sweep's bench shape: random-move
# policy, obs glyphs+blstats, dwarven Valkyrie) in this process group and
# waits for them. Run it UNDER duty_governor.py: the governor SIGSTOPs /
# SIGCONTs the whole group. Workers measure their duration by wall clock,
# so frozen time counts against them — total steps / governor wall time is
# the honest effective sustained rate.
set -u
N=$1; DUR=$2; OUT=$3
BASE=$HOME/nethack-solver
mkdir -p "$OUT"
for i in $(seq 1 "$N"); do
  "$BASE/.venv/bin/python" "$BASE/soak_worker.py" \
    --duration "$DUR" --seed $((1000 + i * 7)) \
    --progress "$OUT/progress-$i.txt" &
done
wait
