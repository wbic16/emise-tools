#!/bin/sh
# ranch-ssh.sh — ssh/rsync transport to the AWS box (44.248.235.76).
#
# Why not plain `ssh -J wbic16@100.88.154.1`? Verified 2026-10-31:
#  - Direct connection to aletheia-core (100.88.154.1:22) from this VM is
#    "Operation not permitted" — ranch nodes are only reachable through the
#    Tailscale proxy on hatch-egress-proxy:3130 (see TOOLS.md).
#  - `ssh -J` cannot be combined with a ProxyCommand ("Cannot specify -J
#    with ProxyCommand"), and ProxyJump with our local key fails auth on
#    the AWS box: the last hop is authenticated by wbic16's key ON
#    aletheia-core, not by ours.
# So: nested ssh. Hop 1 uses our key + the proxy; hop 2 runs on
# aletheia-core and uses its own key. Works for both ssh and rsync -e.
#
# Usage (ssh form):    ranch-ssh.sh <ignored-host> [remote command...]
# Usage (rsync form):  rsync -e ranch-ssh.sh ... host:/path/
set -eu
KEY=${SSH_IDENTITY:-$HOME/.ssh/id_ed25519}
JUMP=${RANCH_JUMP:-wbic16@100.88.154.1}
TARGET=${RANCH_TARGET:-wbic16@44.248.235.76}
# Drop transport preamble: rsync passes `-l <user>` before the host,
# plain ssh form passes just the host. (Found live 2026-10-31: an unstripped
# `-l` made the far shell try to execute `wbic16` as a command.)
while [ $# -ge 2 ] && [ "$1" = "-l" ]; do shift 2; done
[ $# -ge 1 ] && shift   # drop the host argument ssh/rsync passes us

quote() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

if [ $# -eq 0 ]; then
  INNER="ssh $TARGET"
else
  INNER="ssh -o BatchMode=yes $TARGET"
  for a in "$@"; do INNER="$INNER $(quote "$a")"; done
fi
exec ssh -i "$KEY" -o IdentitiesOnly=yes -o BatchMode=yes \
  -o "ProxyCommand=nc -X connect -x hatch-egress-proxy:3130 %h %p" \
  "$JUMP" "$INNER"
