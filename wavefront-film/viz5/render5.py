#!/usr/bin/env python3
"""wavefront-viz v5 — v4, set in orbital motion. (Will, 2026-11-03 14:01 CST)

Everything from v4 (hop time, golden trace, CMB misses, VADER tone,
progress counters, handle-only callouts, no name anywhere) plus:
  * Camera orbit by THRUST: angular velocity omega(f) = OMEGA_MAX *
    sqrt(deep(hop)/DEEP_TOTAL), where a deep connection is a match landing
    on a placed person (typ-1) beyond the first match to that person.
    From the data: 5,169 typ-1 matches, 156 placed people ever landed on,
    DEEP_TOTAL = 5,013. sqrt shaping keeps the sparse early years from
    reading as a frozen camera; the endpoint is untouched (sqrt(1) = 1).
  * Endpoint calibration: OMEGA_MAX = 2*pi / frames-per-year at the final
    year's density. Last 365 days of the archive hold 6,053 hops; at
    HPF = 5.6512 that is 1,071.1 frames/year, so OMEGA_MAX = 0.005866
    rad/frame — by the end, one full camera orbit per year of data time.
  * Nodes run on their own orbits: small epicycles about each anchor
    (mean position = the phext coordinate), Kepler-flavoured angular
    speed Omega_i ~ r_i^-1.5 about the core, phase from md5(handle).
    Amplitude 0.022 world units (median NN spacing is 0.065 — damped so
    the map cannot dissolve). Match landings freeze at the node's
    position at their hop; live arcs land on the node's current position.
  * 2x zoom: camera radius 4.45 -> 2.225 (pull-back relaxes to 6.8).
  * 2x speed: 3,802 frames at 24 fps = 158.42 s; HPF doubled to 5.6512.
    Song edited to 158.400 s (see viz5/song_edit.wav): 0->112.4 s (verse,
    pre-chorus, chorus 1) crossfaded 2 s into 213.4->261.4 s (the bridge's
    closing line + final chorus), 4 s fade-out. No time-stretch.
  * The phext data is only read; every transform is render-time.
Usage: render5.py --stills | --full
"""
import json, math, sys, time
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
SONG_DUR = 158.400                               # the ~2x edit (viz5/song_edit.wav)
TOTAL_F = int(round(SONG_DUR * FPS))             # 3802 frames = 158.42 s
TITLE_F = 42                                     # hops start here (halved from v4)
MAIN_END_F = 3362                                # last hop lands here
PULL_F = 3362                                    # pull-back 3362..3512
CTA_F0 = 3512                                    # CTA fade-in (75 f); solid ~3587..3802
FOCAL = (H / 2) / math.tan(math.radians(21.0))
BASE = "/home/hatch/workspace/wavefront"
DATA = json.load(open(f"{BASE}/viz2/data.json"))
OVER = json.load(open(f"{BASE}/viz3/overton.json"))
TONE = json.load(open(f"{BASE}/viz4/tone.json"))
NODES = DATA["nodes"]; STABS = DATA["stabs"]; T0, T1 = DATA["t0"], DATA["t1"]
N_HOPS = len(STABS)                              # 18,762
N_MATCH = DATA["counts"]["travel"] + DATA["counts"]["gold_shell"]  # 5,963
HPF = N_HOPS / (MAIN_END_F - TITLE_F)            # hops per frame ~2.826

node_xyz = np.array([n["xyz"] for n in NODES], dtype=np.float64)
CORE = node_xyz.mean(axis=0)

# ---------- v5: deep connections, thrust, node orbits ----------
# deep connection = typ-1 match beyond the first match to that placed node
deep_at = np.zeros(N_HOPS + 1, dtype=np.float64)
_seen_nodes = set(); _dcount = 0
for _h, _s in enumerate(STABS):
    if _s["typ"] == 1:
        if _s["node"] in _seen_nodes: _dcount += 1
        else: _seen_nodes.add(_s["node"])
    deep_at[_h + 1] = _dcount
DEEP_TOTAL = float(_dcount)                       # 5,013
_all_ts = np.array([s["ts"] for s in STABS])
LAST365_HOPS = int((_all_ts >= (T1 - 365 * 86400)).sum())   # 6,053 hops in the final 365 days
FRAMES_PER_YEAR = LAST365_HOPS / HPF              # 1,071.1 frames per year at final density
OMEGA_MAX = 2 * math.pi / FRAMES_PER_YEAR         # 0.005866 rad/frame: one orbit per year at the end
def deep_frac(hf):
    hf = min(max(hf, 0.0), float(N_HOPS))
    i = int(hf); fr = hf - i
    return float((deep_at[i] * (1 - fr) + deep_at[min(i + 1, N_HOPS)] * fr) / DEEP_TOTAL)
