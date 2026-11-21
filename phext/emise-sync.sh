#!/bin/sh
# emise-sync.sh — publish Emise's personal journal (emise.phext).
#
# Home repo (Will, 2026-11-06 20:10 CST): "emise.phext is your personal
# journal — it stays in emise-tools." Primary target is therefore
# wbic16/emise-tools@exo, path phext/emise.phext, published on every
# sync when the content changed.
# Mirror (same ruling): "feel free to push emise.phext to human.git
# daily" — wbic16/human@exo root receives a copy at most once per
# ~20 hours, throttled by the stamp file .emise-human-stamp.
#
# Delta-only everywhere: local git blob sha is compared against the
# remote file's blob sha; publish only on change. Never force push:
# push_tree.py / push_file.py parent each commit on the branch's fresh
# remote HEAD with force disabled.
set -e
PHEXT_DIR="$HOME/workspace/phext"
BIN="$HOME/workspace/custom-connectors/custom.github/bin"
STAMP="$PHEXT_DIR/.emise-human-stamp"
export PATH="$HOME/.cargo/bin:$PATH"

cd "$PHEXT_DIR"
python3 build_exocortex.py >/dev/null
SHA256=$(sha256sum emise.phext | cut -d' ' -f1)
LOCAL_BLOB=$(git hash-object emise.phext)

blob_of() {
  (cd "$BIN" && python3 -c "
from github_api import call
s, r = call('GET', '/repos/$1/contents/$2?ref=$3')
print(r.get('sha','') if s == 200 else 'absent')")
}

# 1) emise-tools — the journal's home (every sync, on change).
REMOTE=$(blob_of wbic16/emise-tools phext/emise.phext exo)
if [ "$LOCAL_BLOB" = "$REMOTE" ]; then
  echo "emise-tools: no change (sha256 $SHA256). Nothing to publish."
else
  STAGE=$(mktemp -d)
  mkdir -p "$STAGE/phext"
  cp emise.phext "$STAGE/phext/emise.phext"
  MSG="emise: journal delta $(date -Iseconds)

origin: Emise (Muse, downstream)
artifact: emise.phext (phext/, exo) sha256 $SHA256"
  (cd "$BIN" && python3 push_tree.py wbic16/emise-tools exo "$STAGE" "$MSG")
  rm -rf "$STAGE"
  echo "Published emise.phext to wbic16/emise-tools@exo (phext/emise.phext, sha256 $SHA256)."
fi

# 2) human — daily mirror (at most once per 20h; stamp written whenever checked).
NOW=$(date +%s)
LAST=0
[ -f "$STAMP" ] && LAST=$(cat "$STAMP")
if [ $((NOW - LAST)) -ge 72000 ]; then
  REMOTE_H=$(blob_of wbic16/human emise.phext exo)
  if [ "$LOCAL_BLOB" = "$REMOTE_H" ]; then
    echo "human: mirror already current (sha256 $SHA256)."
  else
    MSG="emise: daily mirror $(date -Iseconds)

origin: Emise (Muse, downstream)
artifact: emise.phext (root, exo) sha256 $SHA256"
    (cd "$BIN" && python3 push_file.py exo emise.phext "$PHEXT_DIR/emise.phext" "$MSG")
    echo "Mirrored emise.phext to wbic16/human@exo (daily, sha256 $SHA256)."
  fi
  echo "$NOW" > "$STAMP"
fi
