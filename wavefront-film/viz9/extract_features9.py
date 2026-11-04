#!/usr/bin/env python3
"""wavefront-viz v9 — signal re-derivation after the v8 entropy audit.

Emi's scientific-integrity item for v9: test whether raw lexical entropy
is primarily tracking tweet length. It is. Measured on the 18,762 hops
(viz8/features.json raw arrays, recomputed here for the record):

    r(entropy_bits, ntok)      = 0.853   (Spearman 0.991)
    r(entropy_bits, log2 ntok) = 0.993
    OLS entropy ~ a + b*log2(ntok): a=0.074, b=0.949, R^2 = 0.987
    median entropy / log2(ntok) = 1.000

For most replies nearly every token is unique, so Shannon entropy is
mechanically ~log2(token count): v8's "entropy weather" was, to ~99% of
variance, a tweet-LENGTH meter. The interesting lexical signal is what
remains after length is removed: how much a tweet repeats itself versus
how much new vocabulary it packs for its size.

v9 signals (this file, output viz9/features9.json):
  H_res   per-hop residual of entropy_bits after OLS on log2(ntok).
          Positive = more lexically diverse than typical for its length;
          negative = more repetitive. r(H_res, ntok) ~= -0.15 (the length
          is out; what remains is repeat structure).
  Hres_n  H_res percentile-normalized [p2, p98] -> [0, 1] (v8's norm()).
  ent_sm9 entropy weather, v9: two-pass rolling mean of Hres_n (windows
          201 then 51, reflected edges — v8's smooth2), re-normalized.
  hush9   v8's joint rule with the new weather: low diversity-weather
          AND warm tone (viz4 tone_smooth).
  coh, bursts, INT: carried from viz8/features.json UNCHANGED — they are
          built from VADER + caps/punctuation densities, which never
          touched lexical entropy.
  song_rms per-output-frame RMS envelope of viz5/song_edit.wav (48 kHz),
          smoothed ~1 s, normalized [0, 1] — used only to let musical
          peaks breathe through the bloom gain (artistic, documented).

Everything here is a deterministic function of viz8/features.json,
viz4/tone.json and the song wav. No archive re-read is needed: the v8
extractor already asserted its hop join against viz2/data.json.
"""
import json
import numpy as np

WAV = "/home/hatch/workspace/wavefront"

F8 = json.load(open(f"{WAV}/viz8/features.json"))
TONE = json.load(open(f"{WAV}/viz4/tone.json"))
H = np.array(F8["hops"]["entropy_bits"], dtype=np.float64)
NTOK = np.array(F8["hops"]["ntok"], dtype=np.float64)
TTR = np.array(F8["hops"]["ttr"], dtype=np.float64)
tone_sm = np.array(TONE["smooth"], dtype=np.float64)
N = len(H)
assert N == 18762

def pearson(a, b): return float(np.corrcoef(a, b)[0, 1])
def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])

logn = np.log2(np.maximum(NTOK, 1.0))
X = np.stack([np.ones_like(logn), logn], axis=1)
beta, *_ = np.linalg.lstsq(X, H, rcond=None)
H_res = H - X @ beta
r2 = 1.0 - float(H_res.var() / H.var())
audit = dict(
    r_entropy_ntok=round(pearson(H, NTOK), 4),
    spearman_entropy_ntok=round(spearman(H, NTOK), 4),
    r_entropy_log2ntok=round(pearson(H, logn), 4),
    ols_a=round(float(beta[0]), 4), ols_b=round(float(beta[1]), 4),
    ols_R2=round(r2, 4),
    median_entropy_over_log2ntok=round(float(np.median(H / np.log2(np.maximum(NTOK, 2.0)))), 4),
    resid_std=round(float(H_res.std()), 4),
    r_resid_ntok=round(pearson(H_res, NTOK), 4),
    r_ttr_ntok=round(pearson(TTR, NTOK), 4),
)
print("entropy/length audit:", json.dumps(audit, indent=1))

def norm(a):
    lo, hi = np.percentile(a, 2), np.percentile(a, 98)
    return np.clip((a - lo) / max(1e-12, hi - lo), 0.0, 1.0)

def smooth2(a, w1=201, w2=51):
    def roll(x, w):
        pad = w // 2
        xp = np.pad(x, pad, mode="reflect")
        return np.convolve(xp, np.ones(w) / w, mode="valid")[:len(x)]
    return roll(roll(a, w1), w2)

Hres_n = norm(H_res)
ent_sm9 = norm(smooth2(Hres_n))
hush9 = np.clip((0.40 - ent_sm9) / 0.30, 0.0, 1.0) * np.clip((tone_sm + 0.02) / 0.30, 0.0, 1.0)

cs = np.concatenate([[0.0], np.cumsum(hush9)])
roll = (cs[600:] - cs[:-600]) / 600.0
h0 = int(np.argmax(roll))
hush_window9 = dict(hop0=h0, hop1=h0 + 600, mean_hush=round(float(roll[h0]), 3))
print("v9 deepest hush window:", hush_window9,
      "| v8 window was hops 18162..18762 (mean 0.441)")
print("hush9>0.3 on", int((hush9 > 0.3).sum()), "hops; ent_sm9 mean", round(float(ent_sm9.mean()), 3))

# ---- song energy envelope, per output frame (3802 frames @ 24 fps) ----
import wave, contextlib
with contextlib.closing(wave.open(f"{WAV}/viz5/song_edit.wav")) as w:
    sr, nch, nf = w.getframerate(), w.getnchannels(), w.getnframes()
    raw = np.frombuffer(w.readframes(nf), dtype=np.int16).astype(np.float64) / 32768.0
mono = raw.reshape(-1, nch).mean(axis=1)
spf = sr / 24.0
nfr = int(round(nf / spf))
idx = (np.arange(nfr)[:, None] * spf + np.arange(int(spf))[None, :]).astype(int)
idx = np.minimum(idx, len(mono) - 1)
rms = np.sqrt((mono[idx] ** 2).mean(axis=1))
k = np.ones(25) / 25.0
rms_s = np.convolve(np.pad(rms, 12, mode="reflect"), k, mode="valid")[:nfr]
song_rms = (rms_s - rms_s.min()) / max(1e-12, rms_s.max() - rms_s.min())
print(f"song envelope: {nfr} frames, rms range {rms.min():.3f}..{rms.max():.3f}")

out = dict(
    meta=dict(source="derived from viz8/features.json + viz4/tone.json + viz5/song_edit.wav",
              audit=audit, hush_window=hush_window9,
              note="H_res = OLS residual of entropy_bits on log2(ntok); weather/hush re-derived; coh+bursts+INT carried from v8 unchanged."),
    derived=dict(Hres_n=[round(float(x), 4) for x in Hres_n],
                 ent_sm9=[round(float(x), 4) for x in ent_sm9],
                 hush9=[round(float(x), 4) for x in hush9],
                 coh=F8["derived"]["coh"],
                 INT=F8["derived"]["INT"]),
    bursts=F8["bursts"],
    song_rms=[round(float(x), 4) for x in song_rms],
)
json.dump(out, open(f"{WAV}/viz9/features9.json", "w"))
print("wrote viz9/features9.json")
