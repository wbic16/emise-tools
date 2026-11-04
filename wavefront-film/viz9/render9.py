#!/usr/bin/env python3
"""wavefront-viz v9 — "The Exocortex, Shaken yet Stirred": the fidelity cut.

Built on v8's verified pipeline (viz8/render8.py, untouched) with the
consolidated v9 feedback internalized (Emi Prime's OP review, Grok's
frame measurements, Claude's tagged notes, Will's three additions).
Full change log, root-cause evidence and conflict resolutions live in
viz9/BUILD-NOTES.md. Headlines:

  * P0 flash frames FIXED at the root: v8's unguarded trace-head block
    write (numpy negative-index wrap when the head left the canvas)
    painted top-left white rectangles on 5 frames. Guarded here, and
    a YAVG/black-frame QA gate now ships with the pipeline (qa9.py).
  * Entropy signal re-derived: v8's raw lexical entropy was ~99% a
    tweet-length meter (r=0.993 vs log2 tokens). v9 drives weather,
    arc bow/jitter and hush from LENGTH-RESIDUALIZED entropy
    (viz9/extract_features9.py -> features9.json).
  * Entropy-weather phase INTEGRATES its rate (v8 multiplied the
    current rate by elapsed frames, making the phase jump whenever
    the weather changed).
  * Bezier control points are built in WORLD space (v8 used the
    camera forward vector, so connection geometry swam as the
    camera moved).
  * Temporal depth: the accumulated trace is age-graded — subdued
    history, brighter recent arrivals, dominant active head. Hush now
    CLEARS the foreground (trace/nodes dim, the single landing and
    the head carry the frame) instead of only settling the backdrop.
  * Top-20 mutuals each get exactly one highlight (density-peak
    arrival: node pulse, ring, boosted arc, backed label with a
    pointer line). Most Echoed card arrivals pulse Will's node.
  * Film strip at 50% panel opacity (masthead stays opaque), header
    corrected to "Top 20 by echoes · in time order", fades in at the
    first card, 5-line cells, year readout in the masthead.
  * Cinematic pass: soft-knee tone mapping (no more additive clip
    blow-out), selective bloom breathing with the song's RMS envelope,
    depth attenuation + atmospheric perspective on nodes, full-res
    multi-octave background with vignette and fixed film grain,
    3 parallax star shells, era chapters via radius/warmth (azimuth
    untouched — still exactly 5 revolutions), event ripples,
    temporal AA by 3-subframe motion blur, bundled Inter font.
  * CTA retimed: strip fully gone before the text, network recedes
    as the card arrives, ~7.6 s full-strength hold, map drifting
    behind the veil. CTA text verbatim from v6–v8.
  * A2 (Will, reel review — ledger W5/W6): the CMB afterglow is
    DARKENED (CMB_DARK 0.50 on the static layer; the boil keeps 0.70
    of its amplitude, so the weather reads as motion over a quiet
    field, and hush darkening composes on top as before). Stable
    MICRO-SHELLS: one world-locked covariance ellipsoid per DBSCAN
    mutual cluster (viz9/clusters9.json, from derive_clusters.py),
    drawn as a near-transparent fill with a fresnel-style rim — no
    weather, boil or hush term touches them; they are the still
    geometry the weather moves against.
  * Chunk B (Will, 2026-11-04 — ledger W7/W8): the CMB grain/boil is
    REPLACED by light snow — sparse closed-form specks in two depth
    layers over a faint drifting haze, at the W5 darkness budget; the
    residual-entropy weather now drives a wind (drift + fall clocks,
    integrated exactly like the boil phase was) and hush lets the
    snow hang nearly still. A 1965 Apollo-era film treatment rides
    in render_frame as a pure post stage: animated monochrome grain,
    warm halation on the brightest highlights, a film response curve
    (lifted blacks, gentle S, soft shoulder, whisper of split-tone),
    a slow +-1.5% exposure wander, and a modestly deeper vignette.
    No gate weave, no dust/scratches, no scene changes. A
    stop-and-amend (Will, 00:51, ledger W9/W10) then transplanted
    two devices from a protein-structure film — dotted orbital
    rings around each micro-shell and a diegetic CONTACTS
    REMAINING process counter — and demoted the snow to a sparse
    whisper over the film grain, which now carries the dark
    field's texture on its own.

Usage: render9.py --stills | --range A B --out PATH | --frame F --out PATH
Env: V9_ROOT (tree root), V9_SUBN (subframes per output frame, default 1;
the stress reel renders with 3), V9_DUMP (dir: also dump raw rgb frames).
"""
import json, math, sys, time, re, html, os
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 3840, 2160, 24          # internal render canvas: 4K
OUT_W, OUT_H = 1920, 1080           # delivered master: down-sampled to 1080p
DS = 3                              # design scale vs v6's 720p canvas
SONG_DUR = 158.400                               # viz5/song_edit.wav
TOTAL_F = int(round(SONG_DUR * FPS))             # 3802 frames = 158.42 s
TITLE_F = 42                                     # hops start here
MAIN_END_F = 3362                                # last hop lands here
PULL_F = 3362                                    # pull-back 3362..3554
CTA_F0 = 3554                                    # CTA fade-in (64 f); full by 3618, ~7.6 s hold
FOCAL = (H / 2) / math.tan(math.radians(21.0))
ROOT = os.environ.get("V9_ROOT", "/home/hatch/workspace")   # ranch render mirrors the tree under V9_ROOT
BASE = f"{ROOT}/wavefront"
SUBN = int(os.environ.get("V9_SUBN", "1"))
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
AMP_F = 1.0                                       # per-frame entropy scaling of the epicycles (set in render)
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

# ---------- v9 content signals (extract_features9.py) ----------
# v8's raw entropy was a length meter (r=0.993 vs log2 tokens, R^2=0.987).
# v9 uses length-residualized entropy throughout: Hres_n per hop, the
# re-derived weather ent_sm9 and hush9; coh and bursts are carried from
# v8 unchanged (they never touched lexical entropy).
FEAT9 = json.load(open(f"{BASE}/viz9/features9.json"))
HN9_HOP = np.array(FEAT9["derived"]["Hres_n"], dtype=np.float64)   # per-hop diversity beyond length
ENT_SM9 = np.array(FEAT9["derived"]["ent_sm9"], dtype=np.float64)  # v9 entropy weather (smoothed)
HUSH9_HOP = np.array(FEAT9["derived"]["hush9"], dtype=np.float64)  # per-hop stillness, v9
COH_HOP = np.array(FEAT9["derived"]["coh"], dtype=np.float64)      # re-coherence envelope (v8, unchanged)
SONG_RMS = np.array(FEAT9["song_rms"], dtype=np.float64)           # per-frame song energy 0..1
assert len(HN9_HOP) == N_HOPS and len(SONG_RMS) == TOTAL_F
BURSTS = FEAT9["bursts"]
for _b in BURSTS:
    _b["frame"] = TITLE_F + _b["hop"] / HPF
    _rng_b = np.random.default_rng(77000 + _b["hop"])
    _n = 36 if _b["hard"] else 14
    _d = _rng_b.normal(size=(_n, 3)); _d /= np.linalg.norm(_d, axis=1, keepdims=True)
    _b["dirs"] = _d
    _b["spd"] = (0.010 + 0.030 * _b["strength"]) * (0.45 + 0.55 * _rng_b.random(_n))
    _b["life"] = 26.0 if _b["hard"] else 16.0
print(f"features9: {len(BURSTS)} bursts ({sum(1 for b in BURSTS if b['hard'])} hard), "
      f"deepest hush9 window hops {FEAT9['meta']['hush_window']['hop0']}..{FEAT9['meta']['hush_window']['hop1']}", flush=True)
def sig_at(arr, h):
    h = min(max(float(h), 0.0), N_HOPS - 1.001)
    i = int(h); t = h - i
    return float(arr[i] * (1.0 - t) + arr[i + 1] * t)

