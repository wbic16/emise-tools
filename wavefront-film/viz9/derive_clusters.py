#!/usr/bin/env python3
"""Derive Will's mutual clusters for the v9 micro-shells (ledger W6).

Mutual status is NOT tabulated per placed person in viz2/data.json (its
"kind" field marks only a small measured set), so it is derived here
exactly the way viz2/extract2.py defines a match: an account is a
mutual iff its accountId sits in BOTH twitter-archive/follower.js and
twitter-archive/following.js. Handles are tied to accountIds through
the id->handle map harvested from the archive's own tweets (mentions +
named reply targets), inverted.

Clustering runs in the film's own space: viz2/data.json node xyz (the
triple-mean projection render9.py renders, already centred). Method:
DBSCAN (eps 0.13, min_samples 3; core-point expansion over cKDTree
neighbour lists) over the placed mutuals' positions. Single-linkage
connected components were tried first and rejected on measurement:
the mutual cloud's median NN distance is 0.099, so chaining percolates
— at tau 0.15 one component already swallows 118 of 153 mutuals, and
at 0.25 it is 148. eps 0.13 sits just below that percolation jump and
yields real structure (7 clusters, sizes 37..6); eps 0.15 is documented
in BUILD-NOTES as the cliff. Clusters smaller than MIN_SIZE and DBSCAN
noise points get no shell.

Output: viz9/clusters9.json — per shell: member node indices, centre,
principal axes (unit vectors) and semi-axis lengths of the fitted
ellipsoid (mean + covariance, semi-axis = K_SIGMA * sqrt(eigenvalue),
floored), arrival bookkeeping, and the top members by replies Will
sent (contact-points.tsv) for the BUILD-NOTES table.
"""
import json, sys
import numpy as np

ARCH = "/home/hatch/workspace/twitter-archive"
WAV = "/home/hatch/workspace/wavefront"
MIN_SIZE = 4
K_SIGMA = 2.0
AXIS_FLOOR = 0.10
AXIS_CAP = 1.60

def load_js(path):
    s = open(path).read()
    return json.loads(s[s.index("=") + 1:].strip())

followers = {e["follower"]["accountId"] for e in load_js(f"{ARCH}/follower.js")}
following = {e["following"]["accountId"] for e in load_js(f"{ARCH}/following.js")}
mutual_ids = followers & following
print(f"archive: {len(followers)} followers, {len(following)} following, {len(mutual_ids)} mutual ids")

tweets = [e["tweet"] for e in json.load(open(f"{ARCH}/tweets.json"))]
id2handle = {}
for t in tweets:
    for m in t.get("entities", {}).get("user_mentions", []):
        id2handle[m["id_str"]] = m["screen_name"].lower()
    sn, uid = t.get("in_reply_to_screen_name"), t.get("in_reply_to_user_id_str")
    if sn and uid:
        id2handle[uid] = sn.lower()
handle2id = {}
for uid, h in id2handle.items():
    handle2id.setdefault(h, set()).add(uid)
multi = {h: v for h, v in handle2id.items() if len(v) > 1}
print(f"id2handle: {len(id2handle)} ids, {len(handle2id)} handles, {len(multi)} handles with >1 id")

DATA = json.load(open(f"{WAV}/viz2/data.json"))
NODES = DATA["nodes"]
XYZ = np.array([n["xyz"] for n in NODES], dtype=np.float64)

mutual_idx, unknown = [], []
for i, n in enumerate(NODES):
    ids = handle2id.get(n["key"] or "", set())
    if not ids:
        unknown.append(i)
    elif ids & mutual_ids:
        mutual_idx.append(i)
print(f"placed nodes: {len(NODES)}; mutual: {len(mutual_idx)}; no-id-in-archive-map: {len(unknown)} "
      f"({[NODES[i]['key'] for i in unknown]})")

# sanity anchors from the record: top-1 mutual in, two known non-mutuals out
by_key = {n["key"]: i for i, n in enumerate(NODES)}
for h, want in (("ctzn5", True), ("eigenhector", True), ("grady_booch", False), ("eshear", False)):
    i = by_key.get(h)
    got = (i in set(mutual_idx)) if i is not None else None
    print(f"anchor @{h}: mutual={got} (expected {want})")
    assert got == want, h

P = XYZ[mutual_idx]
# nearest-neighbour distances among placed mutuals (grounds the tau scan)
from scipy.spatial import cKDTree
nn = cKDTree(P).query(P, k=2)[0][:, 1]
print(f"mutual NN distance: median {np.median(nn):.3f}, p25 {np.percentile(nn,25):.3f}, "
      f"p75 {np.percentile(nn,75):.3f}, max {nn.max():.3f}")