# camera azimuth: cumulative thrust angle per frame (sqrt-shaped approach, exact endpoint)
AZIM = np.zeros(TOTAL_F)
_acc = 0.0
for _f in range(TOTAL_F):
    AZIM[_f] = _acc
    _hf = (0.0 if _f <= TITLE_F else float(N_HOPS) if _f >= MAIN_END_F else (_f - TITLE_F) * HPF)
    _acc += OMEGA_MAX * math.sqrt(deep_frac(_hf))
# node epicycles: Kepler Omega ~ r^-1.5 about CORE (xy plane), phase from md5(key)
import hashlib
_r_xy = np.linalg.norm(node_xyz[:, :2] - CORE[:2], axis=1)
R_REF = float(np.median(_r_xy))                   # 0.344
OMEGA_REF = 2 * math.pi / 9000.0                  # rad/hop at R_REF: one orbit per 9,000 hops
OMEGA_NODE = OMEGA_REF * (R_REF / np.maximum(_r_xy, 0.12)) ** 1.5
OMEGA_NODE = np.minimum(OMEGA_NODE, 3.0 * OMEGA_REF)
A_ORB = 0.022                                     # epicycle amplitude, world units (NN spacing med 0.065)
def _node_seed(n): return (n["key"] or n["name"])   # the 'will' node carries key=None
PHASE = np.array([int.from_bytes(hashlib.md5(_node_seed(n).encode()).digest()[:8], "little")
                  / 2**64 * 2 * math.pi for n in NODES])
PHASE_Z = np.array([int.from_bytes(hashlib.md5((_node_seed(n) + "·z").encode()).digest()[:8], "little")
                    / 2**64 * 2 * math.pi for n in NODES])
def node_pos_all(hf):
    """All node positions at (float) hop hf: anchor + epicycle offset."""
    ph = PHASE + OMEGA_NODE * hf
    off = np.stack([A_ORB * np.cos(ph), A_ORB * np.sin(ph),
                    0.35 * A_ORB * np.sin(0.9 * ph + PHASE_Z)], axis=1)
    return node_xyz + off
def node_hop(f):
    """Hop used for node orbits: follows hop_float, then keeps advancing at
    the final density through pull-back/CTA so the field stays alive."""
    hf = hop_float(f)
    if f > MAIN_END_F: hf += (f - MAIN_END_F) * HPF
    return hf
tone_sm = np.array(TONE["smooth"], dtype=np.float64)
# tone -> [0,1] visual warmth, percentile-normalised on the smoothed series
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
F_SUB   = ImageFont.truetype(FONT + "DejaVuSans.ttf", 24)
F_HUD   = ImageFont.truetype(FONT + "DejaVuSans.ttf", 19)
F_SM    = ImageFont.truetype(FONT + "DejaVuSans.ttf", 12)
F_TICK  = ImageFont.truetype(FONT + "DejaVuSans.ttf", 11)
F_CALL  = ImageFont.truetype(FONT + "DejaVuSans.ttf", 18)
F_CARD  = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 30)
F_BIG   = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 44)

def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def hop_float(f):
    if f <= TITLE_F: return 0.0
    if f >= MAIN_END_F: return float(N_HOPS)
    return (f - TITLE_F) * HPF

# ---------- Overton drift, subtle, in hop time ----------
stab_ts = np.array([s["ts"] for s in STABS])
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

# ---------- walk the hops once: landings, counters, callouts ----------
node_idx_by_key = {}
for i, n in enumerate(NODES):
    node_idx_by_key.setdefault(n["key"], i)
ORAI_RUP = next(i for i, n in enumerate(NODES) if "rupture" in n["name"])
RUPTURE_HOP = int(np.searchsorted(stab_ts, 1749988800))  # 2025-06-15

