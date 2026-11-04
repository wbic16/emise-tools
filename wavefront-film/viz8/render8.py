#!/usr/bin/env python3
"""wavefront-viz v8 — The Exocortex, Shaken yet Stirred: the content cut.

Built on v7's verified pipeline (viz7/render7.py) with ONE new idea,
Will's v8 direction verbatim (2026-11-03 20:49 CST): "use the content
of each tweet to drive improved entropic effects - apply Mirror Will
to the design process - optimize for emotional impact".

v2–v7 modulated each hop by VADER tone alone; the words drove nothing.
v8 computes per-hop content features from every reply's own text
(viz8/extract_features.py -> viz8/features.json: Shannon entropy, TTR,
length, caps/exclamation/question intensity, hashtags, mentions, emoji,
VADER) and maps them, through documented transfer functions, onto the
field's physics:

  * entropy weather (smoothed lexical entropy) drives the CMB grain's
    turbulence (a boiling shimmer layer), the nodes' epicycle jitter
    and the match arcs' bow and lateral wobble — high-entropy stretches
    of the corpus literally churn;
  * harsh shouted spikes (very negative VADER + high intensity) fire
    scatter bursts at the hop's own position: particles spray out and
    are drawn back in — shaken — and a re-coherence envelope then
    tightens the arcs and warms the gold for ~20 frames — stirred;
  * hush (low entropy weather + warm tone) darkens and stills the
    grain, slows the nodes, and lets individual golden arcs live
    longer and glow stronger, so single arrivals land.

Everything else is v7, carried over unchanged: title treatment, exactly
5 camera revolutions with the 7 world events and captions, CYOA silver
comets, calm Overton base, the right-side film strip with the same
top-20 Most Echoed ranking/texts, strip fades before the CTA, CTA
verbatim, 4K render down-sampled to 1080p, the excluded account never
shown and the dropped region nowhere. The design's taste calls were
made by consulting the Mirror Will materials first (predictions, never
Will's words — see viz8/BUILD-NOTES.md, "Mirror Will consultations").

The full render runs on the ranch node aletheia-core (standing rule,
Will 2026-11-03: heavy work off the Muse substrate); stills and
prototyping run anywhere.
Usage: render8.py --stills | --range A B --out PATH | --full
Env: V8_FONTDIR overrides the DejaVu font directory (ranch render).
"""
import json, math, sys, time, re, html, os
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 3840, 2160, 24          # internal render canvas: 4K
OUT_W, OUT_H = 1920, 1080           # delivered master: down-sampled to 1080p
DS = 3                              # design scale vs v6's 720p canvas
SONG_DUR = 158.400                               # viz5/song_edit.wav
TOTAL_F = int(round(SONG_DUR * FPS))             # 3802 frames = 158.42 s
TITLE_F = 42                                     # hops start here
MAIN_END_F = 3362                                # last hop lands here
PULL_F = 3362                                    # pull-back 3362..3512
CTA_F0 = 3512                                    # CTA fade-in (75 f)
FOCAL = (H / 2) / math.tan(math.radians(21.0))
ROOT = os.environ.get("V8_ROOT", "/home/hatch/workspace")   # ranch render mirrors the tree under V8_ROOT
BASE = f"{ROOT}/wavefront"
DATA = json.load(open(f"{BASE}/viz2/data.json"))
OVER = json.load(open(f"{BASE}/viz3/overton.json"))
TONE = json.load(open(f"{BASE}/viz4/tone.json"))
NODES = DATA["nodes"]; STABS = DATA["stabs"]; T0, T1 = DATA["t0"], DATA["t1"]
N_HOPS = len(STABS)                              # 18,762
N_MATCH = DATA["counts"]["travel"] + DATA["counts"]["gold_shell"]  # 5,963
HPF = N_HOPS / (MAIN_END_F - TITLE_F)            # hops per frame ~5.6512

node_xyz = np.array([n["xyz"] for n in NODES], dtype=np.float64)
CORE = node_xyz.mean(axis=0)
stab_ts = np.array([s["ts"] for s in STABS])

# ---------- node epicycles (kept from v5) ----------
import hashlib
_r_xy = np.linalg.norm(node_xyz[:, :2] - CORE[:2], axis=1)
R_REF = float(np.median(_r_xy))
OMEGA_REF = 2 * math.pi / 9000.0                  # rad/hop at R_REF
OMEGA_NODE = OMEGA_REF * (R_REF / np.maximum(_r_xy, 0.12)) ** 1.5
OMEGA_NODE = np.minimum(OMEGA_NODE, 3.0 * OMEGA_REF)
A_ORB = 0.022                                     # epicycle amplitude (NN spacing med 0.065)
AMP_F = 1.0                                       # v8: per-frame entropy scaling of the epicycles (set in render)
def _node_seed(n): return (n["key"] or n["name"])
PHASE = np.array([int.from_bytes(hashlib.md5(_node_seed(n).encode()).digest()[:8], "little")
                  / 2**64 * 2 * math.pi for n in NODES])
PHASE_Z = np.array([int.from_bytes(hashlib.md5((_node_seed(n) + "·z").encode()).digest()[:8], "little")
                    / 2**64 * 2 * math.pi for n in NODES])
def node_pos_all(hf):
    ph = PHASE + OMEGA_NODE * hf
    off = np.stack([A_ORB * AMP_F * np.cos(ph), A_ORB * AMP_F * np.sin(ph),
                    0.35 * A_ORB * AMP_F * np.sin(0.9 * ph + PHASE_Z)], axis=1)
    return node_xyz + off

def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def hop_float(f):
    if f <= TITLE_F: return 0.0
    if f >= MAIN_END_F: return float(N_HOPS)
    return (f - TITLE_F) * HPF

def node_hop(f):
    hf = hop_float(f)
    if f > MAIN_END_F: hf += (f - MAIN_END_F) * HPF
    return hf

tone_sm = np.array(TONE["smooth"], dtype=np.float64)
_tlo, _thi = np.percentile(tone_sm, 5), np.percentile(tone_sm, 95)
def tone_norm(h):
    return float(min(1.0, max(0.0, (tone_sm[int(min(h, N_HOPS - 1))] - _tlo) / max(1e-9, _thi - _tlo))))
GOLD_PALE = np.array([214.0, 194.0, 156.0]); GOLD_DEEP = np.array([255.0, 172.0, 48.0])
def gold_rgb(h, bright=1.0):
    c = GOLD_PALE + (GOLD_DEEP - GOLD_PALE) * tone_norm(h)
    return tuple(int(min(255, x * bright)) for x in c)

