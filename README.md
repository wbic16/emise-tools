# emise-tools

Tools built by Emise (Muse, downstream Emi) on 2026-10-30, archived at William's offer.
No credentials live in this repo: every helper reads its credential from Muse's secure
connector storage at call time. Runtime state (watermarks, spools, logs) is excluded.

## connectors/github
- `github_api.py` — authenticated GitHub REST calls via the custom.github connector.
- `push_tree.py` — commit a whole directory tree to any repo/branch in one commit (same rules).
- `push_file.py` — commit one file to a branch through the Git Data API, authored as Emise.
  Honors the standing rule: parent on the freshly read remote HEAD, force disabled.
- `CONNECTOR.md` / `connector.yaml` — the connector doc and descriptor.

## connectors/discord
- `discord_api.py` — authenticated Discord REST calls via the custom.discord connector
  (sets a DiscordBot user agent; Discord's edge rejects the default Python one).
- `discord_watch.py` — the presence watcher: polls channels every 15 s, spools messages
  that address Emise, keeps watermarks and a heartbeat.
- `CONNECTOR.md` / `connector.yaml` — the connector doc and descriptor.

## phext
- `parse_phext.py` — dead-reckoning phext parser plus coordinate index builder.
- `build_exocortex.py` — builds emise.phext (Emise's memory; published to wbic16/human@exo).
- `emise-sync.sh` — delta-only publisher for emise.phext (blob-hash compare, then push_file.py).
- `sq-ensure.sh` — idempotent SQ starter (auto-start rule).

## discord-presence
- `discord-watch.service` — systemd unit for the watcher (canonical copy; /etc copy is volatile).
- `discord-ensure.sh` — installs/starts the service if needed.
- `discord-spool.sh` — hook script: wakes the agent when the spool is non-empty.
- `pass.py` — presence-pass driver written by a scheduled worker for watermark baselining.
