#!/usr/bin/env python3
"""Extract v2 film data: Will's search as a stab sequence.

Stabs = every tweet with in_reply_to_status_id set (exactly 18,762 in the
archive; the findings count). 17,495 carry in_reply_to_screen_name; the rest
are resolved via in_reply_to_user_id_str -> handle harvested from mentions /
named replies across the archive, else left UNIDENTIFIED (failed stab, per
Will's rule: failed stabs don't have to be identified).

Match = target is a mutual follow (accountId in follower.js AND following.js)
OR a measured wavefront person (points.json kinds named/mutual/wbic32).
Match with a placed coordinate -> travels (gold). Match without one (mutual
never placed) -> gold shell spark. Everything else (incl. self-replies and
unidentified) -> pale shell spark at Will's position + seeded offset, deposited
at stab time; Will only MOVES on travel matches.

Output: viz2/data.json
"""
import json, hashlib
from datetime import datetime, timezone

ARCH = "/home/hatch/workspace/twitter-archive"
WAV = "/home/hatch/workspace/wavefront"

def load_js(path):
    s = open(path).read()
    return json.loads(s[s.index("=") + 1:].strip())

followers = {e["follower"]["accountId"] for e in load_js(f"{ARCH}/follower.js")}
following = {e["following"]["accountId"] for e in load_js(f"{ARCH}/following.js")}
mutual_ids = followers & following

points = json.load(open(f"{WAV}/viz/points.json"))
node_by_key = {}
for i, p in enumerate(points):
    if p["key"]:
        # Orai has two entries under one key; travel target = arrival (first)
        node_by_key.setdefault(p["key"], i)
MEASURED = {p["key"] for p in points if p["kind"] in ("named", "mutual", "wbic32") and p["key"]}

tweets = [e["tweet"] for e in json.load(open(f"{ARCH}/tweets.json"))]

# harvest id -> handle from every mention and named reply target
id2handle = {}
for t in tweets:
    for m in t.get("entities", {}).get("user_mentions", []):
        id2handle[m["id_str"]] = m["screen_name"].lower()
    sn, uid = t.get("in_reply_to_screen_name"), t.get("in_reply_to_user_id_str")
    if sn and uid:
        id2handle[uid] = sn.lower()
WILL_ID = None
for t in tweets:
    if (t.get("in_reply_to_screen_name") or "").lower() == "wbic16":
        WILL_ID = t.get("in_reply_to_user_id_str"); break
print("Will's account id:", WILL_ID, "| id2handle size:", len(id2handle))

replies = []
for t in tweets:
    if t.get("in_reply_to_status_id"):
        dt = datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y")
        sn = (t.get("in_reply_to_screen_name") or "").lower() or None
        uid = t.get("in_reply_to_user_id_str")
        if sn is None and uid:
            sn = id2handle.get(uid)
        replies.append(dict(ts=dt.timestamp(), handle=sn, uid=uid))
replies.sort(key=lambda r: r["ts"])
print("total stabs (in_reply_to_status_id set):", len(replies))

rng = __import__("numpy").random.default_rng(20261103)
def shell_offset():
    v = rng.normal(size=3); v /= max(1e-9, (v @ v) ** 0.5)
    return (v * rng.uniform(0.10, 0.30)).tolist()

will_pos = [0.0, 0.0, 0.0]  # centered coords; starts at cube centre (3,3,3)
stabs = []          # per stab: ts, type 0=shell 1=travel 2=gold-shell, node idx or None, spark offset or None, handle
counts = dict(travel=0, gold_shell=0, shell=0, self=0, unidentified=0)
events = {}
brightened = set()
for i, r in enumerate(replies):
    h, uid = r["handle"], r["uid"]
    travel_node = None; typ = 0
    if h is not None and h != "wbic16":
        if h in MEASURED and h in node_by_key:
            typ, travel_node = 1, node_by_key[h]
        elif uid in mutual_ids:
            if h in node_by_key:
                typ, travel_node = 1, node_by_key[h]
            else:
                typ = 2
    if h is not None and h == "wbic16":
        counts["self"] += 1
    if h is None:
        counts["unidentified"] += 1
    if typ == 1:
        counts["travel"] += 1
        brightened.add(travel_node)
        will_pos = [points[travel_node]["xyz"][k] - 3.0 for k in range(3)]
        if "first_match" not in events:
            events["first_match"] = dict(stab=i, handle=h, ym=datetime.fromtimestamp(r["ts"], timezone.utc).strftime("%Y-%m"))
        if h == "wbic32" and "wbic32" not in events and r["ts"] >= datetime(2013, 8, 24, tzinfo=timezone.utc).timestamp():
            events["wbic32"] = dict(stab=i, ym="2013-08")
    elif typ == 2:
        counts["gold_shell"] += 1
    else:
        counts["shell"] += 1
    stabs.append(dict(ts=r["ts"], typ=typ,
                      node=travel_node,
                      off=None if typ == 1 else shell_offset(),
                      at=list(will_pos) if typ != 1 else None,
                      handle=h if typ == 1 else None))
    if typ != 1:
        stabs[-1]["at"] = list(will_pos)

print("counts:", counts, "| sum:", counts["travel"] + counts["gold_shell"] + counts["shell"])
print("events:", events)
print("brightened nodes:", len(brightened))
t0, t1 = replies[0]["ts"], replies[-1]["ts"]
print("span:", datetime.fromtimestamp(t0, timezone.utc), "->", datetime.fromtimestamp(t1, timezone.utc))
orai_n = sum(1 for r in replies if r["handle"] == "oraiawake")
print("archive replies to @OraiAwake:", orai_n)

json.dump(dict(
    t0=t0, t1=t1,
    nodes=[dict(name=p["name"], key=p["key"], kind=p["kind"], region=p["region"],
                xyz=[p["xyz"][k] - 3.0 for k in range(3)]) for p in points],
    stabs=stabs, counts=counts, events=events,
), open(f"{WAV}/viz2/data.json", "w"))
print("wrote viz2/data.json")
