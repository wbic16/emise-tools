#!/usr/bin/env python3
"""Assemble the v9 stress reel from the ranch-rendered segments.

Blocks (timeline frames, 24 fps): opening 0-301, turbulence 868-969,
burst 1003-1104, mutuals 1096-1286, hush 3258-3359, pullback+CTA
3520-3802. Video blocks join with 0.4 s dissolves (xfade); the song
(viz5/song_edit.wav) is sliced at the SAME timeline offsets and joined
with matching 0.4 s crossfades, faded out over the final 2 s, and
loudness-normalized single-pass to -14 LUFS integrated / TP -1.5 dBFS
(the G7/C19 resolved target; the achieved values are measured on the
output file afterwards, not assumed).
Output: ~/workspace/wavefront/wavefront-viz-v9-stress-reel.mp4
"""
import subprocess, sys, os

SEG = os.path.expanduser("~/workspace/wavefront/viz9/segs")
SONG = os.path.expanduser("~/workspace/wavefront/viz5/song_edit.wav")
OUT = os.path.expanduser("~/workspace/wavefront/wavefront-viz-v9-stress-reel.mp4")
FPS = 24

BLOCKS = [  # (segment file, timeline frame a, frame b)
    ("s1.mp4", 0, 301), ("s2.mp4", 868, 969), ("s3.mp4", 1003, 1104),
    ("s4.mp4", 1096, 1286), ("s5.mp4", 3258, 3359), ("s6.mp4", 3520, 3802),
]
XF = 0.4

def run(cmd):
    print("+", " ".join(cmd[:6]), "…", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:]); sys.exit(1)

# 1) lossless concat of the two split pairs
for pair, parts in (("s1.mp4", ("s1a.mp4", "s1b.mp4")), ("s6.mp4", ("s6a.mp4", "s6b.mp4"))):
    lst = os.path.join(SEG, pair + ".txt")
    with open(lst, "w") as fh:
        for p in parts: fh.write(f"file '{os.path.join(SEG, p)}'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", os.path.join(SEG, pair)])

# 2) xfade video + crossfaded song slices + loudnorm
inputs = []
for name, a, b in BLOCKS: inputs += ["-i", os.path.join(SEG, name)]
inputs += ["-i", SONG]
song_in = len(BLOCKS)
fc = []
for i in range(len(BLOCKS)):
    fc.append(f"[{i}:v]format=yuv420p,setsar=1,fps=24[v{i}]")
prev = "v0"; cum = (BLOCKS[0][2] - BLOCKS[0][1]) / FPS
for i in range(1, len(BLOCKS)):
    dur = (BLOCKS[i][2] - BLOCKS[i][1]) / FPS
    off = cum - XF
    lbl = f"x{i}"
    fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.4f}[{lbl}]")
    prev = lbl; cum = cum + dur - XF
fc.append(f"[{prev}]null[vout]")
aprev = None
for i, (name, a, b) in enumerate(BLOCKS):
    lbl = f"a{i}"
    fc.append(f"[{song_in}:a]atrim=start={a / FPS:.4f}:end={b / FPS:.4f},asetpts=PTS-STARTPTS[{lbl}]")
    if aprev is None: aprev = lbl
    else:
        nl = f"ax{i}"
        fc.append(f"[{aprev}][{lbl}]acrossfade=d={XF}:c1=tri:c2=tri[{nl}]")
        aprev = nl
total = cum
# NOTE: this single-pass loudnorm undershoots on hot material (landed
# -11.9 LUFS / -1.3 TP when the reel was first assembled). The delivered
# reel's audio is finished by fix_reel_audio.py (two-pass measured
# loudnorm, TP -1.7 in the WAV to pre-compensate AAC overshoot).
fc.append(f"[{aprev}]afade=t=out:st={total - 2.0:.4f}:d=2.0,"
          f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
run(["ffmpeg", "-y", "-v", "error"] + inputs +
    ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
     "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT])
print("reel ->", OUT, os.path.getsize(OUT), "bytes;", round(total, 2), "s expected")
