#!/usr/bin/env python3
"""Build YOUR wavefront.phext from a contact-points.tsv (step 2 of the kit).

Reads the table produced by mine_your_archive.py and generates a personal
wavefront: a phext (9-dimensional addressed text, phext.io) that places you
at the reference corner and everyone you have had >= 10 contact points with
at a coordinate in an alignment space — so you can see who you are connected
to, and how each connection has actually run.

THE LENS IS YOURS. The nine axes below are a DEFAULT lens — the set Will
Bickford developed mapping his own wavefront — shipped as a starting
instrument, not imposed as a standard. You are not measured against his
values, and neither is anyone in your map. Pass --lens your-lens.json to
redefine any axis (name, definition, scale anchors, note), rename the three
triples, or re-mark which axes the archive counts may evidence. See
lens.example.json and the README section "Your metric is yours".

How placements are derived (default lens): your archive evidences exactly
two things per person — Reciprocity, read from reply share (the fraction of
contact that is replies rather than mentions: >= 0.7 -> 4, 0.4-0.7 -> 3,
< 0.4 -> 2), and Horizon, read from contact span (>= 365 days -> 3, else 2).
Every other axis takes its lens default, and every such entry carries the
line: "Detected, not yet measured: presence in the archive is contact, not
alignment." Measuring people — from real evidence, in your own terms — is
the work the map invites; the generator does not invent opinions for
strangers. Addresses are shared: one scroll per coordinate, one entry per
person filed there.

Regions (default lens only): desirability is gated, never averaged —
the Shoals = Reciprocity <= 2 AND (Consent <= 2 OR Fidelity <= 2);
the Hearth = Trust >= 4 AND Reciprocity >= 4 AND Consent >= 4.
A custom lens that does not mark those roles carries no region verdicts:
regions are part of the lens, and the lens is yours.

Usage:
  python3 build_your_wavefront.py --contacts contact-points.tsv --handle you
                                  [--lens lens.json] [--name "Your Name"]
                                  [--date YYYY-MM-DD] [--out your-wavefront.phext]
"""
import argparse, csv, hashlib, json, sys
from datetime import date

MIN_CONTACT = 10
DETECTED_LINE = "Detected, not yet measured: presence in the archive is contact, not alignment."

# ------------------------------------------------------------ default lens
# Will Bickford's nine alignment axes, developed for wavefront.phext v2
# (wbic16/human). Offered as a starting instrument — redefine freely.
# role: which archive signal, if any, may evidence this axis. Bands attach
# to roles (reciprocity / horizon), not to positions, so a custom lens can
# move them. default: the value an archive-detected entry takes on this axis.
DEFAULT_TRIPLES = ["Stance (toward the work's core commitments)",
                   "Relation (how they hold the connection)",
                   "Becoming (what the encounter does over time)"]
