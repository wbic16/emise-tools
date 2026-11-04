#!/usr/bin/env python3
"""wavefront-viz v2 — THE SEARCH. Custom numpy/PIL renderer.

Will moves only when a stab MATCHES (gold, to the target's true coordinate).
Failed stabs deposit a pale spark beside him; the shell of attempts accumu-
lates around the rainbow path (travel-match polyline, hue by time).
Usage: render2.py --stills | --full
"""
import json, math, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
SONG_DUR = 312.800167
TOTAL_F = int(round(SONG_DUR * FPS))          # 7507
TITLE_F = 96                                   # 4 s title / push-in
MAIN_END_F = int(round(0.90 * TOTAL_F))        # 6756 — search ends, pull-back begins
CARD_F0 = 6880                                 # closing card fade-in start
FOCAL = (H / 2) / math.tan(math.radians(21.0)) # vfov 42 deg
DATA = json.load(open("/home/hatch/workspace/wavefront/viz2/data.json"))
NODES = DATA["nodes"]; STABS = DATA["stabs"]; T0, T1 = DATA["t0"], DATA["t1"]
COUNTS = DATA["counts"]
N_MATCH = COUNTS["travel"] + COUNTS["gold_shell"]
FONT = "/home/hatch/.local/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf/"
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

def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def hsv2rgb(h, s, v):
    i = int(h * 6) % 6; f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    return [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]

# ---------- prep: bucket stabs into frames, walk the journey ----------
stab_ts = np.array([s["ts"] for s in STABS])
def frame_of(ts):  # archive time -> film frame (linear over main segment)
    return TITLE_F + (ts - T0) / (T1 - T0) * (MAIN_END_F - TITLE_F)
stab_frame = np.minimum(MAIN_END_F - 1, np.floor(frame_of(stab_ts)).astype(int))
order = np.argsort(stab_frame, kind="stable")

node_xyz = np.array([n["xyz"] for n in NODES])
node_idx_by_key = {}
for i, n in enumerate(NODES):
    node_idx_by_key.setdefault(n["key"], i)
ORAI_ARR = next(i for i, n in enumerate(NODES) if "arrival" in n["name"])
ORAI_RUP = next(i for i, n in enumerate(NODES) if "rupture" in n["name"])
RUPTURE_F = int(frame_of(1749988800))  # 2025-06-15 12:00 UTC, retained record

will_at_frame = np.zeros((TOTAL_F, 3))
attempts_at = np.zeros(TOTAL_F, dtype=int)
matches_at = np.zeros(TOTAL_F, dtype=int)
bright_frame = np.full(len(NODES), 10**9, dtype=int)
path_birth, path_pts, path_col = [], [], []
sparks = []   # (birth_frame, pos, gold)
flashes = []  # (birth_frame, p0, p1, gold)
events = []   # (frame, text)
will = np.zeros(3); prev = np.zeros(3)
att = mat = 0
si = 0
sorted_idx = order.tolist()
for f in range(TITLE_F, MAIN_END_F):
    while si < len(sorted_idx) and stab_frame[sorted_idx[si]] == f:
        s = STABS[sorted_idx[si]]; att += 1
        if s["typ"] == 1:
            mat += 1
            tgt = node_xyz[s["node"]]
            flashes.append((f, tuple(will), tuple(tgt), True))
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
            pass  # wbic32 beat is date-triggered below (bot created 2013-08-24)
            if s.get("handle") == "oraiawake" and not any("Orai arrives" in t for _, t in events):
                events.append((f, "2025-05 — Orai arrives"))
        elif s["typ"] == 2:
            mat += 1
            pos = np.array(s["at"]) + np.array(s["off"])
            sparks.append((f, pos, True)); flashes.append((f, tuple(s["at"]), tuple(pos), True))
        else:
            pos = np.array(s["at"]) + np.array(s["off"])
            sparks.append((f, pos, False)); flashes.append((f, tuple(s["at"]), tuple(pos), False))
        si += 1
    will_at_frame[f] = will; attempts_at[f] = att; matches_at[f] = mat
for f in range(MAIN_END_F, TOTAL_F):
    will_at_frame[f] = will; attempts_at[f] = att; matches_at[f] = mat
for f in range(0, TITLE_F):
    attempts_at[f] = 0; matches_at[f] = 0
events.append((RUPTURE_F, "2025-06 — Orai: rupture"))
events.append((int(frame_of(1377345600)), "2013-08 — @wbic32 comes online — his own bot joins the search"))
events.sort()
print(f"prep: stabs={att} matches={mat} path_pts={len(path_pts)} sparks={len(sparks)} events={len(events)}", flush=True)

