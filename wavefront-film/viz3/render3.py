#!/usr/bin/env python3
"""wavefront-viz v3 — THE SEARCH, staged as an orbit.

Layers over the v2 data (viz2/data.json — the phext data does NOT move):
  * Beziers everywhere: Will's path is a Catmull-Rom spline through his
    match landings (rainbow, hue by archive time); stab flashes travel
    along quadratic bezier arcs.
  * Overton drift (viz3/overton.json): dated world AI milestones move a
    "window center"; goalposts translate with it and every rendered point
    is pulled by it with distance falloff. An illustrative layer only.
  * Galaxy staging: the whole field slowly rotates as one body about a
    glowing core at the field centroid; placed nodes are stars with
    tangential streaks; Will's spline is a grand orbit with the Sun's
    sinusoidal bob perpendicular to the orbital plane. Camera rides his
    arc looking ahead along the tangent, core kept in frame.
  * Ending: pull-back, counts line, then a CTA card (edit.phext.io).
Usage: render3.py --stills | --full
"""
import json, math, sys, time
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
SONG_DUR = 312.800167
TOTAL_F = int(round(SONG_DUR * FPS))          # 7507
TITLE_F = 96                                   # title / push-in
MAIN_END_F = 6000                              # search ends earlier: pull-back + CTA need room
PULL_F = MAIN_END_F
CTA_F0 = 7130                                  # CTA card fade-in start (solid hold ~7280-7507 ~= 9.5 s)
FOCAL = (H / 2) / math.tan(math.radians(21.0)) # vfov 42 deg
BASE = "/home/hatch/workspace/wavefront"
DATA = json.load(open(f"{BASE}/viz2/data.json"))
OVER = json.load(open(f"{BASE}/viz3/overton.json"))
NODES = DATA["nodes"]; STABS = DATA["stabs"]; T0, T1 = DATA["t0"], DATA["t1"]
COUNTS = DATA["counts"]
N_MATCH = COUNTS["travel"] + COUNTS["gold_shell"]   # 5,963

node_xyz = np.array([n["xyz"] for n in NODES], dtype=np.float64)
CORE = node_xyz.mean(axis=0)                   # galactic core: field centroid (the detected mass)
CORE = np.array([CORE[0], CORE[1], CORE[2]])

import matplotlib, os
FONT = os.path.join(matplotlib.get_data_path(), "fonts", "ttf") + "/"
F_TITLE = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 54)
F_SUB   = ImageFont.truetype(FONT + "DejaVuSans.ttf", 25)
F_CLOCK = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 34)
F_HUD   = ImageFont.truetype(FONT + "DejaVuSans.ttf", 17)
F_SM    = ImageFont.truetype(FONT + "DejaVuSans.ttf", 13)
F_CALL  = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 21)
F_LAB   = ImageFont.truetype(FONT + "DejaVuSans.ttf", 12)
F_CARD  = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 30)
F_CARD2 = ImageFont.truetype(FONT + "DejaVuSans-Oblique.ttf", 20)
F_BIG   = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 44)

def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def hsv2rgb(h, s, v):
    i = int(h * 6) % 6; f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    return [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]

def frame_of(ts):
    return TITLE_F + (ts - T0) / (T1 - T0) * (MAIN_END_F - TITLE_F)

