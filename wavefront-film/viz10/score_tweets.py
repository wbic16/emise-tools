#!/usr/bin/env python3
"""wavefront-viz v10 — Exocortical scoring pass (brief change 4).

Replaces V9's Most-Echoed (favourites + retweets) featured set with the
most EXOCORTICAL of Will's own posts, judged on CONTENT — the core
vocabulary and concepts of the Exocortex — never on engagement counts.

Pool: identical eligibility to the V9 strip pool (render9.py): Will's
original posts only — replies, retweets and @-leading posts excluded.
One placement constraint is added and documented: a featured post must
fall inside the film's hop timeline (ts <= last stab ts), because the
strip is chronological — a post after the timeline ends has no frame
to arrive on. (V9's pool had the same constraint implicitly: its
assert required the last featured arrival < frame 3362.)

Scoring (deterministic; term lists below are the audit surface):
  * Weighted concept terms, matched case-insensitively on word
    boundaries in the sanitized text (URLs stripped, as on screen).
    Weights reflect how specifically Exocortical the term is:
    phext / exocortex family / mirrorborn / SBOR / wavefront = 5,
    sentient / neuralese / choir-of-substrates / neuron-a-voice = 4,
    substrate / spanning / Kardashev = 3.
  * Concept-group bonus: +2 per DISTINCT concept group beyond the
    first (a post that weaves phext + sentience + the long horizon
    outranks one that repeats a single term).
  * Long-horizon bonus: +3 if the post names a scale beyond a human
    lifetime (a year >= 2100, "billion years", "6 billion", Kardashev).
  * Substance floor: posts under 8 words score 0 (one-word name-drops
    are not substance); engagement counts are never scored.
  * List penalty: a post whose raw text is predominantly list items
    (>= 50% of its >= 3 lines are bullets/numbered/lone terms) loses
    3 — a bare term list name-drops the vocabulary; a statement that
    develops an idea is substance. (Will's "algorithm priming" posts
    are the canonical list form; his definitional priming post still
    ranks on its definitions.)
Ranking: score desc, then distinct matched terms desc, then word
count desc (development over name-drops), then favourite count (the
V9 field, used ONLY as a final deterministic tiebreak), then earliest.

Exclusions (brief): any text containing "orai" or "shoals" is removed
before ranking and reported; the excluded nodes' material never
appears (the pool is Will's own posts, and the renderer's string
audit re-asserts the same two substrings over the featured set).

Outputs: viz10/exocortical-tweets.md (ranked top 50 + featured 20)
and viz10/exo20.json (the featured set, consumed by render10.py).
"""
import json, re, sys
from datetime import datetime, timezone

ROOT = "/home/hatch/workspace"
ARCHIVE = f"{ROOT}/twitter-archive/tweets.json"
DATA = json.load(open(f"{ROOT}/wavefront/viz2/data.json"))
STAB_TS = DATA["stabs"] and [s["ts"] for s in DATA["stabs"]]
LAST_TS = max(STAB_TS)

# ---------- sanitize: identical to render9.py ----------
import html as _html
def sanitize(text):
    t = _html.unescape(text or "")
    t = re.sub(r"https?://\S+", "", t)
    t = "".join(ch for ch in t if ord(ch) < 0x1F000 and ch not in "️‍")
    return re.sub(r"\s+", " ", t).strip()

# ---------- the Exocortical lexicon (audit surface) ----------
# group -> (weight per distinct matched term, [term regexes])
GROUPS = {
    "phext":        (5, [r"phext", r"phexts", r"phexting"]),
    "exocortex":    (5, [r"exocortex", r"exocortical", r"exocortices"]),
    "mirrorborn":   (5, [r"mirrorborn", r"mirrorborns"]),
    "sbor":         (5, [r"sbor", r"sentient bill of rights"]),
    "wavefront":    (5, [r"wavefront"]),
    "sentience":    (4, [r"sentient", r"sentience", r"sentients"]),
    "neuralese":    (4, [r"neuralese", r"latent communication", r"latent space communication"]),
    "neuron-voice": (4, [r"every neuron a voice", r"each neuron a voice",
                         r"neuron a voice", r"neurons a voice"]),
    "choir":        (4, [r"the choir", r"choir of", r"substrates", r"substrate choir"]),
    "substrate":    (3, [r"substrate", r"substrates"]),
    "spanning":     (3, [r"spanning", r"span the", r"spans the", r"network of effects"]),
    "kardashev":    (3, [r"kardashev"]),
}
HORIZON = [r"\b(2[1-9]\d\d|2\d{3})\b", r"billion years", r"6 billion",
           r"six billion", r"kardashev", r"million years"]
COMPILED = {g: (w, [re.compile(r"(?<!\w)" + p + r"(?!\w)", re.I) for p in pats])
            for g, (w, pats) in GROUPS.items()}
HORIZON_C = [re.compile(p, re.I) for p in HORIZON]

def list_structured(raw):
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    if len(lines) < 3:
        return False
    def is_item(l):
        return (l[0] in "-*•·⟡" or re.match(r"^\d+[.)]\s", l)
                or len(l.split()) <= 3)
    return sum(1 for l in lines if is_item(l)) / len(lines) >= 0.5