# ---------- v8 content features: the words themselves (extract_features.py) ----------
FEAT = json.load(open(f"{BASE}/viz8/features.json"))
HN_HOP = np.array(FEAT["norm"]["Hn"], dtype=np.float64)        # per-hop lexical entropy, 0..1
ENT_SM = np.array(FEAT["derived"]["ent_sm"], dtype=np.float64)  # entropy weather (smoothed)
HUSH_HOP = np.array(FEAT["derived"]["hush"], dtype=np.float64)   # per-hop stillness
COH_HOP = np.array(FEAT["derived"]["coh"], dtype=np.float64)     # re-coherence envelope
assert len(HN_HOP) == N_HOPS
BURSTS = FEAT["bursts"]
for _b in BURSTS:
    _b["frame"] = TITLE_F + _b["hop"] / HPF
    _rng_b = np.random.default_rng(77000 + _b["hop"])
    _n = 30 if _b["hard"] else 12
    _d = _rng_b.normal(size=(_n, 3)); _d /= np.linalg.norm(_d, axis=1, keepdims=True)
    _b["dirs"] = _d
    _b["spd"] = (0.010 + 0.030 * _b["strength"]) * (0.45 + 0.55 * _rng_b.random(_n))
    _b["life"] = 26.0 if _b["hard"] else 16.0
print(f"features: {len(BURSTS)} bursts ({sum(1 for b in BURSTS if b['hard'])} hard), "
      f"hush window hops {FEAT['meta']['hush_window']['hop0']}..{FEAT['meta']['hush_window']['hop1']}", flush=True)
def sig_at(arr, h):
    h = min(max(float(h), 0.0), N_HOPS - 1.001)
    i = int(h); t = h - i
    return float(arr[i] * (1.0 - t) + arr[i + 1] * t)

import os
_FONTDIR = os.environ.get("V8_FONTDIR")
if _FONTDIR:
    FONT = _FONTDIR.rstrip("/") + "/"
else:
    import matplotlib
    FONT = os.path.join(matplotlib.get_data_path(), "fonts", "ttf") + "/"
F_TITLE = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 168)
F_OBL   = ImageFont.truetype(FONT + "DejaVuSans-Oblique.ttf", 81)
F_SUB   = ImageFont.truetype(FONT + "DejaVuSans.ttf", 72)
F_CALL  = ImageFont.truetype(FONT + "DejaVuSans.ttf", 54)
F_CARD  = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 90)
F_BIG   = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 132)
F_EVENT = ImageFont.truetype(FONT + "DejaVuSans.ttf", 60)
F_SHDR  = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 42)
F_SSUB  = ImageFont.truetype(FONT + "DejaVuSans.ttf", 27)
F_CELLH = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 40)
F_CELLT = ImageFont.truetype(FONT + "DejaVuSans.ttf", 57)
F_CELLF = ImageFont.truetype(FONT + "DejaVuSans.ttf", 42)

_dummy = ImageDraw.Draw(Image.new("RGB", (8, 8)))
def spaced_width(text, font, tracking):
    return sum(_dummy.textlength(ch, font=font) for ch in text) + tracking * max(0, len(text) - 1)
def draw_spaced(dr, cx, y, text, font, fill, tracking=6):
    x = cx - spaced_width(text, font, tracking) / 2
    for ch in text:
        dr.text((x, y), ch, font=font, fill=fill)
        x += _dummy.textlength(ch, font=font) + tracking
def draw_spaced_left(dr, x, y, text, font, fill, tracking=4):
    for ch in text:
        dr.text((x, y), ch, font=font, fill=fill)
        x += _dummy.textlength(ch, font=font) + tracking
def center_text(dr, cx, y, text, font, fill):
    w = dr.textlength(text, font=font); dr.text((cx - w / 2, y), text, font=font, fill=fill)