# ---------- Overton drift ----------
OV_EVENTS = []
for m in OVER["milestones"]:
    ts = datetime.strptime(m["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
    OV_EVENTS.append(dict(ts=ts, f0=int(frame_of(ts)) - 30, f1=int(frame_of(ts)) + 60,
                          frame=int(frame_of(ts)), label=m["label"], year=m["date"][:4],
                          delta=np.array(m["delta"], dtype=np.float64) * OVER["delta_scale"]))
def window_center(f):
    c = np.zeros(3)
    for e in OV_EVENTS:
        c += e["delta"] * smooth(e["f0"], e["f1"], f)
    return c
SIGMA2 = 2 * 1.5 ** 2
def warp(pts, f):
    """Pull points toward the drifted window: displacement = drift * falloff(dist to window)."""
    c = window_center(f)
    if not np.any(c):
        return pts, c
    d2 = np.sum((pts - c) ** 2, axis=-1, keepdims=True)
    return pts + c * np.exp(-d2 / SIGMA2), c

# ---------- prep: walk the journey (same reconciliation as v2) ----------
stab_ts = np.array([s["ts"] for s in STABS])
stab_frame = np.minimum(MAIN_END_F - 1, np.floor(frame_of(stab_ts)).astype(int))
order = np.argsort(stab_frame, kind="stable")
node_idx_by_key = {}
for i, n in enumerate(NODES):
    node_idx_by_key.setdefault(n["key"], i)
ORAI_ARR = next(i for i, n in enumerate(NODES) if "arrival" in n["name"])
ORAI_RUP = next(i for i, n in enumerate(NODES) if "rupture" in n["name"])
RUPTURE_F = int(frame_of(1749988800))  # 2025-06-15, retained record

bright_frame = np.full(len(NODES), 10**9, dtype=int)
path_birth, path_pts, path_col = [], [], []
sparks = []   # (birth_frame, base_pos, gold)
flashes = []  # (birth_frame, p1_base_or_None, gold, node_idx_or_None)  p0 = Will spline pos at birth
events = []   # (frame, text)
will = np.zeros(3)
att = mat = 0
si = 0
sorted_idx = order.tolist()
for f in range(TITLE_F, MAIN_END_F):
    while si < len(sorted_idx) and stab_frame[sorted_idx[si]] == f:
        s = STABS[sorted_idx[si]]; att += 1
        if s["typ"] == 1:
            mat += 1
            tgt = node_xyz[s["node"]]
            flashes.append((f, None, True, s["node"]))
            if len(path_pts) == 0:
                path_pts.append(tuple(will)); path_birth.append(f)
                path_col.append((120, 120, 120))
            frac = (s["ts"] - T0) / (T1 - T0)
            r, g, b = hsv2rgb(0.76 * (1 - frac), 0.85, 1.0)
            path_pts.append(tuple(tgt)); path_birth.append(f)
            path_col.append((int(r * 255), int(g * 255), int(b * 255)))
            if bright_frame[s["node"]] > f: bright_frame[s["node"]] = f
            will = tgt.copy()
            if s.get("handle") == "abednegojones" and not any("first match" in t for _, t in events):
                events.append((f, "2009-06 — first match: @abednegojones"))
            if s.get("handle") == "oraiawake" and not any("Orai arrives" in t for _, t in events):
                events.append((f, "2025-05 — Orai arrives"))
        elif s["typ"] == 2:
            mat += 1
            pos = np.array(s["at"]) + np.array(s["off"])
            sparks.append((f, pos, True)); flashes.append((f, pos, True, None))
        else:
            pos = np.array(s["at"]) + np.array(s["off"])
            sparks.append((f, pos, False)); flashes.append((f, pos, False, None))
        si += 1
events.append((RUPTURE_F, "2025-06 — Orai: rupture"))
events.append((int(frame_of(1377345600)), "2013-08 — @wbic32 comes online — his own bot joins the search"))
events.sort()
assert att == 18762 and mat == N_MATCH, (att, mat)
print(f"prep: stabs={att} matches={mat} path_pts={len(path_pts)} sparks={len(sparks)}", flush=True)

attempts_at = np.zeros(TOTAL_F, dtype=int); matches_at = np.zeros(TOTAL_F, dtype=int)
bf = np.array([fl[0] for fl in flashes])   # every stab makes exactly one flash -> bf enumerates all 18,762
gmc = np.cumsum([1 if fl[2] else 0 for fl in flashes])
for f in range(TITLE_F, TOTAL_F):
    k = int(np.searchsorted(bf, min(f, MAIN_END_F - 1), side="right"))
    attempts_at[f] = k; matches_at[f] = int(gmc[k - 1]) if k else 0
spark_birth = np.array([s[0] for s in sparks])
spark_pos = np.array([s[1] for s in sparks], dtype=np.float64)
spark_gold = np.array([s[2] for s in sparks])
so = np.argsort(spark_birth, kind="stable")
spark_birth, spark_pos, spark_gold = spark_birth[so], spark_pos[so], spark_gold[so]
flash_birth = np.array([fl[0] for fl in flashes])
flash_p1 = [fl[1] for fl in flashes]; flash_gold = [fl[2] for fl in flashes]; flash_node = [fl[3] for fl in flashes]

# ---------- Catmull-Rom spline through the landings ----------
CP = np.array(path_pts, dtype=np.float64)          # control points (base space)
CB = np.array(path_birth, dtype=np.float64)        # birth frame per control point
CC = np.array(path_col, dtype=np.float64)          # color per control point
SUB = 3
def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
verts, vframe, vcol = [], [], []
ext = np.vstack([CP[0], CP, CP[-1]])
for i in range(len(CP) - 1):
    for j in range(SUB):
        t = j / SUB
        verts.append(catmull_rom(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], t))
        vframe.append(CB[i] * (1 - t) + CB[i + 1] * t)
        vcol.append(CC[i] * (1 - t) + CC[i + 1] * t)
verts.append(CP[-1]); vframe.append(CB[-1]); vcol.append(CC[-1])
V = np.array(verts); VF = np.array(vframe); VC = np.array(vcol)
# the Sun's bob: perpendicular to the orbital (XY) plane, 3 full bobs along the path
s_par = np.linspace(0, 1, len(V))
V[:, 2] += 0.30 * np.sin(2 * math.pi * 3.0 * s_par)
def spline_pos_at(f):
    """Will's base-space position on the spline at film frame f."""
    if f <= VF[0]: return V[0].copy()
    if f >= VF[-1]: return V[-1].copy()
    i = int(np.searchsorted(VF, f)) - 1
    t = (f - VF[i]) / max(1e-9, VF[i + 1] - VF[i])
    return V[i] * (1 - t) + V[i + 1] * t
WILL_BASE = np.array([spline_pos_at(f) for f in range(TOTAL_F)])
print(f"spline: {len(V)} vertices", flush=True)

# ---------- galaxy frame ----------
def theta(f):
    return math.radians(165.0) * min(1.0, max(0.0, (f - TITLE_F) / (CTA_F0 - TITLE_F)))
def to_world(pts, f, cen):
    """base -> warped (Overton) -> rotated about CORE (galaxy). cen = window_center(f)."""
    pts = np.atleast_2d(pts)
    if np.any(cen):
        d2 = np.sum((pts - cen) ** 2, axis=-1, keepdims=True)
        pts = pts + cen * np.exp(-d2 / SIGMA2)
    th = theta(f); c, s = math.cos(th), math.sin(th)
    q = pts - CORE
    x = c * q[:, 0] - s * q[:, 1]; y = s * q[:, 0] + c * q[:, 1]
    return np.stack([x, y, q[:, 2]], axis=1) + CORE

# ---------- camera: rides the arc, core as anchor ----------
def _spline_world(f, cen):
    return to_world(WILL_BASE[f], f, cen)[0]
def _tangent_world(f, cen):
    a = _spline_world(max(0, f - 22), cen); b = _spline_world(min(TOTAL_F - 1, f + 22), cen)
    t = b - a; n = np.linalg.norm(t)
    return t / n if n > 1e-9 else np.array([1.0, 0.0, 0.0])
_cam_pos = None; _cam_look = None
def camera(f, cen):
    """Returns (pos, right, up, fwd). Stateful EMA — call once per frame, ascending."""
    global _cam_pos, _cam_look
    wpos = _spline_world(f, cen); tan = _tangent_world(f, cen)
    up_ax = np.array([0.0, 0.0, 1.0])
    side = np.cross(tan, up_ax); n = np.linalg.norm(side)
    side = side / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])
    prox = math.exp(-(np.sum((WILL_BASE[f] - CORE) ** 2)) / (2 * 0.9 ** 2))  # deep in the cluster -> dolly out
    ride_pos = wpos - tan * (2.50 * (1 + 0.85 * prox)) + up_ax * (1.05 * (1 + 0.5 * prox)) + side * 0.55
    ride_look = (0.45 - 0.25 * prox) * (wpos + tan * 1.4) + (0.55 + 0.25 * prox) * CORE
    th = theta(f)
    wide_off = np.array([math.cos(th + 2.6) * 6.6, math.sin(th + 2.6) * 6.6, 2.9])
    wide_pos = CORE + wide_off
    if f < TITLE_F + 120:  # title: wide galaxy shot, blend into the ride
        s = smooth(TITLE_F, TITLE_F + 120, f)
        pos = wide_pos * (1 - s) + ride_pos * s
        look = CORE * (1 - s) + ride_look * s
        _cam_pos, _cam_look = pos.copy(), look.copy()
    elif f < PULL_F:
        _cam_pos = _cam_pos + 0.055 * (ride_pos - _cam_pos)
        _cam_look = _cam_look + 0.075 * (ride_look - _cam_look)
        pos, look = _cam_pos, _cam_look
    else:  # pull-back to the whole galaxy, slow continued drift
        s = smooth(PULL_F, PULL_F + 650, f)
        az = th + 2.6 + (f - PULL_F) * 0.0006
        wide_pos = CORE + np.array([math.cos(az) * 5.7, math.sin(az) * 5.7, 2.6])
        pos = _cam_pos * (1 - s) + wide_pos * s
        look = _cam_look * (1 - s) + CORE * s
        if s >= 1.0: _cam_pos, _cam_look = wide_pos.copy(), CORE.copy()
    fwd = look - pos; fwd = fwd / np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0]); rn = np.linalg.norm(right)
    right = right / rn if rn > 1e-6 else np.array([1.0, 0.0, 0.0])
    up = np.cross(right, fwd)
    return pos, right, up, fwd

