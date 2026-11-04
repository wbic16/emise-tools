#!/usr/bin/env python3
"""wavefront-viz v10 — C13 residual-overshoot audit.

Re-projects every live arc exactly as render10.py draws it — WITH
the C13 relief active (camera() reads the ARC_EDGE series; the bow
cap factor is replicated from render_single; the vertical centre
CY_CUR is set per frame as render_single sets it) — and reports how
far above the top edge any in-field (zc >= 0.9) arc point still
reaches. Run on the node after render10.py is staged; import of the
renderer runs its normal prep (arc-edge cache hit).

Usage: V10_ROOT=... python edge_audit.py [f0 f1]
"""
import math, os, sys
import numpy as np
sys.path.insert(0, "/home/wbic16/emise-v10/root/wavefront/viz10")
import render10 as R

if os.environ.get("EDGE_AUDIT_BASELINE"):
    # A/B control: zero pressure -> camera relief 0, CY centred, bow
    # cap factor 1 — i.e. the v9 framing, measured uncapped.
    R.ARC_EDGE = np.zeros(R.TOTAL_F)
    print("BASELINE MODE: relief disabled (v9 framing)", flush=True)

f0 = int(sys.argv[1]) if len(sys.argv) > 1 else 0
f1 = int(sys.argv[2]) if len(sys.argv) > 2 else R.TOTAL_F

live = {}
for j in range(len(R.land_hop)):
    life_j = 8.0 + 7.0 * float(R.HUSH9_HOP[R.land_hop[j]])
    for f in range(max(f0, int(math.ceil(R.land_frame[j]))),
                   min(f1, int(R.land_frame[j] + life_j) + 1)):
        live.setdefault(f, []).append(j)

worst = []          # (overshoot, frame)
over_frames = 0
for f in range(f0, f1):
    js = live.get(f)
    if not js:
        continue
    ff = float(f)
    hop = R.hop_float(ff)
    edge = float(np.interp(ff, R._fax, R.ARC_EDGE))
    R.CY_CUR = (R.H / 2) + 240.0 * edge * (1.0 - R.smooth(R.PULL_F, R.CTA_F0, ff))
    cam = R.camera(ff)
    pos = R.node_pos_all(R.node_hop(ff))
    coh = R.sig_at(R.COH_HOP, hop)
    fmax = 0.0
    for j in js:
        sj = R.STABS[R.land_hop[j]]
        if sj["typ"] == 1 and sj["node"] in R.EXCLUDE:
            continue
        age = ff - R.land_frame[j]
        life = 8.0 + 7.0 * float(R.HUSH9_HOP[R.land_hop[j]])
        if age < 0 or age > life:
            continue
        p0 = R.to_world(R.land_prev[j], ff, hop)[0]
        p1 = R.to_world(pos[sj["node"]], ff, hop)[0] if sj["typ"] == 1 else R.to_world(R.CP[j], ff, hop)[0]
        bow = (0.50 + 1.20 * float(R.HN9_LAND[j])) * (1.0 - 0.35 * coh) * (1.0 - 0.75 * edge)
        jit = float(R.JIT_LAND[j]) * 0.09 * float(np.linalg.norm(p1 - p0)) * float(R.HN9_LAND[j]) ** 2
        arc = R.bezier_arc9(p0, p1, u_max=min(1.0, age / 4.5), bow_scale=bow, jit_mag=jit)
        if arc is None:
            continue
        _, ay, az, aok = R.project(arc, cam)
        aok = aok & (az >= 0.9)
        if aok.any():
            fmax = max(fmax, -float(np.min(ay[aok])))
    if fmax > 0:
        over_frames += 1
        worst.append((fmax, f))

worst.sort(reverse=True)
print(f"frames audited {f0}..{f1}: frames with any residual overshoot: {over_frames}")
for ov, f in worst[:12]:
    print(f"  frame {f}: residual overshoot {ov:.0f} px (4K) = {ov/2:.0f} px at 1080p")
if worst:
    arr = np.array([w[0] for w in worst])
    print(f"residual overshoot: p50 {np.percentile(arr, 50):.0f}  p90 {np.percentile(arr, 90):.0f}  "
          f"p99 {np.percentile(arr, 99):.0f}  max {arr.max():.0f} px (4K)")
else:
    print("no residual overshoot anywhere")
