#!/usr/bin/env python3
"""Probe: silence distribution in the chapter audio, measured from the waveform.
Frame RMS (10 ms), adaptive threshold, report silence runs >= 80 ms."""
import glob, os, wave
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
WAV_DIR = os.path.join(BASE, "out", "wav")

def load(path):
    wf = wave.open(path, "rb")
    x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    wf.close()
    return x

all_sil = []
for path in sorted(glob.glob(os.path.join(WAV_DIR, "*.wav"))):
    x = load(path)
    fr = 160  # 10 ms
    n = len(x) // fr
    rms = np.sqrt((x[:n * fr].reshape(n, fr) ** 2).mean(axis=1) + 1e-12)
    # adaptive threshold: 8% of the 90th-percentile frame RMS, floored at -50 dBFS
    thr = max(np.percentile(rms, 90) * 0.08, 10 ** (-50 / 20))
    quiet = rms < thr
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            runs.append((j - i) * 0.01)
            i = j
        else:
            i += 1
    all_sil.extend(r for r in runs if r >= 0.08)

all_sil.sort()
import statistics
print(f"silences >= 80ms across chapter: n={len(all_sil)}")
if all_sil:
    print(f"min={all_sil[0]:.2f} med={statistics.median(all_sil):.2f} "
          f"p90={all_sil[int(len(all_sil)*0.9)]:.2f} max={all_sil[-1]:.2f}")
    for t in (0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.8, 1.0):
        print(f"  silences >= {t:>4}s: {sum(1 for s in all_sil if s >= t)}")
