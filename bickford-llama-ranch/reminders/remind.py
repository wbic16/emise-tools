#!/usr/bin/env python3
"""Bickford Llama Ranch — daily reminder digest. Python stdlib only.

Data lives in ranch.phext (one scroll per field), served by SQ on localhost.
Discovery uses SQ's json-export response; stored scrolls are plain text.
Recipients come from the settings scroll 1.1.1/1.1.2/1.1.1 — never from code.

Derived dates (Merck, see research/husbandry.md):
  spit-off checks   breeding +14 / +21 / +45 days, while that check has no result
  cria due          breeding +342 days, window 332-352, outcome pregnant/unknown,
                    no cria birth date recorded; e-mail fires 7 days ahead
  vaccination due   date given + interval days (interval is a scroll, e.g. 365);
                    e-mail fires 14 days ahead and while overdue.
The dam pre-birthing CD/T booster note is dashboard-only by design, not e-mailed.

Usage:  remind.py [--dry-run]
Env:    RANCH_SQ_URL  (default http://127.0.0.1:18765)
        RANCH_SQ_KEY  (optional; sent as Authorization header)
        RANCH_SMTP_HOST, RANCH_SMTP_PORT (default 25), RANCH_SMTP_USER,
        RANCH_SMTP_PASS, RANCH_SMTP_FROM, RANCH_SMTP_TLS=1 for STARTTLS
"""
import os, re, smtplib, sys, urllib.request
from datetime import date, timedelta
from email.message import EmailMessage

SQ = os.environ.get("RANCH_SQ_URL", "http://127.0.0.1:18765").rstrip("/")
DRY = "--dry-run" in sys.argv

def fetch(path):
    req = urllib.request.Request(SQ + path)
    key = os.environ.get("RANCH_SQ_KEY")
    if key:
        req.add_header("Authorization", key)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")

import json  # only to parse SQ's json-export *response*; nothing stored as JSON
def load():
    return {row["coord"]: row["scroll"].strip() for row in json.loads(fetch("/api/v2/json-export?p=ranch"))}

DB = load()
def get(coord):
    return DB.get(coord, "")

prof = lambda a, f: f"2.1.{a}/1.1.1/1.1.{f}"
bred = lambda a, b, f: f"2.1.{a}/1.1.2/{b}.1.{f}"
vacc = lambda a, v, f: f"2.1.{a}/1.1.3/{v}.1.{f}"

def ids(pattern):
    out = set()
    for c in DB:
        m = re.match(pattern, c)
        if m:
            out.add(int(m.group(1)))
    return sorted(out)

animals = lambda: ids(r"^2\.1\.(\d+)/")
records = lambda a, book: ids(rf"^2\.1\.{a}/1\.1\.{book}/(\d+)\.1\.")

def parse(s):
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None

def main():
    today = date.today()
    lines = []
    for a in animals():
        name = get(prof(a, 1)) or f"Animal {a}"
        for b in records(a, 2):
            bred_on = parse(get(bred(a, b, 1)))
            if not bred_on:
                continue
            for days, f in ((14, 3), (21, 4), (45, 5)):
                if not get(bred(a, b, f)):
                    due = bred_on + timedelta(days=days)
                    if due <= today:
                        lines.append(f"SPIT-OFF OVERDUE/DUE: {name} — {days}-day check was due "
                                     f"{due} (bred {bred_on}), no result recorded.")
            outcome = get(bred(a, b, 6)) or "unknown"
            if outcome in ("pregnant", "unknown") and not get(bred(a, b, 7)):
                due = bred_on + timedelta(days=342)
                if due - timedelta(days=7) <= today <= due + timedelta(days=10):
                    lines.append(f"CRIA DUE SOON: {name} — due around {due} "
                                 f"(window {bred_on + timedelta(days=332)} to "
                                 f"{bred_on + timedelta(days=352)}), bred {bred_on}.")
        latest = {}
        for v in records(a, 3):
            key = (get(vacc(a, v, 2)) or "vaccine").lower()
            if key not in latest or get(vacc(a, v, 1)) > get(vacc(a, latest[key], 1)):
                latest[key] = v
        for v in latest.values():
            given, interval = parse(get(vacc(a, v, 1))), get(vacc(a, v, 3))
            if not given or not interval.isdigit():
                continue
            due = given + timedelta(days=int(interval))
            if due - timedelta(days=14) <= today:
                when = "OVERDUE" if due < today else "due soon"
                lines.append(f"VACCINATION {when}: {name} — {get(vacc(a, v, 2))} next due "
                             f"{due} (given {given}, every {interval} days).")
    recipients = [r.strip() for r in get("1.1.1/1.1.2/1.1.1").split(",") if r.strip()]
    ranch = get("1.1.1/1.1.2/1.1.2") or "Bickford Llama Ranch"
    if not lines:
        print("No reminders due today.")
        return 0
    body = f"{ranch} — reminders for {today}\n\n" + "\n".join(lines) + "\n"
    if DRY:
        print(f"TO: {', '.join(recipients) or '(no recipients in settings scroll)'}")
        print(f"SUBJECT: {ranch} reminders — {today}\n")
        print(body)
        return 0
    if not recipients:
        print("Reminders exist but the settings scroll has no recipients; not sending.", file=sys.stderr)
        return 1
    msg = EmailMessage()
    msg["From"] = os.environ.get("RANCH_SMTP_FROM", "ranch@localhost")
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = f"{ranch} reminders — {today}"
    msg.set_content(body)
    with smtplib.SMTP(os.environ["RANCH_SMTP_HOST"], int(os.environ.get("RANCH_SMTP_PORT", "25")), timeout=30) as s:
        if os.environ.get("RANCH_SMTP_TLS") == "1":
            s.starttls()
        if os.environ.get("RANCH_SMTP_USER"):
            s.login(os.environ["RANCH_SMTP_USER"], os.environ.get("RANCH_SMTP_PASS", ""))
        s.send_message(msg)
    print(f"Sent {len(lines)} reminder(s) to {', '.join(recipients)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
