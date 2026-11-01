# Bickford Llama Ranch — admin.bickfordllamaranch.com

Branded for **Libby Bickford and Will Bickford — Bickford Llama Ranch**.
Modern TLS site (nginx + Let's Encrypt, same box and pattern as mirrorborn.us),
no build process, vanilla HTML/CSS/JS, total page weight far under the 200 KB
non-media budget (admin 14,628 B · public 3,291 B — see VERIFY.md).

## The data model — phext is the database

**No JSON data structures anywhere.** One file, `ranch.phext`, hosted by SQ
(`sq host`, /api/v2). Every field and every record is **its own scroll at its
own coordinate**, holding a plain-text value (`2026-10-17`, `CD/T`, `female`).
An edit is exactly one request:

```
POST /api/v2/update?p=ranch&c=<coordinate>     body = the new raw value
```

No read-modify-write, no blob, nothing to lock or merge. SQ saves to disk
immediately. The browser parses SQ's `json-export`/`toc` responses only to
*discover* which coordinates exist — that is transport, never storage.

### Coordinate map

Coordinate form: `Library.Shelf.Series / Collection.Volume.Book / Chapter.Section.Scroll`

**Homepage CMS** — Library 1, one scroll per field:

| Coordinate | Field |
|---|---|
| 1.1.1/1.1.1/1.1.1 | Site title |
| 1.1.1/1.1.1/1.1.2 | Tagline |
| 1.1.1/1.1.1/1.1.3 | Announcement |
| 1.1.1/1.1.1/1.1.4 | About text |
| 1.1.1/1.1.1/1.1.5 | Contact line |

**Settings** — 1.1.1/1.1.2/1.1.F: F=1 reminder email recipients (comma-separated,
plain text), F=2 ranch name / branding line. The reminder script reads
recipients from here, never from code.

**Animals** — Library 2. Animal A lives at Series = A. Profile fields at
`2.1.A/1.1.1/1.1.F`:

| F | Field | | F | Field |
|---|---|---|---|---|
| 1 | name | | 5 | dam |
| 2 | sex (female/male/gelding) | | 6 | color / markings |
| 3 | birth date | | 7 | status (active/sold/deceased) |
| 4 | sire | | 8 | notes |

(CMS sits in Library 1, animals in Library 2, so animal 1's profile at
2.1.1/1.1.1/1.1.F can never collide with the CMS block at 1.1.1/1.1.1/1.1.F.)

**Breeding record B** for animal A — `2.1.A/1.1.2/B.1.F`:

| F | Field | | F | Field |
|---|---|---|---|---|
| 1 | breeding date | | 5 | spit-off 45d result |
| 2 | sire name / id | | 6 | outcome (pregnant/open/unknown) |
| 3 | spit-off 14d result | | 7 | cria birth date |
| 4 | spit-off 21d result | | 8 | cria note (name/sex) |

**Vaccination event V** for animal A — `2.1.A/1.1.3/V.1.F`:

| F | Field |
|---|---|
| 1 | date given |
| 2 | vaccine name |
| 3 | interval days until next due (e.g. 365) |
| 4 | notes |

Next due is **computed** (date + interval), never stored. New records take the
next free B/V number for that animal; new animals take the next free A.

## Modules

- **Herd (admin)** — `site/admin/`: herd list with inline per-field editing
  (one SQ update per field, on change), add-animal / add-breeding /
  add-vaccination forms that write only the new record's scrolls, a computed
  Due list, the 5-field Homepage CMS editor, and Settings. Vanilla JS.
- **Public homepage** — `site/public/`: renders the 5 CMS scrolls with five
  SQ `select` calls. Read-only.
- **Email reminders** — `reminders/remind.py`, Python stdlib only, daily cron.
  One digest via SMTP (`RANCH_SMTP_*` env), recipients from the settings
  scroll. `--dry-run` prints instead of sending. Rules (Merck-sourced, see
  `research/husbandry.md`):
  - spit-off checks at breeding **+14, +21, +45 days**, reminded while that
    check's result scroll is still empty and the date has arrived;
  - vaccination due = last given + its interval scroll (default suggestion
    365 in the form — CD/T and rabies are both annual in camelids), reminded
    14 days ahead and while overdue;
  - cria due = breeding **+342 days** (window 332–352), only when outcome is
    pregnant/unknown and no cria birth date is recorded; e-mail fires 7 days
    ahead;
  - the dam's pre-birthing CD/T booster window (due −42…−28 days, if no CD/T
    vaccination falls inside it) is a **dashboard note only**, not an e-mail.
  No other schedules are invented: shearing, toenails and deworming are
  herd/condition-based and deliberately not computed.

## Security shape (no complexity without a purpose)

- SQ runs with `--key` on port 18765, data-dir confined, key in a
  server-only EnvironmentFile. SQ has no TLS — nginx terminates TLS.
- The key is **never in JavaScript**: nginx injects it
  (`proxy_set_header Authorization`, from a chmod-600 server file).
- Public vhost: nginx proxies **only** `select|toc|version` GETs; everything
  else under /api/ 404s.
- Admin vhost: the whole vhost, /api included, sits behind nginx Basic Auth
  (htpasswd). One gate, no user system.
- SQ binds 0.0.0.0 in host mode — the box firewall must keep 18765 private.

## Deploy

See `deploy/README.md`. Short version: `./deploy/deploy.sh --dry-run`, then
`./deploy.sh` — rsyncs via the aletheia-core hop to wbic16@44.248.235.76
(direct access is blocked; the box's git-pull key is broken, so files are
placed directly, as with mirrorborn.us), installs nginx vhosts + the
`sq-ranch` systemd unit, restarts SQ (never hot-swap a hosted phext),
`nginx -t` + reload. Idempotent; never overwrites an existing server
`ranch.phext`. TLS once: `certbot --nginx` for apex, www and admin.

Seed data: `seed/make_seed.sh` rebuilds `seed/ranch.phext` through the real
SQ API (CMS + settings + 2 clearly-marked EXAMPLE animals, each with one
breeding and one vaccination, dates chosen so the reminder rules fire).

## Open decisions for Will

1. **DNS** — point `admin.bickfordllamaranch.com` (and apex/www) at
   44.248.235.76 so certbot can issue.
2. **E-mail** — real reminder recipients (replace the `example.com` seed
   values in Settings) and SMTP credentials for the box (`RANCH_SMTP_*`:
   which provider/account sends the digest?).
3. **Basic-auth users** — usernames/passwords for Libby and Will
   (`htpasswd` entries, created on the server, never in this repo).
4. **Real herd data** — replace the two EXAMPLE animals, or start from an
   empty phext and add animals in the admin page.
