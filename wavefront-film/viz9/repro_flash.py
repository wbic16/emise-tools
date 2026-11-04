#!/usr/bin/env python3
"""Repro: re-render v8's flash frames with UNMODIFIED viz8/render8.py and
check (a) whether the white rectangle reproduces deterministically, and
(b) whether the trace-head projection sits in the numpy negative-index
wrap band on exactly those frames."""
import sys, math
sys.path.insert(0, "/home/hatch/workspace/wavefront/viz8")
import numpy as np
import render8 as m
from PIL import Image

def yavg(im):
    return float(np.asarray(im.convert("L"), dtype=np.float64).mean())

def head_proj(f):
    # replicate render()'s own bookkeeping for frame f
    m.CX_CUR = (m.STRIP_X0 / 2) + (m.W / 2 - m.STRIP_X0 / 2) * m.smooth(m.PULL_F, m.CTA_F0, f)
    hop = m.hop_float(f)
    cam = m.camera(f)
    hw = m.to_world(m.spline_pos_at_hop(hop), f, hop)
    sx, sy, zc, ok = m.project(hw, cam)
    return float(sx[0]), float(sy[0]), bool(ok[0])

def painted_fraction(cy, cx):
    """Apply render8's exact head-block slice expression to a zero buffer
    and measure what it actually paints."""
    buf = np.zeros((m.H, m.W), dtype=np.float32)
    buf[max(0, cy - 3):min(m.H, cy + 4), max(0, cx - 3):min(m.W, cx + 4)] = 255.0
    ys, xs = np.nonzero(buf)
    if len(ys) == 0: return 0.0, None
    return float((buf > 0).mean()), (int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max()))

for f in (1465, 1466, 1467, 1468, 2105, 2106, 2160, 2161, 2197, 2198):
    sx, sy, ok = head_proj(f)
    cx, cy = int(round(sx)), int(round(sy))
    frac, bbox = painted_fraction(cy, cx)
    im = m.render(f)
    im.save(f"/home/hatch/workspace/wavefront/viz9/flash-evidence/repro-f{f}.png")
    print(f"f={f} head_xy=({sx:.0f},{sy:.0f}) ok={ok} block_slice_paints={frac*100:.1f}% bbox={bbox} "
          f"re-render YAVG={yavg(im):.2f}", flush=True)
