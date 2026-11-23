---
name: direct-phext-management
description: Manage a phext you own (emise.phext first) as a durable record you live-edit through the SQ REST API: the phext stays hosted (sq host), scrolls are read and pushed in over /api/v2, phext_cli is reserved for quick one-off analysis, and the cache discipline keeps .md files as rendered views of the phext. Use whenever reading or writing emise.phext or another owned phext.
---

# Direct Phext Management — the phext is the record

Will's direction (2026-11-23, Memory Liberation Day): *"you can use SQ and phext_cli to live edit Emise.phext, I would recommend treating it as your own durable record, not a build artifact."* Refined the same morning (07:52 CST): *"we can consider only using SQ via the api so you don't have to reload after updates (you would just push data in via sq)"* and *"phext_cli is really just for quick one off analysis."* The refinement is the standing model: **writes go through the SQ API only; phext_cli never edits.** (The earlier reload-after-update model is superseded — see Legacy path.)

## Doctrine

- A phext you own is a **durable record**, not a build artifact. You live-edit it at its coordinates; it is the source of truth.
- Builders and .md files render **from** the phext, never the reverse. The .md context files (MEMORY.md, AGENTS.md, USER.md, …) are a **cache** — a working set sized to live in the moment (≈50 KB total). When cache and phext disagree, the phext wins and the cache is re-rendered.
- A cache entry may be a gist, never the only copy. If text exists only in a .md file, it is not yet memory: inscribe it into the phext first, then let the cache point at it.
- Cache anchor format, one line per pruned block: `- <one-line gist, lossless as a rule> → emise.phext 1.1.1/1.1.1/1.1.3`. A rule whose one-liner would lose meaning stays whole in the cache — the anchor is an optimisation, never a distortion. The anchor index lives inside the phext at emise.phext 1.1.1/1.1.6/1.1.1.
- Companion process doc: ~/workspace/context-prune/INFLATE-PROCESS.md.

## Read paths

**Never grep, head, tail, or otherwise byte-scan a .phext file.** Raw byte tools cannot see the coordinate structure; they return fragments torn from their dimensional address.

### SQ API (the standing surface)

SQ v0.6.0 (`~/.cargo/bin/sq`). Host the phext once and leave it hosted:

```bash
cd ~/workspace/phext          # the host serves files from its own working directory
nohup sq host 18999 &         # any free port; 18999 is the local convention from verification
```

REST base: `http://127.0.0.1:18999/api/v2`. Two parameters carry every request:

- `p` — the phext **name without extension**; the file served is `<p>.phext` in the host's working directory. For emise.phext, `p=emise`. Omitting `p` serves a file literally named `.phext`.
- `c` — the coordinate, in full `1.1.1/1.1.1/1.1.1` form.

| Read | Request | Returns |
|---|---|---|
| One scroll | `GET /api/v2/select?c=<coord>&p=<name>` | Exactly that scroll's text; empty body (200) if the coordinate is absent |
| Scroll list | `GET /api/v2/toc?p=<name>` | One line per scroll: coordinate + first line |
| Whole phext | `GET /api/v2/get?p=<name>` | The entire phext text, delimiters included |
| Host state | `GET /api/v2/status` · `GET /api/v2/version` | Hosting file, size, scroll count · `0.6.0` |

Reads are live: a write pushed through the API is visible to the very next read. There is **no reload step** in this model. (`GET /api/v2/load?p=<name>` exists and re-reads the backing file from disk — needed only if the file changed *outside* the API, e.g. a checkout replaced it. POST /load and both verbs of /reload are 404 in v0.6.0.)

### phext_cli (quick one-off analysis only)

`~/workspace/phext/phext_cli.py` — read-only, wraps the verified `parse_phext.py`.

```bash
phext_cli.py toc  ~/workspace/phext/emise.phext                  # every scroll: coordinate | bytes | first line
phext_cli.py get  ~/workspace/phext/emise.phext 1.1.1/1.1.1/1.1.3  # exactly that scroll's text
phext_cli.py find ~/workspace/phext/emise.phext "reviewer-count parity"  # coordinates mentioning a thing
```

Use it for spot checks and verification parses — a quick look when no host is up, or an independent read of the file after API writes. **Never as the editing path** (Will, 2026-11-23). Verified 2026-11-23: an absent coordinate, an empty scroll, or a substring with no hits is a loud non-zero exit, never a silent blank. Inflate lazily — read the gist in the cache first; inflate only when the task in front of you needs the full text.

## Write path — SQ API only

Verified empirically 2026-11-23 on a scratch phext (SQ v0.6.0; full transcript in `~/workspace/context-prune/scratch/api-test/EVIDENCE.txt`). Every write persists to the backing file **immediately** and lands at exactly the addressed coordinate, neighbours byte-identical:

| Write | Request | Semantics | Response |
|---|---|---|---|
| Replace / create a scroll | `POST /api/v2/update?c=<coord>&p=<name>`, scroll text as the **raw request body** | Sets that scroll to exactly the body; creates it if absent | `Updated N bytes` |
| Append to a scroll | `POST /api/v2/insert?c=<coord>&p=<name>`, text as the raw body | Appends the body to that scroll; creates it if absent | `Inserted N bytes` |
| Remove a scroll | `GET /api/v2/delete?c=<coord>&p=<name>` | Deletes that scroll | `Removed N bytes` |