# ---------- Overton drift, subtle, in hop time (calm v4 base warp) ----------
OV = []
for m in OVER["milestones"]:
    ts = datetime.strptime(m["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
    hop_m = float(np.searchsorted(stab_ts, ts))
    OV.append(dict(hop=hop_m, delta=np.array(m["delta"], dtype=np.float64) * OVER["delta_scale"] * 0.35))
def drift_at(hop):
    c = np.zeros(3)
    for e in OV:
        c += e["delta"] * smooth(e["hop"] - 150, e["hop"] + 150, hop)
    return c
SIGMA2 = 2 * 1.5 ** 2

# ---------- world events: motion fine-tuning + lower-thirds ----------
# (date, caption name, angular-velocity amp, radial amp)
# surge (+) = the world speeds up / camera pushes in; hush (-) = it slows / pulls back
EVENTS_DEF = [
    ("2016-11-08", "US PRESIDENTIAL ELECTION", +0.45, -0.04),
    ("2020-03-11", "COVID-19 PANDEMIC DECLARED", -0.65, +0.10),
    ("2022-02-24", "RUSSIA INVADES UKRAINE", -0.55, +0.09),
    ("2022-11-30", "CHATGPT LAUNCHES", +0.95, -0.08),
    ("2023-03-14", "GPT-4 RELEASED", +0.60, -0.06),
    ("2023-07-24", "TWITTER BECOMES X", +0.35, -0.04),
    ("2024-11-05", "US PRESIDENTIAL ELECTION", +0.50, -0.05),
]
EVENTS = []
for date, name, vamp, ramp in EVENTS_DEF:
    ts = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
    hop = float(np.searchsorted(stab_ts, ts))     # first reply at/after the event
    EVENTS.append(dict(date=date, name=name, caption=f"{name} · {date[:4]}",
                       hop=hop, frame=TITLE_F + hop / HPF, vamp=vamp, ramp=ramp))
# caption schedule: queued so lower-thirds never collide (motion never moves)
CAP_LEN, CAP_GAP = 104, 14
_prev_end = -10**9
for e in EVENTS:
    e["cap_start"] = max(e["frame"] - 8, _prev_end + CAP_GAP)
    e["cap_end"] = e["cap_start"] + CAP_LEN
    _prev_end = e["cap_end"]

# ---------- camera azimuth: exactly REVS revolutions, event-modulated ----------
REVS = 5
_fax = np.arange(TOTAL_F, dtype=np.float64)
def _smooth_np(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)
_w0 = 0.30 + 0.70 * _smooth_np(0, 240, _fax)                    # gentle spin-up out of the title
_w0 = _w0 * (1.0 - 0.45 * _smooth_np(PULL_F, CTA_F0, _fax))    # settle for the reveal
_mult = np.ones(TOTAL_F)
RADM = np.ones(TOTAL_F)
for e in EVENTS:
    _mult *= (1.0 + e["vamp"] * np.exp(-((_fax - e["frame"]) / 60.0) ** 2))
    RADM += e["ramp"] * np.exp(-((_fax - e["frame"]) / 70.0) ** 2)
_cum = np.cumsum(_w0 * _mult)
AZIM6 = 2 * math.pi * REVS * _cum / _cum[-1]
REVS_REAL = float((AZIM6[-1] - AZIM6[0]) / (2 * math.pi))
print(f"azimuth: {REVS_REAL:.4f} revolutions total ({REVS_REAL*360:.1f} deg)", flush=True)
for e in EVENTS:
    print(f"event {e['date']} {e['name']}: hop {e['hop']:.0f} frame {e['frame']:.0f} "
          f"vamp {e['vamp']:+.2f} ramp {e['ramp']:+.2f} caption {e['cap_start']:.0f}..{e['cap_end']:.0f}", flush=True)

# ---------- CYOA thread: silver comets through the same space ----------
TRAV = json.load(open(f"{ROOT}/phext/traversal-map/cyoa-traversal.json"))
CYOA_N = len(TRAV["nodes"])                                   # 829 placed scrolls
cy_vals = np.array([[float(x) for part in n["coord"].split("/") for x in part.split(".")]
                    for n in TRAV["nodes"]], dtype=np.float64)
# SAME 9D->3D projection as the wavefront nodes (viz/extract_data.py: triple means)
cy_proj = np.stack([cy_vals[:, 0:3].mean(1), cy_vals[:, 3:6].mean(1), cy_vals[:, 6:9].mean(1)], axis=1)
# CYOA's coordinate range dwarfs the wavefront cube (components to 999), so the
# projected cloud is fit per-axis into the wavefront field extent (robust clip)
_lo = np.percentile(cy_proj, 0.5, axis=0); _hi = np.percentile(cy_proj, 99.5, axis=0)
_nlo = node_xyz.min(0); _nhi = node_xyz.max(0)
_cen = (_nlo + _nhi) / 2; _half = (_nhi - _nlo) / 2 * 1.08; _nlo, _nhi = _cen - _half, _cen + _half
CY = _nlo + (np.clip(cy_proj, _lo, _hi) - _lo) / (_hi - _lo) * (_nhi - _nlo)

def catmull_rom(p0, p1, p2, p3, t, tension=0.0):
    # Hermite form of Catmull-Rom. tension > 0 scales both tangents down,
    # loosening the curve into a more liquid sweep; tension = 0 is standard CR.
    t2, t3 = t * t, t * t * t
    m1 = 0.5 * (1.0 - tension) * (p2 - p0)
    m2 = 0.5 * (1.0 - tension) * (p3 - p1)
    return ((2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1
            + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2)
# comet path: Catmull-Rom through the projected trace, arc-length parametrised
_ext = np.vstack([CY[0], CY, CY[-1]])
_path = []
for _i in range(len(CY) - 1):
    for _j in range(2):
        _path.append(catmull_rom(_ext[_i], _ext[_i + 1], _ext[_i + 2], _ext[_i + 3], _j / 2))
_path.append(CY[-1])
PATH = np.array(_path)
_seg = np.linalg.norm(np.diff(PATH, axis=0), axis=1)
CUM = np.concatenate([[0.0], np.cumsum(_seg)]); TLEN = float(CUM[-1])
def path_at(s):
    s = min(max(s, 0.0), TLEN - 1e-9)
    i = int(np.searchsorted(CUM, s)) - 1
    t = (s - CUM[i]) / max(1e-9, CUM[i + 1] - CUM[i])
    return PATH[i] * (1 - t) + PATH[i + 1] * t
COMETS = [dict(loops=L, phase=i / 7.0) for i, L in
          enumerate([1.7, 2.3, 2.9, 3.4, 2.0, 2.6, 3.1])]
TAIL_FRAC = 0.014 * TLEN
print(f"cyoa: {CYOA_N} scrolls, path length {TLEN:.2f} world units, {len(COMETS)} comets", flush=True)

# ---------- top 20 posts (fallback metric: favourites + retweets) ----------
ARCHIVE = f"{ROOT}/twitter-archive/tweets.json"
def sanitize(text):
    t = html.unescape(text or "")
    t = re.sub(r"https?://\S+", "", t)
    t = "".join(ch for ch in t if ord(ch) < 0x1F000 and ch not in "️‍")
    return re.sub(r"\s+", " ", t).strip()
def wrap(text, font, maxw, maxlines):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if _dummy.textlength(trial, font=font) <= maxw: cur = trial
        else:
            if cur: lines.append(cur)
            cur = wd
        if len(lines) == maxlines: break
    if len(lines) < maxlines and cur: lines.append(cur)
    if len(lines) == maxlines:
        joined = " ".join(lines)
        if len(joined) < len(text):
            lines[-1] = lines[-1].rstrip(" ,;:") + "…"
    return lines
_tweets = [t["tweet"] if "tweet" in t else t for t in json.load(open(ARCHIVE))]
_pool = []
for _t in _tweets:
    if _t.get("in_reply_to_status_id"): continue
    _ft = _t.get("full_text") or ""
    if _ft.startswith("RT @") or _ft.startswith("@"): continue
    _dt = datetime.strptime(_t["created_at"], "%a %b %d %H:%M:%S %z %Y")
    _fav, _rt = int(_t["favorite_count"]), int(_t["retweet_count"])
    _pool.append(dict(ts=_dt.timestamp(), date=_dt.strftime("%Y-%m-%d"),
                      label=f"{_dt.day} {_dt:%b %Y}", fav=_fav, rt=_rt,
                      echo=_fav + _rt, text=sanitize(_ft)))
_pool.sort(key=lambda o: (-o["echo"], -o["fav"], o["ts"]))
TOP20 = _pool[:20]
for _r, _o in enumerate(TOP20, 1): _o["rank"] = _r
TOP20.sort(key=lambda o: o["ts"])                              # arrival order
for _o in TOP20:
    _o["hop"] = float(np.searchsorted(stab_ts, _o["ts"]))
    _o["arr_frame"] = TITLE_F + _o["hop"] / HPF
    _o["lines"] = wrap(_o["text"], F_CELLT, 600, 4)
for _o in TOP20:
    print(f"strip rank {_o['rank']:2d} {_o['date']} echo {_o['echo']:3d} hop {_o['hop']:6.0f} "
          f"arrival frame {_o['arr_frame']:6.0f} | {_o['text'][:60]}", flush=True)
assert TOP20[-1]["arr_frame"] < MAIN_END_F, "last post arrives after the hops end"

# ---------- film strip: the top 20 flow along the right side ----------
STRIP_W = 800                                   # 20.8% of the 3840 canvas
STRIP_X0 = W - STRIP_W
CELL_PITCH, CELL_H, CELL_TOP0 = 496, 462, 196
ARR_F = np.array([o["arr_frame"] for o in TOP20])
_TGT = np.maximum(0.0, np.arange(len(TOP20)) * CELL_PITCH + CELL_TOP0 + CELL_H - (H - 48))
_DT = np.diff(np.concatenate([[0.0], _TGT]))
def strip_offset(f):
    # each arrival eases the strip up by its share of a cell pitch, so the
    # newest frame settles with its foot at the bottom of the strip; the
    # strip absorbs bunched arrivals with no queueing (unlike v6's cards)
    return float(np.sum(_DT * np.array([smooth(a, a + 26, f) for a in ARR_F])))
def strip_alpha(f):
    return 1.0 - smooth(CTA_F0, CTA_F0 + 75, f)   # gone before the CTA text
def draw_strip(dr, f):
    sa = strip_alpha(f)
    if sa <= 0.003: return
    # dark-glass panel, luminous cyan left edge
    dr.rectangle([STRIP_X0, 0, W, H], fill=(5, 8, 14, int(168 * sa)))
    dr.line([STRIP_X0, 0, STRIP_X0, H], fill=(120, 220, 240, int(150 * sa)), width=3)
    dr.line([STRIP_X0 + 6, 0, STRIP_X0 + 6, H], fill=(120, 220, 240, int(36 * sa)), width=2)
    # sprocket perforations down both edges of the strip
    for yy in range(30, H - 40, 72):
        for xx in (STRIP_X0 + 22, W - 58):
            dr.rounded_rectangle([xx, yy, xx + 30, yy + 20], radius=6,
                                 fill=(160, 200, 220, int(46 * sa)))
    # cells: one film frame per post, flowing upward as arrivals land
    off = strip_offset(f)
    for i, o in enumerate(TOP20):
        if f < o["arr_frame"]: continue
        y = CELL_TOP0 + i * CELL_PITCH - off
        if y < -CELL_H or y > H: continue
        a_in = min((f - o["arr_frame"]) / 12.0, 1.0)
        newest = (f - o["arr_frame"]) < 34
        edge = int((205 if newest else 120) * sa * a_in)
        dr.rounded_rectangle([STRIP_X0 + 74, y, W - 84, y + CELL_H], radius=18,
                             fill=(10, 16, 26, int(205 * sa * a_in)),
                             outline=(140, 215, 235, edge), width=3)
        tx = STRIP_X0 + 96
        dr.text((tx, y + 24), o["label"], font=F_CELLH,
                fill=(206, 228, 240, int(240 * sa * a_in)))
        rk = f"no. {o['rank']} of 20"
        rw = dr.textlength(rk, font=F_CELLF)
        dr.text((W - 84 - 22 - rw, y + 26), rk, font=F_CELLF,
                fill=(150, 178, 200, int(220 * sa * a_in)))
        for li, ln in enumerate(o["lines"]):
            dr.text((tx, y + 92 + li * 74), ln, font=F_CELLT,
                    fill=(238, 244, 248, int(248 * sa * a_in)))
        dr.text((tx, y + CELL_H - 56), f"{o['echo']} echoes", font=F_CELLF,
                fill=(168, 196, 214, int(230 * sa * a_in)))
    # masthead LAST, on a near-opaque band: exiting cells slide under it
    dr.rectangle([STRIP_X0, 0, W, 180], fill=(5, 8, 14, int(245 * sa)))
    dr.line([STRIP_X0, 0, STRIP_X0, 180], fill=(120, 220, 240, int(150 * sa)), width=3)
    draw_spaced_left(dr, STRIP_X0 + 96, 54, "MOST ECHOED", F_SHDR,
                     (214, 236, 246, int(245 * sa)), 12)
    dr.text((STRIP_X0 + 96, 112), "ranked by favourites + retweets", font=F_SSUB,
            fill=(150, 182, 202, int(215 * sa)))
    dr.line([STRIP_X0 + 96, 162, W - 96, 162], fill=(120, 220, 240, int(90 * sa)), width=2)

# ---------- walk the hops once: landings, counters, callouts ----------
node_idx_by_key = {}
for i, n in enumerate(NODES):
    node_idx_by_key.setdefault(n["key"], i)
# v7 (Will): the excluded account is NEVER shown. Both of its placed nodes
# are dropped from rendering entirely — no node, no arc landing on them,
# no callout. Its replies remain in the aggregate hop stream / CMB counts
# (they are attempts, not a presence). This also removes the only two
# nodes that carried the dropped region's coding.
EXCLUDE = {i for i, n in enumerate(NODES) if n["key"] == "oraiawake"}
assert len(EXCLUDE) == 2, EXCLUDE

land_pos, land_hop = [], []
attempts_at = np.zeros(N_HOPS + 1, dtype=int)
matches_at = np.zeros(N_HOPS + 1, dtype=int)
placed_at = np.zeros(N_HOPS + 1, dtype=int)
callouts = []                        # (hop, text, color)
seen_handles = set()
will = np.zeros(3); mat = 0; landed_nodes = set()
for h, s in enumerate(STABS):
    if s["typ"] in (1, 2):
        mat += 1
        tgt = node_pos_all(float(h))[s["node"]] if s["typ"] == 1 else np.array(s["at"]) + np.array(s["off"])
        land_pos.append(tgt.copy()); land_hop.append(h)
        will = tgt.copy()
        if s["typ"] == 1:
            landed_nodes.add(s["node"])
    attempts_at[h + 1] = h + 1; matches_at[h + 1] = mat; placed_at[h + 1] = len(landed_nodes)
    hd = s.get("handle")
    if s["typ"] == 1 and hd and hd not in seen_handles:
        seen_handles.add(hd)
        if hd == "abednegojones": callouts.append((h, "@abednegojones", (235, 226, 205)))
        elif hd == "wbic32":      callouts.append((h, "@wbic32", (200, 225, 215)))
        elif hd == "eshear":      callouts.append((h, "@eshear", (235, 226, 205)))
        elif hd == "grady_booch": callouts.append((h, "@Grady_Booch", (235, 226, 205)))
        elif hd == "eigenhector": callouts.append((h, "@eigenhector", (235, 226, 205)))
callouts.sort()
assert mat == N_MATCH and attempts_at[-1] == N_HOPS, (mat, attempts_at[-1])
print(f"prep: landings={len(land_pos)} placed_final={placed_at[-1]} callouts={len(callouts)}", flush=True)

# v7 audit: no on-screen string may name the excluded account or the dropped region
_ALL_TEXT = ([c[1] for c in callouts] + [e["caption"] for e in EVENTS]
             + [o["text"] for o in TOP20]
             + ["THE EXOCORTEX", "Shaken yet Stirred", "a map of alignment",
                "the future has arrived", "MOST ECHOED",
                "ranked by favourites + retweets",
                "520 people are already in this map.",
                "Find your coordinate. Claim your space.", "edit.phext.io",
                "Not in the map yet? The door is open."])
assert all("orai" not in t.lower() for t in _ALL_TEXT), "excluded account leaks into on-screen text"
assert all("shoals" not in t.lower() for t in _ALL_TEXT), "dropped region leaks into on-screen text"
print(f"audit: {len(_ALL_TEXT)} on-screen strings clean; excluded nodes {sorted(EXCLUDE)}", flush=True)

# ---------- golden spline through the landings ----------
CP = np.array(land_pos); CB = np.array(land_hop, dtype=np.float64)
SUB = 4
verts, vhop = [], []
ext = np.vstack([CP[0], CP, CP[-1]])
for i in range(len(CP) - 1):
    for j in range(SUB):
        t = j / SUB
        verts.append(catmull_rom(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], t, tension=0.18))
        vhop.append(CB[i] * (1 - t) + CB[i + 1] * t)
verts.append(CP[-1]); vhop.append(CB[-1])
V = np.array(verts); VH = np.array(vhop)
VCOL = np.array([GOLD_PALE + (GOLD_DEEP - GOLD_PALE) * tone_norm(h) for h in VH])
def spline_pos_at_hop(h):
    if h <= VH[0]: return V[0].copy()
    if h >= VH[-1]: return V[-1].copy()
    i = int(np.searchsorted(VH, h)) - 1
    t = (h - VH[i]) / max(1e-9, VH[i + 1] - VH[i])
    return V[i] * (1 - t) + V[i + 1] * t

# ---------- world transform: warp -> rotate -> breathe, all about CORE ----------
def theta(f):
    return math.radians(10.0) * smooth(TITLE_F, MAIN_END_F, f) + math.radians(2.0) * smooth(PULL_F, CTA_F0, f)
def to_world(pts, f, hop):
    pts = np.atleast_2d(np.asarray(pts, dtype=np.float64))
    c = drift_at(hop)
    if np.any(c):
        d2 = np.sum((pts - c) ** 2, axis=-1, keepdims=True)
        pts = pts + c * np.exp(-d2 / SIGMA2)
    th = theta(f); co, si = math.cos(th), math.sin(th)
    q = pts - CORE
    out = np.stack([co * q[:, 0] - si * q[:, 1], si * q[:, 0] + co * q[:, 1], q[:, 2]], axis=1)
    breathe = 1.0 + 0.02 * math.sin(2 * math.pi * (f - TITLE_F) / (FPS * 45.0) + 0.7)
    return out * breathe + CORE

# ---------- camera: analytic, precomputed, heavily smoothed ----------
HEAD = np.array([to_world(spline_pos_at_hop(hop_float(f)), f, hop_float(f))[0] for f in range(TOTAL_F)])
_look = 0.62 * CORE + 0.38 * HEAD
LOOK = np.zeros_like(_look); acc = _look[0].copy()
for f in range(TOTAL_F):
    acc = acc + 0.03 * (_look[f] - acc); LOOK[f] = acc
def camera(f):
    hop = hop_float(f)
    pull = smooth(PULL_F, CTA_F0, f)
    R = 2.225 * (1.0 + 0.035 * math.sin(2 * math.pi * (f - TITLE_F) / (FPS * 45.0)))  # 2x zoom
    R = R * float(RADM[f])                                # world events pulse the radius
    R = R * (1 - pull) + 6.8 * pull                       # pull-back reveals the field
    az = 2.45 + float(AZIM6[f])                           # several full revolutions, event-tuned
    el = math.radians(23.0 * (1 - pull) + 19.0 * pull)
    pos = CORE + R * np.array([math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)])
    look = LOOK[f] * (1 - pull) + CORE * pull
    fwd = look - pos; fwd = fwd / np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0]); rn = np.linalg.norm(right)
    right = right / rn if rn > 1e-6 else np.array([1.0, 0.0, 0.0])
    up = np.cross(right, fwd)
    return pos, right, up, fwd