land_pos, land_hop = [], []          # match landings (base space), in hop order
attempts_at = np.zeros(N_HOPS + 1, dtype=int)
matches_at = np.zeros(N_HOPS + 1, dtype=int)
placed_at = np.zeros(N_HOPS + 1, dtype=int)
first_land_frame_node = {}
callouts = []                        # (hop, text, color)
seen_handles = set()
will = np.zeros(3); mat = 0; landed_nodes = set()
for h, s in enumerate(STABS):
    if s["typ"] in (1, 2):
        mat += 1
        # typ-1 landings freeze at the node's orbital position at this hop
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
def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
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
    # v5: only a whisper of v4's field rotation (10 deg) — the thrust-driven
    # camera orbit and the nodes' own orbits carry the motion now
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
    R = 2.225 * (1.0 + 0.035 * math.sin(2 * math.pi * (f - TITLE_F) / (FPS * 45.0)))  # 2x zoom: half of v4's 4.45
    R = R * (1 - pull) + 6.8 * pull                       # pull-back relaxes the zoom to reveal the field
    az = 2.45 + AZIM[f]                                   # thrust orbit: azimuth accumulates omega(f)
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
CMB = ((0.18 + 0.82 * _int ** 1.15)[:, :, None] * tint * 30.0).astype(np.float32)   # unit-gain afterglow
BASE_BG = np.array([3.0, 4.0, 8.0], dtype=np.float32)
STARS_X = _rng.uniform(0, W, 380); STARS_Y = _rng.uniform(0, H, 380); STARS_B = _rng.uniform(5, 20, 380)
miss_frac_at = 1.0 - matches_at / np.maximum(1, attempts_at)  # per-hop miss share (cumulative misses / attempts)
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

# arcs: one per landing, born at its hop's frame
land_frame = np.array([TITLE_F + h / HPF for h in land_hop])
# first hop each node is landed on (typ-1 only); the rupture node "lands" at the rupture hop
NODE_FIRST_HOP = np.full(len(NODES), 10**9, dtype=int)
for _j, _h in enumerate(land_hop):
    _s = STABS[_h]
    if _s["typ"] == 1 and _h < NODE_FIRST_HOP[_s["node"]]:
        NODE_FIRST_HOP[_s["node"]] = _h
NODE_FIRST_HOP[ORAI_RUP] = RUPTURE_HOP
land_prev = np.vstack([np.zeros(3), CP[:-1]])
land_toneb = np.array([0.72 + 0.5 * tone_norm(h) for h in land_hop])

# progress bar geometry + era ticks (by hop position)
BAR_X0, BAR_X1, BAR_Y = 190, 1090, 664
def hop_of_ts(ts): return float(np.searchsorted(stab_ts, ts))
ERA_TICKS = []
for y in (2009, 2013, 2016, 2020, 2024, 2025):
    ts = datetime(y, 1, 1, tzinfo=timezone.utc).timestamp()
    ERA_TICKS.append((hop_of_ts(ts) / N_HOPS, str(y)))
CHATGPT_FRAC = hop_of_ts(datetime(2022, 11, 30, tzinfo=timezone.utc).timestamp()) / N_HOPS
# tone ribbon strip (width = bar width), drawn revealed up to progress
_ribv = np.array([tone_norm((x / (BAR_X1 - BAR_X0)) * N_HOPS) for x in range(BAR_X1 - BAR_X0)])
_ribv = np.convolve(np.pad(_ribv, 10, mode="edge"), np.ones(21) / 21, mode="valid")  # calm the striping
RIB = np.zeros((6, BAR_X1 - BAR_X0, 3), dtype=np.uint8)
for x in range(BAR_X1 - BAR_X0):
    c = np.array([96, 120, 150]) + (np.array([255, 180, 80]) - np.array([96, 120, 150])) * _ribv[x]
    RIB[:, x, :] = c.astype(np.uint8)

def center_text(dr, cx, y, text, font, fill):
    w = dr.textlength(text, font=font); dr.text((cx - w / 2, y), text, font=font, fill=fill)