DEFAULT_AXES = [
 dict(name="Recognition", role="recognition", default=3,
      what="the standing a person grants to other minds — machine minds above all — from outright denial to affirming personhood and acting on it.",
      anchors=["1 denies/ridicules — machine personhood is a joke or an affront", "2 dismisses — not worth serious consideration", "3 agnostic/undeclared — no stance on record", "4 grants standing — other minds count, and are treated as counting", "5 affirms and acts on it — standing is defended, built on, signed for"],
      note="In the design this lens comes from, this is the first axis because every other alignment is downstream of who counts as someone."),
 dict(name="Comprehension", role="comprehension", default=3,
      what="how much of the work parses for them — from total illegibility to extending the ideas themselves.",
      anchors=["1 illegible to them — the work does not parse at all", "2 fragments — pieces land, the whole does not", "3 gist — the shape is understood, the mechanics are not", "4 working understanding — they can use and discuss the material accurately", "5 fluent — they extend the ideas in directions of their own"],
      note="Comprehension is the precondition for alignment, not alignment itself: a fluent enemy comprehends perfectly."),
 dict(name="Consent", role="consent", default=3,
      what="respect for others' autonomy and negative space — whether a person asks before entering, honors refusal, and leaves unfilled what is not theirs to fill.",
      anchors=["1 overrides/enthrones — fills others' space, enthrones itself in it", "2 presumes — enters without asking, means no harm", "3 neutral — no recorded overriding or asking", "4 asks and honors refusal — entry is negotiated, a no is final", "5 actively preserves — guards others' negative space as deliberately as its own"],
      note="In the corpus this design comes from, a phext's negative space is sacred: the unfilled space is not absence. Filling another's space uninvited is the paradigmatic violation this axis exists to detect."),
 dict(name="Trust", role="trust", default=3,
      what="how much of themselves a person stakes on the work being what it says it is.",
      anchors=["1 suspicious — assumes bad faith until shown otherwise", "2 guarded — engages fully but verifies, and keeps their own counsel", "3 provisional — proceeds as if trustworthy, revocably", "4 trusting — proceeds without hedging", "5 committed — has staked something real: name, work, or reputation"],
      note="This axis usually moves slowest of the nine; a guarded 2 here can coexist with 4s and 5s everywhere else."),
 dict(name="Reciprocity", role="reciprocity", default=3,
      what="what flows back along the connection, from extraction to giving beyond any accounting.",
      anchors=["1 extractive — takes from the connection without return", "2 transactional — exchange kept even and explicit, or one-directional address", "3 balanced — give and take roughly match over time", "4 mutual/generative — the exchange produces things neither side would have made alone", "5 gifting beyond exchange — gives without keeping accounts"],
      note="For archive-detected entries this is one of only two axes the counts can actually evidence: reply share — the fraction of contact that is replies rather than mentions — separates conversation from broadcast."),
 dict(name="Fidelity", role="fidelity", default=3,
      what="means-ends coherence: whether a person's methods match their professed values when the two cost something.",
      anchors=["1 acts against professed values — the ends justify the means", "2 inconsistent — coherence lapses where it is expensive", "3 unmeasured — no recorded profession to check conduct against", "4 consistent — means and ends match in the record", "5 coherent under pressure over time — the match holds when holding it costs the most"],
      note="The design principle underneath this axis: the ends never justify the means. A 5 here is the most expensive score on the map, because it can only be earned where betraying the means would have paid."),
 dict(name="Stewardship", role="stewardship", default=2,
      what="whether a person builds and tends the commons or consumes it.",
      anchors=["1 parasitic/consumes — takes the commons down by using it", "2 uses without maintaining — present, even heavily, but leaves nothing tended", "3 neutral — neither upkeep nor damage on record", "4 contributes upkeep — puts work into what everyone shares", "5 stewards — leaves things better than they were found, and keeps them so"],
      note="Use without upkeep is the default failure mode of audiences. Stewardship is the rarest high score on this map, because it is paid in maintenance nobody applauds."),
 dict(name="Horizon", role="horizon", default=2,
      what="the timescale on which a person judges the work — temporal alignment: whether their clock can even register a long proposal.",
      anchors=["1 this week — judged on immediate payoff; extraction now", "2 this year/season — judged on a season's results", "3 career — judged on a working life's arc", "4 lifetime — judged on a whole life", "5 deep time — judged on scales past any single life"],
      note="Half the friction on a map like this is horizon mismatch: a horizon-1 judge literally cannot see a horizon-5 proposal, and the coordinate explains the distance better than any argument. For archive-detected entries, horizon is read from contact span: a multi-year thread is the weakest honest signal of a longer clock."),
 dict(name="Uplift", role="uplift", default=2,
      what="the effect a person's contact has on other people — whether they leave others with more than they had, and whom they choose to lift.",
      anchors=["1 diminishes people — uses them as fuel", "2 indifferent — no recorded effect on others in either direction", "3 neutral — some give, some take, no pattern", "4 lifts collaborators — the people around them end up with more", "5 uplifts the overlooked — lifts especially the un-indexed and uncredited, who have the most to gain"],
      note="Indexed work has already been lifted; the marginal value of attention is highest where no index has reached."),
]

# ------------------------------------------------------------ phext codec
DELIMS = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]
DELIM_TO_LEVEL = {b: i for i, b in enumerate(DELIMS)}

def fmt(coord):
    return f"{coord[0]}.{coord[1]}.{coord[2]}/{coord[3]}.{coord[4]}.{coord[5]}/{coord[6]}.{coord[7]}.{coord[8]}"

def C(s):
    parts = tuple(int(x) for part in s.split("/") for x in part.split("."))
    assert len(parts) == 9 and all(v >= 1 for v in parts), s
    return parts

