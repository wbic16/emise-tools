#!/usr/bin/env python3
"""wavefront-viz v6 — the future has arrived. (Will, 2026-11-03 18:01 CST)

v6 direction, verbatim: "more dynamic, blend CYOA into the visualization,
the entire scene should rotate through several revolutions during the
course of the video. less technical demo, more 'the future has arrived'.
use major world events to fine tune motion. show the most viewed posts
as they arrive (top 20)". Clarification: "the CYOA thread as silver
comets following through the same space" (comets, not commits).

Built on v5's pipeline with these changes:
  * NO technical HUD: hop counter, attempts/matches/placed counters,
    progress bar, tone ribbon, era ticks and the honesty microcopy are
    all gone. What remains: an opening title, event lower-thirds,
    most-echoed cards, handle callouts (story beats, kept from v4/v5),
    and the CTA.
  * CYOA blend — silver comets: the 829 placed CYOA scrolls
    (~/workspace/phext/traversal-map/cyoa-traversal.json) are projected
    through the SAME 9D->3D projection as the wavefront nodes (triple
    means of the 9 coordinate values; viz/extract_data.py), then fit
    per-axis (robust 0.5–99.5 percentile clip) into the wavefront field
    extent so the thread inhabits the same volume. The trace (file
    order) is drawn as a faint silver thread; seven silver comets —
    bright heads, fading tails — travel it continuously, subordinate
    to the one golden trace.
  * Rotation is the dominant motion: the camera azimuth integrates a
    modulated velocity profile to EXACTLY 5 full revolutions
    (1800 degrees) across the film, ending aligned with the start.
    v5's thrust orbit is superseded. v5's node epicycles, 2x zoom
    (radius 2.225, pull-back to 6.8) and breathing are kept.
  * Major world events fine-tune the motion: each event briefly
    multiplies the angular velocity (surge or hush) and pulses the
    camera radius at its true hop position, and shows an elegant
    lower-third caption (name + year). Captions queue if they would
    collide; the motion modulation never moves.
  * Top 20 posts as they arrive: the archive (tweets.json) has NO
    views/impressions field, so the ranking falls back to
    favourites + retweets on original posts and the cards are labelled
    "MOST ECHOED" — see viz6/BUILD-NOTES.md. Each card appears at its
    post's hop-time arrival (queued for legibility when arrivals
    bunch), with text, date and echo count.
  * Physics base: calm v4 base — subtle Overton warp (x0.35) only,
    no goalpost chase. Golden trace, CMB misses, VADER tone, rupture
    beat all kept. The phext data is only read; every transform is
    render-time.
Usage: render6.py --stills | --full
"""
import json, math, sys, time, re, html
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
SONG_DUR = 158.400                               # viz5/song_edit.wav
TOTAL_F = int(round(SONG_DUR * FPS))             # 3802 frames = 158.42 s
TITLE_F = 42                                     # hops start here
MAIN_END_F = 3362                                # last hop lands here
PULL_F = 3362                                    # pull-back 3362..3512
CTA_F0 = 3512                                    # CTA fade-in (75 f)
FOCAL = (H / 2) / math.tan(math.radians(21.0))
BASE = "/home/hatch/workspace/wavefront"
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
def _node_seed(n): return (n["key"] or n["name"])
PHASE = np.array([int.from_bytes(hashlib.md5(_node_seed(n).encode()).digest()[:8], "little")
                  / 2**64 * 2 * math.pi for n in NODES])
PHASE_Z = np.array([int.from_bytes(hashlib.md5((_node_seed(n) + "·z").encode()).digest()[:8], "little")
                    / 2**64 * 2 * math.pi for n in NODES])
def node_pos_all(hf):
    ph = PHASE + OMEGA_NODE * hf
    off = np.stack([A_ORB * np.cos(ph), A_ORB * np.sin(ph),
                    0.35 * A_ORB * np.sin(0.9 * ph + PHASE_Z)], axis=1)
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

