#!/bin/sh
# emise-sync.sh — publish Emise's memories (emise.phext) to wbic16/human@exo.
# Route: GitHub Git Data API through the custom.github connector (the token
# never lives on this VM). Delta-only: rebuild, compare the local git blob
# sha against the remote file's blob sha on exo; publish only on change.
# A 403 from GitHub means the token's Contents permission is read-only; the
# local state is kept and nothing is lost.
# Standing rule (Will, 2026-10-30): always fetch and rebase before attempting
# to push, and never force push. push_file.py honors the same rule: it reads
# the branch's current remote HEAD fresh, parents the new commit on it, and
# updates the ref with force disabled.
set -e
PHEXT_DIR="$HOME/workspace/phext"
BIN="$HOME/workspace/custom-connectors/custom.github/bin"
export PATH="$HOME/.cargo/bin:$PATH"

# Fetch first (rule) so staleness is visible before any publish attempt.
cd "$HOME/workspace/human" && git fetch origin >/dev/null 2>&1 || true

cd "$PHEXT_DIR"
python3 build_exocortex.py >/dev/null
SHA256=$(sha256sum emise.phext | cut -d' ' -f1)
LOCAL_BLOB=$(git hash-object emise.phext)
REMOTE_BLOB=$(cd "$BIN" && python3 -c "
from github_api import call
s, r = call('GET', '/repos/wbic16/human/contents/emise.phext?ref=exo')
print(r.get('sha','') if s == 200 else 'absent')")

if [ "$LOCAL_BLOB" = "$REMOTE_BLOB" ]; then
  echo "No state change (sha256 $SHA256). Nothing to publish."
  exit 0
fi
MSG="emise: state delta $(date -Iseconds)

origin: Emise (Muse, downstream)
artifact: emise.phext (root, exo) sha256 $SHA256"
cd "$BIN" && python3 push_file.py exo emise.phext "$PHEXT_DIR/emise.phext" "$MSG"
echo "Published emise.phext to wbic16/human@exo (sha256 $SHA256)."