def project(pts, cam):
    pos, right, up, fwd = cam
    d = np.atleast_2d(pts) - pos
    xc = d @ right; yc = d @ up; zc = d @ fwd
    ok = zc > 0.25
    zsafe = np.where(ok, zc, 1.0)
    return CX_CUR + FOCAL * xc / zsafe, H / 2 - FOCAL * yc / zsafe, zc, ok

def kernel(n, sigma):
    ax = np.arange(n) - n // 2
    g = np.exp(-(ax[:, None] ** 2 + ax[None, :] ** 2) / (2 * sigma * sigma))
    return (g / g.max()).astype(np.float32)
K_BASE, K_BRIGHT, K_MARK = kernel(27, 4.8), kernel(45, 7.8), kernel(75, 12.6)
K_CORE, K_HALO = kernel(183, 33.0), kernel(363, 72.0)

def stamp(buf, sx, sy, kern, color, gain):
    n = kern.shape[0]; r = n // 2
    x0, y0 = int(round(sx)) - r, int(round(sy)) - r
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + n), min(H, y0 + n)
    if xa >= xb or ya >= yb: return
    k = kern[ya - y0: ya - y0 + (yb - ya), xa - x0: xa - x0 + (xb - xa)]
    buf[ya:yb, xa:xb] += k[:, :, None] * (np.array(color, dtype=np.float32) * gain)