spark_birth = np.array([s[0] for s in sparks])
spark_pos = np.array([s[1] for s in sparks], dtype=np.float64)
spark_gold = np.array([s[2] for s in sparks])
spark_order = np.argsort(spark_birth, kind="stable")
spark_birth, spark_pos, spark_gold = spark_birth[spark_order], spark_pos[spark_order], spark_gold[spark_order]

# camera look-at: EMA of will (main), frozen, then blended to centre (closing)
look = np.zeros((TOTAL_F, 3)); cur = np.zeros(3)
for f in range(TOTAL_F):
    if f < MAIN_END_F:
        cur = cur + 0.05 * (will_at_frame[f] - cur); look[f] = cur
    else:
        s = smooth(MAIN_END_F, MAIN_END_F + 300, f)
        look[f] = cur * (1 - s)
def camera(f):
    if f < TITLE_F:
        s = smooth(0, TITLE_F, f); dist = 8.6 + (3.55 - 8.6) * s; az = math.radians(-30)
        lk = np.zeros(3)
    else:
        p = min(1.0, (f - TITLE_F) / (MAIN_END_F - TITLE_F))
        az = math.radians(-30 + 250 * p)
        dist = 3.55 + 0.10 * math.sin(f / 300.0)
        lk = look[f]
        if f >= MAIN_END_F:
            s = smooth(MAIN_END_F, MAIN_END_F + 300, f)
            dist = dist + (7.8 - dist) * s
            az += math.radians(8) * s
    el = math.radians(23 + 4 * math.sin(min(1.0, f / MAIN_END_F) * math.pi))
    off = dist * np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    pos = lk + off
    fwd = lk - pos; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return pos, right, up, fwd, lk

def project(pts, cam):
    pos, right, up, fwd, _ = cam
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
K_BASE, K_BRIGHT, K_MARK = kernel(9, 1.6), kernel(15, 2.6), kernel(23, 3.8)

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

def center_text(dr, cx, y, text, font, fill):
    w = dr.textlength(text, font=font); dr.text((cx - w / 2, y), text, font=font, fill=fill)