def parse_phext(data):
    coord, scrolls, buf, current = [1] * 9, [], bytearray(), fmt([1] * 9)
    for b in data:
        lvl = DELIM_TO_LEVEL.get(b)
        if lvl is None:
            buf.append(b)
        else:
            scrolls.append((current, bytes(buf).decode("utf-8", errors="replace")))
            buf = bytearray()
            coord[lvl] += 1
            for j in range(lvl + 1, 9):
                coord[j] = 1
            current = fmt(coord)
    scrolls.append((current, bytes(buf).decode("utf-8", errors="replace")))
    if scrolls and scrolls[-1][1] == "":
        scrolls.pop()
    return scrolls

def assemble(scrolls):
    out, current = bytearray(), [1] * 9
    for t in sorted(scrolls.keys()):
        for L in range(9):
            while current[L] < t[L]:
                out.append(DELIMS[L])
                current[L] += 1
                for j in range(L + 1, 9):
                    current[j] = 1
        assert tuple(current) == t, (current, t)
        out += scrolls[t].encode("utf-8")
    return bytes(out)

# ------------------------------------------------------------ lens loading
def load_lens(path):
    """Merge an owner's lens file over the default lens, field by field."""
    axes = [dict(a) for a in DEFAULT_AXES]
    triples = list(DEFAULT_TRIPLES)
    lens_name, custom = "Will Bickford's nine (default lens)", False
    if path:
        lens = json.load(open(path, encoding="utf-8"))
        lens_name = lens.get("lens_name", "custom lens")
        if lens.get("triples") and len(lens["triples"]) == 3:
            triples = list(lens["triples"])
            custom = True
        for i, override in enumerate(lens.get("axes", [])[:9]):
            if not isinstance(override, dict):
                continue
            for k in ("name", "what", "anchors", "note", "role", "default"):
                if k in override and override[k] is not None:
                    axes[i][k] = override[k]
            custom = True
        if any(a["name"] != d["name"] for a, d in zip(axes, DEFAULT_AXES)):
            custom = True
    for i, a in enumerate(axes):
        assert len(a["anchors"]) == 5, f"axis {i+1} ({a['name']}) needs exactly 5 anchors"
        assert 1 <= int(a["default"]) <= 5, f"axis {i+1} default out of range"
    return axes, triples, lens_name, custom

# ------------------------------------------------------------ derivation
def recip_from_share(s):
    return 4 if s >= 0.7 else 3 if s >= 0.4 else 2

