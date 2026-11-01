#!/usr/bin/env python3
"""build_audio_phext.py — phext-native speech-to-text prototype.

Thesis: speech carries boundary markers at multiple scales, produced by
processes the speaker does not consciously perform — breath/chunk grouping,
prosodic boundary marking, continuous-stream segmentation. This build
INFERS those markers from the signal (waveform silence, energy, F0) and
from ASR word timing, and treats them as phext delimiters:

    silence >= 0.50 s            -> section break  (0x18)
    silence >= 0.25 s            -> scroll break   (0x17)
    utterance (file) boundary    -> chapter break  (0x19)
    LibriSpeech chapter          -> book           (1.1.1/1.1.<book>)

Output is not a flat transcript: an addressed phext in which every segment
is a scroll carrying three bands —
    gist:  the ASR words (the one-dimensional projection)
    vec:   measured acoustics: duration, RMS energy, following pause,
           F0 start->end, mean word confidence
    links: coordinates of other segments sharing a rare content word
           (the stream's recurrence structure: prediction/memory made
           addressable)

Pipeline: FLAC -> WAV (ffmpeg) -> Vosk word timestamps -> waveform
silence segmentation -> features -> emit -> verify (phext parser) ->
evaluate (WER vs LibriSpeech reference; retrieval tasks flat vs phext).

Refinement (William, 2026-10-30): the original audio places speech in
coordinate space. The phext address is therefore an anchor/projection
into the audio's native space (source file, sample interval, time),
not a replacement for it — each scroll carries a fourth band:
    src:   the segment's native coordinates: source file/book, sample
           rate, sample start/end on the analysis-frame grid, time
           interval, duration, utterance/segment provenance
so the mapping stays auditable and reversible back to the waveform.

Reuses the emit() convention of ../neuralese/build_neuralese.py.
Cache: out/decode_<spk>-<ch>.json — delete it or pass --fresh to re-decode.
"""
import json, math, os, re, subprocess, sys, wave
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
SPEAKER, CHAPTER = "2277", "149896"
CH_DIR = os.path.join(BASE, "data", "LibriSpeech", "dev-clean", SPEAKER, CHAPTER)
MODEL = os.path.join(BASE, "data", "vosk-model-small-en-us-0.15")
OUT = os.path.join(BASE, "out")
WAV_DIR = os.path.join(OUT, "wav")
PHEXT_PATH = os.path.join(OUT, "audio_2277-149896.phext")
FLAT_PATH = os.path.join(OUT, "flat_transcript.txt")
RESULTS_JSON = os.path.join(OUT, "evaluation.json")

# Marker thresholds (seconds of measured waveform silence), tuned on this
# chapter's silence distribution: 157 silences >= 80 ms; >= 0.25 s: 70;
# >= 0.50 s: 15; none >= 0.80 s inside pre-cut LibriSpeech utterances.
SIL_CANDIDATE = 0.12   # below this, a gap is a stop closure, not a pause
SCROLL_T = 0.25        # phrase/breath-group boundary
SECTION_T = 0.50       # major constituent boundary
FRAME = 160            # 10 ms frames at 16 kHz

STOP = set("""the a an and or of to in was he she it his her had not as at on for
with by that this from but were are been have has would could their they them then
than so such into upon about over under out up down all one two no yes when what
where which who whom how now there here more very just also again still once any
some only own same too can will""".split())

# ---------------------------------------------------------------- ASR decode
def decode_all(fresh=False):
    cache = os.path.join(OUT, f"decode_{SPEAKER}-{CHAPTER}.json")
    if os.path.exists(cache) and not fresh:
        return json.load(open(cache))
    import vosk
    vosk.SetLogLevel(-1)
    model = vosk.Model(MODEL)
    trans = {}
    for line in open(os.path.join(CH_DIR, f"{SPEAKER}-{CHAPTER}.trans.txt")):
        uid, text = line.strip().split(" ", 1)
        trans[uid] = text
    results = []
    for uid in sorted(trans):
        wav_path = os.path.join(WAV_DIR, uid + ".wav")
        if not os.path.exists(wav_path):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i",
                            os.path.join(CH_DIR, uid + ".flac"),
                            "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
                            wav_path], check=True)
        wf = wave.open(wav_path, "rb")
        rec = vosk.KaldiRecognizer(model, 16000)
        rec.SetWords(True)
        words = []
        while True:
            frames = wf.readframes(4000)
            if not frames:
                break
            if rec.AcceptWaveform(frames):
                words.extend(json.loads(rec.Result()).get("result", []))
        words.extend(json.loads(rec.FinalResult()).get("result", []))
        results.append({"uid": uid, "duration": wf.getnframes() / 16000.0,
                        "ref": trans[uid], "words": words})
        wf.close()
    json.dump(results, open(cache, "w"), indent=1)
    return results

