# Verification — 2026-10-31 (America/Chicago; host clock UTC reads 2026-11-01)

All tests ran locally against throwaway copies of the seed. Nothing was
deployed to the live box; both test SQ instances were killed afterwards
(ports 18767/18768 confirmed closed).

## Seed build
- `seed/make_seed.sh` wrote every value through a real `sq host` (port 18766)
  via `POST /api/v2/update`, one POST per scroll.
- Parsed back with `~/workspace/phext/parse_phext.py`: **43 scroll slots,
  38 non-empty scrolls**, first 1.1.1/1.1.1/1.1.1, last 2.1.2/1.1.3/1.1.4 —
  every value at exactly its coordinate-map address, CMS (Library 1) and
  animal 1 (Library 2) collision-free.

## SQ behaviour (sq host 18767, copy of the seed in /tmp)
- `GET select c=1.1.1/1.1.1/1.1.1` → `Bickford Llama Ranch`
- **One field edit = one POST**: `POST update c=2.1.1/1.1.1/1.1.6` body
  `White with grey patches` → `Updated 23 bytes`; select back returned the new
  value; the neighbouring name scroll (2.1.1/1.1.1/1.1.1) was untouched
  (`Example — Willow`). No read-modify-write of any blob.
- **Add a breeding** (animal 1, record B=2): 3 POSTs (date 2026-10-30, sire,
  outcome) → select of 2.1.1/1.1.2/2.1.1 returned `2026-10-30`.
- JS: `node --check` passes for `site/admin/app.js` and `site/public/home.js`;
  `remind.py` compiles (`py_compile`). The admin Due list uses the same
  constants/formulas as remind.py (14/21/45, +342 window 332–352, interval).

## Reminder dry-run (remind.py --dry-run, against the pristine seed)
Seed dates were chosen relative to 2026-10-31 so the rules fire; all four
expected items appeared in ONE digest, recipients read from the settings
scroll (1.1.1/1.1.2/1.1.1):

- `SPIT-OFF OVERDUE/DUE: Example — Willow — 14-day check was due 2026-10-31 (bred 2026-10-17)`
- `VACCINATION due soon: Example — Willow — CD/T next due 2026-11-10 (given 2025-11-10, every 365 days)` (14-day warning)
- `CRIA DUE SOON: Example — Maple — due around 2026-11-05 (window 2026-10-26 to 2026-11-15), bred 2025-11-28` (7-day warning)
- `VACCINATION OVERDUE: Example — Maple — CD/T next due 2026-10-01 (given 2025-10-01, every 365 days)`

## Page weight (non-media, shared style.css counted once per page)
| Page | Bytes | Budget |
|---|---|---|
| Admin (index.html 3,208 + app.js 9,737 + style.css 1,683) | **14,628** | 200 KB — 7.1% |
| Public (index.html 756 + home.js 852 + style.css 1,683) | **3,291** | 200 KB — 1.6% |

## Deploy
- `deploy/deploy.sh --dry-run` prints the full step list (mkdir, 5 rsyncs,
  seed-if-absent, config install, secrets check, SQ restart, nginx -t +
  reload) and touches nothing; exit 0. A `set -e` bug in the dry-run path
  was found and fixed during this verification.
- Live deploy was NOT run (by instruction).

## Not verified / caveats
- Admin/public pages were exercised through their exact SQ API calls via
  curl, not in a live browser.
- nginx configs and the systemd unit are written but untested on the box
  (no live deploy); `nginx -t` runs as part of deploy.sh before reload.
