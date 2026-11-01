# SQ v0.5.6 compatibility — Bickford Llama Ranch app

Date: 2026-10-31 (America/Chicago)
Question: does the ranch app work against SQ **v0.5.6** (the version on the
AWS box, `/usr/local/bin/sq`), or does it need its own v0.6.0 binary?

## Verdict

**(a) The app works as-is on v0.5.6. No code changes, no separate binary.**

Every endpoint the app actually calls was tested live against the box's own
v0.5.6 and behaves identically to v0.6.0, including response shapes and
auto-save. `deploy/sq-ranch.service` works exactly as written — its
`ExecStart=/usr/local/bin/sq host 18765 --key ${RANCH_SQ_KEY} --data-dir …`
uses the same syntax the box's production tenants already run under 0.5.6.

Two differences from 0.6.0 were found; **neither affects the app** (details
below): `/api/v2/query` does not exist in 0.5.6, and the `X-SQ-API-Key`
header is not accepted. The app uses neither.

Deployment consequence: **do not** follow the old deploy/README step 3
("install sq 0.6.0 to /usr/local/bin/sq"). That binary is shared with the
box's production SQ tenants (ports 1337–1339, running since Oct 23);
replacing it is unnecessary risk. Recommended doc fix (only change of any
kind): rewrite that step to say the box's existing v0.5.6 is verified
compatible and must be left in place.

## What the app actually calls (from the code, not assumptions)

| Caller | SQ calls |
|---|---|
| `site/admin/app.js` | `GET /api/v2/json-export?p=ranch` (expects a JSON array of objects with keys **`coord`** and **`scroll`**); `POST /api/v2/update?p=ranch&c=<coord>` with raw body |
| `site/public/home.js` | `GET /api/v2/select?p=ranch&c=<coord>` |
| `reminders/remind.py` | `GET /api/v2/json-export?p=ranch`, key sent as `Authorization: <key>` |
| `seed/make_seed.sh` | `POST /api/v2/update` (same path as admin) |
| `deploy/nginx-*.conf` | proxy GET `select` / `toc` / `version` (public vhost) and all of `/api/v2/` (admin vhost); key injected server-side as `Authorization` via `sq-proxy.conf` |

`query`, `toc`, and `version` are not called by any app code (`toc`/`version`
are only in the public vhost's proxy allowlist). They were tested anyway,
per the brief.

## Test method

On the AWS box itself (44.248.235.76, via aletheia-core hop), using the
box's own `/usr/local/bin/sq`:

- Seed `ranch.phext` transferred byte-identical (854 B, md5
  `082aabfa00ff721cfa0ad1f922b75537` before and after transfer) into a
  throwaway `/tmp/ranch056/`.
- Test instance: `sq host 18798 --key testkey056 --data-dir /tmp/ranch056`
  → log: `Auth enabled (pmb-v1 key required)` / `SQ v0.5.6 listening on
  port 18798 (max 512 concurrent connections)...`
- All requests curled from the box against `127.0.0.1:18798`.
- Afterward: test process killed (port 18798 verified closed), `/tmp/ranch056`
  deleted, and production verified untouched — PIDs 648/649/652 still running
  their original command lines (`sq host 1337 --config /etc/sq/tenants.json`,
  `sq host 1338/1339 --key … --data-dir /var/lib/sq/tenants/…`), ports
  1337–1339 still listening.
- Recon note: on 0.5.6, `sq --version` / `sq --help` print the client usage
  line (`Usage: sq <command> <coordinate> <message>`); the version subcommand
  is `sq version` → `0.5.6`. Cosmetic only; hosting is unaffected.

## Per-endpoint results (actual outputs)

| # | Test | Result | Evidence |
|---|---|---|---|
| 1 | `sq host <port> --key <k> --data-dir <dir>` starts | **PASS** | Log lines above; port listening |
| 2 | `GET /api/v2/version` — no key | **PASS** (auth enforced) | `Unauthorized`, HTTP 401 |
| 3 | `GET /api/v2/version` — wrong key | **PASS** | `Unauthorized`, HTTP 401 |
| 4 | `GET /api/v2/version?p=ranch` — `Authorization: <key>` | **PASS** | `0.5.6`, HTTP 200 |
| 5 | `GET /api/v2/toc?p=ranch` | **PASS** | All 38 seed scrolls in the familiar `* <coord>: <preview>` format, HTTP 200 |
| 6 | `GET /api/v2/select?p=ranch&c=1.1.1/1.1.1/1.1.1` | **PASS** | `Bickford Llama Ranch`, HTTP 200 |
| 7 | `GET /api/v2/json-export?p=ranch` | **PASS** | Exists in 0.5.6; same shape as 0.6.0: `[{ "coord": "…", "scroll": "…" }, …]` — exactly the keys `app.js` (`r.coord`, `r.scroll`) and `remind.py` (`row["coord"]`, `row["scroll"]`) read. Order is hash order (not sorted) in both versions' usage here; the app builds a Map/dict, so order is irrelevant |
| 8 | `POST /api/v2/update` raw body, with key (`2.1.1/1.1.1/1.1.6` ← `White with grey patches`) | **PASS** | `Updated 23 bytes`, HTTP 200 |
| 9 | Select the updated scroll back | **PASS** | `White with grey patches` |
| 10 | Neighbour scroll untouched (select `2.1.1/1.1.1/1.1.1`) | **PASS** | `Example — Willow` (unchanged) |
| 11 | Auto-save to disk after POST update | **PASS** | New value found in `/tmp/ranch056/ranch.phext` on disk (grep count 1; file md5 changed) with no save call |
| 12 | `POST /api/v2/update` with **no** key | **PASS** (write blocked) | `Unauthorized`, HTTP 401; scroll still held its original value (`White with brown patches`) when selected afterwards |
| 13 | Auth via `Authorization: Bearer <key>` | **PASS** | Select returned `Bickford Llama Ranch`, HTTP 200 (remind.py uses the plain `Authorization: <key>` form, test 4/7) |
| 14 | Auth via `X-SQ-API-Key: <key>` header | **FAIL — differs from 0.6.0** | `Unauthorized`, HTTP 401 (0.6.0 accepts this header). **Not used anywhere** in the app, remind.py, or the nginx configs — all send `Authorization`. Do not switch header style while on 0.5.6 |
| 15 | `GET /api/v2/query?p=ranch&from=…&to=…` | **FAIL — absent in 0.5.6** | `Not Found`, HTTP 404 |
| 16 | `GET /api/v2/query?p=ranch&set=…` | **FAIL — absent in 0.5.6** | `Not Found`, HTTP 404 |

Tests 15–16 are the only functional gaps, and nothing in the app calls
`query` (verified by grepping `site/`, `reminders/`, `seed/`, `deploy/`:
the only `/api/v2/` paths used are `json-export`, `select`, `update`, plus
the nginx-proxied `toc`/`version`). If a future feature wants `query`, that
feature — not the current app — is what would need a 0.6.0 binary.

## What this means for deploy

- `deploy/sq-ranch.service`: **no change needed.** It already points at the
  box's `/usr/local/bin/sq`, and its `host --key --data-dir` invocation is
  the same shape as the box's running production tenants.
- No isolated 0.6.0 install (`/usr/local/bin/sq-ranch-060`, `/opt/sq-ranch/`)
  is needed.
- Only recommended edit: `deploy/README.md` one-time-setup step 3 — replace
  the "install sq 0.6.0" instruction with a note that the box's v0.5.6 is
  verified compatible (this file is the evidence) and the shared binary must
  not be replaced.