# ------------------------------------------------------------------- signal
def load_wav(uid):
    wf = wave.open(os.path.join(WAV_DIR, uid + ".wav"), "rb")
    x = np.frombuffer(wf.readframes(wf.getnframes()),
                      dtype=np.int16).astype(np.float32) / 32768.0
    wf.close()
    return x

def silence_runs(x):
    """Measured silences (start_s, end_s) with an adaptive per-file threshold:
    8% of the 90th-percentile 10 ms frame RMS, floored at -50 dBFS."""
    n = len(x) // FRAME
    rms = np.sqrt((x[:n * FRAME].reshape(n, FRAME) ** 2).mean(axis=1) + 1e-12)
    thr = max(np.percentile(rms, 90) * 0.08, 10 ** (-50 / 20))
    quiet = rms < thr
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= SIL_CANDIDATE:
                runs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return runs

def f0_window(x, t0, t1):
    """Crude autocorrelation pitch tracker: median F0 (Hz) over voiced frames
    in [t0, t1], or None. Signal decimated to 4 kHz; lags for 60-350 Hz."""
    seg = x[int(t0 * 16000):int(t1 * 16000)]
    if len(seg) < 1600:
        return None
    seg = seg[:len(seg) // 4 * 4]
    d = seg.reshape(-1, 4).mean(axis=1)  # 4 kHz
    fl, hop = 200, 100                    # 50 ms frames, 25 ms hop at 4 kHz
    lo, hi = int(4000 / 350), int(4000 / 60)
    vals = []
    for s in range(0, len(d) - fl, hop):
        fr = d[s:s + fl] - d[s:s + fl].mean()
        if np.sqrt((fr ** 2).mean()) < 0.005:
            continue
        ac = np.correlate(fr, fr, "full")[fl - 1:]
        if ac[0] <= 0:
            continue
        acn = ac / ac[0]
        lag = lo + int(np.argmax(acn[lo:hi]))
        if acn[lag] > 0.45:
            vals.append(4000.0 / lag)
    return round(float(np.median(vals))) if len(vals) >= 2 else None

# -------------------------------------------------------------- segmentation
def segment_utterance(u):
    """Split one utterance's words at measured silences. Returns segments:
    dicts with words, pause_after, break level AFTER the segment
    ('section' | 'scroll' | 'chapter'), and the native-coordinate anchors
    sil_before / sil_after: the (start_s, end_s) of the break silence
    bounding the segment in the waveform (None at the file edges)."""
    x = load_wav(u["uid"])
    runs = [r for r in silence_runs(x)
            if r[0] > 0.05 and r[1] < u["duration"] - 0.02]  # interior only
    bounds = []  # (boundary_time, level, silence_len, sil_start_s, sil_end_s)
    for s0, s1 in runs:
        ln = s1 - s0
        if ln >= SECTION_T:
            bounds.append(((s0 + s1) / 2, "section", ln, s0, s1))
        elif ln >= SCROLL_T:
            bounds.append(((s0 + s1) / 2, "scroll", ln, s0, s1))
    segs, cur, bi = [], [], 0
    sil_before = None  # break silence preceding the words in `cur`
    for w in u["words"]:
        mid = (w["start"] + w["end"]) / 2
        while bi < len(bounds) and mid > bounds[bi][0] and cur:
            sil = (bounds[bi][3], bounds[bi][4])
            segs.append({"words": cur, "pause_after": bounds[bi][2],
                         "level_after": bounds[bi][1], "x": x,
                         "nsamp": len(x), "sil_before": sil_before,
                         "sil_after": sil})
            sil_before = sil
            cur, bi = [], bi + 1
        cur.append(w)
    if cur:
        segs.append({"words": cur, "pause_after": 0.0,
                     "level_after": "chapter", "x": x, "nsamp": len(x),
                     "sil_before": sil_before, "sil_after": None})
    elif segs:
        segs[-1]["level_after"] = "chapter"
    return segs

def features(seg):
    ws, x = seg["words"], seg["x"]
    t0, t1 = ws[0]["start"], ws[-1]["end"]
    # Native coordinates: the segment's waveform interval runs from the
    # END of the break silence before it to the START of the break
    # silence after it (file start/end at the edges), so the bounding
    # pauses belong to neither segment and pause_after stays consistent
    # with vec. Silence edges are frame indices x 0.01 s, i.e. exact
    # multiples of FRAME=160 samples; the file-end index is the true
    # sample count. Word times (t0/t1) are ASR estimates, not grid-exact.
    sb, sa = seg["sil_before"], seg["sil_after"]
    samp0 = int(round(sb[1] * 16000)) if sb else 0
    samp1 = int(round(sa[0] * 16000)) if sa else seg["nsamp"]
    s = x[int(t0 * 16000):int(t1 * 16000)]
    rms = float(np.sqrt((s ** 2).mean())) if len(s) else 0.0
    db = 20 * math.log10(rms) if rms > 0 else -99.0
    f0a = f0_window(x, t0, min(t1, t0 + 0.6))
    f0b = f0_window(x, max(t0, t1 - 0.6), t1)
    conf = float(np.mean([w.get("conf", 0.0) for w in ws]))
    return {"t0": t0, "t1": t1, "dur": t1 - t0, "rms": rms, "db": db,
            "samp0": samp0, "samp1": samp1,
            "pause_after": seg["pause_after"], "f0a": f0a, "f0b": f0b,
            "conf": conf, "nwords": len(ws),
            "text": " ".join(w["word"] for w in ws),
            "level_after": seg["level_after"]}

# ---------------------------------------------------------------- phext emit
DELIM = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]
def emit(targets):
    cur = [1] * 9; out = []; first = True
    for coord, text in targets:
        if first:
            assert list(coord) == [1] * 9; first = False
        else:
            for d in range(9):
                while cur[d] < coord[d]:
                    out.append(chr(DELIM[d])); cur[d] += 1
                    for k in range(d + 1, 9):
                        cur[k] = 1
            assert cur == list(coord), (cur, coord)
        out.append(text)
    return "".join(out)

