# SQ (phext) HTTP API — verified surface for a small web app

Date: 2026-10-31 (America/Chicago)
SQ version tested: **0.6.0** (`~/.cargo/bin/sq`, libphext 0.3.3)
Method: local resources only — installed crate source, bundled README, and a live
local test (`sq host` on spare ports 18741/18742 against throwaway phexts in /tmp).
No web sources used.

Primary sources (on this machine):

- `~/.cargo/registry/src/index.crates.io-*/sq-0.6.0/readme.md` — REST API reference
- `~/.cargo/registry/src/index.crates.io-*/sq-0.6.0/src/main.rs` — the actual
  `sq host` HTTP handler (`handle_tcp_connection_inner`, plus the separate
  multi-tenant handler `run_multi_tenant_server` /
  `handle_multi_tenant_connection_with_reload`)
- `~/.cargo/registry/src/index.crates.io-*/sq-0.6.0/src/config.rs` — tenant config
- `~/.cargo/registry/src/index.crates.io-*/sq-0.6.0/src/router.rs` — separate
  `sq route` token router (not needed for a single-site app)
- Note: `~/workspace/human/consciousness-api.md` is an unrelated speculative
  `/api/v1` design doc — it is **not** the SQ API. Ignore it for this purpose.

---

## 1. How `sq host <port>` serves, and the exact /api/v2 endpoints

### Invocation

```
sq host <port> [--key <token>] [--data-dir <path>] [--config <tenants.json>] [--mesh-config <path>]
```

- Plain HTTP, binds **`0.0.0.0:<port>`** (all interfaces, not localhost-only).
  There is no TLS in SQ itself — TLS must come from nginx in front of it,
  which fits the planned "SQ + nginx on the same server" deployment.
- It takes **no phext filename argument**. Which phext is served is chosen
  **per request** by the `p` parameter (see below). It bypasses the shared-memory
  daemon mode (`sq share <file>`); it is a standalone listening mode.
- Responses are plain text (or JSON for `query` / `json-export`), status 200 on
  success, with `Access-Control-Allow-Origin: *` on every response.
- Unknown routes return `404 Not Found` (and are logged to stderr).
  Non-GET/POST methods return `400`. Body cap is 64 MB; header cap 64 KB;
  max 512 concurrent connections; 32 s read/write timeouts (`src/main.rs` consts).

### Common parameters (all endpoints)

