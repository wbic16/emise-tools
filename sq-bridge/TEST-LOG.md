# sq-bridge TEST-LOG

All results below are from commands actually run on this VM on 2026-11-04
(CST), against SQ v0.6.0 (`~/.cargo/bin/sq`, banner: "SQ v0.6.0 listening on
port …"). No original phext was touched: every write test hit the scratch
copy in `test-data/`.

## Step 1 — Probe SQ's REST API directly (curl, scratch host on :18761)

Before coding, a throwaway `sq host 18761` was started in `test-data/` on a
freshly built 3-scroll `test.phext` (alpha @ 1.1.1/1.1.1/1.1.1, beta @
1.1.1/1.1.1/1.1.2, gamma @ 1.1.1/1.1.2/1.1.1; built with the PyPI `phext`
package's implode, scrolls in ascending coordinate order). Findings, each
observed, not assumed:

- **The `p` parameter is the phext name WITHOUT `.phext`.** `p=test` works.
  `p=test.phext` silently addressed a different file: SQ created an empty
  `test.phext.phext` and its TOC returned one empty scroll.
- **SQ creates phexts for unknown names.** `toc?p=ghost` returned
  `* 1.1.1/1.1.1/1.1.1: ` (empty) and a new empty `ghost.phext` appeared in
  the directory. (Both probe artifacts were deleted.) → The bridge checks
  file existence itself and refuses unknown names.
- **toc** returns plain text, one line per scroll: `* <coord>: <full scroll text>`.
- **select** (`p`, `c`) returns one scroll's exact text.
- **get ignores `c` entirely**: with and without a coordinate it returned
  the whole phext as raw text (delimiters \x17, \x1a visible). → The bridge
  reads via `select`, never `get`.
- **load** returns the literal text `Loaded test.phext` (a status string,
  not content).
- **query is a coordinate range, not a text search.** `q=needle` →
  `Bad Request: query needs a range (from + to) or a set of coordinates`.
  `from=1.1.1/1.1.1/1.1.1&to=1.1.1/1.1.1/1.1.2` returned
  `[{"coordinate":"1.1.1/1.1.1/1.1.1","scroll":"alpha scroll: the first test scroll"},{"coordinate":"1.1.1/1.1.1/1.1.2","scroll":"beta scroll: phext bridges make channels"}]`.
  Guessed set-parameter names (`coords=`, `coordinates=`) were both rejected
  with the same Bad Request, so the bridge exposes range query only.
- **update works as documented**: `POST /api/v2/update?p=test&c=1.1.1/1.1.1/1.1.3`
  with a raw body → `Updated 37 bytes`, the scroll read back via select,
  and `test.phext` grew on disk (auto-save, whole-file rewrite).
- **Auth**: a second host on :18762 with `--key sekret-token` returned
  `401 Unauthorized` with no header and with a wrong key, and `200` with
  both `Authorization: sekret-token` (bare) and `Authorization: Bearer …`.
  The bridge sends the bare form.
- **No status endpoint**: `GET /` → `404 Not Found` (the bridge treats any
  HTTP answer, including 404, as "host is up").
- **`sq --version` is not a version probe**: in a bare directory it errors
  `MapOpenFailed(2)`; inside a data dir it prints
  `Usage: sq <command> <coordinate> <message>`. The version string only
  appears in the `sq host` banner. `sq_status` labels its probe honestly.

## Step 2 — End-to-end MCP test (test_client.py, stdio, port 18763)

`test.phext` was regenerated clean (SHA-256 before:
`14f3daee477537e4d05b3a1c2d7339a13945d9ca62d56a7b5d094ae981b819ba`) and
`.venv/bin/python test_client.py` ran against the shipped `sq_bridge.py`
(exit 0; raw output saved as `test-run.log`, server stderr as
`test-run-stderr.log`). Verbatim client output:

```
=== Phase A: SQ_BRIDGE_READONLY=1 (default) ===
--- tools: sq_status, sq_open_channel, sq_toc, sq_read, sq_query, sq_write, sq_close_channel
--- A sq_status (isError=False)
sq binary: /home/hatch/.cargo/bin/sq (exists: True)
sq CLI probe (--version, cwd=SQ_DIR): Usage: sq <command> <coordinate> <message>
data dir (SQ_DIR): /home/hatch/workspace/sq-bridge/test-data
phexts in SQ_DIR: test.phext
port: 18763  base URL: http://127.0.0.1:18763
host answering: False
host started by this bridge: False
auth key configured: False
mode: READ-ONLY (writes refused)
--- A sq_open_channel(test) (isError=False)
channel open: http://127.0.0.1:18763 serves test.phext from /home/hatch/workspace/sq-bridge/test-data (started sq host, pid 12194, log /home/hatch/workspace/sq-bridge/test-data/.sq-bridge-18763.log)
--- A sq_toc(test) (isError=False)
* 1.1.1/1.1.1/1.1.1: alpha scroll: the first test scroll
* 1.1.1/1.1.1/1.1.2: beta scroll: phext bridges make channels
* 1.1.1/1.1.2/1.1.1: gamma scroll: a needle in the lattice
--- A sq_read alpha (isError=False)
alpha scroll: the first test scroll
--- A sq_query range (isError=False)
[{"coordinate":"1.1.1/1.1.1/1.1.1","scroll":"alpha scroll: the first test scroll"},{"coordinate":"1.1.1/1.1.1/1.1.2","scroll":"beta scroll: phext bridges make channels"}]
--- A sq_write (must refuse) (isError=True)
Error executing tool sq_write
--- A sq_read missing phext (must refuse) (isError=True)
Error executing tool sq_read
--- A sq_close_channel (isError=False)
channel closed: sq host on port 18763 stopped (pid was 12194, exit -15)
=== Phase B: SQ_BRIDGE_READONLY=0 ===
--- B sq_open_channel(test) (isError=False)
channel open: http://127.0.0.1:18763 serves test.phext from /home/hatch/workspace/sq-bridge/test-data (started sq host, pid 12271, log /home/hatch/workspace/sq-bridge/test-data/.sq-bridge-18763.log)
--- B sq_write delta (isError=False)
wrote test.phext @ 1.1.1/1.1.1/1.1.3: SQ said 'Updated 40 bytes'
--- B sq_read delta back (isError=False)
delta scroll: written through the bridge
--- B sq_write bad coord (must refuse) (isError=True)
Error executing tool sq_write
--- B sq_close_channel (isError=False)
channel closed: sq host on port 18763 stopped (pid was 12271, exit -15)
--- B sq_status after close (isError=False)
host answering: False
mode: WRITES ENABLED (SQ_DIR only)
```
(Phase B status output is abridged here — the full text is in test-run.log.)

The MCP client surfaces tool refusals only as "Error executing tool …";
the actual refusal reasons are in the bridge's server stderr
(`test-run-stderr.log`), verbatim:

- `sq-bridge is READ-ONLY (SQ_BRIDGE_READONLY=1); write refused.`
- `no such phext in SQ_DIR: ghost.phext … Refusing: SQ would silently create an empty phext for a new name.`
- `coordinate components are 1-based; 0 is not valid phext`

## Step 3 — Verify the write on disk, independent of SQ

After the run, `test.phext` SHA-256:
`289fec467b0091bde59b1515557113ca146876f46986ed4581183a3b3797716e`
(changed from the pre-test hash above). Exploding the file with the PyPI
`phext` package shows exactly 4 scrolls — the original 3 plus
`1.1.1/1.1.1/1.1.3 -> delta scroll: written through the bridge` — proving
SQ's update auto-saved through to disk and the read-only phase's refused
write ("delta scroll: must not land") is nowhere in the file. Port 18763
was confirmed closed after the tests (`ss -ltn` shows no listener).

## Not tested

- Authenticated end-to-end run through the bridge (SQ_KEY set): the header
  behaviour was verified by curl in Step 1, but no MCP phase ran with a key.
- Daemon mode (`sq share` / `sq status|toc|select` CLI channel): the bridge
  is HTTP-only in v1, matching how Claude's bridge picked one transport.
