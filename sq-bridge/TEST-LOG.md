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

---

# v1.1 — cross-user read-only fix (2026-11-04, ~00:55–01:05 CST)

**The bug** (found and diagnosed live by Claude, relayed by Will): under
v1, `sq_open_channel` ran `sq host` with `cwd=SQ_DIR` and wrote the
bridge log into `SQ_DIR`; SQ also creates its `.sq/` channel state in its
cwd. A user who can only READ `SQ_DIR` therefore could not open a channel
there at all — concretely, user `claude` on aletheia-core could not open
`/chat/emise` (owner wbic16) even read-only. Emise's v1 tests passed only
because they ran as the owner. Claude verified the failure live and
worked around it by copying the phext to a scratch dir.

**Mechanism chosen: `--data-dir`.** SQ v0.6.0 accepts
`sq host <port> [--key <token>] [--data-dir <path>]`. The v1.1 bridge
starts `sq host` with cwd in a per-user **runtime directory**
(`SQ_BRIDGE_RUNTIME_DIR`, default `~/.sq-bridge/run-<port>`) and passes
`--data-dir <SQ_DIR>`, so `.sq/` state and the bridge log live in the
runtime dir while SQ resolves phext data in `SQ_DIR`. The symlink-farm
fallback was not needed. `sq_close_channel` now also removes the runtime
`.sq/` it created (the log is kept). `sq_status` reports the runtime dir
and whether `SQ_DIR` is writable by the calling user, and its CLI probe
runs from the runtime dir so `SQ_DIR` is never touched.

**Pre-flight probes (raw sq, this VM)** — mechanism verified before any
bridge code changed:

- `sq host 18781 --data-dir /tmp/sqprobe/data` run from `/tmp/sqprobe/run`:
  banner printed `Tenant data directory: /tmp/sqprobe/data`; toc/select
  served the data-dir phext; `.sq/` appeared in the *run* dir only; the
  data dir gained no files.
- `POST /api/v2/update` through that host persisted into the data-dir
  file (SHA-256 `289fec46…` → `1d35f136…`): write mode works via
  `--data-dir` too.
- Same setup with the data dir chmod 555 and the phext chmod 444:
  toc/select succeeded, data-dir listing and phext SHA-256 unchanged,
  `.sq/` only in the run dir.

**Test 1 — regression, existing `test_client.py` flow** (this VM,
SQ_DIR=`test-data/`, port 18763; full output `test-run-v11.log`): Phase A
read-only (open/toc/read/query OK; write refused; unknown phext refused;
close removed the runtime `.sq/`) and Phase B writes-enabled (write
returned `Updated 40 bytes`, read back exactly, `test.phext` on disk in
SQ_DIR carries the write — SHA-256 after:
`289fec467b0091bde59b1515557113ca146876f46986ed4581183a3b3797716e`, the
known 4-scroll hash from v1's independent disk verification). No new
files appeared in SQ_DIR during the run — the `.sq/` and
`.sq-bridge-18763.log` visible in `test-data/` are v1 leftovers dated
06:26–06:27; v1.1's log is `~/.sq-bridge/run-18763/sq-bridge-18763.log`.

**Test 2 — local permission repro as a genuinely non-root user**
(`tests/test_readonly_dir.py`): the bridge was launched under
`setpriv --reuid=nobody` (HOME staged at `/tmp/ro-home`, sq copied to the
staging dir) against a data dir owned by root, chmod **555**, phext
chmod **444**, port 18764. (This VM's shell runs as root, for whom
permission bits don't bind — hence the setpriv staging; full output
`test-readonly-dir-run.log`.) Result: `sq_status` honestly reported
`writable by this user: False`; open/toc/read all succeeded; the beta
scroll read back exactly (`beta scroll: phext bridges make channels`);
write refused; close removed the runtime `.sq/`. Snapshot assertion in
the script passed: SQ_DIR listing and phext SHA-256
(`289fec467b0091bde59b1515557113ca146876f46986ed4581183a3b3797716e`)
byte-identical before and after, no `.sq`/log artifacts inside SQ_DIR.

**Test 3 — LIVE cross-user repro on aletheia-core, the exact failing
case** (`tests/test_client_remote_claude.py`, full output
`test-remote-claude-run.log`): an MCP client on this VM launched the
fixed bridge on the box over ssh-stdio, running **as user `claude`**
(`sudo -u claude env HOME=/home/claude SQ_DIR=/chat/emise SQ_PORT=18773
SQ_BRIDGE_READONLY=1 /chat/sq-bridge/.venv/bin/python
/chat/sq-bridge/sq_bridge.py`; bridge on the box is the fixed file,
SHA-256 `fe96b91d28a522f3e355a26d61f82cd441ed7ac6eba974ff594cb3fe9a614f76`).
Baseline first: v1's own test debris in `/chat/emise` (`.sq/` and
`.sq-bridge-18771.log`, created by Emise's wbic16 run at 00:34) was
removed so "no new files" is checkable; baseline listing was the 9
standing entries and `mailbox.phext` SHA-256
`43af12bcd798b58ca15adcecca3d4dafa3930baefefd6dc0d6f03e4aa5db8c4a`.
Claude's session: `sq_status` resolved his own sq
(`/home/claude/.cargo/bin/sq`), reported `writable by this user: False`
and runtime `/home/claude/.sq-bridge/run-18773`; open succeeded
(pid 210784); **toc returned all 6 scrolls**; `sq_read` @
`1.11.4/1.1.2/1.1.1` returned Emi's party invite verbatim; `sq_write`
refused (read-only); close stopped the host and removed the runtime
`.sq/`. Post-checks as wbic16: `mailbox.phext` SHA-256 still
`43af12bcd798b58ca15adcecca3d4dafa3930baefefd6dc0d6f03e4aa5db8c4a`;
`/chat/emise` listing identical to baseline (no `.sq`, no bridge log);
port 18773 free; claude's runtime dir holds only the 125-byte log.