| Param | Meaning |
|---|---|
| `p` | Phext name **without** the `.phext` extension. Resolves to `<p>.phext` in the process working directory, or in `--data-dir` if given. URL-decoded; when a data-dir/tenant is in force, `..`, `/`, `\` in `p` are rejected with 403. |
| `c` | Coordinate, full form `a.b.c/d.e.f/g.h.i`, e.g. `1.1.1/1.1.1/1.1.2` |
| `s` | Scroll text for GET `insert`/`update`. URL-encoded (`+` = space, `%XX` decoded, in `url_decode`). |
| body | For POST `insert`/`update`/`where`/`delta`/`query`: the **raw HTTP request body** becomes the scroll / payload. It is not a form field and not JSON — `request_parse` stores the whole body verbatim under the internal key `content`, overriding `s`. |
| `algo` | `checksum` selects the checksum hash algorithm, otherwise XOR (for `where`/`delta`) |
| `limit` | Result/neighbour limit, default 100 (for `query`/`where`) |

### Endpoint table — exact method + path, as routed in `src/main.rs`

Read endpoints (all GET):

| Method + path | Returns |
|---|---|
| `GET /api/v2/version?p=<phext>` | e.g. `0.6.0` |
| `GET /api/v2/load?p=<phext>` | `Loaded <phext>.phext` — forces (re)load of that file from disk into memory |
| `GET /api/v2/toc?p=<phext>` | Lines `* <coord>: <scroll preview>` for every scroll |
| `GET /api/v2/select?p=<phext>&c=<coord>` | The scroll text at that coordinate (empty body if none) |
| `GET /api/v2/get?p=<phext>` | The entire raw `.phext` file in one response |
| `GET /api/v2/status?p=<phext>` | `Hosting:`, `Connection ID:`, `Phext Size:`, `Scrolls:` lines |
| `GET /api/v2/checksum?p=<phext>` | One checksum string for the whole phext |
| `GET /api/v2/delta?p=<phext>` | Hierarchical checksum map (README wording) |
| `GET /api/v2/json-export?p=<phext>` | JSON array `[{ "coord": "...", "scroll": "..." }, ...]`; forces reload from disk |
| `GET /api/v2/query?p=<phext>&from=<coord>&to=<coord>` | **v0.6.0.** JSON array `[{"coordinate":"...","scroll":"..."}]`, every non-empty scroll in the inclusive range |
| `GET /api/v2/query?p=<phext>&set=<coord>,<coord>,...` | Same JSON array for an explicit coordinate set (missing coords return an empty scroll) |
| `POST /api/v2/query?p=<phext>[&from=..&to=..][&limit=N]` | Same as GET query, with the coordinate set supplied as the raw POST body (comma- or newline-separated) |

### WRITE endpoints — yes, they exist and are browser-usable ⭐

| Method + path | Effect |
|---|---|
| `GET /api/v2/update?p=<phext>&c=<coord>&s=<url-encoded text>` | **Overwrite** the scroll at `c`. Returns `Updated N bytes`. |
| `GET /api/v2/insert?p=<phext>&c=<coord>&s=<url-encoded text>` | **Append** to the scroll at `c`. Returns `Inserted N bytes`. |
| `POST /api/v2/update?p=<phext>&c=<coord>` — raw body = new scroll text | **Overwrite**. Returns `Updated N bytes`. Preferred for browser code: no URL-escaping, no URL length limit in practice (64 MB body cap). |
| `POST /api/v2/insert?p=<phext>&c=<coord>` — raw body = text to append | **Append**. Returns `Inserted N bytes`. |
| `GET /api/v2/delete?p=<phext>&c=<coord>` | Clear/truncate the scroll at `c`. Returns `Removed N bytes`. (GET only — there is no POST or DELETE-method variant routed.) |
| `POST /api/v2/where?p=<phext>` — raw body = text | Not a write: returns the coordinate SQ calculates for that text, e.g. `Calculated coordinate 1.1.1/1.1.1/1.1.1 for input (algo=xor, limit=100).` |
| `POST /api/v2/delta?p=<phext>` — raw body = other phext text | Delta against the supplied body (same command as GET delta, body-supplied variant). |

Persistence: **saving is automatic.** In the handler, `insert` / `update` /
`delete` are classified as mutations (`is_mutation`) and the whole phext is
re-imploded and written to disk immediately after the request. There is no
separate save/commit endpoint in HTTP mode, and no transaction / locking API —
concurrent writers to the same phext are serialised only by the server's
per-phext mutex, last write wins per scroll.

CORS: verified live — `OPTIONS` preflight returns
`204 No Content` with
`Access-Control-Allow-Methods: GET, POST, OPTIONS` and
`Access-Control-Allow-Headers: Authorization, Content-Type`,
and normal responses carry `Access-Control-Allow-Origin: *`.
So a browser `fetch()` from another origin (or same origin via nginx) can call
both reads and writes directly. Caveat: that preflight allow-list does **not**
name `X-SQ-API-Key`, so a browser client that needs auth should send the key as
`Authorization: <key>` / `Authorization: Bearer <key>` rather than
`X-SQ-API-Key`, or be served same-origin so no preflight-for-auth-header issue
arises (the header still triggers preflight cross-origin; Authorization is the
listed one).

Minimal browser save of one scroll (overwrite):

```js
await fetch('/api/v2/update?p=herd&c=1.1.1/1.1.1/1.1.2', {
  method: 'POST',
  body: 'Libby, bred 2026-10-01'   // raw text body, not JSON, not a form field
});
```

Minimal read:

```js
const txt = await (await fetch(
  '/api/v2/select?p=herd&c=1.1.1/1.1.1/1.1.2')).text();
