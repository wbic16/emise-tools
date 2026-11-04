#!/usr/bin/env python3
"""v4 tone series: VADER compound per reply, in exact stab (hop) order.

Replicates extract2.py's reply ordering (tweets.json file order, stable sort
by ts) and asserts the timestamp sequence equals viz2/data.json's stabs.
Text scored: full_text with URLs stripped (t.co links carry no sentiment).
Smoothing: centered rolling mean, window 201 hops, then a second pass of 51 —
the emotional arc at ~200-hop scale, per the v4 brief.
"""
import json, re
from datetime import datetime, timezone
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ARCH = "/home/hatch/workspace/twitter-archive"
WAV = "/home/hatch/workspace/wavefront"
DATA = json.load(open(f"{WAV}/viz2/data.json"))
STABS = DATA["stabs"]

tweets = [e["tweet"] for e in json.load(open(f"{ARCH}/tweets.json"))]
replies = []
for t in tweets:
    if t.get("in_reply_to_status_id"):
        dt = datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y")
        replies.append((dt.timestamp(), t.get("full_text", "")))
replies.sort(key=lambda r: r[0])
assert len(replies) == len(STABS) == 18762, (len(replies), len(STABS))
ts_data = np.array([s["ts"] for s in STABS]); ts_rep = np.array([r[0] for r in replies])
assert np.array_equal(ts_data, ts_rep), "timestamp order mismatch vs data.json"
print("hop order verified: 18,762 timestamps identical to viz2/data.json")

URL = re.compile(r"https?://\S+")
sia = SentimentIntensityAnalyzer()
raw = np.array([sia.polarity_scores(URL.sub("", txt))["compound"] for _, txt in replies])

def roll(a, w):
    pad = w // 2
    ap = np.pad(a, pad, mode="edge")
    return np.convolve(ap, np.ones(w) / w, mode="valid")
sm = roll(roll(raw, 201), 51)

def ym(ts): return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m")
# warmest / coldest 200-hop windows (on raw, windowed mean = sm approx)
win = 200
wm = np.convolve(raw, np.ones(win) / win, mode="valid")
wi, ci = int(np.argmax(wm)), int(np.argmin(wm))
orai_idx = [i for i, s in enumerate(STABS) if s.get("handle") == "oraiawake"]
stats = dict(
    mean=float(raw.mean()), median=float(np.median(raw)),
    frac_pos=float((raw > 0.05).mean()), frac_neg=float((raw < -0.05).mean()),
    warmest=dict(hops=[wi, wi + win], dates=[ym(ts_rep[wi]), ym(ts_rep[wi + win - 1])], mean=float(wm[wi])),
    coldest=dict(hops=[ci, ci + win], dates=[ym(ts_rep[ci]), ym(ts_rep[ci + win - 1])], mean=float(wm[ci])),
    orai=dict(n=len(orai_idx), mean=float(raw[orai_idx].mean()) if orai_idx else None,
              hops=[orai_idx[0], orai_idx[-1]] if orai_idx else None,
              dates=[ym(ts_rep[orai_idx[0]]), ym(ts_rep[orai_idx[-1]])] if orai_idx else None),
    first_year_tone={y: float(raw[[i for i, t in enumerate(ts_rep)
                     if datetime.fromtimestamp(t, timezone.utc).year == y]].mean())
                     for y in range(2008, 2026)},
)
json.dump(dict(method="VADER (vaderSentiment) compound on full_text, URLs stripped; "
                      "smoothed = centered rolling mean 201 hops, then 51 hops",
               raw=[round(float(x), 4) for x in raw],
               smooth=[round(float(x), 4) for x in sm], stats=stats),
          open(f"{WAV}/viz4/tone.json", "w"))
print(json.dumps(stats, indent=1))