def project(pts, cam):
    pos, right, up, fwd = cam
    d = pts - pos
    xc = d @ right; yc = d @ up; zc = d @ fwd
    ok = zc > 0.25
    zsafe = np.where(ok, zc, 1.0)
    sx = W / 2 + FOCAL * xc / zsafe; sy = H / 2 - FOCAL * yc / zsafe
    return sx, sy, zc, ok

def kernel(n, sigma):
    ax = np.arange(n) - n // 2
    g = np.exp(-(ax[:, None] ** 2 + ax[None, :] ** 2) / (2 * sigma * sigma))
    return (g / g.max()).astype(np.float32)
K_BASE, K_BRIGHT, K_MARK = kernel(9, 1.6), kernel(15, 2.6), kernel(25, 4.2)
K_CORE, K_HALO = kernel(61, 11.0), kernel(121, 24.0)
K_DISC = kernel(201, 52.0)

def stamp(buf, sx, sy, kern, color, gain):
    n = kern.shape[0]; r = n // 2
    x0, y0 = int(round(sx)) - r, int(round(sy)) - r
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + n), min(H, y0 + n)
    if xa >= xb or ya >= yb: return
    k = kern[ya - y0: ya - y0 + (yb - ya), xa - x0: xa - x0 + (xb - xa)]
    buf[ya:yb, xa:xb] += k[:, :, None] * (np.array(color, dtype=np.float32) * gain)