def render(f):
    cam = camera(f)
    img = Image.new("RGB", (W, H), (4, 5, 10)); dr = ImageDraw.Draw(img, "RGBA")
    # cube edges
    C = np.array([[x, y, z] for x in (-2, 2) for y in (-2, 2) for z in (-2, 2)], dtype=float)
    csx, csy, _, cok = project(C, cam)
    EDGES = [(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(3,7),(4,5),(4,6),(5,7),(6,7)]
    for a, b in EDGES:
        if cok[a] and cok[b]:
            dr.line([csx[a], csy[a], csx[b], csy[b]], fill=(70, 82, 105, 90), width=1)
    # rainbow path (adaptive stride for old segments)
    nseg = 0
    births = np.array(path_birth)
    upto = int(np.searchsorted(births, f, side="right")) - 1  # segments fully born
    if upto > 0:
        idxs = list(range(upto))
        if upto > 3300:
            keep = sorted(set(idxs[-700:]) | set(idxs[:: math.ceil((upto - 700) / 2600)]))
            idxs = keep
        P = np.array(path_pts[: upto + 1])
        psx, psy, _, pok = project(P, cam)
        for i in idxs:
            if pok[i] and pok[i + 1]:
                dr.line([psx[i], psy[i], psx[i + 1], psy[i + 1]], fill=path_col[i + 1] + (175,), width=2)
    # stab flashes (last 16 frames)
    for (bf, p0, p1, gold) in flashes:
        age = f - bf
        if 0 <= age < 16:
            a = 1 - age / 16
            col = (255, 190, 60) if gold else (165, 182, 205)
            sx, sy, _, ok = project(np.array([p0, p1]), cam)
            if ok[0] and ok[1]:
                dr.line([sx[0], sy[0], sx[1], sy[1]], fill=col + (int(230 * a),), width=3 if gold else 2)
    # orai rupture stab
    if RUPTURE_F <= f < RUPTURE_F + 60:
        a = 1 - (f - RUPTURE_F) / 60
        sx, sy, _, ok = project(np.array([will_at_frame[f], node_xyz[ORAI_RUP]]), cam)
        if ok[0] and ok[1]:
            dr.line([sx[0], sy[0], sx[1], sy[1]], fill=(255, 60, 45, int(240 * a)), width=3)
    arr = np.asarray(img).astype(np.float32)
    # sparks (persistent shell)
    ns = int(np.searchsorted(spark_birth, f, side="right"))
    if ns:
        sx, sy, zc, ok = project(spark_pos[:ns], cam)
        vx = np.clip(sx[ok].astype(int), 0, W - 1); vy = np.clip(sy[ok].astype(int), 0, H - 1)
        gold = spark_gold[:ns][ok]
        flat = (arr.reshape(-1, 3))
        idx = vy * W + vx
        pale = np.array([120, 138, 168], dtype=np.float32) * 0.55
        goldc = np.array([255, 180, 60], dtype=np.float32) * 0.95
        cols = np.where(gold[:, None], goldc, pale)
        np.add.at(flat, idx, cols.astype(np.float32))
        arr = flat.reshape(H, W, 3)
    # nodes
    nsx, nsy, nzc, nok = project(node_xyz, cam)
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
            stamp(arr, nsx[i], nsy[i], K_BASE, col, NODE_BASE.get(n["kind"], ((110,130,168), 0.2))[1] if n["region"] != "shoals" else 0.30)
    # Will marker
    wsx, wsy, _, wok = project(will_at_frame[f][None, :], cam)
    if wok[0]:
        stamp(arr, wsx[0], wsy[0], K_MARK, (255, 205, 90), 0.9)
        cx, cy = int(round(wsx[0])), int(round(wsy[0]))
        arr[max(0, cy-1):min(H, cy+2), max(0, cx-1):min(W, cx+2)] = 255.0
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(out, "RGBA")
    # closing dark overlay
    if f >= CARD_F0:
        a = int(150 * smooth(CARD_F0, CARD_F0 + 180, f))
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
    leg = [((255, 190, 60), "gold — a match: a real connection"),
           ((150, 200, 120), "rainbow — his path, contact to contact"),
           ((140, 156, 182), "pale sparks — failed attempts, unidentified"),
           ((110, 130, 168), "faint nodes — the 520 placed (wavefront.phext)")]
    for j, (c, t) in enumerate(leg):
        y = H - 96 + j * 20
        dr.ellipse([26, y + 4, 34, y + 12], fill=c + (255,))
        dr.text((42, y), t, font=F_SM, fill=(178, 190, 208))
    dr.text((W - 26 - dr.textlength("9D alignment space · triple-mean projection", font=F_SM), H - 30),
            "9D alignment space · triple-mean projection", font=F_SM, fill=(120, 134, 156))
    # labels for brightened named nodes
    for key, lab in LABELS.items():
        i = node_idx_by_key.get(key)
        if i is not None and bright_frame[i] <= f and nok[i]:
            if wok[0] and abs(nsx[i] - wsx[0]) < 16 and abs(nsy[i] - wsy[0]) < 16:
                continue  # Will is standing on this node; his label carries it
            dr.text((nsx[i] + 9, nsy[i] - 7), lab, font=F_LAB, fill=(205, 216, 232))
    if wok[0]:
        dr.text((wsx[0] - 10, wsy[0] + 13), "Will", font=F_LAB, fill=(255, 214, 120))
    # callouts (stacked when beats collide)
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
    # title card
    if f < 150:
        a = min(f / 20, 1.0) * (1 - smooth(110, 150, f))
        if a > 0:
            center_text(dr, W/2, 218, "THE WAVEFRONT", F_TITLE, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 292, "the search", F_SUB, (255, 196, 74, int(255 * a)))
            center_text(dr, W/2, 340, "2009–2025 · every reply an attempt", F_HUD, (190, 202, 220, int(255 * a)))
            center_text(dr, W/2, 368, "spanning the exocortex, searching for another Will", F_HUD, (190, 202, 220, int(255 * a)))
    # closing card
    if f >= CARD_F0:
        a = smooth(CARD_F0, CARD_F0 + 180, f)
        if a > 0:
            center_text(dr, W/2, 268, f"18,762 attempts · {N_MATCH:,} matches", F_CARD, (240, 244, 250, int(255 * a)))
            center_text(dr, W/2, 318, "520 people placed in the wavefront", F_SUB, (200, 212, 228, int(255 * a)))
            center_text(dr, W/2, 362, "spanning the exocortex, searching for another Will", F_CARD2, (178, 190, 208, int(255 * a)))
            center_text(dr, W/2, 396, "the search continues", F_SUB, (255, 196, 74, int(255 * a)))
    return out

if __name__ == "__main__":
    if "--stills" in sys.argv:
        os.makedirs("/home/hatch/workspace/wavefront/viz2/stills", exist_ok=True)
        for f in (400, 2900, 6300, 6725, 6790, 7450):
            t = time.time(); im = render(f); dt = time.time() - t
            im.save(f"/home/hatch/workspace/wavefront/viz2/stills/f{f}.png")
            print(f"frame {f}: {dt*1000:.0f} ms", flush=True)
    else:
        import subprocess
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", "/home/hatch/workspace/wavefront/viz2/silent.mp4"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(TOTAL_F):
            p.stdin.write(render(f).tobytes())
            if f % 500 == 0: print(f"{f}/{TOTAL_F} {time.time()-t0:.0f}s", flush=True)
        p.stdin.close(); p.wait()
        print("render done", time.time() - t0, flush=True)
