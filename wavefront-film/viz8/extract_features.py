#!/usr/bin/env python3
"""wavefront-viz v8 — per-hop content features from the reply texts.

Will's v8 direction (2026-11-03 20:49 CST): "use the content of each tweet
to drive improved entropic effects". v2–v7 modulated every hop by VADER
tone only; the words themselves drove nothing. This extractor computes,
for each of the 18,762 hops (replies, in the hop order of viz2/data.json),
a principled feature set from the reply's own text, plus corpus statistics
and the derived signals render8.py maps to entropic effects.

JOIN: viz2/extract2.py built data.json's stab stream by taking every
archive tweet with in_reply_to_status_id set and stable-sorting by parsed
created_at. This script replicates that procedure exactly (same file
order, same parse, same stable sort) and asserts the resulting timestamp
sequence equals data.json's stab ts sequence element-for-element, so
feature row i IS hop i. VADER compound per hop is taken from
viz4/tone.json's raw series (same hop order by construction, len-checked).

TOKENIZATION (for the lexical features): URLs removed; @mentions removed
(they are addresses, not words — they are counted separately); '#'
stripped so hashtags count as the words they carry; tokens are lowercase
[a-z0-9]+('[a-z]+)? sequences.

FEATURES per hop:
  entropy_bits  Shannon entropy of the token distribution, bits
                (0 when fewer than 2 tokens)
  ttr           type-token ratio, unique/total (0 when no tokens)
  ntok, nchar   token count; raw character count of full_text
  caps_ratio    uppercase / all alpha chars (URLs+mentions removed)
  excl_n/ques_n raw '!' / '?' counts; excl_d/ques_d = count per token
  hashtags      entities.hashtags length
  mentions      entities.user_mentions length
  emoji_n       codepoints in U+1F000–1FAFF, U+2600–27BF, U+2B00–2BFF
  vader         VADER compound (viz4/tone.json raw)

NORMALIZATION: each continuous feature is percentile-clipped to its
corpus [p2, p98] and mapped to [0, 1] (suffix n). Percentiles are computed
on this corpus only — no hand-set scales.

DERIVED SIGNALS (all documented in viz8/BUILD-NOTES.md):
  INT   intensity ("shouting") = max(capsn, excln, quesn) per hop
  ent_sm  entropy weather: rolling mean of Hn, window 201 hops, then 51
          (the same two-pass smoothing viz4 used for tone), reflected edges
  hush  per-hop stillness = clip((0.40 - ent_sm_n)/0.30) * clip((tone_smooth
          + 0.02)/0.30): high only where entropy weather is low AND the
          tone is warm — the corpus's quiet, held stretches
  bursts  a hop is a burst when vader <= -0.50 (≈ bottom 5.5% of tone)
          AND INT >= 0.60 (a shouted harsh spike). It is a HARD burst
          when vader <= -0.65 (≈ bottom 1.5%). strength in [0, 1] from
          how far below -0.50 the tone falls (hard bursts floored at 0.85)
  coh   re-coherence envelope: each burst contributes a gaussian rebound
          centred 120 hops (≈21 frames) after it, width 60 hops, weight
          0.5 (soft) / 1.0 (hard); summed and clipped to [0, 1]. This is
          the "stirred" half of shaken-yet-stirred: after every shake the
          field measurably re-settles.

Output: viz8/features.json (per-hop arrays + stats + bursts + hush windows).
The phext data and the archive are only read.
"""
import json, math, re
from collections import Counter
from datetime import datetime
import numpy as np

ARCH = "/home/hatch/workspace/twitter-archive"
WAV = "/home/hatch/workspace/wavefront"
OUT = f"{WAV}/viz8/features.json"

DATA = json.load(open(f"{WAV}/viz2/data.json"))
TONE = json.load(open(f"{WAV}/viz4/tone.json"))
tweets = [e["tweet"] for e in json.load(open(f"{ARCH}/tweets.json"))]

# ---- replicate extract2.py's reply stream exactly; assert the join ----
reps = []
for t in tweets:
    if t.get("in_reply_to_status_id"):
        dt = datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y")
        reps.append((dt.timestamp(), t))
reps.sort(key=lambda r: r[0])
assert len(reps) == len(DATA["stabs"]) == 18762, (len(reps), len(DATA["stabs"]))
ts_join = np.array([r[0] for r in reps])
assert np.array_equal(ts_join, np.array([s["ts"] for s in DATA["stabs"]])), "hop join mismatch"
vader = np.array(TONE["raw"], dtype=np.float64)
tone_sm = np.array(TONE["smooth"], dtype=np.float64)
assert len(vader) == len(reps)
print("join verified: 18,762 hops, ts sequences identical")

URL = re.compile(r"https?://\S+")
MEN = re.compile(r"@\w+")
TOK = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
EMOJI = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")

def tokens_of(text):
    t = URL.sub(" ", text or "")
    t = MEN.sub(" ", t)
    t = t.replace("#", " ")
    return TOK.findall(t.lower())

N = len(reps)
F = {k: np.zeros(N) for k in
     ("entropy_bits", "ttr", "ntok", "nchar", "caps_ratio", "excl_n", "ques_n",
      "excl_d", "ques_d", "hashtags", "mentions", "emoji_n")}