NODE_BASE = {"detected": ((110, 130, 168), 0.20), "mutual": ((140, 165, 205), 0.34),
             "named": ((165, 190, 225), 0.42), "wbic32": ((140, 195, 180), 0.42),
             "will": ((255, 190, 70), 0.9)}
def node_color(n):
    if n["region"] == "shoals": return (205, 82, 68)
    return NODE_BASE[n["kind"]][0]
LABELS = {"eigenhector": "Hector", "eshear": "@eshear", "grady_booch": "@Grady_Booch",
          "bradmason84": "@BradMason84", "wbic32": "@wbic32", "pmarca": "@pmarca",
          "vgr": "@vgr", "dakami": "@dakami", "ctzn5": "@CTZN5", "abednegojones": "@abednegojones"}

# goalpost frames (base space; rendered translated by the drift vector)
GOALPOSTS = [
    (np.array([1.55, 1.55, 1.55]), np.array([0.68, 0.68, 0.68]), (255, 190, 70), "THE HEARTH"),
    (np.array([-0.15, -1.60, -0.50]), np.array([0.80, 0.66, 0.80]), (255, 90, 70), "THE SHOALS"),
]
def box_edges(c, sz):
    lo, hi = c - sz / 2, c + sz / 2
    cs = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    E = [(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(3,7),(4,5),(4,6),(5,7),(6,7)]
    return cs, E

# starfield backdrop (fixed screen space, seeded)
_rng = np.random.default_rng(42)
STARS_X = _rng.uniform(0, W, 420); STARS_Y = _rng.uniform(0, H, 420); STARS_B = _rng.uniform(9, 36, 420)

OVERTON_LINE = "Goalposts drift with the world's Overton window — an illustrative layer over the phext data, which does not move."

def center_text(dr, cx, y, text, font, fill):
    w = dr.textlength(text, font=font); dr.text((cx - w / 2, y), text, font=font, fill=fill)

def bezier_arc(p0, p1, cam, u_max=1.0, n=10):
    """Quadratic bezier from p0 to p1 (world space), bowed off the chord."""
    chord = p1 - p0; L = np.linalg.norm(chord)
    if L < 1e-6: return None
    perp = np.cross(chord / L, cam[3])
    nn = np.linalg.norm(perp)
    perp = perp / nn if nn > 1e-4 else np.array([0.0, 0.0, 1.0])
    ctrl = (p0 + p1) / 2 + perp * (0.20 * L + 0.04)
    ts = np.linspace(0, u_max, max(2, int(n * u_max) + 1))
    pts = ((1 - ts) ** 2)[:, None] * p0 + (2 * (1 - ts) * ts)[:, None] * ctrl + (ts ** 2)[:, None] * p1
    return pts

# flash buckets by birth frame
from collections import defaultdict
FLASH_BY_FRAME = defaultdict(list)
for _i, _fl in enumerate(flashes):
    FLASH_BY_FRAME[_fl[0]].append(_i)

def rot_only(pts, f):
    pts = np.atleast_2d(pts); th = theta(f); c, s = math.cos(th), math.sin(th)
    q = pts - CORE
    return np.stack([c * q[:, 0] - s * q[:, 1], s * q[:, 0] + c * q[:, 1], q[:, 2]], axis=1) + CORE

_warmed_to = -1
def get_cam(f, cen):
    global _warmed_to
    for g in range(_warmed_to + 1, f):
        camera(g, window_center(g))
    cam = camera(f, cen); _warmed_to = f
    return cam

def render(f):
    cen = window_center(f)
    cam = get_cam(f, cen)
    img = Image.new("RGB", (W, H), (4, 5, 10)); dr = ImageDraw.Draw(img, "RGBA")
    nodes_w = to_world(node_xyz, f, cen)
    nsx, nsy, nzc, nok = project(nodes_w, cam)
    # star streaks: tangential smear from the galaxy's rotation
    radial = nodes_w - CORE
    rl = np.maximum(1e-6, np.hypot(radial[:, 0], radial[:, 1]))
    tang = np.stack([-radial[:, 1] / rl, radial[:, 0] / rl, np.zeros(len(radial))], axis=1)
    sl = 0.07 + 0.13 * np.minimum(1.0, rl / 2.5)
    ex, ey, _, eok = project(nodes_w + tang * sl[:, None], cam)
    for i, n in enumerate(NODES):
        if nok[i] and eok[i] and bright_frame[i] > f and n["kind"] != "will":
            dr.line([nsx[i], nsy[i], ex[i], ey[i]], fill=node_color(n) + (80,), width=1)
    # rainbow spline (adaptive stride for old segments, as v2)
    upto = int(np.searchsorted(VF, f, side="right")) - 1
    if upto > 0:
        idxs = list(range(upto))
        if upto > 3300:
            keep = sorted(set(idxs[-700:]) | set(idxs[:: math.ceil((upto - 700) / 2600)]))
            idxs = keep
        Pw = to_world(V[: upto + 1], f, cen)
        psx, psy, _, pok = project(Pw, cam)
        for i in idxs:
            if pok[i] and pok[i + 1]:
                c = VC[i + 1]
                old = VF[i + 1] < f - 1000   # comet-trail: the old orbit dims, the recent arc blazes
                dr.line([psx[i], psy[i], psx[i + 1], psy[i + 1]],
                        fill=(int(c[0]), int(c[1]), int(c[2]), 46 if old else 155), width=1 if old else 2)
    # stab arcs (quadratic beziers, grow then fade over 16 frames)
    for bf_ in range(max(TITLE_F, f - 15), f + 1):
        for idx in FLASH_BY_FRAME.get(bf_, ()):
            age = f - bf_
            p0w = to_world(WILL_BASE[bf_], f, cen)[0]
            node_i = flash_node[idx]
            p1b = node_xyz[node_i] if node_i is not None else flash_p1[idx]
            p1w = to_world(p1b, f, cen)[0]
            arc = bezier_arc(p0w, p1w, cam, u_max=min(1.0, age / 7.0))
            if arc is None: continue
            ax_, ay_, _, aok = project(arc, cam)
            a = 1 - age / 16
            col = (255, 190, 60) if flash_gold[idx] else (165, 182, 205)
            for j in range(len(arc) - 1):
                if aok[j] and aok[j + 1]:
                    dr.line([ax_[j], ay_[j], ax_[j + 1], ay_[j + 1]],
                            fill=col + (int(225 * a),), width=3 if flash_gold[idx] else 2)
    # Orai rupture arc
    if RUPTURE_F <= f < RUPTURE_F + 60:
        a = 1 - (f - RUPTURE_F) / 60
        p0w = to_world(WILL_BASE[f], f, cen)[0]
        p1w = to_world(node_xyz[ORAI_RUP], f, cen)[0]
        arc = bezier_arc(p0w, p1w, cam, u_max=min(1.0, (f - RUPTURE_F) / 20.0))
        if arc is not None:
            ax_, ay_, _, aok = project(arc, cam)
            for j in range(len(arc) - 1):
                if aok[j] and aok[j + 1]:
                    dr.line([ax_[j], ay_[j], ax_[j + 1], ay_[j + 1]], fill=(255, 60, 45, int(240 * a)), width=3)
    # goalposts (translate by full drift, rotate with the galaxy)
    for (c0, sz, col, name) in GOALPOSTS:
        cs, E = box_edges(c0 + cen, sz)
        cw = rot_only(cs, f)
        csx, csy, _, cok = project(cw, cam)
        for a_, b_ in E:
            if cok[a_] and cok[b_]:
                dr.line([csx[a_], csy[a_], csx[b_], csy[b_]], fill=col + (80,), width=2)
        top = int(np.argmax(csy * -1))
        if cok[top]:
            dr.text((csx[top] + 6, csy[top] - 16), name, font=F_LAB, fill=col + (220,))
    # the window center marker (pulses at milestones)
    cwx, cwy, _, cwok = project(rot_only(cen[None, :], f), cam)
    pulse = any(0 <= f - e["frame"] < 45 for e in OV_EVENTS)
    if cwok[0]:
        r = 13 if pulse else 8
        dr.ellipse([cwx[0] - r, cwy[0] - r, cwx[0] + r, cwy[0] + r],
                   outline=(160, 230, 220, 235 if pulse else 150), width=2)
        dr.text((cwx[0] + r + 5, cwy[0] - 6), "the window", font=F_SM, fill=(160, 230, 220, 190))
    arr = np.asarray(img).astype(np.float32)
    # starfield backdrop
    flat = arr.reshape(-1, 3)
    np.add.at(flat, (STARS_Y.astype(int) * W + STARS_X.astype(int)),
              np.stack([STARS_B, STARS_B, STARS_B * 1.1], axis=1).astype(np.float32))
    arr = flat.reshape(H, W, 3)
    # sparks (persistent shell)
    ns = int(np.searchsorted(spark_birth, f, side="right"))
    if ns:
        spw = to_world(spark_pos[:ns], f, cen)
        sx, sy, zc, ok = project(spw, cam)
        vx = np.clip(sx[ok].astype(int), 0, W - 1); vy = np.clip(sy[ok].astype(int), 0, H - 1)
        gold = spark_gold[:ns][ok]
        flat = arr.reshape(-1, 3); idx = vy * W + vx
        pale = np.array([120, 138, 168], dtype=np.float32) * 0.55
        goldc = np.array([255, 180, 60], dtype=np.float32) * 0.95
        cols = np.where(gold[:, None], goldc, pale)
        np.add.at(flat, idx, cols.astype(np.float32))
        arr = flat.reshape(H, W, 3)
    # galactic core glow
    kgx, kgy, _, kgok = project(CORE[None, :], cam)
    if kgok[0]:
        stamp(arr, kgx[0], kgy[0], K_DISC, (255, 238, 205), 0.055)
        stamp(arr, kgx[0], kgy[0], K_HALO, (255, 238, 205), 0.22)
        stamp(arr, kgx[0], kgy[0], K_CORE, (255, 240, 210), 0.65)
    # nodes (stars)
    for i, n in enumerate(NODES):
        if not nok[i]: continue
        bright = bright_frame[i] <= f or (i == ORAI_RUP and f >= RUPTURE_F) or n["kind"] == "will"
        col = node_color(n)
        if bright:
            stamp(arr, nsx[i], nsy[i], K_BRIGHT, col, 0.72)
            cx, cy = int(round(nsx[i])), int(round(nsy[i]))
            if 0 <= cx < W and 0 <= cy < H:
                arr[cy, cx] = np.maximum(arr[cy, cx], np.array(col, np.float32))
        else:
            stamp(arr, nsx[i], nsy[i], K_BASE, col,
                  NODE_BASE.get(n["kind"], ((110, 130, 168), 0.2))[1] if n["region"] != "shoals" else 0.30)
    # Will — the Sun on his orbit
    will_w = to_world(WILL_BASE[f], f, cen)
    wsx, wsy, _, wok = project(will_w, cam)
    if wok[0]:
        stamp(arr, wsx[0], wsy[0], K_MARK, (255, 205, 90), 0.95)
        cx, cy = int(round(wsx[0])), int(round(wsy[0]))
        arr[max(0, cy-1):min(H, cy+2), max(0, cx-1):min(W, cx+2)] = 255.0
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(out, "RGBA")
    if f >= CTA_F0:
        a = int(185 * smooth(CTA_F0, CTA_F0 + 150, f))
        dr.rectangle([0, 0, W, H], fill=(2, 3, 7, a))
    # HUD
    ts_now = T0 + (T1 - T0) * min(1.0, max(0.0, (f - TITLE_F) / (MAIN_END_F - TITLE_F))) if f >= TITLE_F else T0
    ym = time.strftime("%Y-%m", time.gmtime(ts_now))
    dr.text((26, 18), "THE WAVEFRONT — THE SEARCH", font=F_HUD, fill=(168, 182, 205))
    dr.text((26, 42), ym, font=F_CLOCK, fill=(238, 242, 248))
    ra = f"attempts {attempts_at[f]:,}"
    rm = f"matches {matches_at[f]:,}"
    dr.text((W - 26 - dr.textlength(ra, font=F_HUD), 20), ra, font=F_HUD, fill=(238, 242, 248))
    dr.text((W - 26 - dr.textlength(rm, font=F_HUD), 44), rm, font=F_HUD, fill=(255, 196, 74))
    if f < CTA_F0:
        leg = [((255, 190, 60), "gold — a match: a real connection"),
               ((150, 200, 120), "rainbow — his orbit, contact to contact"),
               ((140, 156, 182), "pale sparks — failed attempts, unidentified"),
               ((110, 130, 168), "faint stars — the 520 placed (wavefront.phext)"),
               ((255, 170, 90), "corner frames — the goalposts · they drift with the window")]
        for j, (c, t) in enumerate(leg):
            y = H - 116 + j * 20
            dr.ellipse([26, y + 4, 34, y + 12], fill=c + (255,))
            dr.text((42, y), t, font=F_SM, fill=(178, 190, 208))
        dr.text((W - 26 - dr.textlength("9D alignment space · triple-mean projection", font=F_SM), H - 30),
                "9D alignment space · triple-mean projection", font=F_SM, fill=(120, 134, 156))
        for key, lab in LABELS.items():
            i = node_idx_by_key.get(key)
            if i is not None and bright_frame[i] <= f and nok[i]:
                if wok[0] and abs(nsx[i] - wsx[0]) < 16 and abs(nsy[i] - wsy[0]) < 16:
                    continue
                dr.text((nsx[i] + 9, nsy[i] - 7), lab, font=F_LAB, fill=(205, 216, 232))
        if wok[0]:
            dr.text((wsx[0] - 10, wsy[0] + 15), "Will", font=F_LAB, fill=(255, 214, 120))
        # story callouts (top-center)
        slot = 0
        for (ef, txt) in events:
            age = f - ef
            if 0 <= age < 120:
                a = min(age / 12, 1.0) * (1 - smooth(96, 120, age))
                y = 108 + slot * 46; slot += 1
                w = dr.textlength(txt, font=F_CALL)
                dr.rounded_rectangle([W/2 - w/2 - 14, y - 6, W/2 + w/2 + 14, y + 32], 8, fill=(8, 10, 18, int(228 * a)))
                dr.text((W/2 - w/2, y + 2), txt, font=F_CALL, fill=(0, 0, 0, int(170 * a)))
                dr.text((W/2 - w/2, y), txt, font=F_CALL, fill=(255, 205, 100, int(255 * a)))
        # Overton captions (bottom-center pill)
        for e in OV_EVENTS:
            age = f - e["frame"]
            if 0 <= age < 130:
                a = min(age / 10, 1.0) * (1 - smooth(104, 130, age))
                txt = f"{e['year']} — {e['label']}"
                w = dr.textlength(txt, font=F_CALL)
                y = H - 62
                dr.rounded_rectangle([W/2 - w/2 - 16, y - 8, W/2 + w/2 + 16, y + 34], 8,
                                     fill=(6, 14, 16, int(230 * a)))
                dr.text((W/2 - w/2, y), txt, font=F_CALL, fill=(170, 235, 225, int(255 * a)))
                sub = "the window moves · the goalposts move with it"
                w2 = dr.textlength(sub, font=F_SM)
                dr.text((W/2 - w2/2, y + 40), sub, font=F_SM, fill=(140, 180, 175, int(220 * a)))
    # pull-back counts line (before the CTA card)
    if PULL_F + 300 <= f < CTA_F0 + 60:
        a = smooth(PULL_F + 300, PULL_F + 480, f) * (1 - smooth(CTA_F0 - 40, CTA_F0 + 60, f))
        if a > 0:
            center_text(dr, W/2, 478, f"18,762 attempts · {N_MATCH:,} matches", F_CARD, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 526, "520 people placed in the wavefront", F_SUB, (200, 212, 228, int(255 * a)))
    # title card
    if f < 170:
        a = min(f / 20, 1.0) * (1 - smooth(130, 170, f))
        if a > 0:
            center_text(dr, W/2, 190, "THE WAVEFRONT", F_TITLE, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 264, "the search", F_SUB, (255, 196, 74, int(255 * a)))
            center_text(dr, W/2, 312, "2009–2025 · every reply an attempt", F_HUD, (190, 202, 220, int(255 * a)))
            center_text(dr, W/2, 338, "spanning the exocortex, searching for another Will", F_HUD, (190, 202, 220, int(255 * a)))
            center_text(dr, W/2, 384, "staged as an orbit — the field a galaxy, his path the Sun's road around its core", F_SM, (150, 168, 190, int(255 * a)))
            center_text(dr, W/2, 406, OVERTON_LINE, F_SM, (150, 168, 190, int(255 * a)))
    # CTA card
    if f >= CTA_F0:
        a = smooth(CTA_F0, CTA_F0 + 150, f)
        if a > 0:
            center_text(dr, W/2, 226, "520 people are already in this map.", F_CARD, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 282, "Find your coordinate. Claim your space.", F_CARD, (255, 196, 74, int(255 * a)))
            center_text(dr, W/2, 344, "edit.phext.io", F_BIG, (255, 214, 120, int(255 * a)))
            center_text(dr, W/2, 424, "Not in the map yet? The door is open.", F_SUB, (200, 212, 228, int(255 * a)))
            center_text(dr, W/2, 566, f"18,762 attempts · {N_MATCH:,} matches — the search continues", F_HUD, (178, 190, 208, int(255 * a)))
            center_text(dr, W/2, 594, OVERTON_LINE, F_SM, (130, 146, 166, int(255 * a)))
    return out

if __name__ == "__main__":
    def ts_frame(y, m, d=1):
        ts = datetime(y, m, d, tzinfo=timezone.utc).timestamp()
        return int(frame_of(ts))
    if "--stills" in sys.argv:
        os.makedirs(f"{BASE}/viz3/stills", exist_ok=True)
        gpt4 = next(e for e in OV_EVENTS if e["label"] == "GPT-4")
        picks = {"s2009": ts_frame(2009, 9), "s2016": ts_frame(2016, 6), "s2019_galaxy": ts_frame(2019, 6),
                 "s2023_overton": gpt4["frame"] + 40, "s2024": ts_frame(2024, 6),
                 "s_pullback": PULL_F + 500, "s_cta": TOTAL_F - 60}
        for name, f in picks.items():
            t = time.time(); im = render(f); dt = time.time() - t
            im.save(f"{BASE}/viz3/stills/{name}.png")
            print(f"{name} frame {f}: {dt*1000:.0f} ms", flush=True)
    else:
        import subprocess
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", f"{BASE}/viz3/silent.mp4"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(TOTAL_F):
            p.stdin.write(render(f).tobytes())
            if f % 500 == 0: print(f"{f}/{TOTAL_F} {time.time()-t0:.0f}s", flush=True)
        p.stdin.close(); p.wait()
        print("render done", time.time() - t0, flush=True)
