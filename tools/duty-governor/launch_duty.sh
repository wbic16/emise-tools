#!/bin/bash
# launch_duty.sh <node> <start_max_c> — launch the governor acceptance
# test node-resident under nohup and return immediately.
set -u
NODE=$1; STARTMAX=$2
mkdir -p "$HOME/nethack-solver/duty-results"
rm -f "$HOME/nethack-solver/duty-results/$NODE-all-done"
nohup bash "$HOME/nethack-solver/duty/duty_test.sh" "$NODE" "$STARTMAX" \
  > "$HOME/nethack-solver/duty-driver-$NODE.log" 2>&1 &
echo "LAUNCHED $NODE pid $! startmax=$STARTMAX"