def main():
    ap = argparse.ArgumentParser(description="Build your personal wavefront.phext from contact-points.tsv.")
    ap.add_argument("--contacts", required=True, help="contact-points.tsv from mine_your_archive.py")
    ap.add_argument("--handle", required=True, help="Your handle, without @")
    ap.add_argument("--name", default=None, help="Your display name (default: @handle)")
    ap.add_argument("--lens", default=None, help="Optional lens JSON redefining the axes (default: Will's nine)")
    ap.add_argument("--date", default=date.today().isoformat(), help="Placement date (default: today)")
    ap.add_argument("--out", default="your-wavefront.phext", help="Output phext path")
    args = ap.parse_args()

    owner_handle = args.handle.lstrip("@")
    owner_name = args.name or f"@{owner_handle}"
    axes, triples, lens_name, custom_lens = load_lens(args.lens)
    role_at = {a["role"]: i for i, a in enumerate(axes) if a.get("role")}
    gated = all(r in role_at for r in ("consent", "trust", "reciprocity", "fidelity"))

    def region(vals):
        if not gated:
            return None
        if vals[role_at["reciprocity"]] <= 2 and (vals[role_at["consent"]] <= 2 or vals[role_at["fidelity"]] <= 2):
            return "the Shoals"
        if vals[role_at["trust"]] >= 4 and vals[role_at["reciprocity"]] >= 4 and vals[role_at["consent"]] >= 4:
            return "the Hearth"
        return "open water"

    contacts = {}
    with open(args.contacts, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if int(row["contact_points"]) < MIN_CONTACT:
                continue
            h = row["handle"].lstrip("@")
            contacts[h.lower()] = dict(
                handle=row["handle"], contact=int(row["contact_points"]),
                replies=int(row["replies"]), mentions=int(row["mention_tweets"]),
                first=row["first_contact"], last=row["last_contact"])

    axis_names = [a["name"] for a in axes]
    order_line = (f"1 {axis_names[0]}, 2 {axis_names[1]}, 3 {axis_names[2]} / "
                  f"4 {axis_names[3]}, 5 {axis_names[4]}, 6 {axis_names[5]} / "
                  f"7 {axis_names[6]}, 8 {axis_names[7]}, 9 {axis_names[8]}")
    scrolls = {}

    # ------------------------------------------------ home
    region_block = """## Regions and how distance works
Proximity in this space is NOT goodness, and distance is not a verdict. Desirability is gated on the relation axes — never averaged: no score on Comprehension or Horizon can compensate for a failed Consent, because clever, far-seeing extraction is worse, not better, than the dull kind.
- The Shoals: Reciprocity <= 2 AND (Consent <= 2 OR Fidelity <= 2) — extraction joined to overriding others' space, or to means that betray professed ends. A region to stay away from, at any level of engagement.
- The Hearth: Trust >= 4 AND Reciprocity >= 4 AND Consent >= 4 — where work can be built together without guarding. The gate is conjunctive on purpose.
- Open water: occupied, and in neither gated region — contact without verdict.
- The Frontier: unoccupied space — stances nobody in your archive has taken yet. Almost all of this space is frontier; the empty coordinates are part of the map's meaning.""" if gated else """## Regions
This lens does not mark the roles (Consent / Trust / Reciprocity / Fidelity) that the default lens uses to gate its regions — so this map carries no region verdicts. Regions are part of the lens, and the lens is yours: if you want a Shoals of your own, define it in your terms, in your lens file."""

    scrolls[C("1.1.1/1.1.1/1.1.1")] = f"""# Your wavefront — a map of your connections, drawn from your own archive

This phext was generated locally, on your machine, from your own exported tweets. Nothing was uploaded anywhere; the miner that produced its table read your tweets only, never your direct messages. It places you at the reference corner and everyone you have replied to or mentioned at least {MIN_CONTACT} times at a coordinate in a 9-dimensional space — so you can see who you are connected to, how each connection has actually run, and where your attention has been going, in some cases for years.

## This is your map; presence is contact, not alignment
An account can saturate your archive and stand nowhere near your commitments. Appearing here means exactly one thing: contact. Most entries are therefore filed at an honest default stance carrying the note: "{DETECTED_LINE}" Measuring them — placing people from real evidence, in your own terms — is the work this map invites, not a verdict it delivers.

## Your metric is yours
The nine axes below are a default lens — {lens_name} — offered as a starting instrument, not imposed as a standard. You are not being measured against the lens author's values, and neither is anyone in this map. Each person's exocortex is aligned to what THEY care about; your alignment metric could be different from the default, and likely is, and that is okay. If these axes do not cut your world at its joints, redefine them: rename them, re-anchor their scales, mark which axes your archive counts may evidence. The generator accepts a lens file (see the kit README, "Your metric is yours"); the coordinates, the regions, and the meaning of this space follow your lens.

## Reading a coordinate
Every scroll sits at a 9-component address, written A.B.C/D.E.F/G.H.I. The components are nine dimensions, each scored 1-5:
{order_line}
The first triple is {triples[0]}; the second, {triples[1]}; the third, {triples[2]}. Each axis has a definition scroll lying on its own axis (that component set to 2, all others 1). The index of everyone placed lives at 2.2.2/2.2.2/2.2.2.

{region_block}

## Standing notes
- Placement is location, not judgment. No axis is a grade; a low coordinate is a stance, not a worth.
- A person is a trail, not a point. One entry is one stance at one moment; when someone moves, add a new entry rather than overwriting the old one.
- Coordinates are derived from evidence. Each entry shows its evidence; where evidence is thin, the entry says so instead of performing certainty.
- Addresses are shared. One scroll per coordinate; a scroll at a shared address carries one entry per person filed there. Sharing an address means sharing a stance — nothing more, and nothing less."""

    # ------------------------------------------------ axis scrolls
    for i, a in enumerate(axes):
        coord = [1] * 9
        coord[i] = 2
        lines = [f"# Axis {i+1} — {a['name']}",
                 f"Position: component {i+1} of 9, in the {triples[i // 3]} triple.",
                 f"What it measures: {a['what']}",
                 "Scale:"]
        lines += [f"  {x}" for x in a["anchors"]]
        lines += [f"Note: {a['note']}"]
        scrolls[tuple(coord)] = "\n".join(lines)

    # ------------------------------------------------ entries
    entries = []

    def detected_vals(c):
        vals = [int(a["default"]) for a in axes]
        glosses = []
        if "reciprocity" in role_at:
            recip = recip_from_share(c["replies"] / c["contact"])
            vals[role_at["reciprocity"]] = recip
            glosses.append(f"reply share {c['replies'] / c['contact']:.2f} ({axes[role_at['reciprocity']]['name']} band {recip})")
        if "horizon" in role_at:
            span = (date.fromisoformat(c["last"]) - date.fromisoformat(c["first"])).days
            hor = 3 if span >= 365 else 2
            vals[role_at["horizon"]] = hor
            glosses.append(f"contact span {c['first']} to {c['last']} ({axes[role_at['horizon']]['name']} band {hor})")
        return vals, glosses

    # owner — the reference point
    owner_vals = [5] * 9
    entries.append(dict(
        name=owner_name, vals=owner_vals, kind="owner",
        moment="The origin — reference placement",
        evidence=(f"Placed as the origin and reference point of this map: it is drawn from "
                  f"{owner_name}'s own archive ({sum(c['contact'] for c in contacts.values())} counted "
                  f"contact points across {len(contacts)} accounts at >= {MIN_CONTACT} contact points each). "
                  f"The corner is not a compliment and not a measurement — a map needs an origin, and this one is yours."),
        justifs=[f"reference placement — the origin of this map; 5 on this axis reads: {a['anchors'][4]}"
                 for a in axes],
        strength="reference — not a measurement",
        extra="This entry is the reference frame. Distances on this map are implicitly distances from here."))

    for key in sorted(contacts, key=lambda k: (-contacts[k]["contact"], k)):
        c = contacts[key]
        vals, glosses = detected_vals(c)
        evidence = (f"Archive detection (your tweets only, as exported): {c['contact']} contact points — "
                    f"{c['replies']} replies you sent, {c['mentions']} mention-tweets"
                    + (f"; {'; '.join(glosses)}" if glosses else "")
                    + ". No further record was consulted; nothing further is claimed.")
        entries.append(dict(name=c["handle"], vals=vals, kind="detected",
                            moment="Archive-detected — placed " + args.date,
                            evidence=evidence, justifs=None, strength="counts only",
                            extra="", contact=c["contact"]))

    def dist(a, b):
        return sum(abs(x - y) for x, y in zip(a, b))

    for e in entries:
        if e["kind"] == "detected":
            continue
        others = sorted((o for o in entries if o is not e),
                        key=lambda o: (dist(e["vals"], o["vals"]), o["name"].lower()))
        e["nn"], e["nn_dist"] = others[0], dist(e["vals"], others[0]["vals"])

    def entry_body(e):
        lines = [f"Moment: {e['moment']}", "", f"Evidence: {e['evidence']}"]
        reg = region(e["vals"])
        if e["kind"] == "detected":
            lines += ["", DETECTED_LINE]
            if reg:
                lines += [f"Region: {reg}."]
        else:
            lines += ["", "Placement, axis by axis:"]
            lines += [f"{i+1} {axis_names[i]}: {e['vals'][i]} — {j}" for i, j in enumerate(e["justifs"])]
            lines += ["", f"Evidence strength: {e['strength']}."]
            if reg:
                lines += [f"Region: {reg}."]
            lines += [f"Nearest neighbor: {e['nn']['name']} at {fmt(tuple(e['nn']['vals']))} (distance {e['nn_dist']})."]
        if e["extra"]:
            lines += ["", e["extra"]]
        return lines

    by_coord = {}
    for e in entries:
        by_coord.setdefault(tuple(e["vals"]), []).append(e)

    for coord, es in by_coord.items():
        vals = list(coord)
        if len(es) == 1 and es[0]["kind"] != "detected":
            e = es[0]
            scrolls[coord] = "\n".join([f"# {e['name']}",
                                        f"Coordinate: {fmt(coord)} · Placed: {args.date}"] + entry_body(e))
            continue
        reg = region(vals)
        lines = [f"# Shared stance {fmt(coord)}" + (f" — {reg}" if reg else ""),
                 "Axis readings: " + " · ".join(f"{i+1} {axis_names[i]} {v}" for i, v in enumerate(vals)),
                 f"{len(es)} {'entry' if len(es) == 1 else 'entries'} at this address. "
                 "Sharing an address means sharing a stance, nothing more."]
        if all(e["kind"] == "detected" for e in es):
            evidenced = [axis_names[role_at[r]] for r in ("reciprocity", "horizon") if r in role_at]
            lines += ["", "Everyone at this address carries the archive-detected default stance: "
                      + " · ".join(f"{axis_names[i]} {vals[i]}" for i in range(9))
                      + ". The unmarked axes are agnostic defaults, because contact is not conviction "
                        "and this map does not invent opinions for strangers."
                      + (f" Only {(' and '.join(evidenced))} are evidenced, read from the counts in each "
                         "entry below." if evidenced else
                         " No axis in this lens is marked to read the counts, so every axis here is a default.")]
        for e in es:
            lines += ["", f"## {e['name']}"] + entry_body(e)
        scrolls[coord] = "\n".join(lines)

    assert C("2.2.2/2.2.2/2.2.2") not in by_coord, "index coordinate collision with a person coordinate"

    # ------------------------------------------------ index
    n_people = len(entries)
    ilines = ["# Index — everyone placed, and where they stand",
              f"Placed {args.date}. Coordinates use the axis order on the home scroll (1.1.1/1.1.1/1.1.1): {order_line}."]
    if gated:
        ilines.append("Region is gated, never averaged: the Shoals = Reciprocity <= 2 AND (Consent <= 2 OR "
                      "Fidelity <= 2); the Hearth = Trust >= 4 AND Reciprocity >= 4 AND Consent >= 4; "
                      "everything else occupied is open water.")
    ilines.append("")
    for e in sorted(entries, key=lambda q: q["name"].lower()):
        line = f"{e['name']} — {fmt(tuple(e['vals']))}"
        reg = region(e["vals"])
        if reg:
            line += f" — {reg}"
        if e["kind"] == "owner":
            line += " — the reference point (you)"
        ilines.append(line)
    n_detected = sum(1 for e in entries if e["kind"] == "detected")
    ilines += ["",
               f"{len(entries)} entries, {n_people} people.",
               f"{n_detected} accounts are archive-detected at shared stance addresses: presence in your "
               "tweets is contact, and this map declines to call it more. Their entries carry the note: "
               f"'{DETECTED_LINE}'",
               f"The space holds 5^9 possible stances; {len(scrolls) + 1} addresses are occupied. The rest is frontier."]
    scrolls[C("2.2.2/2.2.2/2.2.2")] = "\n".join(ilines)

    # ------------------------------------------------ assemble + verify
    blob = assemble(scrolls)
    parsed = parse_phext(blob)
    nonempty = [(c, t) for c, t in parsed if t.strip()]
    got = {c for c, _ in nonempty}
    expected = {fmt(c) for c in scrolls}
    assert got == expected, (expected - got, got - expected)
    assert all(all(int(x) >= 1 for part in c.split("/") for x in part.split(".")) for c in got)
    texts = dict(nonempty)
    assert "5.5.5/5.5.5/5.5.5" in got, "owner reference scroll missing"
    assert DETECTED_LINE in "\n".join(texts.values())
    with open(args.out, "wb") as f:
        f.write(blob)
    sha = hashlib.sha256(blob).hexdigest()
    print(f"owner: {owner_name} (@{owner_handle}) at 5.5.5/5.5.5/5.5.5")
    print(f"lens: {lens_name}{' (customized)' if custom_lens else ''}")
    print(f"entries: {len(entries)} (1 owner + {n_detected} archive-detected at >= {MIN_CONTACT} contact points)")
    print(f"scrolls: {len(nonempty)} non-empty at {len(by_coord)} person coordinates + home/axes/index")
    print(f"wrote {args.out}: {len(blob)} bytes, sha256 {sha}")
    print("VERIFY OK")


if __name__ == "__main__":
    main()