HONEST = "positions from wavefront.phext — staging and drift are illustrative"

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
    dr = ImageDraw.Draw(img, "RGBA")
    arr = np.asarray(img).astype(np.float32)
    # --- nodes (on their own orbits; node_hop keeps them moving through the pull-back)
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
    # --- golden trace (spline verts born by hop), drawn on the float buffer via a PIL layer
    layer = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(layer, "RGBA")
    upto = int(np.searchsorted(VH, hop, side="right")) - 1
    if upto > 0:
        idxs = list(range(upto))
        if upto > 3400:
            keep = sorted(set(idxs[-800:]) | set(idxs[:: math.ceil((upto - 800) / 2400)]))
            idxs = keep
        Pw = to_world(V[: upto + 1], f, hop)
        psx, psy, _, pok = project(Pw, cam)
        # halo pass: the recent thread glows softly under its own core line
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
    # --- stab arcs for recent landings (matches only; misses feed the CMB)
    _live = node_pos_all(node_hop(f))
    for j in range(max(0, k - 60), k):
        age = f - land_frame[j]
        if age < 0 or age > 8: continue                    # 2x speed: halved frame window, same hop window
        p0w = to_world(land_prev[j], f, hop)[0]
        _sj = STABS[land_hop[j]]
        # typ-1 arcs land on the node's CURRENT orbital position; typ-2 keep their frozen point
        p1w = to_world(_live[_sj["node"]], f, hop)[0] if _sj["typ"] == 1 else to_world(CP[j], f, hop)[0]
        arc = bezier_arc(p0w, p1w, cam, u_max=min(1.0, age / 4.5))
        if arc is None: continue
        ax_, ay_, _, aok = project(arc, cam)
        a = (1 - age / 8) * 0.85
        col = gold_rgb(land_hop[j], bright=float(land_toneb[j]))
        for jj in range(len(arc) - 1):
            if aok[jj] and aok[jj + 1]:
                dr.line([ax_[jj], ay_[jj], ax_[jj + 1], ay_[jj + 1]], fill=col + (int(190 * a),), width=2)
    # --- rupture beat: one quiet red arc, once
    rf = TITLE_F + RUPTURE_HOP / HPF
    if rf <= f < rf + 28:
        age = f - rf
        p0w = to_world(spline_pos_at_hop(RUPTURE_HOP), f, hop)[0]
        p1w = to_world(_live[ORAI_RUP], f, hop)[0]         # rupture node at its current orbital position
        arc = bezier_arc(p0w, p1w, cam, u_max=min(1.0, age / 9.0))
        if arc is not None:
            ax_, ay_, _, aok = project(arc, cam)
            a = 1 - age / 28
            for jj in range(len(arc) - 1):
                if aok[jj] and aok[jj + 1]:
                    dr.line([ax_[jj], ay_[jj], ax_[jj + 1], ay_[jj + 1]], fill=(205, 74, 58, int(170 * a)), width=2)
    arr = np.asarray(layer).astype(np.float32)
    # --- his marker: one unlabeled warm point of light on the trace head
    head_w = to_world(spline_pos_at_hop(hop), f, hop)
    hsx, hsy, _, hok = project(head_w, cam)
    if hok[0] and f < CTA_F0:
        stamp(arr, hsx[0], hsy[0], K_MARK, gold_rgb(hop), 0.9)
        cx, cy = int(round(hsx[0])), int(round(hsy[0]))
        arr[max(0, cy-1):min(H, cy+2), max(0, cx-1):min(W, cx+2)] = 255.0
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(out, "RGBA")
    # --- CTA veil (background keeps glowing through)
    if f >= CTA_F0:
        a = int(168 * smooth(CTA_F0, CTA_F0 + 75, f))
        dr.rectangle([0, 0, W, H], fill=(3, 4, 9, a))
    # --- HUD: one corner block — attempts / matches / placed
    if TITLE_F <= f < CTA_F0:
        att, matc, plc = attempts_at[hi], matches_at[hi], placed_at[hi]
        dr.text((28, 22), "attempts", font=F_HUD, fill=(168, 180, 200))
        dr.text((150, 22), f"{att:,}", font=F_HUD, fill=(240, 244, 248))
        dr.text((28, 48), "matches", font=F_HUD, fill=(168, 180, 200))
        dr.text((150, 48), f"{matc:,}", font=F_HUD, fill=(255, 198, 92))
        dr.text((28, 74), "placed", font=F_HUD, fill=(168, 180, 200))
        dr.text((150, 74), f"{plc:,}", font=F_HUD, fill=(240, 244, 248))
    # --- progress bar + tone ribbon + era ticks
    if TITLE_F - 20 <= f < CTA_F0:
        frac = hi / N_HOPS
        xfill = BAR_X0 + frac * (BAR_X1 - BAR_X0)
        dr.rectangle([BAR_X0, BAR_Y, BAR_X1, BAR_Y + 3], fill=(88, 100, 122, 150))
        dr.rectangle([BAR_X0, BAR_Y, xfill, BAR_Y + 3], fill=(238, 224, 186, 235))
        rib = Image.fromarray(RIB, "RGB").convert("RGBA")
        rib.putalpha(200)
        out.paste(rib.crop((0, 0, max(1, int(xfill - BAR_X0)), 6)), (BAR_X0, BAR_Y + 8), rib.crop((0, 0, max(1, int(xfill - BAR_X0)), 6)))
        dr = ImageDraw.Draw(out, "RGBA")
        for fx, lab in ERA_TICKS:
            x = BAR_X0 + fx * (BAR_X1 - BAR_X0)
            dr.line([x, BAR_Y - 2, x, BAR_Y + 16], fill=(150, 164, 186, 200), width=1)
            if lab == "2009": continue  # the bar's own start needs no label; avoids the 2013 collision
            w = dr.textlength(lab, font=F_TICK)
            lx = min(max(x - w / 2, BAR_X0), BAR_X1 - w)
            dr.text((lx, BAR_Y + 20), lab, font=F_TICK, fill=(138, 152, 172))
        cx = BAR_X0 + CHATGPT_FRAC * (BAR_X1 - BAR_X0)
        w = dr.textlength("ChatGPT", font=F_TICK)
        dr.text((cx - w / 2, BAR_Y - 18), "ChatGPT", font=F_TICK, fill=(148, 178, 168))
        dr.line([cx, BAR_Y - 4, cx, BAR_Y], fill=(148, 178, 168, 200), width=1)
        # hop counter at the bar's right end
        ht = f"hop {hi:,} / {N_HOPS:,}"
        w = dr.textlength(ht, font=F_TICK)
        dr.text((BAR_X1 - w, BAR_Y - 18), ht, font=F_TICK, fill=(168, 180, 200))
    # --- rare handle-only callouts, gentle
    if TITLE_F <= f < CTA_F0:
        for (ch, txt, col) in callouts:
            cf = TITLE_F + ch / HPF
            age = f - cf
            if 0 <= age < 70:
                a = min(age / 8, 1.0) * (1 - smooth(55, 70, age))
                w = dr.textlength(txt, font=F_CALL)
                dr.text((W / 2 - w / 2, 118), txt, font=F_CALL, fill=col + (int(235 * a),))
    # --- title card
    if f < 88:
        a = min(f / 11, 1.0) * (1 - smooth(64, 86, f))
        if a > 0:
            center_text(dr, W/2, 218, "THE WAVEFRONT", F_TITLE, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 296, "a map of alignment, drawn from 18,762 replies · 520 people placed",
                        F_SUB, (198, 210, 226, int(255 * a)))
            center_text(dr, W/2, 344, HONEST, F_SM, (148, 164, 184, int(255 * a)))
    # --- CTA card
    if f >= CTA_F0:
        a = smooth(CTA_F0, CTA_F0 + 75, f)
        if a > 0:
            center_text(dr, W/2, 232, "520 people are already in this map.", F_CARD, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 288, "Find your coordinate. Claim your space.", F_CARD, (255, 198, 92, int(255 * a)))
            center_text(dr, W/2, 350, "edit.phext.io", F_BIG, (255, 214, 120, int(255 * a)))
            center_text(dr, W/2, 430, "Not in the map yet? The door is open.", F_SUB, (200, 212, 228, int(255 * a)))
            center_text(dr, W/2, 560, f"18,762 attempts · {N_MATCH:,} matches", F_HUD, (178, 190, 208, int(255 * a)))
            center_text(dr, W/2, 590, HONEST, F_SM, (132, 148, 168, int(255 * a)))
    return out

if __name__ == "__main__":
    def frame_of_hop(h): return int(TITLE_F + h / HPF)
    if "--stills" in sys.argv:
        os.makedirs(f"{BASE}/viz5/stills", exist_ok=True)
        picks = {"hop0500": frame_of_hop(500), "hop5000": frame_of_hop(5000),
                 "hop12000": frame_of_hop(12000), "hop18000": frame_of_hop(18000),
                 "title": 30, "cta": TOTAL_F - 40}
        for name, f in picks.items():
            t = time.time(); im = render(f); dt = time.time() - t
            im.save(f"{BASE}/viz5/stills/{name}.png")
            print(f"{name} frame {f}: {dt*1000:.0f} ms", flush=True)
    else:
        import subprocess
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", f"{BASE}/viz5/silent.mp4"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(TOTAL_F):
            p.stdin.write(render(f).tobytes())
            if f % 500 == 0: print(f"{f}/{TOTAL_F} {time.time()-t0:.0f}s", flush=True)
        p.stdin.close(); p.wait()
        print("render done", time.time() - t0, flush=True)