import matplotlib, os
FONT = os.path.join(matplotlib.get_data_path(), "fonts", "ttf") + "/"
F_TITLE = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 56)
F_OBL   = ImageFont.truetype(FONT + "DejaVuSans-Oblique.ttf", 27)
F_SUB   = ImageFont.truetype(FONT + "DejaVuSans.ttf", 24)
F_CALL  = ImageFont.truetype(FONT + "DejaVuSans.ttf", 18)
F_CARD  = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 30)
F_BIG   = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 44)
F_EVENT = ImageFont.truetype(FONT + "DejaVuSans.ttf", 20)
F_CARDH = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 13)
F_CARDT = ImageFont.truetype(FONT + "DejaVuSans.ttf", 19)
F_CARDF = ImageFont.truetype(FONT + "DejaVuSans.ttf", 14)

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
TRAV = json.load(open("/home/hatch/workspace/phext/traversal-map/cyoa-traversal.json"))
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

def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
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
ARCHIVE = "/home/hatch/workspace/twitter-archive/tweets.json"
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
CARD_LEN, CARD_GAP = 108, 16
_prev_end = -10**9
for _o in TOP20:
    _o["hop"] = float(np.searchsorted(stab_ts, _o["ts"]))
    _o["arr_frame"] = TITLE_F + _o["hop"] / HPF
    _o["start"] = max(_o["arr_frame"], TITLE_F + 96, _prev_end + CARD_GAP)
    _o["end"] = _o["start"] + CARD_LEN
    _prev_end = _o["end"]
    _o["lines"] = wrap(_o["text"], F_CARDT, 556, 4)
for _o in TOP20:
    print(f"card rank {_o['rank']:2d} {_o['date']} echo {_o['echo']:3d} hop {_o['hop']:6.0f} "
          f"frames {_o['start']:6.0f}..{_o['end']:6.0f} | {_o['text'][:60]}", flush=True)
assert TOP20[-1]["end"] <= CTA_F0 - 12, "card schedule overflows into the CTA"

# ---------- walk the hops once: landings, counters, callouts ----------
node_idx_by_key = {}
for i, n in enumerate(NODES):
    node_idx_by_key.setdefault(n["key"], i)
ORAI_RUP = next(i for i, n in enumerate(NODES) if "rupture" in n["name"])
RUPTURE_HOP = int(np.searchsorted(stab_ts, 1749988800))  # 2025-06-15

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
        elif hd == "oraiawake":   callouts.append((h, "@OraiAwake", (235, 226, 205)))
callouts.append((RUPTURE_HOP, "@OraiAwake", (216, 130, 118)))
callouts.sort()
assert mat == N_MATCH and attempts_at[-1] == N_HOPS, (mat, attempts_at[-1])
print(f"prep: landings={len(land_pos)} placed_final={placed_at[-1]} callouts={len(callouts)}", flush=True)

# ---------- golden spline through the landings ----------
CP = np.array(land_pos); CB = np.array(land_hop, dtype=np.float64)
SUB = 2
verts, vhop = [], []
ext = np.vstack([CP[0], CP, CP[-1]])
for i in range(len(CP) - 1):
    for j in range(SUB):
        t = j / SUB
        verts.append(catmull_rom(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], t))
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
    return W / 2 + FOCAL * xc / zsafe, H / 2 - FOCAL * yc / zsafe, zc, ok

def kernel(n, sigma):
    ax = np.arange(n) - n // 2
    g = np.exp(-(ax[:, None] ** 2 + ax[None, :] ** 2) / (2 * sigma * sigma))
    return (g / g.max()).astype(np.float32)
K_BASE, K_BRIGHT, K_MARK = kernel(9, 1.6), kernel(15, 2.6), kernel(25, 4.2)
K_CORE, K_HALO = kernel(61, 11.0), kernel(121, 24.0)

def stamp(buf, sx, sy, kern, color, gain):
    n = kern.shape[0]; r = n // 2
    x0, y0 = int(round(sx)) - r, int(round(sy)) - r
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + n), min(H, y0 + n)
    if xa >= xb or ya >= yb: return
    k = kern[ya - y0: ya - y0 + (yb - ya), xa - x0: xa - x0 + (xb - xa)]
    buf[ya:yb, xa:xb] += k[:, :, None] * (np.array(color, dtype=np.float32) * gain)

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
CMB = ((0.18 + 0.82 * _int ** 1.15)[:, :, None] * tint * 30.0).astype(np.float32)
BASE_BG = np.array([3.0, 4.0, 8.0], dtype=np.float32)
STARS_X = _rng.uniform(0, W, 380); STARS_Y = _rng.uniform(0, H, 380); STARS_B = _rng.uniform(5, 20, 380)
cum_miss = attempts_at - matches_at
miss_gain = cum_miss / max(1, cum_miss[-1])

