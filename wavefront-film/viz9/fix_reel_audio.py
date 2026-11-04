#!/usr/bin/env python3
"""Two-pass loudness for the v9 stress reel.

The single-pass loudnorm in assemble_reel.py landed at -11.9 LUFS /
-1.3 dBTP (dynamic single-pass undershoots hot source material).
Standard cure: measure the assembled mix with loudnorm's JSON
analysis, then apply loudnorm with measured_* parameters and
linear=true, remux over the existing (untouched) video, and MEASURE
the result on the output file.

Target (ledger decision, G7/C19): -14 LUFS integrated, TP <= -1.5 dBFS.
"""
import json, re, subprocess, sys, os

WS = os.path.expanduser("~/workspace/wavefront")
SONG = os.path.join(WS, "viz5/song_edit.wav")
REEL = os.path.join(WS, "wavefront-viz-v9-stress-reel.mp4")
TMP = os.path.expanduser("~/workspace/wavefront/viz9/reel_audio_tmp")
os.makedirs(TMP, exist_ok=True)
FPS = 24
BLOCKS = [(0, 301), (868, 969), (1003, 1104), (1096, 1286), (3258, 3359), (3520, 3802)]
XF = 0.4
TOTAL = sum(b - a for a, b in BLOCKS) / FPS - XF * (len(BLOCKS) - 1)  # 42.833

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stderr[-2500:]); sys.exit(1)
    return r

# 1) the mix, un-normalized
fc, prev = [], None
for i, (a, b) in enumerate(BLOCKS):
    fc.append(f"[0:a]atrim=start={a / FPS:.4f}:end={b / FPS:.4f},asetpts=PTS-STARTPTS[a{i}]")
    if prev is None: prev = "a0"
    else:
        fc.append(f"[{prev}][a{i}]acrossfade=d={XF}:c1=tri:c2=tri[ax{i}]"); prev = f"ax{i}"
fc.append(f"[{prev}]afade=t=out:st={TOTAL - 2.0:.4f}:d=2.0[aout]")
mix = os.path.join(TMP, "mix.wav")
run(["ffmpeg", "-y", "-v", "error", "-i", SONG, "-filter_complex", ";".join(fc),
     "-map", "[aout]", "-ar", "48000", mix])

# 2) measure
r = run(["ffmpeg", "-hide_banner", "-i", mix, "-af",
         "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S).group(0))
print("mix measured:", {k: m[k] for k in ("input_i", "input_tp", "input_lra", "input_thresh")})

# 3) apply with measured parameters. TP target is -1.7 here (not -1.5):
# the AAC encode adds ~0.1-0.2 dB of true-peak overshoot, measured on
# the first pass (WAV -1.5 -> MP4 -1.4); the delivered file must sit
# at <= -1.5, so the WAV is normalized with headroom.
norm = os.path.join(TMP, "norm.wav")
ln = (f"loudnorm=I=-14:TP=-1.7:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
      f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
      f":offset={m['target_offset']}:linear=true")
run(["ffmpeg", "-y", "-v", "error", "-i", mix, "-af", ln, "-ar", "48000", norm])

# 4) remux over the existing video
fixed = REEL + ".fixed.mp4"
run(["ffmpeg", "-y", "-v", "error", "-i", REEL, "-i", norm, "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", fixed])
os.replace(fixed, REEL)

# 5) verify on the delivered file (audio stream only; summary values
# are the LAST I:/Peak: lines ebur128 prints)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", REEL, "-map", "0:a", "-af",
                    "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
i_lufs = re.findall(r"I:\s+(-?[0-9.]+) LUFS", r.stderr)[-1]
tp = re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", r.stderr)[-1]
print(f"REEL FINAL: integrated {i_lufs} LUFS, true peak {tp} dBFS  (target -14 LUFS, TP <= -1.5)")
