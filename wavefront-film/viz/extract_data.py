#!/usr/bin/env python3
"""Extract visualization points from wavefront.phext (v2.1) + contact-points.tsv.

Output: points.json — one record per phext entry (522 entries, 520 people):
  name, vals[9], proj [x,y,z] (triple means), jittered [x,y,z],
  kind: will | wbic32 | named | mutual | detected
  region: hearth | shoals | open
  appear: "YYYY-MM" first-contact month (Will = origin, present from 2008-06;
          Orai arrival 2025-05 / rupture 2025-06 from the retained record —
          his contact ran off-archive, so the tsv has no row for him)
  contact: archive contact points (0 when not archive-derived)
"""
import csv, json, re, sys, hashlib
sys.path.insert(0, "/home/hatch/workspace/phext")
from parse_phext import parse

WAV = "/home/hatch/workspace/wavefront"
scrolls = dict((c, t) for c, t in parse(f"{WAV}/wavefront.phext"))
index = scrolls["2.2.2/2.2.2/2.2.2"]

contacts = {}
with open(f"{WAV}/contact-points.tsv") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        contacts[row["handle"].lstrip("@").lower()] = row

MUTUALS = {"ctzn5", "madeofmistak3", "bitcloud", "dakami", "vveeveeanna",
           "viemccoy", "wordgrammer", "prmshra", "mimi10v3", "jaivinwylde",
           "megs_io", "jaelruble", "sporadicalia", "heyellieday", "1mortrix",
           "djcows", "eloffd", "ki11switch03", "izzyz"}
NAMED_KEYS = {"eigenhector", "grady_booch", "eshear", "bradmason84"}

LINE = re.compile(r"^(.+?) — (\d(?:\.\d){2}(?:/\d(?:\.\d){2}){2}) — "
                  r"(the Hearth|the Shoals|open water)\b")
HANDLE = re.compile(r"\(@([A-Za-z0-9_]+)\)")

def gate(vals):
    if vals[4] <= 2 and (vals[2] <= 2 or vals[5] <= 2):
        return "shoals"
    if vals[3] >= 4 and vals[4] >= 4 and vals[2] >= 4:
        return "hearth"
    return "open"

def jitter(name, amp):
    h = hashlib.md5(name.encode()).digest()
    return [((h[i] / 255.0) * 2 - 1) * amp for i in range(3)]

points = []
for line in index.splitlines():
    m = LINE.match(line.strip())
    if not m:
        continue
    name, coord, region_txt = m.group(1), m.group(2), m.group(3)
    vals = [int(x) for part in coord.split("/") for x in part.split(".")]
    assert len(vals) == 9, name
    region = {"the Hearth": "hearth", "the Shoals": "shoals"}.get(region_txt, "open")
    assert region == gate(vals), (name, region, gate(vals))

    proj = [sum(vals[0:3]) / 3, sum(vals[3:6]) / 3, sum(vals[6:9]) / 3]
    hm = HANDLE.search(name)
    key = hm.group(1).lower() if hm else (name.lstrip("@").lower() if name.startswith("@") else None)

    if name == "Will Bickford":
        kind, appear, contact = "will", "2008-06", 0
        amp = 0.0
    elif key == "wbic32":
        kind = "wbic32"
        appear = contacts["wbic32"]["first_contact"][:7]
        contact = int(contacts["wbic32"]["contact_points"])
        amp = 0.10
    elif "Orai" in name:
        kind = "named"
        appear = "2025-06" if "rupture" in name else "2025-05"
        contact = 0
        amp = 0.0
    elif key in NAMED_KEYS:
        kind = "named"
        appear = contacts[key]["first_contact"][:7]
        contact = int(contacts[key]["contact_points"])
        amp = 0.05
    elif key in MUTUALS:
        kind = "mutual"
        appear = contacts[key]["first_contact"][:7]
        contact = int(contacts[key]["contact_points"])
        amp = 0.13
    else:
        kind = "detected"
        assert key in contacts, name
        appear = contacts[key]["first_contact"][:7]
        contact = int(contacts[key]["contact_points"])
        amp = 0.34

    j = jitter(name, amp)
    points.append(dict(name=name, key=key, vals=vals, proj=proj,
                       xyz=[proj[i] + j[i] for i in range(3)],
                       kind=kind, region=region, appear=appear, contact=contact))

people = {p["name"] for p in points}
print(f"entries: {len(points)}")
from collections import Counter
print("kinds:", Counter(p["kind"] for p in points))
print("regions:", Counter(p["region"] for p in points))
print("appear range:", min(p["appear"] for p in points), "->", max(p["appear"] for p in points))
for p in points:
    if p["kind"] in ("will", "wbic32", "named"):
        print(f"  {p['name']}: proj={[round(v,2) for v in p['proj']]} appear={p['appear']} region={p['region']}")
assert len(points) == 522, len(points)

with open("/home/hatch/workspace/wavefront/viz/points.json", "w") as f:
    json.dump(points, f, indent=1)
print("wrote points.json")
