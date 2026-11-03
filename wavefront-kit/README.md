# Your own exocortex — the wavefront starter kit

For 17 years, one person's Twitter use was a single search run by hand:
29,539 tweets, 2008–2025, spanning an exocortex — looking for another mind
working the way his does. He never found another one of himself. He found
520 people instead, and mapped them: who he was connected to, how each
connection actually ran, and what it added up to. That map is
`wavefront.phext`, and its method is not a secret or a service. It is this
kit.

Run the same search on your own account. You get two things:

1. **A table of your connections** — everyone you have ever replied to or
   mentioned, counted honestly: how much contact, how much of it was
   conversation (replies) vs. address (mentions), and over what span.
2. **Your own wavefront** — a phext that places you at the origin and
   everyone with at least 10 contact points at a coordinate in a
   9-dimensional alignment space, so you can see who you are connected to
   and why — and what your network is actually for.

## Privacy facts (read first)

- **Everything runs on your machine.** Nothing is uploaded anywhere. There
  is no account, no server, no telemetry.
- **The miner reads your tweets only.** It never opens your direct-message
  files, your likes, or anything else in the export. Your DMs are yours;
  the instrument does not need them.
- Your archive stays where you put it. The outputs are two files you own.

## Step 0 — download your X archive

1. On X: Settings → Your account → **Download an archive of your data**.
2. Confirm your password and wait for the email (this can take a day).
3. Download and unzip it. You will have a folder containing a `data/`
   subfolder. That is all the kit needs.

## Step 1 — mine your archive

```sh
python3 mine_your_archive.py --archive ~/Downloads/twitter-archive
```

Your handle is auto-detected from `data/account.js`; if that fails, add
`--handle yourhandle`. Output: `contact-points.tsv` — one row per account:
contact points, replies, mention-tweets, first/last contact, years active.
(No dependencies beyond Python 3 itself.)

## Step 2 — build your wavefront

```sh
python3 build_your_wavefront.py --contacts contact-points.tsv --handle yourhandle
```

Output: `your-wavefront.phext`. Open it in any text editor — a phext is
plain text with addresses. Or host and browse it with
[SQ](https://github.com/wbic16/sq), the phext server this work comes from.

## How to read your map

- **You are at 5.5.5/5.5.5/5.5.5** — the reference corner. That is not a
  score. A map needs an origin; this one is yours.
- **Everyone else sits at a coordinate** of nine numbers, 1–5 each, in
  three triples: *Stance* (toward the work's core commitments), *Relation*
  (how they hold the connection), *Becoming* (what the encounter does over
  time). The home scroll of your phext (address 1.1.1/1.1.1/1.1.1) explains
  every axis; each axis also has its own definition scroll.
- **Presence is contact, not alignment.** Your archive proves who you
  addressed — not what anyone is like. So the generator evidences only the
  two things counts can honestly show — *Reciprocity* (from reply share:
  conversation vs. broadcast) and *Horizon* (from contact span) — and files
  everyone else at an unmeasured default carrying the note: *"Detected, not
  yet measured."* Placing people for real, from evidence you gather, is the
  work the map invites. That work is the exocortex differentiating: your
  judgment, addressed and kept, instead of an algorithm's feed.
- **Regions are gated, never averaged.** The *Shoals* (Reciprocity ≤ 2 with
  Consent ≤ 2 or Fidelity ≤ 2) are a region to stay away from at any level
  of engagement; the *Hearth* (Trust, Reciprocity, Consent all ≥ 4) is
  where work can be built together without guarding. Almost everything else
  is open water, and almost all of the space is frontier — stances nobody in
  your archive has taken yet.
- **A person is a trail, not a point.** When someone moves, add an entry;
  don't overwrite. **Addresses are shared** — sharing a coordinate means
  sharing a stance, nothing more.

## Your metric is yours

The nine axes in the default lens — Recognition, Comprehension, Consent /
Trust, Reciprocity, Fidelity / Stewardship, Horizon, Uplift — are Will
Bickford's set, developed to map his own wavefront. They are a **starting
instrument, not a standard**. You are not being measured against his values,
and nobody in your map is either. Each person's exocortex is aligned to
what *they* care about; your alignment metric could be different from his,
and likely is, and that's okay.

To make the metric yours, write a lens file (JSON) and pass it in:

```sh
python3 build_your_wavefront.py --contacts contact-points.tsv --handle yourhandle --lens my-lens.json
```

A lens file overrides the default field by field, axis by axis (axes are
listed in coordinate order, 1–9; delete anything you don't want to change).
Per axis you can set:

- `name` — call it what it is in your world;
- `what` — the one-line definition;
- `anchors` — the five scale lines, low to high;
- `note` — why this axis exists;
- `default` — the value an archive-detected entry takes on it (1–5);
- `role` — what the archive counts may evidence. The `reciprocity` role
  receives the reply-share band; the `horizon` role receives the
  contact-span band. The region gate reads the `consent`, `trust`,
  `reciprocity`, and `fidelity` roles — a lens that doesn't mark all four
  carries no region verdicts, because regions are part of the lens too.

`lens.example.json` in this kit is a worked example: it renames Stewardship
to *Craft* with new anchors, renames Uplift to *Generosity*, and changes one
default. Start from it, or from scratch. The coordinates, the regions, and
the meaning of the space follow your lens.

## Provenance

The counting method is the one that produced Will's published table: a
contact point is one of your tweets replying to or mentioning an account,
counted once per tweet (`in_reply_to_screen_name` +
`entities.user_mentions`, case-insensitive). Run on Will's archive, this kit
reproduces his `contact-points.tsv` exactly — 7,636 accounts, 520 at ≥ 10
contact points. The worked example lives in `example/`: his table and his
personal wavefront, regenerated by these two scripts.

License: MIT, like everything in the Exocortex. The fabric this builds,
one personal map at a time, is a network of effects — what you do with
yours is yours.
