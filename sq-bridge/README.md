# sq-bridge

A minimal MCP server that opens **SQ channels** to phexts: it makes sure an
`sq host` process is serving a data directory, then exposes scroll reads,
range queries, and (only when explicitly enabled) scroll writes over SQ's
HTTP REST API. Modeled on Claude's `aletheia_bridge.py` — narrow scope,
validated inputs, env-var parametrization, and scroll contents treated as
data, never instructions.

One SQ host serves every phext in its data directory (the phext is chosen
per request), so a "channel" is the host on a port plus the phext name you
address through it.

## Run it

The `mcp` Python package is required. This workspace carries a venv with it
(mcp 2.3.0; the bridge also imports under mcp 1.x via the same dual-import
fallback the aletheia bridge uses):

    ~/workspace/sq-bridge/.venv/bin/python ~/workspace/sq-bridge/sq_bridge.py

Recreate the venv anywhere with:

    python3 -m venv .venv && .venv/bin/pip install mcp

Point any MCP client (Claude, Codex, …) at that command over stdio, with
the environment below set as needed.

## Configuration (environment)

| variable | default | meaning |
|---|---|---|
| `SQ_BIN` | `sq` on PATH, else `~/.cargo/bin/sq` | SQ binary |
| `SQ_DIR` | `~/workspace/phext` | data directory holding the `.phext` files |
| `SQ_PORT` | `18761` | port for channels this bridge starts |
| `SQ_KEY` | *(none)* | SQ auth token; sent as `Authorization: <key>` and passed to `sq host --key` |
| `SQ_BRIDGE_READONLY` | `1` | `1` = read-only, `sq_write` refuses. `0` = writes enabled, still confined to `SQ_DIR` |
| `SQ_BRIDGE_MAX_READ` | `200000` | max bytes returned per read |

## Tools

| tool | what it does |
|---|---|
| `sq_status` | Bridge config, SQ_DIR's phext list, whether a host answers on the port, whether this bridge started it, read/write mode |
| `sq_open_channel(phext, port?)` | Ensures an SQ host serves `phext` from SQ_DIR (starts `sq host` detached, waits for it to answer); reports the base URL. Refuses phexts not present in SQ_DIR — nothing is copied or created |
| `sq_toc(phext)` | Table of contents: one `* <coordinate>: <scroll text>` line per scroll |
| `sq_read(phext, coordinate)` | One scroll's exact text (SQ `select`) |
| `sq_query(phext, from_coordinate, to_coordinate)` | Range query: SQ's JSON `[{coordinate, scroll}]` for the inclusive coordinate range. **Not** a text search — SQ has none |
| `sq_write(phext, coordinate, text)` | Overwrite one scroll (SQ `update`, auto-saves, whole file rewritten). Only with `SQ_BRIDGE_READONLY=0` |
| `sq_close_channel(port?)` | Stops a host **this bridge started**; hosts started by anything else are left alone |

Phext names are accepted with or without the `.phext` suffix (`test` and
`test.phext` are the same file). Coordinates are strictly validated
(9 components, each 1–999, 1-based).

## Safety

- Read-only by default. Writes additionally refuse: files outside SQ_DIR,
  nonexistent phexts (SQ would silently *create* an empty phext for a new
  name — the bridge checks first), invalid coordinates, and any text
  containing phext delimiter bytes, which would corrupt the structure.
- `sq_close_channel` never kills a host it didn't start.
- Started hosts log to `SQ_DIR/.sq-bridge-<port>.log`. A host started by
  the bridge outlives the bridge process only if the bridge dies without
  closing it — check `sq_status` / the port if one is ever orphaned.

## Tests

`test_client.py` drives the real bridge over MCP stdio against a scratch
phext in `test-data/` (a 3-scroll `test.phext`, never an original):

    .venv/bin/python test_client.py

Phase A (read-only): tool list, status, open, toc, read, query, a write
attempt (refused), a missing-phext read (refused), close. Phase B
(`SQ_BRIDGE_READONLY=0`): write a scroll, read it back, a bad-coordinate
write (refused), close. Full output and the SQ REST quirks found while
probing are in `TEST-LOG.md`.