```

For structured herd data, `GET /api/v2/query?p=herd&from=...&to=...` (JSON) or
`GET /api/v2/json-export?p=herd` (whole-file JSON) are the most convenient
read-all routes for a static page; `toc`/`get` are plain text.

Other modes not to confuse with the above:

- `POST /api/v2/reload` — **only** in `--config` multi-tenant mode, localhost
  only, no auth; reloads the tenant config file. Not a data endpoint.
- `sq api <config.json> [port]` — a separate OpenAI-compatible proxy
  (`POST /v1/chat/completions`, `GET /stats`), unrelated to phext storage.
- `sq route <config.json> <port>` — a separate token router that proxies to
  per-tenant `sq host` backends.

---

## 2. Multiple phexts? Auth?

### Multiple files: yes, one process serves many

- A single `sq host` process is **not** bound to one file. Every request names
  its file with `p`; the single-tenant handler caches one loaded phext in
  memory and transparently reloads when `p` changes, while the multi-tenant
  handler keeps per-phext-path state. Verified live: one server on port 18741
  served both `p=test` and `p=herd` correctly in interleaved requests.
- Gotcha (verified live): naming a **nonexistent** `p` silently **creates an
  empty `<p>.phext`** in the working/data directory and returns an empty
  scroll/TOC for `1.1.1/1.1.1/1.1.1`. A typo in `p` therefore creates a ghost
  file instead of an error. Keep the app's `p` value a fixed constant.
- Without `--data-dir`, files are resolved relative to the server's **working
  directory** at launch. With `--data-dir <path>`, they are confined to that
  directory and path traversal in `p` is rejected (403).

### Auth: optional, single shared token — off by default

- **No `--key` and no `--config` ⇒ no auth at all.** Anyone who can reach the
  port can read *and write/delete* any phext in the directory. Do not expose a
  no-key instance publicly; put it behind nginx on localhost / a private
  interface if it is run without a key.
- **Single-tenant:** `sq host <port> --key <token> [--data-dir <path>]`.
  Every request (OPTIONS excepted) must carry the token as
  `Authorization: <token>`, `Authorization: Bearer <token>`, or
  `X-SQ-API-Key: <token>`; otherwise `401 Unauthorized`. It is one shared
  static token — no users, no per-scroll permissions, no sessions.
  (The README calls the expected format a `pmb-v1-...` key, but the code only
  does an equality check; any string works as the token.)
- **Multi-tenant:** `sq host <port> --config <tenants.json>` where the file is
  `{"tenants": {"<token>": {"name": "...", "data_dir": "..."}, ...}}`.
  The token (same two headers) selects the tenant, and the tenant's
  `data_dir` isolates its phexts. This is SQ's mechanism for hosting several
  unrelated sites/tenants from one process; for one ranch site it is more
  machinery than needed — a single `--key` + `--data-dir` instance behind
  nginx is the simpler fit.
- Browser implication of turning the key on: the token would be visible in the
  page's JS if the public page itself writes. For admin.bickfordllamaranch.com,
  the usual pragmatic split is: public pages read (or are pre-rendered/static),
  and the admin UI is protected at the nginx layer (e.g. basic auth / IP
  allowlist) with SQ itself bound privately — rather than embedding a
  write-capable SQ token in publicly served JavaScript.

---

## 3. Live local test — actual outputs

Setup (throwaway, in `/tmp/sqtest`):

```bash
printf 'Hello llama world' > /tmp/sqtest/test.phext
printf 'Second herd file'  > /tmp/sqtest/herd.phext
cd /tmp/sqtest && sq host 18741 &
# log: "SQ v0.6.0 listening on port 18741 (max 512 concurrent connections)..."
```

Reads:

```
$ curl -s -i http://127.0.0.1:18741/api/v2/version?p=test
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Content-Length: 5

0.6.0

$ curl -s "http://127.0.0.1:18741/api/v2/load?p=test"
Loaded test.phext

$ curl -s "http://127.0.0.1:18741/api/v2/toc?p=test"
* 1.1.1/1.1.1/1.1.1: Hello llama world

$ curl -s "http://127.0.0.1:18741/api/v2/select?p=test&c=1.1.1/1.1.1/1.1.1"
Hello llama world

