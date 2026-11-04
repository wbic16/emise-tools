#!/usr/bin/env python3
"""wavefront-viz v9 — permanent QA gate (Claude C1/C20b, Emi E17).

Runs on any rendered segment set or finished film:
  1. YAVG flash gate: decode every frame's mean luma (ffmpeg
     signalstats); FAIL if |dYAVG| > 8 between consecutive frames.
     (v8 shipped 5 such events; the gate exists so v9 never does.
     For the assembled stress reel, editorial joints are excluded
     explicitly — cuts are supposed to jump.)
  2. Black-frame check: FAIL if any frame's YAVG < 3.0 (a dropped or
     unpainted frame in this film sits near 0; legitimate dark frames
     — title, CTA veil — measure ~5-10).
  3. Palette audit: sample every 6th frame; count green-dominant
     pixels (G - max(R,B) > 25 and G > 110). v8's master measured 0 at
     Claude's cited timestamps; v9 keeps the count at ~0 by scan.
  4. Determinism: sha256-compare two raw-frame dumps of the same
     timeline frame produced by different render processes.

Usage:
  qa9.py gate SEG.mp4 [SEG2.mp4 ...]        # flash + black gates
  qa9.py palette FILM.mp4                    # green-dominance scan
  qa9.py determinism A.rgb B.rgb             # byte-compare raw frames
  qa9.py contact REEL.mp4 OUT.png            # 1 frame / 4 s contact sheet
"""
import os, re, subprocess, sys, hashlib
import numpy as np
from PIL import Image

def yavg_series(path):
    # format=yuv420p first: the gate's thresholds are display-referred
    # 8-bit code values. Without the conversion, signalstats reports
    # YAVG in the file's NATIVE depth — on the 10-bit v9 master every
    # value reads x4.006 and quiet frames trip the flash threshold
    # (found on the Chunk B master, 2026-11-04: raw 10-bit run showed
    # 4 "jumps" of 2.4-3.1 in true 8-bit terms). Thresholds unchanged.
    p = subprocess.run(["ffmpeg", "-v", "info", "-i", path,
                        "-vf", "format=yuv420p,signalstats,metadata=print:key=lavfi.signalstats.YAVG",
                        "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(x) for x in re.findall(r"lavfi\.signalstats\.YAVG=([0-9.]+)", p.stderr)]

def gate(paths, exclude_joints=()):
    ok = True
    for path in paths:
        ys = yavg_series(path)
        jumps = []
        for i in range(1, len(ys)):
            if abs(ys[i] - ys[i - 1]) > 8 and not any(abs(i - j) <= 1 for j in exclude_joints):
                jumps.append((i, round(ys[i - 1], 2), round(ys[i], 2)))
        blacks = [i for i, y in enumerate(ys) if y < 3.0]
        status = "PASS" if not jumps and not blacks else "FAIL"
        if jumps or blacks: ok = False
        print(f"[{status}] {path}: {len(ys)} frames, mean YAVG {np.mean(ys):.2f}, "
              f"flash-jumps {len(jumps)} {jumps[:6]}, black frames {len(blacks)} {blacks[:6]}")
    return ok

def palette(path, w=1920, h=1080):
    """Single decode pass, chunked (the per-frame subprocess version
    took minutes and an in-memory version OOM'd; this streams)."""
    fb = w * h * 3
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path,
                             "-vf", r"select='not(mod(n\,6))'", "-vsync", "vfr",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE)
    tot = 0; frames = 0
    while True:
        raw = proc.stdout.read(fb * 12)
        if not raw: break
        n = len(raw) // fb
        if n == 0: break
        fr = np.frombuffer(raw[: n * fb], dtype=np.uint8).reshape(n, h, w, 3).astype(np.int32)
        tot += int(((fr[:, :, :, 1] - np.maximum(fr[:, :, :, 0], fr[:, :, :, 2]) > 25)
                    & (fr[:, :, :, 1] > 110)).sum()); frames += n
    proc.wait()
    print(f"palette: {frames} sampled frames, green-dominant pixels total {tot}")
    return tot

def determinism(a, b):
    ha = hashlib.sha256(open(a, "rb").read()).hexdigest()
    hb = hashlib.sha256(open(b, "rb").read()).hexdigest()
    print(f"determinism: {a} sha256 {ha[:16]}…")
    print(f"determinism: {b} sha256 {hb[:16]}…")
    print("determinism:", "IDENTICAL" if ha == hb else "DIFFER")
    return ha == hb

def contact(path, outp, every_s=4):
    import io
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())
    times = list(range(0, int(dur), every_s))
    thumbs = []
    for t in times:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path,
                            "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True)
        thumbs.append(Image.open(io.BytesIO(p.stdout)).convert("RGB"))
    tw, th = 480, 270
    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (10, 10, 12))
    for i, im in enumerate(thumbs):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    sheet.save(outp)
    print(f"contact sheet: {len(thumbs)} frames ({times}) -> {outp}")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "gate":
        joints = [int(x) for x in os.environ.get("QA_JOINTS", "").split(",") if x.strip()]
        sys.exit(0 if gate(sys.argv[2:], exclude_joints=joints) else 1)
    elif cmd == "palette":
        palette(sys.argv[2])
    elif cmd == "determinism":
        sys.exit(0 if determinism(sys.argv[2], sys.argv[3]) else 1)
    elif cmd == "contact":
        contact(sys.argv[2], sys.argv[3])