for i, (_, t) in enumerate(reps):
    ft = t.get("full_text") or ""
    tk = tokens_of(ft)
    n = len(tk)
    F["ntok"][i] = n
    F["nchar"][i] = len(ft)
    if n >= 2:
        c = Counter(tk); tot = float(sum(c.values()))
        F["entropy_bits"][i] = -sum((v / tot) * math.log2(v / tot) for v in c.values())
        F["ttr"][i] = len(c) / tot
    elif n == 1:
        F["ttr"][i] = 1.0
    clean = MEN.sub(" ", URL.sub(" ", ft))
    alpha = [ch for ch in clean if ch.isalpha()]
    F["caps_ratio"][i] = (sum(1 for ch in alpha if ch.isupper()) / len(alpha)) if alpha else 0.0
    F["excl_n"][i] = ft.count("!")
    F["ques_n"][i] = ft.count("?")
    F["excl_d"][i] = F["excl_n"][i] / max(1, n)
    F["ques_d"][i] = F["ques_n"][i] / max(1, n)
    ent = t.get("entities", {})
    F["hashtags"][i] = len(ent.get("hashtags", []))
    F["mentions"][i] = len(ent.get("user_mentions", []))
    F["emoji_n"][i] = len(EMOJI.findall(ft))
F["vader"] = vader

def pct(a, ps=(1, 2, 5, 25, 50, 75, 95, 98, 99)):
    return {f"p{p}": round(float(np.percentile(a, p)), 4) for p in ps}

def norm(a):
    lo, hi = np.percentile(a, 2), np.percentile(a, 98)
    return np.clip((a - lo) / max(1e-12, hi - lo), 0.0, 1.0)

NORM = {"Hn": norm(F["entropy_bits"]), "TTRn": norm(F["ttr"]),
        "LENn": norm(F["ntok"]), "CAPSn": norm(F["caps_ratio"]),
        "EXCLn": norm(F["excl_d"]), "QUESn": norm(F["ques_d"])}
INT = np.maximum.reduce([NORM["CAPSn"], NORM["EXCLn"], NORM["QUESn"]])

def smooth2(a, w1=201, w2=51):
    def roll(x, w):
        pad = w // 2
        xp = np.pad(x, pad, mode="reflect")
        return np.convolve(xp, np.ones(w) / w, mode="valid")[:len(x)]
    return roll(roll(a, w1), w2)

ent_sm = smooth2(NORM["Hn"])
ent_sm_n = norm(ent_sm)
hush = np.clip((0.40 - ent_sm_n) / 0.30, 0.0, 1.0) * np.clip((tone_sm + 0.02) / 0.30, 0.0, 1.0)

bursts = []
for i in range(N):
    if vader[i] <= -0.50 and INT[i] >= 0.60:
        hard = bool(vader[i] <= -0.65)
        s = float(np.clip((-vader[i] - 0.50) / 0.35, 0.0, 1.0))
        if hard: s = max(s, 0.85)
        bursts.append(dict(hop=i, strength=round(s, 3), hard=hard,
                           typ=int(DATA["stabs"][i]["typ"]),
                           vader=round(float(vader[i]), 3), inten=round(float(INT[i]), 3)))
coh = np.zeros(N)
for b in bursts:
    c = b["hop"] + 120
    w = 1.0 if b["hard"] else 0.5
    lo, hi = max(0, c - 240), min(N, c + 240)
    x = np.arange(lo, hi)
    coh[lo:hi] += w * np.exp(-((x - c) / 60.0) ** 2)
coh = np.clip(coh, 0.0, 1.0)

# deepest sustained hush window: 600-hop rolling mean, windows fully in-film
cs = np.concatenate([[0.0], np.cumsum(hush)])
roll = (cs[600:] - cs[:-600]) / 600.0
h0 = int(np.argmax(roll))
hush_window = dict(hop0=h0, hop1=h0 + 600, mean_hush=round(float(roll[h0]), 3))
strongest_hard = max((b for b in bursts if b["hard"]), key=lambda b: b["strength"], default=None)

stats = {k: dict(pct(v), mean=round(float(np.mean(v)), 4)) for k, v in F.items()}
stats["INT"] = dict(pct(INT), mean=round(float(np.mean(INT)), 4))
stats["ent_sm_n"] = dict(pct(ent_sm_n), mean=round(float(np.mean(ent_sm_n)), 4))
stats["hush"] = dict(pct(hush), mean=round(float(np.mean(hush)), 4))
stats["coh"] = dict(pct(coh), mean=round(float(np.mean(coh)), 4))

out = dict(
    meta=dict(n_hops=N, join="ts-exact vs viz2/data.json stabs",
              norm="percentile clip [p2, p98] -> [0,1] per feature",
              burst_rule="vader <= -0.50 and INT >= 0.60; hard if vader <= -0.65",
              n_bursts=len(bursts), n_hard=sum(1 for b in bursts if b["hard"]),
              hush_window=hush_window,
              strongest_hard=strongest_hard,
              emoji_hops=int((F["emoji_n"] > 0).sum())),
    stats=stats, bursts=bursts,
    hops={k: [round(float(x), 4) for x in v] for k, v in F.items()},
    norm={k: [round(float(x), 4) for x in v] for k, v in NORM.items()},
    derived=dict(INT=[round(float(x), 4) for x in INT],
                 ent_sm=[round(float(x), 4) for x in ent_sm_n],
                 hush=[round(float(x), 4) for x in hush],
                 coh=[round(float(x), 4) for x in coh]),
)
json.dump(out, open(OUT, "w"))
print(f"wrote {OUT}")
print(f"bursts: {len(bursts)} ({out['meta']['n_hard']} hard) | emoji hops: {out['meta']['emoji_hops']}")
print(f"deepest hush window: hops {hush_window['hop0']}..{hush_window['hop1']} mean hush {hush_window['mean_hush']}")
for k in ("entropy_bits", "ttr", "ntok", "caps_ratio", "excl_d", "INT", "hush", "coh"):
    print(k, stats[k])