def fmt(coord):
    return (f"{coord[0]}.{coord[1]}.{coord[2]}/{coord[3]}.{coord[4]}.{coord[5]}/"
            f"{coord[6]}.{coord[7]}.{coord[8]}")

# ---------------------------------------------------------------- evaluation
def norm_words(text):
    text = re.sub(r"[^a-z' ]", " ", text.lower())
    return [w.strip("'") for w in text.split() if w.strip("'")]

def wer(ref, hyp):
    r, h = norm_words(ref), norm_words(hyp)
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1): d[i][0] = i
    for j in range(len(h) + 1): d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1,
                          d[i - 1][j - 1] + (r[i - 1] != h[j - 1]))
    return d[len(r)][len(h)], len(r)

# ---------------------------------------------------------------------- main
def main():
    fresh = "--fresh" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    utterances = decode_all(fresh)

    # ---- segment the whole chapter
    chapters = []  # list of list-of-segments (features computed)
    for ui, u in enumerate(utterances, start=1):
        segs = [features(s) for s in segment_utterance(u)]
        for k, s in enumerate(segs, start=1):
            s["uid"] = u["uid"]; s["uchapter"] = ui
            s["seg_idx"] = k; s["seg_n"] = len(segs)
        chapters.append(segs)
    all_segs = [s for ch in chapters for s in ch]

    # ---- coordinates: book 1 = this LibriSpeech chapter; chapter = utterance
    coord_of = {}
    for ui, segs in enumerate(chapters, start=1):
        section, scroll = 1, 0
        for s in segs:
            scroll += 1
            s["coord"] = (1, 1, 1, 1, 1, 1, ui, section, scroll)
            coord_of[id(s)] = s["coord"]
            if s["level_after"] == "section":
                section, scroll = section + 1, 0

    # ---- links: rare content words shared between segments
    df = {}
    for s in all_segs:
        for w in set(norm_words(s["text"])):
            if len(w) >= 4 and w not in STOP:
                df[w] = df.get(w, 0) + 1
    rare = {w for w, c in df.items() if 2 <= c <= 4}
    for s in all_segs:
        mine = {w for w in set(norm_words(s["text"])) if w in rare}
        links = []
        for o in all_segs:
            if o is s:
                continue
            shared = mine & {w for w in set(norm_words(o["text"])) if w in rare}
            if shared:
                links.append((fmt(o["coord"]), ", ".join(sorted(shared))))
        s["links"] = links[:6]

    # ---- emit scrolls
    header = (
        "PHEXT AUDIO STREAM — LibriSpeech dev-clean, speaker 2277, "
        "chapter 149896 (book 1)\n"
        "STREAM MAP (declared at origin, per neuralese scroll 10): the "
        "markers in this stream were INFERRED from signal, not reported by "
        "the speaker.\n"
        "  chapter break = utterance/file boundary (the corpus's cut)\n"
        f"  section break = measured silence >= {SECTION_T:.2f}s "
        "(major prosodic boundary)\n"
        f"  scroll break  = measured silence >= {SCROLL_T:.2f}s "
        "(breath/phrase group)\n"
        "NATIVE COORDINATES: the original audio already places this "
        "speech in a coordinate space (source file, sample interval, "
        "energy, pitch). The phext address below is an anchor into that "
        "space, not a replacement for it: each scroll's src band carries "
        "its measured waveform interval (end of the preceding break "
        "silence to start of the following one), so the mapping is "
        "auditable and any scroll can be traced back to the audio it "
        "came from. Silence edges are exact on the 10 ms (160-sample) "
        "analysis grid; the ASR word span rides in the same line and "
        "can disagree with the energy edges by up to ~0.2 s — both are "
        "kept, so the disagreement is visible rather than hidden.\n"
        "Bands per scroll: gist (ASR words) / src (native coordinates) "
        "/ vec (measured acoustics) / links (segments sharing a rare "
        "content word).\n\n")
    targets = []
    for i, s in enumerate(all_segs):
        f0 = (f"f0={s['f0a']}->{s['f0b']}Hz" if s["f0a"] and s["f0b"]
              else "f0=na")
        vec = (f"vec: t={s['t0']:.2f}-{s['t1']:.2f}s dur={s['dur']:.2f}s "
               f"rms={s['rms']:.4f} ({s['db']:.1f} dBFS) "
               f"pause_after={s['pause_after']:.2f}s {f0} "
               f"words={s['nwords']} conf={s['conf']:.2f}")
        src = (f"src: file={s['uid']}.flac "
               f"book=librispeech/dev-clean/{SPEAKER}/{CHAPTER} sr=16000 "
               f"samp={s['samp0']}-{s['samp1']} "
               f"t={s['samp0'] / 16000:.3f}-{s['samp1'] / 16000:.3f}s "
               f"dur={(s['samp1'] - s['samp0']) / 16000:.2f}s "
               f"utt={s['uid']} seg={s['seg_idx']}/{s['seg_n']} "
               f"words={s['t0']:.2f}-{s['t1']:.2f}s")
        lnk = ("links: " + "; ".join(f"{c} (shared: {w})"
                                     for c, w in s["links"])
               if s["links"] else "links: none")
        body = (f"gist: {s['text']}\n{src}\n{vec}\n{lnk}")
        if i == 0:
            body = header + body
        targets.append((s["coord"], body))
    blob = emit(targets)
    open(PHEXT_PATH, "w").write(blob)

    # ---- flat transcript (the control condition)
    flat = "\n".join(" ".join(w["word"] for w in u["words"])
                     for u in utterances) + "\n"
    open(FLAT_PATH, "w").write(flat)

    # ---- verify with the phext parser
    sys.path.insert(0, os.path.join(BASE, ".."))
    from parse_phext import parse
    parsed = parse(PHEXT_PATH)
    nonempty = [(c, t) for c, t in parsed if t.strip()]
    coords = [c for c, _ in nonempty]
    assert len(nonempty) == len(all_segs), (len(nonempty), len(all_segs))
    assert len(set(coords)) == len(coords), "duplicate coordinates"

    # ---- WER
    tot_e = tot_r = 0
    per_utt = []
    for u in utterances:
        hyp = " ".join(w["word"] for w in u["words"])
        e, n = wer(u["ref"], hyp)
        tot_e += e; tot_r += n
        per_utt.append(e / n if n else 0.0)
    chapter_wer = tot_e / tot_r

    # ---- retrieval comparison: flat text vs phext
    by_coord = {c: t for c, t in nonempty}
    tasks = {}
    # A: every segment mentioning the most-linked rare word
    linkword = max(rare, key=lambda w: df[w]) if rare else None
    if linkword:
        phext_hits = [c for c, t in nonempty
                      if linkword in norm_words(t.split("\n")[0][6:])]
        flat_hits = [i + 1 for i, line in enumerate(flat.splitlines())
                     if linkword in norm_words(line)]
        tasks["A_word_search"] = {
            "query": f"every segment mentioning '{linkword}'",
            "phext": {"returned": phext_hits,
                      "unit": "exact segment addresses (coordinate + bands)"},
            "flat": {"returned_utterance_lines": flat_hits,
                     "unit": "whole-utterance lines only; segment within "
                             "the line is not identified"}}
    # B: the segment at one address
    mid = all_segs[len(all_segs) // 2]
    mid_c = fmt(mid["coord"])
    tasks["B_address_lookup"] = {
        "query": f"segment at {mid_c}",
        "phext": {"returned": by_coord[mid_c].split("\n")[0][:120],
                  "unit": "direct coordinate lookup"},
        "flat": {"returned": None,
                 "unit": "no addresses exist in a flat transcript; the "
                         "nearest analogue (Nth utterance line) is a "
                         "different, coarser unit"}}
    # C: acoustic filter — long segments followed by a real pause
    # (criteria set inside this corpus's measured pause range: the longest
    # interior silence in the chapter is 0.74 s; no 1 s pause exists)
    hits = [fmt(s["coord"]) for s in all_segs
            if s["dur"] > 3.0 and s["pause_after"] >= 0.30]
    tasks["C_acoustic_filter"] = {
        "query": "segments with dur > 3.0s and pause_after >= 0.30s",
        "phext": {"returned": hits,
                  "unit": "vec-band filter over stored measurements"},
        "flat": {"returned": None,
                 "unit": "not representable: a flat transcript retains no "
                         "durations or pauses; answering requires "
                         "re-decoding the audio from scratch"}}

    # ---- silence accounting (for honest threshold reporting)
    sil_interior = sil_edge = 0
    max_interior = 0.0
    for u in utterances:
        x = load_wav(u["uid"])
        for s0, s1 in silence_runs(x):
            if s1 - s0 >= SCROLL_T:
                if s0 > 0.05 and s1 < u["duration"] - 0.02:
                    sil_interior += 1
                    max_interior = max(max_interior, s1 - s0)
                else:
                    sil_edge += 1

    ev = {"engine": "vosk 0.3.45 / vosk-model-small-en-us-0.15",
          "utterances": len(utterances),
          "audio_seconds": round(sum(u["duration"] for u in utterances), 1),
          "segments": len(all_segs),
          "sections": sum(1 for s in all_segs if s["level_after"] == "section"),
          "thresholds": {"scroll_s": SCROLL_T, "section_s": SECTION_T,
                         "candidate_s": SIL_CANDIDATE},
          "silences_ge_scroll_t": {"interior": sil_interior, "file_edge": sil_edge},
          "max_interior_silence_s": round(max_interior, 2),
          "wer_chapter": round(chapter_wer, 4),
          "wer_mean_per_utterance": round(float(np.mean(per_utt)), 4),
          "ref_words": tot_r, "edit_errors": tot_e,
          "phext_bytes": len(blob.encode()), "flat_bytes": len(flat.encode()),
          "link_word": linkword,
          "total_links": sum(len(s["links"]) for s in all_segs),
          "tasks": tasks}
    json.dump(ev, open(RESULTS_JSON, "w"), indent=1)
    print(json.dumps({k: v for k, v in ev.items() if k != "tasks"}, indent=1))
    print("tasks:", json.dumps(tasks, indent=1)[:1200])
    print("wrote", PHEXT_PATH)

if __name__ == "__main__":
    main()