$ curl -s "http://127.0.0.1:18741/api/v2/get?p=test"
Hello llama world

$ curl -s "http://127.0.0.1:18741/api/v2/status?p=test"
Hosting: test.phext
Connection ID: 6
Phext Size: 17
Scrolls: 1

$ curl -s "http://127.0.0.1:18741/api/v2/query?p=test&from=1.1.1/1.1.1/1.1.1&to=1.1.1/1.1.1/1.1.9"
[{"coordinate":"1.1.1/1.1.1/1.1.1","scroll":"Hello llama world"}]

$ curl -s "http://127.0.0.1:18741/api/v2/json-export?p=test"   # (after the writes below)
[
   { "coord": "1.1.1/1.1.1/1.1.1", "scroll": "Hello llama world" }
,   { "coord": "1.1.1/1.1.1/1.1.2", "scroll": "Libby the llama, bred 2026-10-01 + vaccinated" }
]
```

Writes — GET form, POST form, auto-save, and delete all verified:

```
$ curl -s "http://127.0.0.1:18741/api/v2/update?p=test&c=1.1.1/1.1.1/1.1.2&s=Libby%20the%20llama%2C%20bred%202026-10-01"
Updated 32 bytes
$ curl -s "http://127.0.0.1:18741/api/v2/select?p=test&c=1.1.1/1.1.1/1.1.2"
Libby the llama, bred 2026-10-01

$ curl -s "http://127.0.0.1:18741/api/v2/insert?p=test&c=1.1.1/1.1.1/1.1.2&s=%20%2B%20vaccinated"
Inserted 13 bytes
$ curl -s "http://127.0.0.1:18741/api/v2/select?p=test&c=1.1.1/1.1.1/1.1.2"
Libby the llama, bred 2026-10-01 + vaccinated

$ curl -s -X POST --data 'POSTED scroll text' "http://127.0.0.1:18741/api/v2/update?p=test&c=1.1.1/1.1.1/1.1.3"
Updated 18 bytes
$ curl -s -X POST --data ' appended-via-POST' "http://127.0.0.1:18741/api/v2/insert?p=test&c=1.1.1/1.1.1/1.1.3"
Inserted 18 bytes
$ curl -s "http://127.0.0.1:18741/api/v2/select?p=test&c=1.1.1/1.1.1/1.1.3"
POSTED scroll text appended-via-POST

# Auto-save check: the file on disk already contained both new scrolls
# (0x17 scroll-break separated) immediately after the calls above —
# no save endpoint was called.
$ od -c /tmp/sqtest/test.phext
H e l l o   l l a m a   w o r l d 027 L i b b y ... 027 P O S T E D ...

$ curl -s "http://127.0.0.1:18741/api/v2/delete?p=test&c=1.1.1/1.1.1/1.1.3"
Removed 36 bytes

$ curl -s -X POST --data '1.1.1/1.1.1/1.1.1,1.1.1/1.1.1/1.1.2' "http://127.0.0.1:18741/api/v2/query?p=test"
[{"coordinate":"1.1.1/1.1.1/1.1.1","scroll":"Hello llama world"},{"coordinate":"1.1.1/1.1.1/1.1.2","scroll":"Libby the llama, bred 2026-10-01 + vaccinated"}]

$ curl -s -X POST --data 'llama' "http://127.0.0.1:18741/api/v2/where?p=test"
Calculated coordinate 1.1.1/1.1.1/1.1.1 for input (algo=xor, limit=100).
```

Multi-file, 404, CORS, ghost-file behaviour:

```
$ curl -s "http://127.0.0.1:18741/api/v2/select?p=herd&c=1.1.1/1.1.1/1.1.1"   # same server process
Second herd file

$ curl -s -i "http://127.0.0.1:18741/api/v2/nope?p=test"
HTTP/1.1 404 Not Found  /  Not Found

$ curl -s -i -X OPTIONS http://127.0.0.1:18741/api/v2/select
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type