def dbscan(eps, ms):
    nbrs = cKDTree(P).query_ball_point(P, eps)
    core = np.array([len(x) >= ms for x in nbrs])
    lab = np.full(len(P), -1)
    cid = 0
    for i in range(len(P)):
        if lab[i] != -1 or not core[i]:
            continue
        stack = [i]; lab[i] = cid
        while stack:
            a = stack.pop()
            for b in nbrs[a]:
                if lab[b] == -1:
                    lab[b] = cid
                    if core[b]:
                        stack.append(b)
        cid += 1
    return lab

for eps in (0.09, 0.11, 0.13, 0.15, 0.18):
    for ms in (3, 4, 5):
        lab = dbscan(eps, ms)
        sizes = sorted((int((lab == c).sum()) for c in range(lab.max() + 1)), reverse=True)
        big = [s for s in sizes if s >= MIN_SIZE]
        print(f"eps {eps:.2f} ms {ms}: clusters {len(sizes)}, >= {MIN_SIZE}: {len(big)} {big}, "
              f"noise {int((lab == -1).sum())}")
# single-linkage comparison (the rejected method): percolation table
def components(tau):
    parent = list(range(len(P)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in cKDTree(P).query_pairs(tau):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    groups = {}
    for i in range(len(P)):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=len, reverse=True)
for tau in (0.15, 0.25):
    gs = components(tau)
    print(f"single-linkage tau {tau:.2f}: largest component {len(gs[0])} of {len(P)} mutuals (percolated)")

EPS = float(sys.argv[1]) if len(sys.argv) > 1 else None
MS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
if EPS is None:
    print("re-run with a chosen eps (and min_samples) as argv to write clusters9.json")
    sys.exit(0)

# replies Will sent per handle (contact-points.tsv) for member naming
replies = {}
for line in open(f"{WAV}/contact-points.tsv").read().splitlines()[1:]:
    parts = line.split("\t")
    if len(parts) >= 3:
        replies[parts[0].lstrip("@").lower()] = int(parts[2])

_lab = dbscan(EPS, MS)
groups = []
for c in range(_lab.max() + 1):
    g = [int(i) for i in np.where(_lab == c)[0]]
    if len(g) >= MIN_SIZE:
        groups.append(g)
groups.sort(key=len, reverse=True)
shells = []
for g in groups:
    members = [mutual_idx[i] for i in g]
    pts = XYZ[members]
    cen = pts.mean(axis=0)
    cov = np.cov((pts - cen).T) if len(pts) > 1 else np.eye(3) * 0.01
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]
    semi = np.clip(K_SIGMA * np.sqrt(np.maximum(evals, 0.0)), AXIS_FLOOR, AXIS_CAP)
    named = sorted(((replies.get(NODES[i]["key"] or "", 0), NODES[i]["name"], NODES[i]["key"])
                    for i in members), reverse=True)
    shells.append(dict(
        members=members, size=len(members),
        center=[round(float(x), 5) for x in cen],
        axes=[[round(float(x), 5) for x in evecs[:, k]] for k in range(3)],
        semi=[round(float(x), 5) for x in semi],
        top=[[nm, rp] for rp, nm, _k in named[:5]],
    ))
    print(f"shell size {len(members):3d} centre {np.round(cen,2)} semi {np.round(semi,2)} "
          f"top: {', '.join(f'{nm} ({rp})' for rp, nm, _k in named[:4])}")
n_shelled = sum(s["size"] for s in shells)
print(f"eps {EPS} ms {MS}: {len(shells)} shells covering {n_shelled}/{len(mutual_idx)} placed mutuals")
json.dump(dict(
    meta=dict(method="DBSCAN (eps, min_samples) over placed mutuals in data.json xyz space; "
                     "single-linkage rejected: percolates (118/153 in one component at tau 0.15)",
              eps=EPS, min_samples=MS, min_size=MIN_SIZE, k_sigma=K_SIGMA,
              axis_floor=AXIS_FLOOR, axis_cap=AXIS_CAP,
              n_mutual_placed=len(mutual_idx), n_shelled=n_shelled,
              mutual_definition="accountId in follower.js AND following.js (archive snapshot), "
                                "handle<->id via mentions/reply targets harvested from tweets.json"),
    shells=shells), open(f"{WAV}/viz9/clusters9.json", "w"), indent=1)
print("wrote viz9/clusters9.json")