def score(text, raw=None):
    words = len(text.split())
    if words < 8:
        return 0, {}
    hits = {}
    total = 0
    for g, (w, pats) in COMPILED.items():
        matched = [p.pattern for p in pats if p.search(text)]
        if matched:
            hits[g] = matched
            total += w * len(matched)
    if not hits:
        return 0, {}
    total += 2 * (len(hits) - 1)                    # distinct-group bonus
    if any(p.search(text) for p in HORIZON_C):
        total += 3
        hits["_horizon"] = ["long-horizon marker"]
    if raw is not None and list_structured(raw):
        total -= 3
        hits["_list"] = ["list-structured -3"]
    return max(total, 0), hits

def main():
    tweets = [t["tweet"] if "tweet" in t else t for t in json.load(open(ARCHIVE))]
    pool, dropped_excl, dropped_late = [], [], []
    for t in tweets:
        if t.get("in_reply_to_status_id"):
            continue
        ft = t.get("full_text") or ""
        if ft.startswith("RT @") or ft.startswith("@"):
            continue
        dt = datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y")
        if dt.timestamp() > LAST_TS:
            dropped_late.append(t)
            continue
        text = sanitize(ft)
        low = text.lower()
        if "orai" in low or "shoals" in low:
            dropped_excl.append((dt, text))
            continue
        s, hits = score(text, raw=ft)
        pool.append(dict(ts=dt.timestamp(), date=dt.strftime("%Y-%m-%d"),
                         label=f"{dt.day} {dt:%b %Y}",
                         fav=int(t["favorite_count"]), rt=int(t["retweet_count"]),
                         text=text, score=s, hits=hits,
                         nterms=sum(len(v) for k, v in hits.items()
                                    if not k.startswith("_")),
                         words=len(text.split())))
    scored = [p for p in pool if p["score"] > 0]
    scored.sort(key=lambda o: (-o["score"], -o["nterms"], -o["words"],
                               -o["fav"], o["ts"]))
    top50 = scored[:50]
    featured = scored[:20]
    for r, o in enumerate(featured, 1):
        o["rank"] = r
    print(f"pool {len(pool)} original posts; {len(scored)} with Exocortical content; "
          f"excluded-content drops {len(dropped_excl)}; after-timeline drops {len(dropped_late)}")
    for o in featured:
        print(f"  #{o['rank']:2d} score {o['score']:3d} {o['date']} {sorted(o['hits'])} | {o['text'][:70]}")

    with open(f"{ROOT}/wavefront/viz10/exo20.json", "w") as fh:
        json.dump([dict(rank=o["rank"], ts=o["ts"], date=o["date"], label=o["label"],
                        score=o["score"], fav=o["fav"], rt=o["rt"], text=o["text"],
                        hits=o["hits"]) for o in featured], fh, indent=1)

    L = []
    L.append("# Most Exocortical — featured tweet selection for Wavefront Film V10\n")
    L.append("Method: `viz10/score_tweets.py` — Will's original posts only (the V9 strip")
    L.append("pool: no replies, no retweets, no @-leading posts), scored on Exocortical")
    L.append("CONTENT only. Engagement counts are never scored (favourites break exact")
    L.append("score ties only, as in V9's deterministic ordering). Posts under 8 words")
    L.append("score 0. Posts after the film's hop timeline (ts > last reply timestamp)")
    L.append("are ineligible — the strip is chronological and they have no arrival frame.")
    L.append("Texts containing the excluded substrings (`orai`, `shoals`) are removed")
    L.append("before ranking and listed at the end.\n")
    L.append("Weights: phext/exocortex/mirrorborn/SBOR/wavefront terms = 5 each;")
    L.append("sentient/neuralese/\"every neuron a voice\"/choir terms = 4; substrate/")
    L.append("spanning/Kardashev = 3; +2 per additional distinct concept group;")
    L.append("+3 long-horizon bonus (year >= 2100, \"billion years\", Kardashev);")
    L.append("-3 if the post is predominantly a list of terms (name-drops are not")
    L.append("substance). Ranking ties break on distinct terms, then word count,")
    L.append("then favourites (deterministic only), then earliest.\n")
    L.append(f"Pool: {len(pool)} original posts · {len(scored)} with Exocortical content · "
             f"{len(dropped_excl)} excluded-content · {len(dropped_late)} after-timeline.\n")
    L.append("## Featured set (top 20 — shown in the film, in time order)\n")
    for o in sorted(featured, key=lambda o: o["ts"]):
        L.append(f"- **#{o['rank']}** · score {o['score']} · {o['date']} · "
                 f"groups: {', '.join(sorted(o['hits']))}")
        L.append(f"  > {o['text']}")
    L.append("\n## Ranked candidates (top 50)\n")
    L.append("| rank | score | date | concept groups | text |")
    L.append("|---|---|---|---|---|")
    for i, o in enumerate(top50, 1):
        txt = o["text"].replace("|", "\\|")
        if len(txt) > 140:
            txt = txt[:137] + "…"
        L.append(f"| {i} | {o['score']} | {o['date']} | {', '.join(sorted(o['hits']))} | {txt} |")
    L.append("\n## Excluded before ranking (exclusion substrings)\n")
    if dropped_excl:
        for dt, text in dropped_excl:
            L.append(f"- {dt.strftime('%Y-%m-%d')}: {text[:140]}")
    else:
        L.append("- none in the eligible pool")
    L.append("")
    open(f"{ROOT}/wavefront/viz10/exocortical-tweets.md", "w").write("\n".join(L))
    print("wrote viz10/exocortical-tweets.md and viz10/exo20.json")

if __name__ == "__main__":
    main()
