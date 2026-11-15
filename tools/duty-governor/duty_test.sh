#!/bin/bash
# duty_test.sh <node> <start_max_c>
# Node-side driver for the governor acceptance tests: for each instance
# count (4, then 8), cool the node to <= start_max_c, then run the NLE
# bench for 30 min under duty_governor.py with this node's profile.
# Node-resident: launch under nohup; results land in
# ~/nethack-solver/duty-results/<node>-<n>inst/ and a done-file appears
# at ~/nethack-solver/duty-results/<node>-all-done.
set -u
NODE=$1; STARTMAX=$2
BASE=$HOME/nethack-solver
DUTY=$BASE/duty
RES=$BASE/duty-results
mkdir -p "$RES"

tctl() {
  for H in /sys/class/hwmon/hwmon*; do
    [ -r "$H/name" ] || continue
    if [ "$(cat "$H/name" 2>/dev/null)" = "k10temp" ]; then
      awk -v r="$(cat "$H/temp1_input" 2>/dev/null)" \
        'BEGIN { printf "%.1f", r / 1000 }'
      return
    fi
  done
  echo NA
}

wait_cool() {  # wait_cool <limit_c>: 0 when cool, 1 after 10 min
  local limit=$1 waited=0 t ok
  while :; do
    t=$(tctl)
    ok=$(awk -v t="$t" -v l="$limit" 'BEGIN { print (t <= l) ? 1 : 0 }')
    [ "$ok" = 1 ] && return 0
    [ $waited -ge 600 ] && return 1
    sleep 15; waited=$((waited + 15))
  done
}

echo "duty_test $NODE start $(date -Is) startmax=$STARTMAX"
for N in 4 8; do
  RUN=$RES/$NODE-${N}inst
  mkdir -p "$RUN"
  rm -f "$RUN"/governor.log "$RUN"/governor.log.summary.json \
        "$RUN"/progress-*.txt "$RUN"/run-done
  if wait_cool "$STARTMAX"; then
    echo "run $N: cooled to $(tctl) C at $(date -Is)"
  else
    echo "run $N: cooldown CAP hit, tctl=$(tctl) C at $(date -Is) — running anyway, recorded"
  fi
  python3 "$DUTY/duty_governor.py" \
    --profile "$DUTY/profiles/$NODE.json" \
    --log "$RUN/governor.log" \
    -- bash "$DUTY/run_bench.sh" "$N" 1800 "$RUN"
  echo "run $N done $(date -Is) tctl=$(tctl) C"
  touch "$RUN/run-done"
done
touch "$RES/$NODE-all-done"
echo "duty_test $NODE ALL DONE $(date -Is)"
