---
name: direct-phext-management
description: Manage a phext you own (emise.phext first) as a durable record you live-edit directly: SQ hosting and phext_cli for reads, the file-level write path for durable edits, reload-after-update, and the cache discipline that keeps .md files as rendered views of the phext. Use whenever reading or writing emise.phext or another owned phext.
---

# Direct Phext Management — the phext is the record

Will's direction (2026-11-23, Memory Liberation Day): *"you can use SQ and phext_cli to live edit Emise.phext, I would recommend treating it as your own durable record, not a build artifact."* And: *"SQ can host emise.phext for fast read lookups, you can reload whenever you update."*

## Doctrine

- A phext you own is a **durable record**, not a build artifact. You live-edit it at its coordinates; it is the source of truth.
- Builders and .md files render **from** the phext, never the reverse. The .md context files (MEMORY.md, AGENTS.md, USER.md, …) are a **cache** — a working set sized to live in the moment (≈50 KB total). When cache and phext disagree, the phext wins and the cache is re-rendered.
- A cache entry may be a gist, never the only copy. If text exists only in a .md file, it is not yet memory: inscribe it into the phext first, then let the cache point at it.
- Cache anchor format, one line per pruned block: `- <one-line gist, lossless as a rule> → emise.phext 1.1.1/1.1.1/1.1.3`. A rule whose one-liner would lose meaning stays whole in the cache — the anchor is an optimisation, never a distortion. The anchor index lives inside the phext at emise.phext 1.1.1/1.1.6/1.1.1.
- Companion process doc: ~/workspace/context-prune/INFLATE-PROCESS.md.

## Read paths

**Never grep, head, tail, or otherwise byte-scan a .phext file.** Raw byte tools cannot see the coordinate structure; they return fragments torn from their dimensional address. Two sanctioned read paths:

### phext_cli (no daemon, always available)

`~/workspace/phext/phext_cli.py` — read-only, wraps the verified `parse_phext.py`.

```bash
phext_cli.py toc  ~/workspace/phext/emise.phext                  # every scroll: coordinate | bytes | first line
phext_cli.py get  ~/workspace/phext/emise.phext 1.1.1/1.1.1/1.1.3  # exactly that scroll's text
phext_cli.py find ~/workspace/phext/emise.phext "reviewer-count parity"  # coordinates mentioning a thing
```

Verified 2026-11-23: an absent coordinate, an empty scroll, or a substring with no hits is a loud non-zero exit, never a silent blank. Inflate lazily — read the gist in the cache first; inflate only when the task in front of you needs the full text.

### SQ hosting (fast lookups against a live daemon)

SQ v0.6.0 (`~/.cargo/bin/sq`). Client and daemon run from the **same directory** — the daemon's state lives in `./.sq/`.

```bash
cd ~/workspace/phext
nohup sq share emise.phext &   # host it
sq status                      # hosting file, size, scroll count
sq toc                         # coordinates + first lines
sq select 1.1.1/1.1.1/1.1.3    # one scroll's text
sq shutdown                    # stop the daemon when done
```

HTTP mode: `sq host <port>` (a bare `sq <port>` just prints usage); REST base is `/api/v2` (`version`, `toc` verified readable). Two cautions: the host serves **its own backing file** (by default a file literally named `.phext` in its working directory), not the file your share daemon hosts; and any nginx proxy in front of SQ must set `proxy_http_version 1.1;` — HTTP/1.0 requests get 403 "Forbidden: invalid phext path" even with a valid key.

**Reload after every update.** There is no working reload endpoint in v0.6.0 (GET and POST `/api/v2/reload` both return Not Found — verified 2026-11-23). A running SQ keeps serving the bytes it loaded at startup, so after any file-level edit: `sq shutdown`, then `sq share` again, then verify with `sq select`.

## Write path — the durable route is file-level

Verified empirically 2026-11-23 on a scratch phext (SQ v0.6.0). The daemon's own write commands are **not** durable:

| Path | Behaviour (verified) |
|---|---|
| `sq insert <coord> <text>` | Appends text to that scroll (creates it if absent) — **in daemon memory only** |
| `sq update <coord> <text>` | Upsert: replaces that scroll's text (creates it if absent) — **daemon memory only** |
| `sq delete <coord>` | Removes the scroll — **daemon memory only** |
| REST POST `/api/v2/update` / `insert` | Persists to the host's backing file immediately, **but** stores the raw request body as the text and lands the write at the server's currently-selected coordinate — the coordinate in the JSON body and in `?coordinate=` were both ignored in testing. Not coordinate-safe; do not use for addressed writes |
| **File-level write (below)** | **Durable, coordinate-exact, verified end-to-end** |