NODE_BASE = {"detected": ((104, 124, 160), 0.24), "mutual": ((132, 158, 198), 0.34),
             "named": ((158, 184, 218), 0.36), "wbic32": ((134, 188, 174), 0.36),
             "will": ((255, 190, 70), 0.8)}
def node_color(n):
    if n["region"] == "shoals": return (192, 80, 68)
    return NODE_BASE[n["kind"]][0]

def bezier_arc(p0, p1, cam, u_max=1.0, n=10):
    chord = p1 - p0; L = np.linalg.norm(chord)
    if L < 1e-6: return None
    perp = np.cross(chord / L, cam[3]); nn = np.linalg.norm(perp)
    perp = perp / nn if nn > 1e-4 else np.array([0.0, 0.0, 1.0])
    ctrl = (p0 + p1) / 2 + perp * (0.16 * L + 0.03)
    ts = np.linspace(0, u_max, max(2, int(n * u_max) + 1))
    return ((1 - ts) ** 2)[:, None] * p0 + (2 * (1 - ts) * ts)[:, None] * ctrl + (ts ** 2)[:, None] * p1

land_frame = np.array([TITLE_F + h / HPF for h in land_hop])
NODE_FIRST_HOP = np.full(len(NODES), 10**9, dtype=int)
for _j, _h in enumerate(land_hop):
    _s = STABS[_h]
    if _s["typ"] == 1 and _h < NODE_FIRST_HOP[_s["node"]]:
        NODE_FIRST_HOP[_s["node"]] = _h
NODE_FIRST_HOP[ORAI_RUP] = RUPTURE_HOP
land_prev = np.vstack([np.zeros(3), CP[:-1]])
land_toneb = np.array([0.72 + 0.5 * tone_norm(h) for h in land_hop])

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

def card_active(f):
    return any(o["start"] <= f < o["end"] for o in TOP20)