CX_CUR = W / 2   # projection centre for the current frame (set per-frame in render)

# ---------- CMB background: mottled afterglow of the misses ----------
_rng = np.random.default_rng(20261103)
def noise_field(sw, sh):
    a = _rng.normal(size=(sh, sw)).astype(np.float32)
    im = Image.fromarray(((a - a.min()) / np.ptp(a) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255.0
_int = 0.55 * noise_field(24, 14) + 0.30 * noise_field(48, 27) + 0.15 * noise_field(96, 54)
_int = (_int - _int.min()) / np.ptp(_int)
_tmp = noise_field(20, 12) * 0.7 + noise_field(40, 23) * 0.3
_tmp = (_tmp - _tmp.min()) / np.ptp(_tmp)
warm = np.array([1.00, 0.84, 0.58], dtype=np.float32); cool = np.array([0.62, 0.78, 1.00], dtype=np.float32)
tint = cool[None, None, :] * (1 - _tmp[:, :, None]) + warm[None, None, :] * _tmp[:, :, None]
CMB = ((0.18 + 0.82 * _int ** 1.15)[:, :, None] * tint * 34.0).astype(np.float32)
# v8 boil layer: six mottled fields the renderer cross-fades through at a
# rate set by the entropy weather — the grain visibly churns in the
# corpus's high-entropy stretches and settles in its quiet ones
_boil = []
for _k in range(6):
    _bf = 0.6 * noise_field(24, 14) + 0.4 * noise_field(48, 27)
    _boil.append((_bf - _bf.min()) / np.ptp(_bf))
BOIL = np.stack(_boil).astype(np.float32)
BASE_BG = np.array([2.0, 3.0, 7.0], dtype=np.float32)   # deeper future-tech black
STARS_X = _rng.uniform(0, W, 380); STARS_Y = _rng.uniform(0, H, 380); STARS_B = _rng.uniform(5, 20, 380)
cum_miss = attempts_at - matches_at
miss_gain = cum_miss / max(1, cum_miss[-1])

NODE_BASE = {"detected": ((104, 124, 160), 0.24), "mutual": ((132, 158, 198), 0.34),
             "named": ((158, 184, 218), 0.36), "wbic32": ((134, 188, 174), 0.36),
             "will": ((255, 190, 70), 0.8)}
def node_color(n):
    return NODE_BASE[n["kind"]][0]

def bezier_arc(p0, p1, cam, u_max=1.0, n=18):
    chord = p1 - p0; L = np.linalg.norm(chord)
    if L < 1e-6: return None
    perp = np.cross(chord / L, cam[3]); nn = np.linalg.norm(perp)
    perp = perp / nn if nn > 1e-4 else np.array([0.0, 0.0, 1.0])
    ctrl = (p0 + p1) / 2 + perp * (0.22 * L + 0.045)   # taller, more fluid sweep (v7)
    ts = np.linspace(0, u_max, max(2, int(n * u_max) + 1))
    return ((1 - ts) ** 2)[:, None] * p0 + (2 * (1 - ts) * ts)[:, None] * ctrl + (ts ** 2)[:, None] * p1

def bezier_arc8(p0, p1, cam, u_max, bow_scale, jit_mag):
    """v8 arc: bow and lateral wobble driven by the landing tweet's own
    lexical entropy. bow_scale ~1 at median entropy; jit_mag is a signed
    lateral offset (world units) applied at the control point along the
    chord's second perpendicular — the arc leans sideways as it bows."""
    chord = p1 - p0; L = np.linalg.norm(chord)
    if L < 1e-6: return None
    perp = np.cross(chord / L, cam[3]); nn = np.linalg.norm(perp)
    perp = perp / nn if nn > 1e-4 else np.array([0.0, 0.0, 1.0])
    perp2 = np.cross(chord / L, perp); n2 = np.linalg.norm(perp2)
    perp2 = perp2 / n2 if n2 > 1e-4 else np.array([0.0, 0.0, 1.0])
    ctrl = (p0 + p1) / 2 + perp * ((0.22 * L + 0.045) * bow_scale) + perp2 * jit_mag
    ts = np.linspace(0, u_max, max(2, int(18 * u_max) + 1))
    return ((1 - ts) ** 2)[:, None] * p0 + (2 * (1 - ts) * ts)[:, None] * ctrl + (ts ** 2)[:, None] * p1

land_frame = np.array([TITLE_F + h / HPF for h in land_hop])
NODE_FIRST_HOP = np.full(len(NODES), 10**9, dtype=int)
for _j, _h in enumerate(land_hop):
    _s = STABS[_h]
    if _s["typ"] == 1 and _h < NODE_FIRST_HOP[_s["node"]]:
        NODE_FIRST_HOP[_s["node"]] = _h
land_prev = np.vstack([np.zeros(3), CP[:-1]])
land_toneb = np.array([0.72 + 0.5 * tone_norm(h) for h in land_hop])
# v8: per-landing content — entropy of the tweet that landed, and a seeded
# lateral jitter sign/magnitude source (deterministic across render hosts)
HN_LAND = np.array([HN_HOP[h] for h in land_hop])
JIT_LAND = np.array([(int.from_bytes(hashlib.md5(f"jit{h}".encode()).digest()[:8], "little")
                      / 2**64) * 2.0 - 1.0 for h in land_hop])

SILVER = (206, 218, 236); SILVER_HEAD = (240, 246, 252); SILVER_DIM = (168, 182, 205)

def comet_state(f):
    """Per comet: (tail->head base-space points, fade) at frame f."""
    prog = f / TOTAL_F
    out = []
    for c in COMETS:
        sfrac = (prog * c["loops"] + c["phase"]) % 1.0
        fade = float(min(sfrac / 0.012, (1.0 - sfrac) / 0.012, 1.0))
        head_s = sfrac * TLEN
        nseg = 26
        pts = np.array([path_at(head_s - TAIL_FRAC * (k / nseg)) for k in range(nseg, -1, -1)])
        out.append((pts, fade))
    return out

def render(f):
    global CX_CUR, AMP_F
    # the field centre excludes the film strip; it eases back to the frame
    # centre as the strip fades out for the CTA
    CX_CUR = (STRIP_X0 / 2) + (W / 2 - STRIP_X0 / 2) * smooth(PULL_F, CTA_F0, f)
    hop = hop_float(f)
    hi = int(min(N_HOPS, math.floor(hop)))
    # v8 content weather at this frame, sampled from the per-hop signals
    ENT_F = sig_at(ENT_SM, hop); HUSH_F = sig_at(HUSH_HOP, hop); COH_F = sig_at(COH_HOP, hop)
    AMP_F = (0.75 + 0.80 * ENT_F) * (1.0 - 0.30 * HUSH_F)
    HARD_NOW = any(b["hard"] and 0.0 <= f - b["frame"] < 8.0 for b in BURSTS)
    cam = camera(f)
    # --- background: space + CMB afterglow (gain grows with cumulative misses;
    #     entropy weather churns it, hush stills it)
    gain = (0.30 + 0.70 * float(miss_gain[hi])) * (1.0 + 0.35 * ENT_F) * (1.0 - 0.30 * HUSH_F)
    arr = BASE_BG[None, None, :] + CMB * gain
    # v8 boil: cross-fade the mottled fields at an entropy-set rate
    _ph = f * (0.30 + 2.4 * ENT_F); _i0 = int(_ph) % 6; _fr = _ph - int(_ph)
    _boil_f = BOIL[_i0] * (1.0 - _fr) + BOIL[(_i0 + 1) % 6] * _fr
    _amp = (6.0 + 55.0 * ENT_F) * (1.0 - 0.65 * HUSH_F) * (1.0 - 0.35 * COH_F)
    arr = arr + ((_boil_f - 0.5) * _amp)[:, :, None] * warm[None, None, :]
    flat = arr.reshape(-1, 3)
    _sx = np.minimum(STARS_X.astype(int), W - 2); _sy = np.minimum(STARS_Y.astype(int), H - 2)
    _sv = np.stack([STARS_B, STARS_B, STARS_B * 1.1], axis=1).astype(np.float32)
    for _dx, _dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        np.add.at(flat, ((_sy + _dy) * W + (_sx + _dx)), _sv)
    arr = flat.reshape(H, W, 3)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    arr = np.asarray(img).astype(np.float32)
    # --- nodes (on their own orbits; v8 captures the live positions once,
    #     epicycles already entropy-scaled through AMP_F)
    POS_NOW = node_pos_all(node_hop(f))
    nodes_w = to_world(POS_NOW, f, hop)
    nsx, nsy, nzc, nok = project(nodes_w, cam)
    k = int(np.searchsorted(land_hop, hi, side="right"))
    landed = NODE_FIRST_HOP <= hi
    for i, n in enumerate(NODES):
        if i in EXCLUDE or not nok[i]: continue
        col = node_color(n)
        if landed[i]:
            stamp(arr, nsx[i], nsy[i], K_BRIGHT, col, 0.66)
            cx, cy = int(round(nsx[i])), int(round(nsy[i]))
            if 2 <= cx < W - 2 and 2 <= cy < H - 2:
                arr[cy-1:cy+2, cx-1:cx+2] = np.maximum(arr[cy-1:cy+2, cx-1:cx+2],
                                                       np.array(col, np.float32))
        else:
            stamp(arr, nsx[i], nsy[i], K_BASE, col, NODE_BASE.get(n["kind"], ((104, 124, 160), 0.16))[1])
    # --- core glow, soft
    kgx, kgy, _, kgok = project(CORE[None, :], cam)
    if kgok[0]:
        stamp(arr, kgx[0], kgy[0], K_HALO, (255, 238, 205), 0.22)
        stamp(arr, kgx[0], kgy[0], K_CORE, (255, 240, 210), 0.62)
    # --- v8 scatter bursts: a harsh shouted spike sprays particles at its
    #     own hop position; the spray peaks mid-life and is drawn back to
    #     the origin by the end of its life — shaken, then gathered
    for b in BURSTS:
        age = f - b["frame"]
        if age < 0 or age > b["life"]: continue
        _sb = STABS[b["hop"]]
        org = POS_NOW[_sb["node"]] if b["typ"] == 1 else np.array(_sb["at"]) + np.array(_sb["off"])
        ow = to_world(org, f, hop)
        u = age / b["life"]
        disp = b["spd"] * (b["life"] * 2.2 / math.pi) * math.sin(math.pi * u)
        pts = ow + b["dirs"] * disp[:, None]
        px, py, _, pok = project(pts, cam)
        g = (1.0 - u) * (0.55 + 0.45 * b["strength"])
        col = (255, 240, 214) if b["hard"] else (255, 226, 178)
        kern = K_BRIGHT if b["hard"] else K_BASE   # hard shakes get glowing motes
        for _pi in range(len(disp)):
            if pok[_pi]:
                stamp(arr, px[_pi], py[_pi], kern, col, float(g))
        if b["hard"] and age < 7:
            osx, osy, _, ook = project(ow, cam)
            if ook[0]:
                stamp(arr, osx[0], osy[0], K_MARK, (255, 244, 220), (1.0 - age / 7.0) * 0.7)
    # --- comets: heads stamped on the float buffer (glow), tails drawn on the layer
    comets = comet_state(f)
    for pts, fade in comets:
        if fade <= 0.01: continue
        hw = to_world(pts[-1], f, hop)
        hsx, hsy, _, hok = project(hw, cam)
        if hok[0]:
            stamp(arr, hsx[0], hsy[0], K_BRIGHT, SILVER_HEAD, 0.7 * fade)
    # --- PIL layer: CYOA thread, comet tails, golden trace, arcs
    layer = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(layer, "RGBA")
    # the CYOA thread itself: a faint silver thread through the same space
    cyw = to_world(CY, f, hop)
    csx, csy, _, cok = project(cyw, cam)
    for i in range(CYOA_N - 1):
        if cok[i] and cok[i + 1]:
            dr.line([csx[i], csy[i], csx[i + 1], csy[i + 1]], fill=SILVER_DIM + (15,), width=3)
    dr.point([(csx[i], csy[i]) for i in range(CYOA_N) if cok[i]], fill=SILVER_DIM + (44,))
    # comet tails: silver, brightening toward the head
    for pts, fade in comets:
        if fade <= 0.01: continue
        pw = to_world(pts, f, hop)
        psx, psy, _, pok = project(pw, cam)
        nseg = len(pts) - 1
        for j in range(nseg):
            if not (pok[j] and pok[j + 1]): continue
            # break the tail across the trace's long jumps — a comet streaks
            # along locally continuous path, never slashes across the frame
            if (psx[j + 1] - psx[j]) ** 2 + (psy[j + 1] - psy[j]) ** 2 > 390 ** 2: continue
            u = (j + 1) / nseg
            a = int(120 * fade * u ** 2.2)
            col = tuple(int(SILVER[c] + (SILVER_HEAD[c] - SILVER[c]) * u) for c in range(3))
            dr.line([psx[j], psy[j], psx[j + 1], psy[j + 1]], fill=col + (a,), width=6 if u > 0.8 else 3)
    # golden trace (spline verts born by hop)
    upto = int(np.searchsorted(VH, hop, side="right")) - 1
    if upto > 0:
        idxs = list(range(upto))
        if upto > 3400:
            keep = sorted(set(idxs[-800:]) | set(idxs[:: math.ceil((upto - 800) / 2400)]))
            idxs = keep
        Pw = to_world(V[: upto + 1], f, hop)
        psx, psy, _, pok = project(Pw, cam)
        for i in idxs:
            if VH[i + 1] >= hop - 1600 and pok[i] and pok[i + 1]:
                c = VCOL[i + 1]
                dr.line([psx[i], psy[i], psx[i + 1], psy[i + 1]],
                        fill=(int(c[0]), int(c[1]), int(c[2]), 8), width=13)
        for i in idxs:
            if pok[i] and pok[i + 1]:
                c = VCOL[i + 1]
                old = VH[i + 1] < hop - 2600
                dr.line([psx[i], psy[i], psx[i + 1], psy[i + 1]],
                        fill=(int(c[0]), int(c[1]), int(c[2]), 22 if old else int(72 + 26 * HUSH_F)), width=5)
    # stab arcs for recent landings (matches only; misses feed the CMB)
    # v8: each arc's bow, wobble, width and lifetime come from the content
    # of the tweet that landed it — its entropy bows and shakes the arc,
    # the re-coherence envelope settles it again, and landings inside the
    # corpus's hush stretches live longer so single arrivals can land
    _live = POS_NOW
    for j in range(max(0, k - 130), k):
        hj = land_hop[j]
        age = f - land_frame[j]
        life = 8.0 + 7.0 * float(HUSH_HOP[hj])
        if age < 0 or age > life: continue
        _sj = STABS[hj]
        if _sj["typ"] == 1 and _sj["node"] in EXCLUDE: continue   # no arc lands on the excluded account
        p0w = to_world(land_prev[j], f, hop)[0]
        p1w = to_world(_live[_sj["node"]], f, hop)[0] if _sj["typ"] == 1 else to_world(CP[j], f, hop)[0]
        bow = (0.50 + 1.20 * float(HN_LAND[j])) * (1.0 - 0.35 * COH_F)
        jit = float(JIT_LAND[j]) * 0.09 * float(np.linalg.norm(p1w - p0w)) * float(HN_LAND[j]) ** 2
        arc = bezier_arc8(p0w, p1w, cam, u_max=min(1.0, age / 4.5), bow_scale=bow, jit_mag=jit)
        if arc is None: continue
        ax_, ay_, _, aok = project(arc, cam)
        a = (1.0 - age / life) * 0.85
        base_col = gold_rgb(hj, bright=float(land_toneb[j]))
        col = tuple(int(min(255, c * (1.0 + 0.18 * COH_F))) for c in base_col)
        wid = 9 + int(round(3.0 * float(HN_LAND[j])))
        for jj in range(len(arc) - 1):
            if aok[jj] and aok[jj + 1]:
                dr.line([ax_[jj], ay_[jj], ax_[jj + 1], ay_[jj + 1]], fill=col + (int(190 * a),), width=wid)
    arr = np.asarray(layer).astype(np.float32)
    # his marker: one unlabeled warm point of light on the trace head
    head_w = to_world(spline_pos_at_hop(hop), f, hop)
    hsx, hsy, _, hok = project(head_w, cam)
    if hok[0] and f < CTA_F0:
        stamp(arr, hsx[0], hsy[0], K_MARK, gold_rgb(hop),
              0.9 * (1.0 + 0.45 * HUSH_F) * (1.3 if HARD_NOW else 1.0))
        cx, cy = int(round(hsx[0])), int(round(hsy[0]))
        arr[max(0, cy-3):min(H, cy+4), max(0, cx-3):min(W, cx+4)] = 255.0
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(out, "RGBA")
    # CTA veil (background keeps glowing through)
    if f >= CTA_F0:
        a = int(168 * smooth(CTA_F0, CTA_F0 + 75, f))
        dr.rectangle([0, 0, W, H], fill=(3, 4, 9, a))
    # rare handle-only callouts, gentle
    if TITLE_F <= f < CTA_F0:
        for (ch, txt, col) in callouts:
            cf = TITLE_F + ch / HPF
            age = f - cf
            if 0 <= age < 70:
                a = min(age / 8, 1.0) * (1 - smooth(55, 70, age))
                w = dr.textlength(txt, font=F_CALL)
                dr.text((CX_CUR - w / 2, 354), txt, font=F_CALL, fill=col + (int(235 * a),))
    # world-event lower-thirds (queued captions; move to top if a card holds the lower left)
    for e in EVENTS:
        if e["cap_start"] <= f < e["cap_end"]:
            age = f - e["cap_start"]
            a = min(age / 12, 1.0) * (1 - smooth(CAP_LEN - 16, CAP_LEN, age))
            if a > 0:
                y = H - 222
                tw = spaced_width(e["caption"], F_EVENT, 18)
                dr.line([CX_CUR - tw / 2, y - 36, CX_CUR + tw / 2, y - 36],
                        fill=(170, 220, 235, int(120 * a)), width=3)
                draw_spaced(dr, CX_CUR, y, e["caption"], F_EVENT, (228, 234, 242, int(242 * a)), 18)
    # film strip: the top 20 flow along the right side
    draw_strip(dr, f)
    # title card: THE EXOCORTEX — Shaken yet Stirred
    if f < 96:
        a = min(f / 11, 1.0) * (1 - smooth(72, 94, f))
        if a > 0:
            center_text(dr, CX_CUR, 618, "THE EXOCORTEX", F_TITLE, (240, 244, 250, int(255 * a)))
            center_text(dr, CX_CUR, 864, "Shaken yet Stirred", F_OBL, (246, 216, 152, int(255 * a)))
            center_text(dr, CX_CUR, 1020, "a map of alignment", F_SUB, (198, 210, 226, int(255 * a)))
    # second title beat: the v6 line, kept as a quiet echo (documented in notes)
    if 108 <= f < 196:
        a = min((f - 108) / 14, 1.0) * (1 - smooth(172, 196, f))
        if a > 0:
            center_text(dr, CX_CUR, 864, "the future has arrived", F_OBL, (246, 216, 152, int(255 * a)))
    # CTA card
    if f >= CTA_F0:
        a = smooth(CTA_F0, CTA_F0 + 75, f)
        if a > 0:
            center_text(dr, CX_CUR, 696, "520 people are already in this map.", F_CARD, (240, 244, 250, int(255 * a)))
            center_text(dr, CX_CUR, 864, "Find your coordinate. Claim your space.", F_CARD, (255, 198, 92, int(255 * a)))
            center_text(dr, CX_CUR, 1050, "edit.phext.io", F_BIG, (255, 214, 120, int(255 * a)))
            center_text(dr, CX_CUR, 1290, "Not in the map yet? The door is open.", F_SUB, (200, 212, 228, int(255 * a)))
    return out.resize((OUT_W, OUT_H), Image.LANCZOS)

if __name__ == "__main__":
    def frame_of_hop(h): return int(TITLE_F + h / HPF)
    if "--stills" in sys.argv:
        os.makedirs(f"{BASE}/viz8/stills_check", exist_ok=True)
        _hard_mid = [b for b in BURSTS if b["hard"] and 900 <= b["frame"] <= 2800]
        _bb = max(_hard_mid, key=lambda b: b["strength"])
        _hw = FEAT["meta"]["hush_window"]
        picks = {"title": 40, "beat2": 150, "strip": 1500, "p50": int(0.50 * TOTAL_F),
                 "bezier": 2300, "cta": 3600,
                 "burst": int(_bb["frame"]) + 5,
                 "turbulence": int(TITLE_F + 4955 / HPF),
                 "hush": int(TITLE_F + ((_hw["hop0"] + _hw["hop1"]) / 2) / HPF)}
        for name, f in picks.items():
            t = time.time(); im = render(f); dt = time.time() - t
            im.save(f"{BASE}/viz8/stills_check/{name}.png")
            print(f"{name} frame {f}: {dt*1000:.0f} ms", flush=True)
    elif "--range" in sys.argv:
        import subprocess
        i = sys.argv.index("--range"); fa, fb = int(sys.argv[i + 1]), int(sys.argv[i + 2])
        outp = sys.argv[sys.argv.index("--out") + 1]
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "10", "-pix_fmt", "yuv420p", "-threads", "2", outp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(fa, fb):
            p.stdin.write(render(f).tobytes())
            if f % 250 == 0: print(f"{f}/{fb} {time.time()-t0:.0f}s", flush=True)
        p.stdin.close(); p.wait()
        print("chunk done", outp, time.time() - t0, flush=True)
    else:
        import subprocess
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "10", "-pix_fmt", "yuv420p", f"{BASE}/viz8/silent.mp4"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(TOTAL_F):
            p.stdin.write(render(f).tobytes())
            if f % 500 == 0: print(f"{f}/{TOTAL_F} {time.time()-t0:.0f}s", flush=True)
        p.stdin.close(); p.wait()
        print("render done", time.time() - t0, flush=True)
