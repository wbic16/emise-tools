#!/usr/bin/env python3
"""Step 1 of the audio-s2t pipeline: FLAC -> WAV (ffmpeg), Vosk ASR with word
timestamps. Dumps per-utterance word timings + transcripts to JSON so the
segmentation thresholds can be tuned against the measured pause distribution
before the phext is emitted.

Engine: vosk 0.3.45 / vosk-model-small-en-us-0.15 (Kaldi). CPU only.
"""
import json, os, subprocess, sys, wave

BASE = os.path.dirname(os.path.abspath(__file__))
CH_DIR = os.path.join(BASE, "data", "LibriSpeech", "dev-clean", "2277", "149896")
MODEL = os.path.join(BASE, "data", "vosk-model-small-en-us-0.15")
OUT = os.path.join(BASE, "out", "decode_2277-149896.json")
WAV_DIR = os.path.join(BASE, "out", "wav")
os.makedirs(WAV_DIR, exist_ok=True)

import vosk
vosk.SetLogLevel(-1)
model = vosk.Model(MODEL)

def decode(flac_path):
    wav_path = os.path.join(WAV_DIR, os.path.basename(flac_path).replace(".flac", ".wav"))
    if not os.path.exists(wav_path):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", flac_path,
                        "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", wav_path],
                       check=True)
    wf = wave.open(wav_path, "rb")
    assert wf.getframerate() == 16000 and wf.getnchannels() == 1
    rec = vosk.KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    words = []
    while True:
        frames = wf.readframes(4000)
        if not frames:
            break
        if rec.AcceptWaveform(frames):
            r = json.loads(rec.Result())
            words.extend(r.get("result", []))
    r = json.loads(rec.FinalResult())
    words.extend(r.get("result", []))
    dur = wf.getnframes() / 16000.0
    wf.close()
    return words, dur

def main():
    trans = {}
    for line in open(os.path.join(CH_DIR, "2277-149896.trans.txt")):
        uid, text = line.strip().split(" ", 1)
        trans[uid] = text
    results = []
    for uid in sorted(trans):
        words, dur = decode(os.path.join(CH_DIR, uid + ".flac"))
        results.append({"uid": uid, "duration": dur, "ref": trans[uid], "words": words})
        print(f"{uid}: {dur:6.2f}s  {len(words):3d} words  "
              f"{' '.join(w['word'] for w in words)[:70]}", flush=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=1)
    # pause-gap distribution across the chapter (within utterances)
    gaps = []
    for r in results:
        ws = r["words"]
        for a, b in zip(ws, ws[1:]):
            gaps.append(round(b["start"] - a["end"], 3))
    gaps.sort()
    import statistics
    print(f"\nword gaps: n={len(gaps)} min={gaps[0]} med={statistics.median(gaps)} "
          f"p90={gaps[int(len(gaps)*0.9)]} p99={gaps[int(len(gaps)*0.99)]} max={gaps[-1]}")
    for t in (0.2, 0.3, 0.35, 0.5, 0.8, 1.0, 1.5):
        print(f"  gaps >= {t:>4}s: {sum(1 for g in gaps if g >= t)}")
    print("wrote", OUT)

if __name__ == "__main__":
    main()