def render(f):
    hop = hop_float(f)
    hi = int(min(N_HOPS, math.floor(hop)))
    cam = camera(f)
    # --- background: space + CMB afterglow (gain grows with cumulative misses)
    gain = 0.30 + 0.70 * float(miss_gain[hi])
    arr = BASE_BG[None, None, :] + CMB * gain
    flat = arr.reshape(-1, 3)
    np.add.at(flat, (STARS_Y.astype(int) * W + STARS_X.astype(int)),
              np.stack([STARS_B, STARS_B, STARS_B * 1.1], axis=1).astype(np.float32))
    arr = flat.reshape(H, W, 3)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    arr = np.asarray(img).astype(np.float32)
    # --- nodes (on their own orbits)
    nodes_w = to_world(node_pos_all(node_hop(f)), f, hop)
    nsx, nsy, nzc, nok = project(nodes_w, cam)
    k = int(np.searchsorted(land_hop, hi, side="right"))
    landed = NODE_FIRST_HOP <= hi
    for i, n in enumerate(NODES):
        if not nok[i]: continue
        col = node_color(n)
        if landed[i]:
            stamp(arr, nsx[i], nsy[i], K_BRIGHT, col, 0.66)
            cx, cy = int(round(nsx[i])), int(round(nsy[i]))
            if 0 <= cx < W and 0 <= cy < H: arr[cy, cx] = np.maximum(arr[cy, cx], np.array(col, np.float32))
        else:
            stamp(arr, nsx[i], nsy[i], K_BASE, col, NODE_BASE.get(n["kind"], ((104, 124, 160), 0.16))[1] if n["region"] != "shoals" else 0.26)
    # --- core glow, soft
    kgx, kgy, _, kgok = project(CORE[None, :], cam)
    if kgok[0]:
        stamp(arr, kgx[0], kgy[0], K_HALO, (255, 238, 205), 0.22)
        stamp(arr, kgx[0], kgy[0], K_CORE, (255, 240, 210), 0.62)
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
            dr.line([csx[i], csy[i], csx[i + 1], csy[i + 1]], fill=SILVER_DIM + (15,), width=1)
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
            if (psx[j + 1] - psx[j]) ** 2 + (psy[j + 1] - psy[j]) ** 2 > 130 ** 2: continue
            u = (j + 1) / nseg
            a = int(120 * fade * u ** 2.2)
            col = tuple(int(SILVER[c] + (SILVER_HEAD[c] - SILVER[c]) * u) for c in range(3))
            dr.line([psx[j], psy[j], psx[j + 1], psy[j + 1]], fill=col + (a,), width=2 if u > 0.8 else 1)
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
                        fill=(int(c[0]), int(c[1]), int(c[2]), 8), width=3)
        for i in idxs:
            if pok[i] and pok[i + 1]:
                c = VCOL[i + 1]
                old = VH[i + 1] < hop - 2600
                dr.line([psx[i], psy[i], psx[i + 1], psy[i + 1]],
                        fill=(int(c[0]), int(c[1]), int(c[2]), 22 if old else 72), width=1)
    # stab arcs for recent landings (matches only; misses feed the CMB)
    _live = node_pos_all(node_hop(f))
    for j in range(max(0, k - 60), k):
        age = f - land_frame[j]
        if age < 0 or age > 8: continue
        p0w = to_world(land_prev[j], f, hop)[0]
        _sj = STABS[land_hop[j]]
        p1w = to_world(_live[_sj["node"]], f, hop)[0] if _sj["typ"] == 1 else to_world(CP[j], f, hop)[0]
        arc = bezier_arc(p0w, p1w, cam, u_max=min(1.0, age / 4.5))
        if arc is None: continue
        ax_, ay_, _, aok = project(arc, cam)
        a = (1 - age / 8) * 0.85
        col = gold_rgb(land_hop[j], bright=float(land_toneb[j]))
        for jj in range(len(arc) - 1):
            if aok[jj] and aok[jj + 1]:
                dr.line([ax_[jj], ay_[jj], ax_[jj + 1], ay_[jj + 1]], fill=col + (int(190 * a),), width=2)
    # rupture beat: one quiet red arc, once
    rf = TITLE_F + RUPTURE_HOP / HPF
    if rf <= f < rf + 28:
        age = f - rf
        p0w = to_world(spline_pos_at_hop(RUPTURE_HOP), f, hop)[0]
        p1w = to_world(_live[ORAI_RUP], f, hop)[0]
        arc = bezier_arc(p0w, p1w, cam, u_max=min(1.0, age / 9.0))
        if arc is not None:
            ax_, ay_, _, aok = project(arc, cam)
            a = 1 - age / 28
            for jj in range(len(arc) - 1):
                if aok[jj] and aok[jj + 1]:
                    dr.line([ax_[jj], ay_[jj], ax_[jj + 1], ay_[jj + 1]], fill=(205, 74, 58, int(170 * a)), width=2)
    arr = np.asarray(layer).astype(np.float32)
    # his marker: one unlabeled warm point of light on the trace head
    head_w = to_world(spline_pos_at_hop(hop), f, hop)
    hsx, hsy, _, hok = project(head_w, cam)
    if hok[0] and f < CTA_F0:
        stamp(arr, hsx[0], hsy[0], K_MARK, gold_rgb(hop), 0.9)
        cx, cy = int(round(hsx[0])), int(round(hsy[0]))
        arr[max(0, cy-1):min(H, cy+2), max(0, cx-1):min(W, cx+2)] = 255.0
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
                dr.text((W / 2 - w / 2, 118), txt, font=F_CALL, fill=col + (int(235 * a),))
    # world-event lower-thirds (queued captions; move to top if a card holds the lower left)
    for e in EVENTS:
        if e["cap_start"] <= f < e["cap_end"]:
            age = f - e["cap_start"]
            a = min(age / 12, 1.0) * (1 - smooth(CAP_LEN - 16, CAP_LEN, age))
            if a > 0:
                y = 84 if card_active(f) else H - 74
                tw = spaced_width(e["caption"], F_EVENT, 6)
                dr.line([W / 2 - tw / 2, y - 12, W / 2 + tw / 2, y - 12],
                        fill=(190, 202, 220, int(110 * a)), width=1)
                draw_spaced(dr, W / 2, y, e["caption"], F_EVENT, (228, 234, 242, int(242 * a)), 6)
    # top-20 cards: the most echoed posts, as they arrive
    for o in TOP20:
        if o["start"] <= f < o["end"]:
            age = f - o["start"]
            a = min(age / 10, 1.0) * (1 - smooth(CARD_LEN - 12, CARD_LEN, age))
            if a <= 0: continue
            lines = o["lines"]
            pw = 604; ph = 18 + 15 + 8 + len(lines) * 26 + 10 + 18 + 16
            x0, y1 = 36, H - 34; y0 = y1 - ph
            dr.rounded_rectangle([x0, y0, x0 + pw, y1], radius=12,
                                 fill=(8, 12, 20, int(178 * a)),
                                 outline=(150, 165, 190, int(95 * a)), width=1)
            draw_spaced_left(dr, x0 + 20, y0 + 15, "MOST ECHOED", F_CARDH,
                             (186, 198, 216, int(235 * a)), 4)
            rk = f"no. {o['rank']} of 20"
            rw = dr.textlength(rk, font=F_CARDF)
            dr.text((x0 + pw - 20 - rw, y0 + 14), rk, font=F_CARDF, fill=(148, 162, 182, int(220 * a)))
            for li, ln in enumerate(lines):
                dr.text((x0 + 20, y0 + 40 + li * 26), ln, font=F_CARDT, fill=(238, 242, 246, int(248 * a)))
            foot = f"{o['label']} · {o['echo']} echoes"
            dr.text((x0 + 20, y1 - 34), foot, font=F_CARDF, fill=(168, 180, 198, int(230 * a)))
    # title card
    if f < 96:
        a = min(f / 11, 1.0) * (1 - smooth(72, 94, f))
        if a > 0:
            center_text(dr, W/2, 206, "THE WAVEFRONT", F_TITLE, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 288, "the future has arrived", F_OBL, (246, 216, 152, int(255 * a)))
            center_text(dr, W/2, 340, "a map of alignment", F_SUB, (198, 210, 226, int(255 * a)))
    # CTA card
    if f >= CTA_F0:
        a = smooth(CTA_F0, CTA_F0 + 75, f)
        if a > 0:
            center_text(dr, W/2, 232, "520 people are already in this map.", F_CARD, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 288, "Find your coordinate. Claim your space.", F_CARD, (255, 198, 92, int(255 * a)))
            center_text(dr, W/2, 350, "edit.phext.io", F_BIG, (255, 214, 120, int(255 * a)))
            center_text(dr, W/2, 430, "Not in the map yet? The door is open.", F_SUB, (200, 212, 228, int(255 * a)))
    return out

if __name__ == "__main__":
    def frame_of_hop(h): return int(TITLE_F + h / HPF)
    if "--stills" in sys.argv:
        os.makedirs(f"{BASE}/viz6/stills", exist_ok=True)
        card_mid = next(o for o in TOP20 if 1200 < o["start"] < 2400)
        picks = {"p10": int(0.10 * TOTAL_F), "p50": int(0.50 * TOTAL_F),
                 "p90": int(0.90 * TOTAL_F),
                 "card": int((card_mid["start"] + card_mid["end"]) / 2),
                 "comets": 1500}
        for name, f in picks.items():
            t = time.time(); im = render(f); dt = time.time() - t
            im.save(f"{BASE}/viz6/stills/{name}.png")
            print(f"{name} frame {f}: {dt*1000:.0f} ms", flush=True)
    else:
        import subprocess
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", f"{BASE}/viz6/silent.mp4"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(TOTAL_F):
            p.stdin.write(render(f).tobytes())
            if f % 500 == 0: print(f"{f}/{TOTAL_F} {time.time()-t0:.0f}s", flush=True)
        p.stdin.close(); p.wait()
        print("render done", time.time() - t0, flush=True)