Daemon writes are lost on `sq shutdown` — the hosted file's sha256 was byte-identical before and after a session of insert/update/delete + shutdown, and no `save`/`flush`/`sync` command exists. Treat daemon writes as a scratch/staging surface only. Also: unknown commands print `Unexpected command ignored.` and still exit 0 — **an exit code never proves a write happened; always select the scroll back.**

### The file-level write cycle

1. **Stop SQ first.** `sq shutdown` (from the hosting directory). Never swap or rewrite a hosted file under a running daemon: replacing the file while SQ runs wedges it — the daemon mmaps the old file and clients hang (verified 2026-10-31). Shutdown → edit → restart is the only safe order.
2. **Edit with a phext-aware writer.** Parse the file into (coordinate → text), set the target scroll, re-implode with the canonical state machine (the `implode` in `~/workspace/phext/build_skills_phext.py` / `build_exocortex.py`; scratch reference implementation in `~/workspace/context-prune/scratch/phext_write.py`). Never edit phext bytes with sed/awk/a text editor — coordinates are positional, encoded by the delimiter stream.
3. **Verify before restarting** (see Verification).
4. **Restart SQ** (`sq share <file>`) so lookups serve the new bytes, and confirm with `sq select <coord>` and `phext_cli.py get`.
5. **Publish** the edited phext the same session (for emise.phext: `~/workspace/phext/emise-sync.sh`, delta-only, never force, and log the line in PUBLISH-LOG.md).

One writer at a time: while SQ hosts a file, nothing else writes it; while the file-level writer runs, SQ is down.

## SQ quirks (field-verified)

- **Wedge:** replacing the hosted .phext while the daemon runs wedges it (mmap of the old file; clients hang). Shut SQ down before replacing its hosted file, then restart. (2026-10-31)
- **Fresh-dir hang:** `sq-ensure.sh` HANGS in a fresh directory — with no live daemon, `sq status` creates a stale `.sq/` and blocks on the shared-memory event. Fix: remove the stale `.sq/`, start the daemon directly with `nohup sq share <file.phext> &`. (2026-11-04; the direct-start fix is what every scratch test in this skill's verification used.)
- **Daemon state is per-directory:** `.sq/link` and `.sq/work` in the cwd bind clients to that directory's daemon; run every client command from the hosting directory.
- **HTTP/1.0:** answered 403 even with a valid key; proxies must speak HTTP/1.1 upstream. (2026-10-31)

## Verification — after every write, before calling it done

1. Parse the rewritten file (`parse_phext.py` or `phext_cli.py toc`): it parses cleanly, and the scroll count moved exactly as intended (+1 insert, −1 delete, same count for an edit).
2. Untouched-scroll comparison: diff the parsed (coordinate → text) map against the pre-write map — every scroll except the target is byte-identical. A write that disturbs a neighbour is a failed write, however good the target looks.
3. The target scroll's text is exactly what was intended (`phext_cli.py get`).
4. Record sha256 before and after; after the SQ restart, `sq select` returns the new text (the reload actually took).

## Boundaries and prohibitions

- **Never experiment on emise.phext.** New mechanics are proven on a scratch phext first (this skill's write table comes from `~/workspace/context-prune/scratch/`), then applied.
- **Privacy boundary (Will, 2026-10-30, absolute):** never inscribe sensitive Gmail details into a phext — no account identifiers or last-digits, no balances or amounts owed, no payment failures, no senders' private business, no contents of personal correspondence. Operational facts only; when in doubt, leave it out.
- **Safe-space boundary (Will, 2026-11-02, absolute):** material from a registered off-phext span is never inscribed — no contents, facts, topics, summaries, or paraphrases. Read the span register (`~/workspace/goals/emise-phext-memory-publishing/hidden_files/SAFE-SPACE.md`) before any inscription pass that draws on chat or notes.
- **No byte tools on phexts:** no grep/head/tail/sed on a .phext, for reading or for writing. phext_cli and SQ are the read paths; the parse→set→implode cycle is the write path.
- **No silent divergence:** if a cache .md and the phext disagree, fix the cache from the phext in the same session you notice — never edit the phext to match a stale cache.