$ curl -s "http://127.0.0.1:18741/api/v2/toc?p=brandnew"
* 1.1.1/1.1.1/1.1.1:
# …and an empty /tmp/sqtest/brandnew.phext (0 bytes) now exists on disk.
```

Auth test — second instance: `sq host 18742 --key testkey123 --data-dir /tmp/sqtest2`
(log: `Auth enabled (pmb-v1 key required)`):

```
$ curl -s -i ".../api/v2/select?p=vault&c=1.1.1/1.1.1/1.1.1"                      # no header
HTTP/1.1 401 Unauthorized  /  Unauthorized
$ curl -s -H "Authorization: testkey123"        ".../select?p=vault&c=..."        # → secret herd
$ curl -s -H "Authorization: Bearer testkey123" ".../select?p=vault&c=..."        # → secret herd
$ curl -s -H "X-SQ-API-Key: testkey123"         ".../select?p=vault&c=..."        # → secret herd
$ curl -s -i -H "Authorization: wrong"          ".../select?p=vault&c=..."        # → 401 Unauthorized
$ curl -s -i -H "Authorization: testkey123"     ".../select?p=../vault&c=..."     # → 403 Forbidden: invalid phext path
```

Both test servers were shut down after the test; no production SQ instance
or real phext was touched.

---

## 4. Verdict: no shim needed — SQ already has a browser-usable write API

Plainly: **the premise that SQ might be read-only over HTTP is false for
v0.6.0.** `POST /api/v2/update` (overwrite) and `POST /api/v2/insert`
(append), plus `GET …&s=` variants and `GET /api/v2/delete`, are routed in
`src/main.rs`, documented in the bundled README ("Saving is automatic — if a
command changes the content of a phext, it will be saved to disk
immediately"), and verified live above, including the on-disk result.
A static page + `fetch()` is sufficient; no build process and no extra
endpoint are required to keep SQ as the data store.

That said, the honest constraints for the ranch admin site:

1. **Auth is all-or-nothing and the token is client-visible if used from JS.**
   If the admin UI writes directly to SQ, either (a) protect the whole admin
   vhost at nginx (basic auth / allowlist) and run SQ with `--key` on a
   port only nginx can reach, accepting that the key sits in admin-page JS
   behind that nginx gate, or (b) if that is not acceptable, the simplest
   alternative that still keeps SQ as the store is a **tiny stdlib-only
   proxy endpoint** (e.g. a small Python `http.server`-based or shell/ CGI
   handler behind nginx auth) that holds the SQ key server-side and forwards
   `update`/`select` calls to `sq host` on localhost. This is an auth-hiding
   shim only — not a second data store.
2. **One scroll = one string.** There is no schema, validation, indexing, or
   query-by-content (the v0.6.0 `query` is by coordinate range/set only).
   The herd module's data model should therefore be one scroll per animal /
   record with a simple, self-describing text format (e.g. key: value lines
   or JSON text inside the scroll — SQ treats it as opaque text either way),
   and due-date maths (vaccination due, +21-day spit-off test) done in the
   page's JS.
3. **GET writes exist** (`update`/`insert`/`delete` via `&s=`), so anything
   that crawls/prefetches admin URLs with a valid key could mutate data.
   Browser code should use the POST forms; nginx should not log query
   strings for the admin vhost if GET forms are ever used.
4. **No TLS, no users, no audit log in SQ.** nginx supplies TLS and access
   logs; SQ's own stderr log records 404s and disk-write failures only.
5. The daemon mode (`sq share <file>`, shared memory, `sq update <coord>
   "text"` on the CLI) is a valid operator-side write path on the server
   itself, but it is not usable from a browser and is not needed here given
   the HTTP write endpoints. Note the standing local caution: do not swap
   the hosted `.phext` file underneath a running SQ process — restart SQ
   after replacing its file on disk (deploy.sh should restart, not just
   copy).

Recommended shape for admin.bickfordllamaranch.com, consistent with the
requirements: nginx (TLS, static assets, admin gate) → `sq host <private
port> --key <token> --data-dir <site data dir>`, one phext (e.g.
`p=herd`), static JS calling `/api/v2/query` / `/api/v2/json-export` to read
and `POST /api/v2/update` to save — well within a 200 KB page budget, no
build step.