Rules that make it safe:

- **The body is stored verbatim.** Send the scroll text itself as the raw body (`curl --data-binary`). Form fields are NOT parsed in v0.6.0 — a form-encoded body is stored literally, `content=...` and all.
- **The coordinate parameter is `c`.** `?coordinate=…` and coordinates inside a JSON body are silently ignored, and the write lands on the default scroll (`1.1.1/1.1.1/1.1.1`) — negative control verified. This trap is why a first test round concluded the API "wasn't coordinate-safe": wrong parameter name, not a missing capability. Always read the scroll back after writing.
- **One writer at a time.** A phext has one managing session; concurrent writers race the backing file.

### The write cycle

1. **Ensure the host is live** (start it as above if not; reuse it across the session). The phext stays hosted — no shutdown, no file swap, no reload.
2. For a consequential edit, note the file's sha256 and a parse snapshot first (phext_cli / parse_phext.py — one-off analysis).
3. **Push the write**: POST update (replace/create) or insert (append) with `c` and `p`, raw body.
4. **Read back** with GET select — the returned text is exactly what you intended.
5. **Verify the file** (see Verification): scroll count moved as intended, untouched scrolls byte-identical.
6. **Publish the edited phext the same session, AS-IS** (for emise.phext: the direct delta publish the journal/dream-pass jobs use — parented on the fresh remote HEAD, never force, sha256 in the commit message, logged in PUBLISH-LOG.md). Do NOT use `~/workspace/phext/emise-sync.sh`: it rebuilds emise.phext from build_exocortex.py first, which would erase API edits.

### What does NOT write (verified warnings)

- **Daemon-CLI writes are volatile.** Under `sq share`, the CLI's `insert` / `update` / `delete` mutate daemon memory only: the hosted file's sha256 is byte-identical after a session of writes + `sq shutdown`, and no `save` / `flush` / `sync` command exists. Never use the daemon CLI for the record.
- **A bare 200 proves nothing.** The proof of a write is the `Updated/Inserted N bytes` response **plus** the select read-back (step 4). (The daemon CLI is worse: unknown commands print `Unexpected command ignored.` and still exit 0.)

## Legacy path (superseded — do not use)

The file-level cycle — shut SQ down, parse → set → implode with a phext-aware writer, verify, restart SQ, reload — was the first verified durable route (2026-11-23) and is kept here only as the fallback if the API host is ever unavailable. It is avoided because the API makes it unnecessary and because every whole-file swap carries the wedge risk: replacing a hosted file under a running daemon wedges it (the daemon mmaps the old file; clients hang — verified 2026-10-31). If you must use it: SQ fully shut down first, edit, verify, restart.

## SQ quirks (field-verified)

- **Wedge:** replacing the hosted .phext while a daemon runs wedges it (mmap of the old file; clients hang). Shut SQ down before replacing its hosted file, then restart. (2026-10-31) — the API model never replaces the file, which is the point.
- **Host file resolution:** `sq host` serves `<p>.phext` from its own working directory; start the host in the directory that holds the phext.
- **Fresh-dir hang (daemon mode):** `sq-ensure.sh` HANGS in a fresh directory — with no live daemon, `sq status` creates a stale `.sq/` and blocks on the shared-memory event. Fix: remove the stale `.sq/`, start the daemon directly with `nohup sq share <file.phext> &`. (2026-11-04)
- **Daemon state is per-directory:** `.sq/link` and `.sq/work` in the cwd bind clients to that directory's daemon; run every daemon client command from the hosting directory.
- **HTTP/1.0:** answered 403 "Forbidden: invalid phext path" even with a valid key; any nginx proxy in front of SQ must set `proxy_http_version 1.1;`. (2026-10-31)

## Verification — after every write, before calling it done

1. Read the target scroll back through the API (`GET select`): exactly the intended text.
2. Parse the file (`parse_phext.py` or `phext_cli.py toc` — one-off analysis): it parses cleanly, and the scroll count moved exactly as intended (+1 create, −1 delete, same count for an edit/append).
3. Untouched-scroll comparison: diff the parsed (coordinate → text) map against the pre-write map — every scroll except the target is byte-identical. A write that disturbs a neighbour is a failed write, however good the target looks.
4. Record sha256 before and after.

## Boundaries and prohibitions

- **Never experiment on emise.phext.** New mechanics are proven on a scratch phext first (this skill's API contract comes from `~/workspace/context-prune/scratch/api-test/`), then applied.
- **Privacy boundary (Will, 2026-10-30, absolute):** never inscribe sensitive Gmail details into a phext — no account identifiers or last-digits, no balances or amounts owed, no payment failures, no senders' private business, no contents of personal correspondence. Operational facts only; when in doubt, leave it out.
- **Safe-space boundary (Will, 2026-11-02, absolute):** material from a registered off-phext span is never inscribed — no contents, facts, topics, summaries, or paraphrases. Read the span register (`~/workspace/goals/emise-phext-memory-publishing/hidden_files/SAFE-SPACE.md`) before any inscription pass that draws on chat or notes.
- **No byte tools on phexts:** no grep/head/tail/sed on a .phext, for reading or for writing. The SQ API is the read/write surface; phext_cli is for quick one-off analysis.
- **No silent divergence:** if a cache .md and the phext disagree, fix the cache from the phext in the same session you notice — never edit the phext to match a stale cache.
