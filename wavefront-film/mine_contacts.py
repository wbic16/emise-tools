#!/usr/bin/env python3
"""Mine contact points from Will's Twitter archive (tweets.json only).

Contact points for an account = number of Will's tweets that reply to OR mention
that account (each tweet counted once per account). Sources: in_reply_to_screen_name
and entities.user_mentions, matched case-insensitively. Likes and DMs are never read.
Will's own account (@wbic16) is excluded.
Output: ~/workspace/wavefront/contact-points.tsv
"""
import json, sys
from collections import defaultdict
from datetime import datetime

ARCHIVE = "/home/hatch/workspace/twitter-archive/tweets.json"
OUT = "/home/hatch/workspace/wavefront/contact-points.tsv"
SELF = {"wbic16"}

tweets = [t["tweet"] if "tweet" in t else t for t in json.load(open(ARCHIVE))]

stats = {}  # key (lowercase handle) -> dict
def rec(key):
    if key not in stats:
        stats[key] = dict(handle=None, replies=0, mentions=0, contact=0,
                          first=None, last=None, years=set())
    return stats[key]

for tw in tweets:
    dt = datetime.strptime(tw["created_at"], "%a %b %d %H:%M:%S %z %Y")
    date = dt.strftime("%Y-%m-%d")
    reply_to = (tw.get("in_reply_to_screen_name") or "").strip()
    mentions = []
    for m in (tw.get("entities") or {}).get("user_mentions") or []:
        sn = (m.get("screen_name") or "").strip()
        if sn:
            mentions.append(sn)
    contact_keys = {}
    if reply_to:
        contact_keys[reply_to.lower()] = reply_to
    for sn in mentions:
        contact_keys[sn.lower()] = sn
    for key, disp in contact_keys.items():
        if key in SELF:
            continue
        r = rec(key)
        r["handle"] = disp  # keep last-seen display case
        r["contact"] += 1
        if reply_to and reply_to.lower() == key:
            r["replies"] += 1
        if any(sn.lower() == key for sn in mentions):
            r["mentions"] += 1
        if r["first"] is None or date < r["first"]:
            r["first"] = date
        if r["last"] is None or date > r["last"]:
            r["last"] = date
        r["years"].add(dt.year)

# ---- validation against v1 recorded counts (replies, mention-tweets)
EXPECT = {
    "ctzn5": (188, 281), "madeofmistak3": (187, 218), "bitcloud": (174, 310),
    "dakami": (161, 267), "vveeveeanna": (134, 150), "viemccoy": (116, 193),
    "wordgrammer": (106, 138), "prmshra": (106, 152), "mimi10v3": (102, 131),
    "jaivinwylde": (100, 127), "megs_io": (97, 136), "jaelruble": (92, 115),
    "sporadicalia": (88, 119), "heyellieday": (86, 108), "1mortrix": (83, 107),
    "djcows": (83, 90), "eigenhector": (79, 101), "eloffd": (77, 104),
    "ki11switch03": (73, 67), "izzyz": (72, 81),
    "eshear": (50, 76), "grady_booch": (71, 118), "oraiwake" if False else "oraiawake": (None, 51),
}
bad = 0
for key, (er, em) in EXPECT.items():
    r = stats.get(key)
    if r is None:
        print(f"VALIDATION MISS: @{key} not found"); bad += 1; continue
    if er is not None and r["replies"] != er:
        print(f"VALIDATION FAIL @{key}: replies {r['replies']} != expected {er}"); bad += 1
    if em is not None and r["mentions"] != em:
        print(f"VALIDATION FAIL @{key}: mentions {r['mentions']} != expected {em}"); bad += 1
print(f"validation: {'ALL OK' if bad == 0 else f'{bad} failures'}")
if bad:
    sys.exit(1)

rows = sorted(stats.values(), key=lambda r: (-r["contact"], r["handle"].lower()))
with open(OUT, "w") as f:
    f.write("handle\tcontact_points\treplies\tmention_tweets\tfirst_contact\tlast_contact\tyears_active\n")
    for r in rows:
        f.write(f"@{r['handle']}\t{r['contact']}\t{r['replies']}\t{r['mentions']}\t{r['first']}\t{r['last']}\t{len(r['years'])}\n")

over = [r for r in rows if r["contact"] >= 10]
print(f"total accounts seen: {len(rows)}")
print(f"accounts with >= 10 contact points: {len(over)}")
print(f"wrote {OUT}")