# ---------- bundled font: Inter (SIL OFL 1.1, viz9/fonts/) ----------
_FONTDIR = os.environ.get("V9_FONTDIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT = _FONTDIR.rstrip("/") + "/"
F_TITLE = ImageFont.truetype(FONT + "Inter-Bold.ttf", 168)
F_OBL   = ImageFont.truetype(FONT + "Inter-MediumItalic.ttf", 84)
F_SUB   = ImageFont.truetype(FONT + "Inter-Regular.ttf", 72)
F_CALL  = ImageFont.truetype(FONT + "Inter-SemiBold.ttf", 66)
F_CARD  = ImageFont.truetype(FONT + "Inter-Bold.ttf", 90)
F_BIG   = ImageFont.truetype(FONT + "Inter-Bold.ttf", 136)
F_EVENT = ImageFont.truetype(FONT + "Inter-SemiBold.ttf", 84)
F_SHDR  = ImageFont.truetype(FONT + "Inter-Bold.ttf", 44)
F_SSUB  = ImageFont.truetype(FONT + "Inter-Regular.ttf", 30)
F_YEAR  = ImageFont.truetype(FONT + "Inter-SemiBold.ttf", 44)
F_CELLH = ImageFont.truetype(FONT + "Inter-SemiBold.ttf", 40)
F_CELLT = ImageFont.truetype(FONT + "Inter-Regular.ttf", 52)
F_CELLF = ImageFont.truetype(FONT + "Inter-Regular.ttf", 38)
F_LEG   = ImageFont.truetype(FONT + "Inter-Regular.ttf", 46)
F_COUNT = ImageFont.truetype(FONT + "LiberationMono-Regular.ttf", 54)  # W9b instrument readout (Liberation Mono, OFL)
print(f"fonts: Inter from {FONT}", flush=True)

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

# ---------- v9 chapters: era grading via radius + warmth only ----------
# Azimuth, RADM and hop chronology are untouched (the 5.0000 revolutions
# and the event tuning are v8-verbatim); chapters only breathe the
# camera radius (+-5%) and the background warmth, cross-faded slowly.
_CH_BOUNDS = [0.0] + [EVENTS[i]["frame"] for i in (0, 1, 2, 3, 5, 6)] + [float(TOTAL_F)]
_CH_R    = [0.96, 1.00, 1.05, 1.03, 0.94, 0.98, 1.00]   # First light / Widening / Quiet world /
_CH_WARM = [0.00, 0.10, -0.70, -0.90, 0.80, 0.30, 0.20]  # Invasion winter / Ignition / New name / Contact
def _chapter_series(vals):
    mid = [(_CH_BOUNDS[i] + _CH_BOUNDS[i + 1]) / 2 for i in range(len(vals))]
    xs = [0.0] + mid + [float(TOTAL_F - 1)]
    ys = [vals[0]] + list(vals) + [vals[-1]]
    s = np.interp(_fax, xs, ys)
    k = np.ones(201) / 201.0
    return np.convolve(np.pad(s, 100, mode="reflect"), k, mode="valid")[:TOTAL_F]
CH_R = _chapter_series(_CH_R)
CH_WARM = _chapter_series(_CH_WARM)

# ---------- v9 entropy weather: phase INTEGRATES the rate ----------
# v8 used phase = f * rate(f): whenever the weather changed, the boil
# pattern teleported. v9 integrates the instantaneous rate over frames.
_hop_grid = (np.clip(_fax, TITLE_F, MAIN_END_F) - TITLE_F) * HPF
ENT_FRAME = np.interp(_hop_grid, np.arange(N_HOPS, dtype=np.float64), ENT_SM9)
_boil_rate = 0.30 + 2.4 * ENT_FRAME
PHASE_BOIL = np.concatenate([[0.0], np.cumsum(_boil_rate[:-1])])
def boil_phase(ff):
    return float(np.interp(ff, _fax, PHASE_BOIL))
def song_e(ff):
    return float(np.interp(ff, _fax, SONG_RMS))

# ---------- CYOA thread: silver comets through the same space ----------
TRAV = json.load(open(f"{ROOT}/phext/traversal-map/cyoa-traversal.json"))
CYOA_N = len(TRAV["nodes"])                                   # 829 placed scrolls
cy_vals = np.array([[float(x) for part in n["coord"].split("/") for x in part.split(".")]
                    for n in TRAV["nodes"]], dtype=np.float64)
cy_proj = np.stack([cy_vals[:, 0:3].mean(1), cy_vals[:, 3:6].mean(1), cy_vals[:, 6:9].mean(1)], axis=1)
_lo = np.percentile(cy_proj, 0.5, axis=0); _hi = np.percentile(cy_proj, 99.5, axis=0)
_nlo = node_xyz.min(0); _nhi = node_xyz.max(0)
_cen = (_nlo + _nhi) / 2; _half = (_nhi - _nlo) / 2 * 1.08; _nlo, _nhi = _cen - _half, _cen + _half
CY = _nlo + (np.clip(cy_proj, _lo, _hi) - _lo) / (_hi - _lo) * (_nhi - _nlo)

def catmull_rom(p0, p1, p2, p3, t, tension=0.0):
    t2, t3 = t * t, t * t * t
    m1 = 0.5 * (1.0 - tension) * (p2 - p0)
    m2 = 0.5 * (1.0 - tension) * (p3 - p1)
    return ((2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1
            + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2)
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
    _o["lines"] = wrap(_o["text"], F_CELLT, 600, 5)
for _o in TOP20:
    print(f"strip rank {_o['rank']:2d} {_o['date']} echo {_o['echo']:3d} hop {_o['hop']:6.0f} "
          f"arrival frame {_o['arr_frame']:6.0f} | {_o['text'][:60]}", flush=True)
assert TOP20[-1]["arr_frame"] < MAIN_END_F, "last post arrives after the hops end"

# ---------- film strip: the top 20 flow along the right side ----------
# v9 (Will): the panel renders at 50% opacity so the field glows through;
# the masthead band stays near-opaque so no text bleeds above the header.
STRIP_W = 800                                   # 20.8% of the 3840 canvas
STRIP_X0 = W - STRIP_W
CELL_PITCH, CELL_H, CELL_TOP0 = 496, 462, 196
ARR_F = np.array([o["arr_frame"] for o in TOP20])
_TGT = np.maximum(0.0, np.arange(len(TOP20)) * CELL_PITCH + CELL_TOP0 + CELL_H - (H - 48))
_DT = np.diff(np.concatenate([[0.0], _TGT]))
def strip_offset(f):
    return float(np.sum(_DT * np.array([smooth(a, a + 26, f) for a in ARR_F])))
def strip_alpha(f):
    # fades IN as the first card arrives (no more empty rail over the
    # title), fully OUT before the CTA text begins (3554)
    return smooth(ARR_F[0] - 30, ARR_F[0] + 14, f) * (1.0 - smooth(3490, CTA_F0, f))
def draw_strip(dr, f):
    sa = strip_alpha(f)
    if sa <= 0.003: return
    # translucent panel: half of v8's alpha — the field glows through
    dr.rectangle([STRIP_X0, 0, W, H], fill=(5, 8, 14, int(84 * sa)))
    dr.line([STRIP_X0, 0, STRIP_X0, H], fill=(120, 220, 240, int(120 * sa)), width=3)
    dr.line([STRIP_X0 + 6, 0, STRIP_X0 + 6, H], fill=(120, 220, 240, int(30 * sa)), width=2)
    for yy in range(30, H - 40, 72):
        for xx in (STRIP_X0 + 22, W - 58):
            dr.rounded_rectangle([xx, yy, xx + 30, yy + 20], radius=6,
                                 fill=(160, 200, 220, int(26 * sa)))
    off = strip_offset(f)
    for i, o in enumerate(TOP20):
        if f < o["arr_frame"]: continue
        y = CELL_TOP0 + i * CELL_PITCH - off
        if y < -CELL_H or y > H: continue
        a_in = min((f - o["arr_frame"]) / 12.0, 1.0)
        newest = (f - o["arr_frame"]) < 34
        edge = int((190 if newest else 110) * sa * a_in)
        dr.rounded_rectangle([STRIP_X0 + 74, y, W - 84, y + CELL_H], radius=18,
                             fill=(10, 16, 26, int(120 * sa * a_in)),
                             outline=(140, 215, 235, edge), width=3)
        tx = STRIP_X0 + 96
        dr.text((tx, y + 24), o["label"], font=F_CELLH,
                fill=(206, 228, 240, int(240 * sa * a_in)))
        rk = f"no. {o['rank']} of 20"
        rw = dr.textlength(rk, font=F_CELLF)
        dr.text((W - 84 - 22 - rw, y + 26), rk, font=F_CELLF,
                fill=(150, 178, 200, int(220 * sa * a_in)))
        for li, ln in enumerate(o["lines"]):
            dr.text((tx, y + 92 + li * 64), ln, font=F_CELLT,
                    fill=(238, 244, 248, int(248 * sa * a_in)))
        dr.text((tx, y + CELL_H - 48), f"{o['echo']} echoes", font=F_CELLF,
                fill=(168, 196, 214, int(230 * sa * a_in)))
    # masthead LAST, on a FULLY opaque band: exiting cells slide under it
    # (245/255 still ghosted bright cell text through — Claude C9, verified
    # in the v9 hush still; 255 ends the bleed outright)
    dr.rectangle([STRIP_X0, 0, W, 180], fill=(5, 8, 14, int(255 * sa)))
    dr.line([STRIP_X0, 0, STRIP_X0, 180], fill=(120, 220, 240, int(150 * sa)), width=3)
    draw_spaced_left(dr, STRIP_X0 + 96, 54, "MOST ECHOED", F_SHDR,
                     (214, 236, 246, int(245 * sa)), 12)
    dr.text((STRIP_X0 + 96, 112), "Top 20 by echoes · in time order", font=F_SSUB,
            fill=(150, 182, 202, int(215 * sa)))
    # v9 year readout: small, right-aligned, lives in the masthead only
    _hop = hop_float(f)
    _yr = str(datetime.fromtimestamp(stab_ts[int(min(max(_hop, 0.0), N_HOPS - 1))],
                                     tz=timezone.utc).year)
    _yw = dr.textlength(_yr, font=F_YEAR)
    dr.text((W - 96 - _yw, 52), _yr, font=F_YEAR, fill=(168, 208, 226, int(225 * sa)))
    dr.line([STRIP_X0 + 96, 162, W - 96, 162], fill=(120, 220, 240, int(90 * sa)), width=2)

# ---------- walk the hops once: landings, counters, callouts ----------
node_idx_by_key = {}
for i, n in enumerate(NODES):
    node_idx_by_key.setdefault(n["key"], i)
# the excluded account is NEVER shown (v7 ruling, carried): both placed
# nodes dropped entirely; its replies remain in the aggregate hop stream.
EXCLUDE = {i for i, n in enumerate(NODES) if n["key"] == "oraiawake"}
assert len(EXCLUDE) == 2, EXCLUDE
WILL_NODE = next(i for i, n in enumerate(NODES) if n["kind"] == "will")

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
        elif hd == "wbic32":      callouts.append((h, "@wbic32", (198, 226, 228)))
        elif hd == "eshear":      callouts.append((h, "@eshear", (235, 226, 205)))
        elif hd == "grady_booch": callouts.append((h, "@Grady_Booch", (235, 226, 205)))
        # eigenhector is NOT here in v9: he is top mutual #17 and gets the
        # full mutual highlight instead (exactly one highlight each).
callouts.sort()
assert mat == N_MATCH and attempts_at[-1] == N_HOPS, (mat, attempts_at[-1])
print(f"prep: landings={len(land_pos)} placed_final={placed_at[-1]} callouts={len(callouts)}", flush=True)

# ---------- v9: top-20 mutual highlights (Will: each highlighted once) ----------
# The canonical top-20 mutuals by replies Will sent (2026-10-31 archive
# analysis). Each highlight sits at the landing that opens that person's
# densest +-150-hop landing window (their strongest arrival stretch),
# earliest on ties, at or after frame 150 so none hides under the title.
MUTUALS = [("ctzn5", 188), ("madeofmistak3", 187), ("bitcloud", 174), ("dakami", 161),
           ("vveeveeanna", 134), ("viemccoy", 116), ("wordgrammer", 106), ("prmshra", 106),
           ("mimi10v3", 102), ("jaivinwylde", 100), ("megs_io", 97), ("jaelruble", 92),
           ("sporadicalia", 88), ("heyellieday", 86), ("1mortrix", 83), ("djcows", 83),
           ("eigenhector", 79), ("eloffd", 77), ("ki11switch03", 73), ("izzyz", 72)]
land_frame = np.array([TITLE_F + h / HPF for h in land_hop])
_hop_to_j = {h: j for j, h in enumerate(land_hop)}
_landings_by_node = {}
for _j, _h in enumerate(land_hop):
    _s = STABS[_h]
    if _s["typ"] == 1:
        _landings_by_node.setdefault(_s["node"], []).append(_h)
HIGHLIGHTS = []          # dicts: handle, node, hop, j, frame, label
MUT_ARC = {}             # landing index j -> highlight record
for _handle, _cnt in MUTUALS:
    _ni = node_idx_by_key[_handle]
    _hs = np.array(_landings_by_node.get(_ni, []), dtype=np.float64)
    assert len(_hs) > 0, f"mutual {_handle} has no type-1 landing"
    _best = None
    for _h in _hs:
        if TITLE_F + _h / HPF < 150: continue
        _dens = int((( _hs >= _h - 150) & (_hs <= _h + 150)).sum())
        if _best is None or _dens > _best[1]: _best = (int(_h), _dens)
    _hop = _best[0]; _j = _hop_to_j[_hop]
    _nm = NODES[_ni]["name"]
    _label = _nm if _nm.startswith("@") else f"@{_handle}"
    _rec = dict(handle=_handle, node=_ni, hop=_hop, j=_j,
                frame=float(land_frame[_j]), label=_label, replies=_cnt, density=_best[1])
    HIGHLIGHTS.append(_rec); MUT_ARC[_j] = _rec
    print(f"highlight @{_handle}: node {_ni} hop {_hop} frame {_rec['frame']:.0f} "
          f"(density {_best[1]}, {len(_hs)} landings)", flush=True)
assert len(HIGHLIGHTS) == 20 and len(MUT_ARC) == 20
def highlight_env(ff, rec):
    age = ff - rec["frame"]
    if age < 0 or age >= 90: return 0.0
    return smooth(0, 10, age) * (1.0 - smooth(65, 90, age))
def card_pulse(ff):
    """(env, arr_frame) of the strongest live Most-Echoed arrival pulse."""
    env, af = 0.0, -1.0
    for o in TOP20:
        age = ff - o["arr_frame"]
        if 0 <= age < 60:
            e = math.exp(-age / 14.0)
            if e > env: env, af = e, o["arr_frame"]
    return env, af

# ---------- opening legend (v9 judgment call #1 — see BUILD-NOTES) ----------
LEGEND = [("dot",  "a dot is a person"),
          ("line", "a gold line is a reply that reached them"),
          ("silver", "the silver thread is CYOA — a book of choices"),
          ("sun",  "the moving light is Will, writing")]
def legend_env(ff):
    if ff < 120 or ff >= 336: return 0.0
    return smooth(120, 150, ff) * (1.0 - smooth(296, 336, ff)) * 0.96

# ---------- v9 Chunk B (W9b): process counter envelope ----------
# The wavefront's work is the 18,762 hops; the counter reads them
# remaining and counts down as they land, reaching 0 at the final hop
# (frame 3362). It fades in as the title releases and out before the
# CTA — the work is complete when the card arrives.
def counter_env(ff):
    return smooth(48, 96, ff) * (1.0 - smooth(3380, 3500, ff))

# v9 audit: no on-screen string may name the excluded account or the dropped region
_ALL_TEXT = ([c[1] for c in callouts] + [e["caption"] for e in EVENTS]
             + [o["text"] for o in TOP20] + [r["label"] for r in HIGHLIGHTS]
             + [t for _, t in LEGEND]
             + ["THE EXOCORTEX", "Shaken yet Stirred", "a map of alignment",
                "the future has arrived", "MOST ECHOED",
                "Top 20 by echoes · in time order",
                "520 people are already in this map.",
                "Find your coordinate. Claim your space.", "edit.phext.io",
                "Not in the map yet? The door is open.",
                "CONTACTS REMAINING"])
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
def _interp3(arr, ff):
    return np.array([float(np.interp(ff, _fax, arr[:, k])) for k in range(3)])
def camera(ff):
    hop = hop_float(ff)
    pull = smooth(PULL_F, CTA_F0, ff)
    R = 2.225 * (1.0 + 0.035 * math.sin(2 * math.pi * (ff - TITLE_F) / (FPS * 45.0)))  # 2x zoom
    R = R * float(np.interp(ff, _fax, RADM)) * float(np.interp(ff, _fax, CH_R))       # events + chapters
    R = R * (1 - pull) + 6.8 * pull                       # pull-back reveals the field
    az = 2.45 + float(np.interp(ff, _fax, AZIM6))         # several full revolutions, event-tuned
    el = math.radians(23.0 * (1 - pull) + 19.0 * pull)
    pos = CORE + R * np.array([math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)])
    look = _interp3(LOOK, ff) * (1 - pull) + CORE * pull
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

def soft_knee(a):
    """v9 tone map: identity below 200, smooth tanh shoulder above, so
    additive overlaps roll off toward 255 instead of hard-clipping into
    a flat white blob (Grok's blow-out note). C1-continuous at 200."""
    return np.where(a <= 200.0, a, 200.0 + 55.0 * np.tanh((a - 200.0) / 55.0))

CX_CUR = W / 2   # projection centre for the current frame (set per-frame in render)

# ---------- v9 Chunk B (W7): light snow replaces the CMB ----------
# Will (2026-11-04): "the CMB should be more like a light snow
# effect." The mottled CMB grain field and the entropy boil are GONE.
# In their place: sparse soft specks in two depth layers over a faint
# drifting haze, held at the W5 darkness budget — the layer's mean
# luma is measured against A2's darkened-CMB numbers with the same
# V9_BG_DUMP hook (see BUILD-NOTES, Chunk B).
# DETERMINISM RULE (the E3 lesson): every snow position is a pure
# function of (particle id, frame ff). The weather enters through two
# PRECOMPUTED cumulative clocks — integrals of per-frame rates, never
# per-render accumulated state — so any chunk context renders any
# frame byte-identically.
HUSH_FRAME = np.interp(_hop_grid, np.arange(N_HOPS, dtype=np.float64), HUSH9_HOP)
_gust = np.zeros(TOTAL_F)
for _b in BURSTS:
    _sg = max(6.0, 0.8 * _b["life"])
    _gust += _b["strength"] * np.exp(-((_fax - _b["frame"]) / _sg) ** 2)
GUST_F = np.minimum(_gust, 1.2)                       # brief gusts at bursts, capped
# wind: turbulence (residual entropy) drifts the snow sideways and a
# touch faster; hush lets fall and sway decay toward near-still.
_wind_rate = (0.30 + 1.60 * ENT_FRAME + 0.90 * GUST_F) * (1.0 - 0.80 * HUSH_FRAME)
_fall_rate = (1.00 + 0.45 * ENT_FRAME + 0.55 * GUST_F) * (1.0 - 0.88 * HUSH_FRAME)
WINDCLK = np.concatenate([[0.0], np.cumsum(_wind_rate[:-1])])
FALLCLK = np.concatenate([[0.0], np.cumsum(_fall_rate[:-1])])
def wind_clock(ff): return float(np.interp(ff, _fax, WINDCLK))
def fall_clock(ff): return float(np.interp(ff, _fax, FALLCLK))
# haze: three huge soft glow fields (distant snow-mist), computed on a
# 480x270 grid and upsampled. W10 demoted the whole layer: the haze
# survives only as a faint remnant so the field never falls to a flat
# void — the W8 film grain carries the dark field's texture now, and
# the snow itself is a sparse whisper (117 specks, ~25% of the first
# Chunk B pass, and dimmer).
HZ_W, HZ_H = 480, 270
_hzx, _hzy = np.meshgrid(np.arange(HZ_W, dtype=np.float32), np.arange(HZ_H, dtype=np.float32))
HZ_BLOBS = [  # cx, cy (grid px), sigma, amp, drift per wind-clock unit, bob amp, bob period, bob phase
    (0.20 * HZ_W, 0.30 * HZ_H, 95.0, 0.55, 0.012, 5.0, 1150.0, 0.7),
    (0.66 * HZ_W, 0.56 * HZ_H, 118.0, 0.42, 0.009, 7.0, 1490.0, 2.4),
    (0.44 * HZ_W, 0.80 * HZ_H, 74.0, 0.34, 0.015, 4.0, 930.0, 4.4),
]
HAZE_AMP = 0.045
HAZE_COL = np.array([146.0, 170.0, 212.0], dtype=np.float32)   # cool moonlit wash
def _snow_haze(ff, wc):
    fld = np.zeros((HZ_H, HZ_W), dtype=np.float32)
    for cx0, cy0, sg, amp, drift, bamp, bper, bph in HZ_BLOBS:
        cx = (cx0 + drift * wc + sg) % (HZ_W + 2 * sg) - sg
        cy = cy0 + bamp * math.sin(2 * math.pi * ff / bper + bph)
        fld += amp * np.exp(-(((_hzx - cx) ** 2 + (_hzy - cy) ** 2) / (2 * sg * sg))).astype(np.float32)
    im = Image.fromarray(np.clip(fld * 255.0, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255.0
# specks: two depth layers. far = finer, slower, dimmer; near = a
# touch larger, faster, brighter. Kernel sigmas are at 4K; the visible
# cores land at ~1.3 px (far) and ~2.2 px (near) at 1080p delivery.
_snrng = np.random.default_rng(20261104)
def _snow_layer(n, kern, col, g0, vfall, drift, samp_lo, samp_hi):
    return dict(x0=_snrng.uniform(0, W, n), y0=_snrng.uniform(0, H, n),
                samp=_snrng.uniform(samp_lo, samp_hi, n), sper=_snrng.uniform(130.0, 330.0, n),
                sph=_snrng.uniform(0, 2 * math.pi, n), ajit=_snrng.uniform(0.75, 1.25, n),
                kern=kern, col=col, g0=g0, v=vfall, drift=drift)
SNOW_FAR = _snow_layer(75, kernel(11, 1.3), (186, 204, 232), 0.20, 0.90, 0.35, 2.5, 6.5)
SNOW_NEAR = _snow_layer(42, kernel(19, 2.3), (216, 230, 248), 0.30, 1.90, 0.62, 5.0, 11.0)
SNOW_LAYERS = (SNOW_FAR, SNOW_NEAR)
def snow_layer(ff, gain, hush_f, miss_frac):
    """The whole background weather layer for sub-frame ff: a faint
    haze remnant + the snow whisper, a float (H, W, 3) addend over
    BASE_BG. The haze condenses as the archive accumulates (the
    miss-fraction ramp), a last trace of the old CMB arc; in hush
    the fall/sway clocks themselves nearly stop, so the snow hangs."""
    wc = wind_clock(ff); fc = fall_clock(ff)
    haze_gain = HAZE_AMP * gain * (0.42 + 0.58 * min(miss_frac / 0.30, 1.0))
    arr = (_snow_haze(ff, wc) * haze_gain)[:, :, None] * HAZE_COL[None, None, :]
    sway_mul = 1.0 - 0.80 * hush_f
    gscale = 0.50 + 0.50 * gain
    for L in SNOW_LAYERS:
        y = np.mod(L["y0"] + L["v"] * fc, H)
        x = np.mod(L["x0"] + L["drift"] * wc
                   + L["samp"] * sway_mul * np.sin(2 * math.pi * ff / L["sper"] + L["sph"]), W)
        g = L["g0"] * gscale
        kern, col, aj = L["kern"], L["col"], L["ajit"]
        for i in range(len(x)):
            stamp(arr, x[i], y[i], kern, col, g * aj[i])
    return arr
print(f"snow: {sum(len(L['x0']) for L in SNOW_LAYERS)} specks in {len(SNOW_LAYERS)} layers, "
      f"haze amp {HAZE_AMP}, wind clock total {WINDCLK[-1]:.0f}, fall clock total {FALLCLK[-1]:.0f}", flush=True)
BASE_BG = np.array([2.0, 3.0, 7.0], dtype=np.float32)   # deeper future-tech black
# v9: fixed film grain (one seeded field for every frame — determinism
# across render chunks) + a vignette; the grain also dithers the dark
# gradients so the encode stops banding
GRAIN = (np.random.default_rng(4242).normal(0.0, 2.0, (H, W, 1))).astype(np.float32)
_vx = (np.arange(W) - W * 0.42) / (W * 0.66); _vy = (np.arange(H) - H * 0.5) / (H * 0.66)
VIG = (1.0 - 0.30 * np.clip(_vx[None, :] ** 2 + _vy[:, None] ** 2, 0, 1) ** 1.5).astype(np.float32)[:, :, None]
# v9: parallax star shells — world-locked points on three distant
# spheres, projected through the camera every frame (v8 painted stars
# in screen space: no parallax at all)
_srng = np.random.default_rng(777)
STAR_SHELLS = []
for _rad, _cnt, _g in ((26.0, 210, 0.50), (48.0, 140, 0.34), (95.0, 80, 0.22)):
    _d = _srng.normal(size=(_cnt, 3)); _d /= np.linalg.norm(_d, axis=1, keepdims=True)
    STAR_SHELLS.append((CORE[None, :] + _d * _rad, _g))
cum_miss = attempts_at - matches_at
miss_gain = cum_miss / max(1, cum_miss[-1])

NODE_BASE = {"detected": ((104, 124, 160), 0.24), "mutual": ((132, 158, 198), 0.34),
             "named": ((158, 184, 218), 0.36), "wbic32": ((126, 176, 182), 0.36),
             "will": ((255, 190, 70), 0.8)}
FOG_COL = np.array([26.0, 34.0, 52.0])
def node_color(n):
    return NODE_BASE[n["kind"]][0]
def depth_att(zc):
    return float(min(1.25, max(0.45, (2.3 / max(float(zc), 0.3)) ** 1.1)))
def fog_mix(col, zc):
    f = min(0.5, max(0.0, (float(zc) - 2.3) / 4.0))
    c = np.array(col, dtype=np.float64)
    return tuple(int(x) for x in (c * (1 - f) + FOG_COL * f))

def bezier_arc9(p0, p1, u_max=1.0, bow_scale=1.0, jit_mag=0.0):
    """v9 arc: bow and lateral wobble driven by the landing tweet's own
    length-residualized entropy. The control point is built in WORLD
    space from the world up-vector — v8 built it from the camera's
    forward vector, so every connection's geometry changed as the
    camera moved. Here the camera only projects; it never shapes."""
    chord = p1 - p0; L = np.linalg.norm(chord)
    if L < 1e-6: return None
    u = chord / L
    perp = np.cross(u, np.array([0.0, 0.0, 1.0])); nn = np.linalg.norm(perp)
    if nn < 1e-4:
        perp = np.cross(u, np.array([1.0, 0.0, 0.0])); nn = np.linalg.norm(perp)
    perp = perp / nn
    perp2 = np.cross(u, perp); n2 = np.linalg.norm(perp2)
    perp2 = perp2 / n2 if n2 > 1e-4 else np.array([0.0, 0.0, 1.0])
    ctrl = (p0 + p1) / 2 + perp * ((0.22 * L + 0.045) * bow_scale) + perp2 * jit_mag
    ts = np.linspace(0, u_max, max(2, int(18 * u_max) + 1))
    return ((1 - ts) ** 2)[:, None] * p0 + (2 * (1 - ts) * ts)[:, None] * ctrl + (ts ** 2)[:, None] * p1

NODE_FIRST_HOP = np.full(len(NODES), 10**9, dtype=int)
for _j, _h in enumerate(land_hop):
    _s = STABS[_h]
    if _s["typ"] == 1 and _h < NODE_FIRST_HOP[_s["node"]]:
        NODE_FIRST_HOP[_s["node"]] = _h
land_prev = np.vstack([np.zeros(3), CP[:-1]])
land_toneb = np.array([0.72 + 0.5 * tone_norm(h) for h in land_hop])
HN9_LAND = np.array([HN9_HOP[h] for h in land_hop])
JIT_LAND = np.array([(int.from_bytes(hashlib.md5(f"jit{h}".encode()).digest()[:8], "little")
                      / 2**64) * 2.0 - 1.0 for h in land_hop])

# ---------- v9 A2: stable micro-shells around the mutual clusters ----------
# clusters9.json is derived data (derive_clusters.py): DBSCAN over the
# placed mutuals in THIS xyz space — 7 clusters, 103 of 153 placed
# mutuals; noise points and clusters < 4 get no shell. One ellipsoid
# per cluster: centre = member mean, axes = covariance eigenvectors,
# semi-axes = 2*sqrt(eigenvalues) (floored/capped at derive time).
# The shells are WORLD-LOCKED: centre and axis endpoints ride the same
# to_world transform as the nodes every frame. STABILITY RULE: no
# entropy, boil, hush, cohesion or pulse term ever modulates a shell —
# they are the still geometry the weather moves against.
CLUST9 = json.load(open(f"{BASE}/viz9/clusters9.json"))
SHELLS = []
for _s in CLUST9["shells"]:
    _mem = np.array(_s["members"], dtype=int)
    SHELLS.append(dict(center=np.array(_s["center"], dtype=np.float64),
                       axes=np.array(_s["axes"], dtype=np.float64),
                       semi=np.array(_s["semi"], dtype=np.float64),
                       members=_mem,
                       first_hops=NODE_FIRST_HOP[_mem].astype(np.float64),
                       size=int(_s["size"])))
SHELL_COL = np.array([158.0, 180.0, 208.0], dtype=np.float32)  # desaturated silver-cool
SHELL_FILL, SHELL_RIM = 0.045, 0.17      # rim band carries the light (fresnel-style)
print(f"shells: {len(SHELLS)} mutual clusters, {sum(s['size'] for s in SHELLS)} members "
      f"(eps {CLUST9['meta']['eps']}, min_samples {CLUST9['meta']['min_samples']})", flush=True)

# ---------- v9 Chunk B (W9a): dotted orbital rings around the shells ----------
# Transplanted from a protein-structure film (Will, 00:51): each shell
# carries 2-3 dotted orbit rings, tilted at differing angles, radius
# 1.16-1.34x the shell's widest semi-axis, in the cool silver
# instrument colour at very low alpha — instrumentation, not
# decoration. The dots drift slowly along each ring (periods of
# ~2,600-4,000 frames, alternating direction), a closed-form function
# of ff; the rings share their shell's world-lock and fade-in rule.
K_DOT = kernel(9, 1.6)
RING_COL = (168, 192, 218)
RING_A = 0.13
_RING_TILTS = [(0.9, 0.4), (2.2, 1.1), (4.0, 2.2)]      # (theta, phi) in the shell frame
_RING_F = (1.16, 1.25, 1.34)                             # radius x max semi-axis
RINGS = []
for _ci, _sh in enumerate(SHELLS):
    _ax = _sh["axes"]                                    # rows: principal axes
    _smax = float(np.max(_sh["semi"]))
    _nr = 3 if _sh["size"] >= 13 else 2
    _rl = []
    for _k in range(_nr):
        _th, _ph = _RING_TILTS[_k]
        _th += 0.7 * _ci                                 # each cluster's set turned a little
        _n = np.array([math.sin(_ph) * math.cos(_th), math.sin(_ph) * math.sin(_th), math.cos(_ph)])
        _nw = _ax.T @ _n                                 # ring normal, world coords
        _nw = _nw / np.linalg.norm(_nw)
        _u = np.cross(_nw, _ax[0])
        if np.linalg.norm(_u) < 1e-4: _u = np.cross(_nw, _ax[1])
        _u = _u / np.linalg.norm(_u)
        _v = np.cross(_nw, _u)
        _r = _RING_F[_k] * _smax
        _nd = int(min(84, max(36, round(2 * math.pi * _r / 0.055))))
        _per = (2600.0 + 700.0 * _k) * (1.0 if _k % 2 == 0 else -1.0)
        _rl.append(dict(u=_u, v=_v, r=_r, nd=_nd, per=_per))
    RINGS.append(_rl)
print(f"rings: {sum(len(r) for r in RINGS)} dotted orbits over {len(RINGS)} shells", flush=True)
def shell_fade(sh, hop):
    """Fade-in rule: a shell condenses as its people arrive — invisible
    below 30% of members landed (by first-landing hop), full at 55%."""
    if hop <= 0: return 0.0
    frac = float(np.mean(sh["first_hops"] <= hop))
    return smooth(0.30, 0.55, frac)

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

def render_single(ff):
    """One sub-frame at continuous time ff (float frames — the wrapper
    averages three of these per output frame for temporal AA)."""
    global CX_CUR, AMP_F
    CX_CUR = (STRIP_X0 / 2) + (W / 2 - STRIP_X0 / 2) * smooth(PULL_F, CTA_F0, ff)
    hop = hop_float(ff)
    hi = int(min(N_HOPS, math.floor(hop)))
    ENT_F = sig_at(ENT_SM9, hop); HUSH_F = sig_at(HUSH9_HOP, hop); COH_F = sig_at(COH_HOP, hop)
    AMP_F = (0.75 + 0.80 * ENT_F) * (1.0 - 0.30 * HUSH_F)
    HARD_NOW = any(b["hard"] and 0.0 <= ff - b["frame"] < 8.0 for b in BURSTS)
    cam = camera(ff)
    CPULSE, CPULSE_AF = card_pulse(ff)
    # --- background: space + light snow (W7); chapter warmth; vignette; grain
    gain = (0.30 + 0.70 * float(miss_gain[hi])) * (1.0 + 0.35 * ENT_F) * (1.0 - 0.30 * HUSH_F)
    arr = BASE_BG[None, None, :] + snow_layer(ff, gain, HUSH_F, float(miss_gain[hi]))
    _wch = float(np.interp(ff, _fax, CH_WARM))
    arr = arr * np.array([1 + 0.05 * _wch, 1 + 0.01 * _wch, 1 - 0.04 * _wch], dtype=np.float32)[None, None, :]
    arr = arr * VIG + GRAIN
    _bgd = os.environ.get("V9_BG_DUMP")
    if _bgd and abs(ff - round(ff)) < 1e-6:
        os.makedirs(_bgd, exist_ok=True)
        np.save(f"{_bgd}/bg{int(round(ff))}.npy", arr)
    if CPULSE > 0.02:
        arr *= (1.0 - 0.16 * CPULSE)     # the field holds its breath for a card
    # --- parallax stars: world-locked shells through the camera
    for _pts_s, _g_s in STAR_SHELLS:
        _sx, _sy, _sz, _sok = project(_pts_s, cam)
        for _i in range(len(_pts_s)):
            if _sok[_i]:
                stamp(arr, _sx[_i], _sy[_i], K_BASE, (198, 212, 234), _g_s * depth_att(_sz[_i]))
    # --- v9 A2: mutual micro-shells (W6). Each shell is its cluster's
    # covariance ellipsoid: centre + the three axis endpoints are taken
    # through to_world and the camera; the screen silhouette is the
    # image of the unit ball under the 2x3 map of projected axis
    # vectors (E2 = sum_k v_k v_k^T), filled near-transparent with a
    # gaussian rim band at the silhouette — where the surface turns
    # away — carrying the light (fresnel-style). Painted far-to-near
    # (depth-sorted by centre depth) UNDER nodes and trace, so nearer
    # clusters read nearer and the cluster's own people shine through.
    # STABLE by rule: no ENT/HUSH/COH/pulse term appears in this block;
    # the only time-dependence is the world's own transform and the
    # arrival fade-in (shell_fade).
    _sh_order = []
    for _shi, _sh in enumerate(SHELLS):
        _fade = shell_fade(_sh, hop)
        if _fade <= 0.003: continue
        _cen_b = _sh["center"]
        _ep_b = _cen_b[None, :] + _sh["axes"] * _sh["semi"][:, None]
        _w = to_world(np.vstack([_cen_b[None, :], _ep_b]), ff, hop)
        _sx, _sy, _sz, _sok = project(_w, cam)
        if not _sok[0]: continue
        _sh_order.append((float(_sz[0]), _fade, _sx, _sy, _shi, _cen_b))
    _sh_order.sort(key=lambda t: -t[0])          # far first (stable sort)
    for _zc_sh, _fade, _sx, _sy, _shi, _cen_b in _sh_order:
        # v9 Chunk B (W9a): this shell's dotted orbital rings — same
        # paint order (far-to-near, under nodes/trace), same fade;
        # the dots drift slowly along each ring, closed-form in ff
        for _ring in RINGS[_shi]:
            _ts = 2 * math.pi * (np.arange(_ring["nd"]) / _ring["nd"] + ff / _ring["per"])
            _pw = _cen_b[None, :] + _ring["r"] * (np.cos(_ts)[:, None] * _ring["u"][None, :]
                                                  + np.sin(_ts)[:, None] * _ring["v"][None, :])
            _rx, _ry, _rz, _rok = project(to_world(_pw, ff, hop), cam)
            for _di in range(_ring["nd"]):
                if _rok[_di]:
                    stamp(arr, _rx[_di], _ry[_di], K_DOT, RING_COL,
                          RING_A * _fade * depth_att(_rz[_di]))
        _vs = [np.array([_sx[1 + _k] - _sx[0], _sy[1 + _k] - _sy[0]]) for _k in range(3)]
        _E2 = sum(np.outer(_v, _v) for _v in _vs)
        _det = float(_E2[0, 0] * _E2[1, 1] - _E2[0, 1] ** 2)
        if _det < 4.0: continue                  # degenerate sliver this frame
        _rx = math.sqrt(max(float(_E2[0, 0]), 1.0)); _ry = math.sqrt(max(float(_E2[1, 1]), 1.0))
        _x0 = max(0, int(_sx[0] - _rx) - 2); _x1 = min(W, int(_sx[0] + _rx) + 3)
        _y0 = max(0, int(_sy[0] - _ry) - 2); _y1 = min(H, int(_sy[0] + _ry) + 3)
        if _x1 <= _x0 or _y1 <= _y0: continue
        _inv = np.array([[_E2[1, 1], -_E2[0, 1]], [-_E2[0, 1], _E2[0, 0]]]) / _det
        _gx = (np.arange(_x0, _x1) - _sx[0]).astype(np.float32)
        _gy = (np.arange(_y0, _y1) - _sy[0]).astype(np.float32)
        _q2 = (_inv[0, 0] * _gx[None, :] ** 2
               + 2.0 * _inv[0, 1] * _gx[None, :] * _gy[:, None]
               + _inv[1, 1] * _gy[:, None] ** 2).astype(np.float32)
        _in = _q2 <= 1.0
        if not _in.any(): continue
        _rim = np.exp(-(((1.0 - np.sqrt(np.maximum(_q2, 0.0))) / 0.16) ** 2))
        _att = min(1.0, max(0.55, depth_att(_zc_sh)))
        _fm = min(0.5, max(0.0, (_zc_sh - 2.3) / 4.0))          # same fog law as the nodes
        _col = SHELL_COL * (1 - _fm) + FOG_COL * _fm
        _a = ((SHELL_FILL + SHELL_RIM * _rim) * _fade * _att).astype(np.float32)
        _a[~_in] = 0.0
        _reg = arr[_y0:_y1, _x0:_x1]
        arr[_y0:_y1, _x0:_x1] = _reg * (1.0 - _a[:, :, None]) + _col[None, None, :] * _a[:, :, None]
    # --- nodes, with depth attenuation + atmospheric perspective
    POS_NOW = node_pos_all(node_hop(ff))
    nodes_w = to_world(POS_NOW, ff, hop)
    nsx, nsy, nzc, nok = project(nodes_w, cam)
    k = int(np.searchsorted(land_hop, hi, side="right"))
    landed = NODE_FIRST_HOP <= hi
    HUSH_NODE = 1.0 - 0.40 * HUSH_F
    for i, n in enumerate(NODES):
        if i in EXCLUDE or not nok[i]: continue
        col = fog_mix(node_color(n), nzc[i]); att = depth_att(nzc[i])
        if landed[i]:
            stamp(arr, nsx[i], nsy[i], K_BRIGHT, col, 0.66 * att * HUSH_NODE)
            cx, cy = int(round(nsx[i])), int(round(nsy[i]))
            if 2 <= cx < W - 2 and 2 <= cy < H - 2:
                arr[cy-1:cy+2, cx-1:cx+2] = np.maximum(arr[cy-1:cy+2, cx-1:cx+2],
                                                       np.array(col, np.float32))
        else:
            stamp(arr, nsx[i], nsy[i], K_BASE, col,
                  NODE_BASE.get(n["kind"], ((104, 124, 160), 0.16))[1] * att * HUSH_NODE)
    # --- core glow, soft. v9: held to an ember while the title is up so
    # no bright sun sits inside the title text (Claude C10e), igniting
    # as the hops begin.
    TG = 0.22 + 0.78 * smooth(TITLE_F, 130, ff)
    kgx, kgy, kgz, kgok = project(CORE[None, :], cam)
    if kgok[0]:
        stamp(arr, kgx[0], kgy[0], K_HALO, (255, 238, 205), 0.22 * TG)
        stamp(arr, kgx[0], kgy[0], K_CORE, (255, 240, 210), 0.62 * TG)
    # --- Most Echoed card arrival: Will's node pulses (the author is Will)
    WWXY = None
    if CPULSE > 0.02 and ff < CTA_F0:
        _wx, _wy, _wz, _wok = project(to_world(POS_NOW[WILL_NODE], ff, hop), cam)
        if _wok[0]:
            WWXY = (float(_wx[0]), float(_wy[0]), True)
            stamp(arr, _wx[0], _wy[0], K_HALO, (255, 214, 130), 0.50 * CPULSE)
            stamp(arr, _wx[0], _wy[0], K_CORE, (255, 226, 160), 0.45 * CPULSE)
    # --- top-mutual highlight pulses (float stamps; ring + label later)
    HLIVE = []
    for rec in HIGHLIGHTS:
        env = highlight_env(ff, rec)
        if env > 0.01:
            HLIVE.append((rec, env))
            _hx, _hy, _hz, _hok = project(to_world(POS_NOW[rec["node"]], ff, hop), cam)
            rec["_xy"] = (float(_hx[0]), float(_hy[0]), bool(_hok[0]))
            if _hok[0]:
                stamp(arr, _hx[0], _hy[0], K_HALO, (255, 236, 190), 0.55 * env)
                stamp(arr, _hx[0], _hy[0], K_MARK, (255, 244, 214), 0.80 * env)
    # --- scatter bursts: a harsh shouted spike sprays particles at its own
    #     hop position; the spray is drawn back to the origin by design
    for b in BURSTS:
        age = ff - b["frame"]
        if age < 0 or age > b["life"]: continue
        _sb = STABS[b["hop"]]
        org = POS_NOW[_sb["node"]] if b["typ"] == 1 else np.array(_sb["at"]) + np.array(_sb["off"])
        ow = to_world(org, ff, hop)
        u = age / b["life"]
        disp = b["spd"] * (b["life"] * 2.2 / math.pi) * math.sin(math.pi * u)
        pts = ow + b["dirs"] * disp[:, None]
        px, py, pz, pok = project(pts, cam)
        g = (1.0 - u) * (0.55 + 0.45 * b["strength"])
        col = (255, 240, 214) if b["hard"] else (255, 226, 178)
        kern = K_BRIGHT if b["hard"] else K_BASE
        for _pi in range(len(disp)):
            if pok[_pi]:
                stamp(arr, px[_pi], py[_pi], kern, col, float(g) * depth_att(pz[_pi]))
        if b["hard"] and age < 7:
            osx, osy, _, ook = project(ow, cam)
            if ook[0]:
                stamp(arr, osx[0], osy[0], K_MARK, (255, 244, 220), (1.0 - age / 7.0) * 0.85)
    # --- comet heads (glow); tails go on the PIL layer
    comets = comet_state(ff)
    for pts, fade in comets:
        if fade <= 0.01: continue
        hw = to_world(pts[-1], ff, hop)
        hsx, hsy, hz_, hok = project(hw, cam)
        if hok[0]:
            stamp(arr, hsx[0], hsy[0], K_BRIGHT, SILVER_HEAD, 0.7 * fade * depth_att(hz_[0]))
    # --- PIL layer: CYOA thread, comet tails, rings, golden trace, arcs
    layer = Image.fromarray(np.clip(soft_knee(arr), 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(layer, "RGBA")
    cyw = to_world(CY, ff, hop)
    csx, csy, _, cok = project(cyw, cam)
    for i in range(CYOA_N - 1):
        if cok[i] and cok[i + 1]:
            dr.line([csx[i], csy[i], csx[i + 1], csy[i + 1]], fill=SILVER_DIM + (15,), width=3)
    dr.point([(csx[i], csy[i]) for i in range(CYOA_N) if cok[i]], fill=SILVER_DIM + (44,))
    for pts, fade in comets:
        if fade <= 0.01: continue
        pw = to_world(pts, ff, hop)
        psx, psy, _, pok = project(pw, cam)
        nseg = len(pts) - 1
        for j in range(nseg):
            if not (pok[j] and pok[j + 1]): continue
            if (psx[j + 1] - psx[j]) ** 2 + (psy[j + 1] - psy[j]) ** 2 > 390 ** 2: continue
            u = (j + 1) / nseg
            a = int(120 * fade * u ** 2.2)
            col = tuple(int(SILVER[c] + (SILVER_HEAD[c] - SILVER[c]) * u) for c in range(3))
            dr.line([psx[j], psy[j], psx[j + 1], psy[j + 1]], fill=col + (a,), width=6 if u > 0.8 else 3)
    # event ripples: each world event sends a visible ring through the map
    if kgok[0]:
        for e in EVENTS:
            age = ff - e["cap_start"]
            if 0 <= age < 56:
                for _delay, _spd, _amax in ((0.0, 13.0, 100), (14.0, 9.0, 55)):
                    _a2 = age - _delay
                    if _a2 > 0:
                        _r = _a2 * _spd
                        _al = _amax * (1.0 - _a2 / (56.0 - _delay))
                        _ex, _ey = float(kgx[0]), float(kgy[0])
                        dr.ellipse([_ex - _r, _ey - _r, _ex + _r, _ey + _r],
                                   outline=(170, 220, 235, int(_al)), width=4)
    # card pulse ring at Will's node
    if CPULSE > 0.05 and ff < CTA_F0 and WWXY:
        _r = 24 + (ff - CPULSE_AF) * 4.5
        dr.ellipse([WWXY[0] - _r, WWXY[1] - _r, WWXY[0] + _r, WWXY[1] + _r],
                   outline=(255, 214, 130, int(120 * CPULSE)), width=4)
    # highlight rings at the mutuals' nodes
    for rec, env in HLIVE:
        _xy = rec.get("_xy")
        if _xy and _xy[2]:
            _r = 22 + (ff - rec["frame"]) * 3.1
            dr.ellipse([_xy[0] - _r, _xy[1] - _r, _xy[0] + _r, _xy[1] + _r],
                       outline=(255, 214, 130, int(140 * env)), width=5)
    # hard-burst shockwave rings
    for b in BURSTS:
        if not b["hard"]: continue
        age = ff - b["frame"]
        if 0 <= age < 14:
            _sb = STABS[b["hop"]]
            org = POS_NOW[_sb["node"]] if b["typ"] == 1 else np.array(_sb["at"]) + np.array(_sb["off"])
            _ox, _oy, _, _ook = project(to_world(org, ff, hop), cam)
            if _ook[0]:
                _r = 20 + age * 7.5
                _fx, _fy = float(_ox[0]), float(_oy[0])
                dr.ellipse([_fx - _r, _fy - _r, _fx + _r, _fy + _r],
                           outline=(255, 240, 214, int(120 * (1 - age / 14.0))), width=5)
    # golden trace (spline verts born by hop) — v9: AGE-GRADED. History
    # subsides, recent arrivals carry the light, everything is preserved.
    upto = int(np.searchsorted(VH, hop, side="right")) - 1
    HUSH_DIM = 1.0 - 0.80 * HUSH_F       # in hush the foreground itself clears
    if upto > 0:
        idxs = list(range(upto))
        if upto > 3400:
            keep = sorted(set(idxs[-800:]) | set(idxs[:: math.ceil((upto - 800) / 2400)]))
            idxs = keep
        Pw = to_world(V[: upto + 1], ff, hop)
        psx, psy, _, pok = project(Pw, cam)
        for i in idxs:
            if VH[i + 1] >= hop - 1600 and pok[i] and pok[i + 1]:
                c = VCOL[i + 1]
                dr.line([psx[i], psy[i], psx[i + 1], psy[i + 1]],
                        fill=(int(c[0]), int(c[1]), int(c[2]), int(6 * HUSH_DIM)), width=13)
        for i in idxs:
            if pok[i] and pok[i + 1]:
                c = VCOL[i + 1]
                A = hop - VH[i + 1]
                if A < 250: al, wd = 105, 6
                elif A < 1200: al, wd = 74, 6
                elif A < 2600: al, wd = 44, 5
                else: al, wd = 20, 4
                dr.line([psx[i], psy[i], psx[i + 1], psy[i + 1]],
                        fill=(int(c[0]), int(c[1]), int(c[2]), int(al * HUSH_DIM)), width=wd)
    # stab arcs for recent landings — bow/wobble from the landing tweet's
    # length-residualized entropy; world-space control points (arc9)
    _live = POS_NOW
    for j in range(max(0, k - 130), k):
        hj = land_hop[j]
        age = ff - land_frame[j]
        life = 8.0 + 7.0 * float(HUSH9_HOP[hj])
        if age < 0 or age > life: continue
        _sj = STABS[hj]
        if _sj["typ"] == 1 and _sj["node"] in EXCLUDE: continue   # no arc lands on the excluded account
        p0w = to_world(land_prev[j], ff, hop)[0]
        p1w = to_world(_live[_sj["node"]], ff, hop)[0] if _sj["typ"] == 1 else to_world(CP[j], ff, hop)[0]
        bow = (0.50 + 1.20 * float(HN9_LAND[j])) * (1.0 - 0.35 * COH_F)
        jit = float(JIT_LAND[j]) * 0.09 * float(np.linalg.norm(p1w - p0w)) * float(HN9_LAND[j]) ** 2
        arc = bezier_arc9(p0w, p1w, u_max=min(1.0, age / 4.5), bow_scale=bow, jit_mag=jit)
        if arc is None: continue
        ax_, ay_, _, aok = project(arc, cam)
        a = (1.0 - age / life) * 0.85 * (1.0 - 0.60 * HUSH_F)
        base_col = gold_rgb(hj, bright=float(land_toneb[j]))
        col = tuple(int(min(255, c * (1.0 + 0.18 * COH_F))) for c in base_col)
        wid = 9 + int(round(3.0 * float(HN9_LAND[j])))
        _hl = MUT_ARC.get(j)
        if _hl is not None:
            _env = highlight_env(ff, _hl)
            if _env > 0.01:
                wid += 6
                a = min(1.0, a * (1.0 + 0.9 * _env) + 0.25 * _env)
                col = tuple(int(c + (t_ - c) * 0.35 * _env) for c, t_ in zip(col, (255, 240, 205)))
        for jj in range(len(arc) - 1):
            if aok[jj] and aok[jj + 1]:
                dr.line([ax_[jj], ay_[jj], ax_[jj + 1], ay_[jj + 1]], fill=col + (int(190 * a),), width=wid)
    arr = np.asarray(layer).astype(np.float32)
    # the network recedes gently as the end card arrives
    _ffade = 1.0 - 0.22 * smooth(CTA_F0 - 24, CTA_F0 + 64, ff)
    if _ffade < 1.0: arr *= _ffade
    # his marker: one unlabeled warm point of light on the trace head
    head_w = to_world(spline_pos_at_hop(hop), ff, hop)
    hsx, hsy, _, hok = project(head_w, cam)
    if hok[0] and ff < CTA_F0:
        stamp(arr, hsx[0], hsy[0], K_MARK, gold_rgb(hop),
              0.9 * (1.0 + 0.60 * HUSH_F) * (1.3 if HARD_NOW else 1.0)
              * (0.25 + 0.75 * smooth(TITLE_F, 120, ff)))
        cx, cy = int(round(hsx[0])), int(round(hsy[0]))
        # v8 FLASH BUG, fixed: this write was unguarded. When the head sat
        # off-canvas at negative (cx, cy), min(H, cy+4) went negative and
        # numpy read the slice stop as from-the-end — the 7x7 block became
        # a white rectangle over up to 60% of the canvas (v8 frames 1466,
        # 1467, 2106, 2161, 2198). Guarded exactly like the node block.
        if 3 <= cx < W - 3 and 3 <= cy < H - 3:
            arr[cy-3:cy+4, cx-3:cx+4] = 255.0
    out = Image.fromarray(np.clip(soft_knee(arr), 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(out, "RGBA")
    # CTA veil (background keeps glowing through)
    if ff >= CTA_F0:
        a = int(168 * smooth(CTA_F0, CTA_F0 + 64, ff))
        dr.rectangle([0, 0, W, H], fill=(3, 4, 9, a))
    # world-event lower-thirds: bigger, backed, ~4 s holds (ripples above)
    for e in EVENTS:
        if e["cap_start"] <= ff < e["cap_end"]:
            age = ff - e["cap_start"]
            a = min(age / 12, 1.0) * (1 - smooth(CAP_LEN - 16, CAP_LEN, age))
            if a > 0:
                y = H - 222
                tw = spaced_width(e["caption"], F_EVENT, 18)
                dr.rounded_rectangle([CX_CUR - tw / 2 - 36, y - 54, CX_CUR + tw / 2 + 36, y + 96],
                                     radius=16, fill=(6, 10, 18, int(95 * a)))
                dr.line([CX_CUR - tw / 2, y - 36, CX_CUR + tw / 2, y - 36],
                        fill=(170, 220, 235, int(120 * a)), width=3)
                draw_spaced(dr, CX_CUR, y, e["caption"], F_EVENT, (228, 234, 242, int(242 * a)), 18)
    # rare handle-only callouts: backed plates, larger, longer holds
    if TITLE_F <= ff < CTA_F0:
        for (ch, txt, col) in callouts:
            cf = TITLE_F + ch / HPF
            age = ff - cf
            if 0 <= age < 84:
                a = min(age / 8, 1.0) * (1 - smooth(66, 84, age))
                w = dr.textlength(txt, font=F_CALL)
                dr.rounded_rectangle([CX_CUR - w / 2 - 34, 332, CX_CUR + w / 2 + 34, 436],
                                     radius=18, fill=(6, 10, 18, int(170 * a)))
                dr.text((CX_CUR - w / 2, 356), txt, font=F_CALL, fill=col + (int(240 * a),))
    # opening legend (judgment call #1 — flagged in BUILD-NOTES)
    _lenv = legend_env(ff)
    if _lenv > 0.01:
        x0, y0 = 72, H - 452
        dr.rounded_rectangle([x0, y0, x0 + 1246, y0 + 380], radius=20,
                             fill=(7, 11, 19, int(150 * _lenv)),
                             outline=(120, 160, 190, int(80 * _lenv)), width=2)
        for i, (glyph, txt) in enumerate(LEGEND):
            gy = y0 + 42 + i * 84
            gx = x0 + 58
            if glyph == "dot":
                dr.ellipse([gx - 13, gy + 12, gx + 13, gy + 38], fill=(255, 198, 92, int(240 * _lenv)))
            elif glyph == "line":
                dr.line([gx - 34, gy + 25, gx + 34, gy + 25], fill=(255, 190, 80, int(240 * _lenv)), width=7)
            elif glyph == "silver":
                dr.line([gx - 34, gy + 25, gx + 34, gy + 25], fill=(206, 218, 236, int(240 * _lenv)), width=5)
            else:  # sun
                dr.ellipse([gx - 17, gy + 8, gx + 17, gy + 42], fill=(255, 240, 205, int(250 * _lenv)))
            dr.text((x0 + 128, gy), txt, font=F_LEG, fill=(226, 233, 242, int(238 * _lenv)))
    # film strip: the top 20 flow along the right side
    draw_strip(dr, ff)
    # v9 Chunk B (W9b): process counter — diegetic instrument readout,
    # top-left of the open field (the legend owns the bottom-left
    # during the opening; captions own the bottom centre)
    _cenv = counter_env(ff)
    if _cenv > 0.01:
        _rem = int(max(0.0, N_HOPS - math.floor(hop)))
        dr.text((76, 56), f"CONTACTS REMAINING {_rem:,}", font=F_COUNT,
                fill=(150, 190, 215, int(150 * _cenv)))
    # top-mutual labels: backed plate + pointer line to the node (after
    # the strip, so a label can never slide under it)
    for rec, env in HLIVE:
        _xy = rec.get("_xy")
        if not _xy or not _xy[2]: continue
        px, py = _xy[0], _xy[1]
        txt = rec["label"]
        tw = dr.textlength(txt, font=F_CALL)
        pw, phh = tw + 60, 96
        pcx = min(max(px, pw / 2 + 24), STRIP_X0 - pw / 2 - 24)
        pty = min(max(py - 250, 24), H - phh - 24)
        dr.line([px, py, pcx, pty + phh], fill=(255, 205, 110, int(150 * env)), width=3)
        dr.rounded_rectangle([pcx - pw / 2, pty, pcx + pw / 2, pty + phh], radius=18,
                             fill=(6, 10, 18, int(175 * env)),
                             outline=(255, 205, 110, int(150 * env)), width=2)
        dr.text((pcx - tw / 2, pty + 16), txt, font=F_CALL, fill=(255, 240, 214, int(245 * env)))
    # title card: THE EXOCORTEX — Shaken yet Stirred
    if ff < 96:
        a = min(ff / 11, 1.0) * (1 - smooth(72, 94, ff))
        if a > 0:
            center_text(dr, CX_CUR, 618, "THE EXOCORTEX", F_TITLE, (240, 244, 250, int(255 * a)))
            center_text(dr, CX_CUR, 864, "Shaken yet Stirred", F_OBL, (246, 216, 152, int(255 * a)))
            center_text(dr, CX_CUR, 1050, "a map of alignment", F_SUB, (198, 210, 226, int(255 * a)))
    # second title beat: the v6 line, kept as a quiet echo
    if 108 <= ff < 196:
        a = min((ff - 108) / 14, 1.0) * (1 - smooth(172, 196, ff))
        if a > 0:
            center_text(dr, CX_CUR, 864, "the future has arrived", F_OBL, (246, 216, 152, int(255 * a)))
    # CTA card (verbatim)
    if ff >= CTA_F0:
        a = smooth(CTA_F0, CTA_F0 + 64, ff)
        if a > 0:
            center_text(dr, CX_CUR, 696, "520 people are already in this map.", F_CARD, (240, 244, 250, int(255 * a)))
            center_text(dr, CX_CUR, 864, "Find your coordinate. Claim your space.", F_CARD, (255, 198, 92, int(255 * a)))
            center_text(dr, CX_CUR, 1050, "edit.phext.io", F_BIG, (255, 214, 120, int(255 * a)))
            center_text(dr, CX_CUR, 1290, "Not in the map yet? The door is open.", F_SUB, (200, 212, 228, int(255 * a)))
    return out

# ---------- v9 Chunk B (W8): 1965 Apollo-era film treatment ----------
# A POST STAGE in render_frame, after the selective bloom — the scene
# itself is untouched. Every element is a deterministic pure function
# of the output frame number f (a per-frame grain seed; a precomputed
# smoothed wander for the flicker), so chunk contexts cannot disagree.
# Explicitly OUT, per the brief: gate weave (geometry stability is an
# acceptance item) and dust/scratches (dirt on a data film).
FLICK_AMP = 0.015                       # +-1.5% exposure wander
_flk_r = np.random.default_rng(1965).normal(0.0, 1.0, TOTAL_F + 720)
_flk_k = np.exp(-0.5 * (np.arange(-180, 181) / 60.0) ** 2); _flk_k /= _flk_k.sum()
FLICK = np.convolve(_flk_r, _flk_k, mode="same")[360:360 + TOTAL_F]
FLICK = FLICK / max(1e-9, float(np.max(np.abs(FLICK))))
FILM_LIFT = 5.0 / 255.0                 # black point lifted +5/255
GRAIN_SIG = 5.2                         # animated grain sigma at 1080p (dark fields);
                                        # W10: raised — the grain IS the field texture now
HAL_T, HAL_GAIN = 205.0, 0.50           # halation threshold / strength
HAL_COL = np.array([0.55, 0.21, 0.075], dtype=np.float32)   # warm red-orange fringe
_vx9 = (np.arange(OUT_W) - OUT_W * 0.42) / (OUT_W * 0.66)
_vy9 = (np.arange(OUT_H) - OUT_H * 0.5) / (OUT_H * 0.66)
POST_VIG = (1.0 - 0.13 * np.clip(_vx9[None, :] ** 2 + _vy9[:, None] ** 2, 0, 1) ** 1.5).astype(np.float32)[:, :, None]
def _film_curve(x):
    """Gentle film response on 0..255 floats: an S that softens both
    ends (highlights roll off creamy, never clip harshly), then the
    black-point lift."""
    t = np.clip(x / 255.0, 0.0, 1.0)
    t = t - 0.055 * np.sin(2 * math.pi * t)
    return (FILM_LIFT + (1.0 - FILM_LIFT) * t) * 255.0
def film_grade(oa, f):
    """oa: post-bloom float32 (OUT_H, OUT_W, 3), 0..255. Returns the
    graded frame as clipped float32."""
    # 1) exposure flicker: slow smooth wander, never strobing
    x = oa * (1.0 + FLICK_AMP * float(FLICK[f]))
    # 2) response curve + a whisper of split-tone (warm highlights,
    #    cool shadows) — palette discipline holds: gold stays gold,
    #    silver stays silver, the shifts are single-digit levels
    lum = x.max(axis=2) / 255.0
    hi_m = np.clip((lum - 0.50) / 0.50, 0.0, 1.0) ** 2
    lo_m = np.clip((0.40 - lum) / 0.40, 0.0, 1.0) ** 1.5
    x = _film_curve(x)
    x[:, :, 0] += 8.0 * hi_m - 2.5 * lo_m
    x[:, :, 1] += 1.5 * hi_m - 0.5 * lo_m
    x[:, :, 2] += -6.0 * hi_m + 5.5 * lo_m
    # 3) halation: the brightest highlights (suns, trace head, burst
    #    cores) bleed a soft warm fringe — the Ektachrome signature,
    #    distinct from the optical white-gold bloom upstream of it
    lum2 = x.max(axis=2)
    m = np.clip((lum2 - HAL_T) / (255.0 - HAL_T), 0.0, 1.0) ** 1.5
    src = Image.fromarray(np.clip(x * m[:, :, None], 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(16))
    x = x + np.asarray(src, dtype=np.float32) * HAL_COL[None, None, :] * HAL_GAIN
    # 4) vignette: the post pass deepens the scene vignette modestly
    x = x * POST_VIG
    # 5) animated film grain: monochrome, zero-mean, regenerated every
    #    frame from a per-frame seed; eased off in the highlights so
    #    it never crawls over the trace
    gr = np.random.default_rng(900000 + int(f)).normal(0.0, GRAIN_SIG, (OUT_H, OUT_W, 1)).astype(np.float32)
    x = x + gr * (1.0 - 0.55 * np.clip(lum2 / 255.0, 0.0, 1.0)[:, :, None])
    return np.clip(x, 0.0, 255.0)

def render_frame(f):
    """One output frame: SUBN sub-frames averaged (temporal AA / motion
    blur), one Lanczos down-sample, then selective bloom at delivery
    size — soft optical glow on the highlights, breathing with the song."""
    if SUBN <= 1:
        out4k = render_single(float(f))
    else:
        acc = None
        for dlt in (-1.0 / 3.0, 0.0, 1.0 / 3.0):
            ff = min(max(float(f) + dlt, 0.0), TOTAL_F - 1.0)
            im = np.asarray(render_single(ff)).astype(np.float32)
            acc = im if acc is None else acc + im
        out4k = Image.fromarray(np.clip(acc / SUBN, 0, 255).astype(np.uint8))
    small = out4k.resize((OUT_W, OUT_H), Image.LANCZOS)
    oa = np.asarray(small).astype(np.float32)
    lum = oa.max(axis=2, keepdims=True)
    mask = np.clip((lum - 185.0) / 70.0, 0.0, 1.0)
    src = Image.fromarray((oa * mask).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7))
    bgain = 0.45 * (0.85 + 0.30 * song_e(float(f)))
    oa = np.clip(oa + np.asarray(src, dtype=np.float32) * bgain, 0, 255)
    oa = film_grade(oa, f)                       # W8: Apollo post stage
    return Image.fromarray(oa.astype(np.uint8))

if __name__ == "__main__":
    if "--stills" in sys.argv:
        os.makedirs(f"{BASE}/viz9/stills_check", exist_ok=True)
        _hw9 = FEAT9["meta"]["hush_window"]
        picks = {"title": 40, "beat2": 150, "legend": 230,
                 "dakami_highlight": int(HIGHLIGHTS[3]["frame"]) + 30,
                 "strip": 1500,
                 "hush_deep": int(TITLE_F + ((_hw9["hop0"] + _hw9["hop1"]) / 2) / HPF),
                 "turbulence": 918, "burst": 1053, "mutuals": 1180,
                 "p50": int(0.50 * TOTAL_F), "bezier": 2300,
                 "hush": 3308, "pullback": 3480, "cta": 3700}
        for name, f in picks.items():
            t = time.time(); im = render_frame(f); dt = time.time() - t
            im.save(f"{BASE}/viz9/stills_check/{name}.png")
            print(f"{name} frame {f}: {dt*1000:.0f} ms", flush=True)
    elif "--frame" in sys.argv:
        i = sys.argv.index("--frame"); f = int(sys.argv[i + 1])
        outp = sys.argv[sys.argv.index("--out") + 1]
        render_frame(f).save(outp); print("frame done", outp, flush=True)
    elif "--range" in sys.argv:
        import subprocess
        i = sys.argv.index("--range"); fa, fb = int(sys.argv[i + 1]), int(sys.argv[i + 2])
        outp = sys.argv[sys.argv.index("--out") + 1]
        dumpd = os.environ.get("V9_DUMP")
        if dumpd: os.makedirs(dumpd, exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "10", "-pix_fmt", "yuv420p", "-threads", "2", outp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(fa, fb):
            raw = render_frame(f).tobytes()
            if dumpd:
                with open(f"{dumpd}/f{f}.rgb", "wb") as fh: fh.write(raw)
            p.stdin.write(raw)
            if f % 25 == 0: print(f"{f}/{fb} {time.time()-t0:.0f}s", flush=True)
        p.stdin.close(); p.wait()
        print("chunk done", outp, time.time() - t0, flush=True)
