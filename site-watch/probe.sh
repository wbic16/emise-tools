#!/bin/bash
# probe.sh — liveness probe for the awsbox-hosted sites.
# Prints one line per FAILURE; prints nothing when everything is up.
# Exit 0 = all up, 1 = at least one failure.
SITES="https://phext.io/ https://edit.phext.io/ https://register.phext.io/ https://md.phext.io/ https://singularitywatch.org/ https://quickfork.net/ https://apertureshift.com/ https://mirrorborn.us/ https://phextura.com/ https://tluf.org/"
fail=0
for u in $SITES; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$u")
  case "$code" in
    2*|3*|401|403) ;;
    *) echo "DOWN $u -> $code"; fail=1 ;;
  esac
  sleep 1
done
state=$(~/workspace/bickford-llama-ranch/deploy/fleet-ssh.sh awsbox "systemctl is-active nginx" 2>/dev/null | grep -v bashrc | tail -1)
if [ "$state" != "active" ]; then
  echo "DOWN nginx on awsbox -> $state"
  fail=1
fi
exit $fail
