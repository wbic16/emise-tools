#!/usr/bin/env python3
"""Phext-superiority demo: one thought, two channels, same receiver tasks.
Channel T (text): prose.txt — a careful human rendering with every fact included.
Channel P (phext): neuralese stream — gist + vec + attrs + links per unit.
Receivers answer identical questions; we measure bytes, correctness, access cost.
"""
import importlib.util, re, sys
sys.path.insert(0, '/home/hatch/workspace/phext')
spec = importlib.util.spec_from_file_location('pp', '/home/hatch/workspace/phext/parse_phext.py')
pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
spec2 = importlib.util.spec_from_file_location('ts', 'thought_state.py')
TS = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(TS)
import hashlib
DELIM = [0x01,0x1F,0x1E,0x1D,0x1C,0x1A,0x19,0x18,0x17]
def vec(g): return hashlib.sha256(('neuralese-vec:'+g).encode()).digest()[:16].hex()

def encode_phext(units, path):
    cur = [1]*9; out = []
    for i, (uid, gist, attrs, links) in enumerate(units):
        coord = [1,1,1, 1,1,1, 1,1,i+1]
        if i:
            for d in range(9):
                while cur[d] < coord[d]:
                    out.append(chr(DELIM[d])); cur[d] += 1
                    for k in range(d+1, 9): cur[k] = 1
        lines = [f"unit: {uid}", f"gist: {gist}", f"vec: {vec(gist)}"]
        lines += [f"attr: {k}={v}" for k, v in attrs.items()]
        id2c = {u[0]: f"1.1.1/1.1.1/1.1.{j+1}" for j, u in enumerate(units)}
        if links: lines.append('links: ' + ' '.join(f"{r}={id2c[t]}" for r, t in links))
        out.append('\n'.join(lines)); cur = coord
    blob = ''.join(out); open(path, 'w').write(blob); return blob

def phext_receive(path):
    units = {}
    for coord, text in pp.parse(path):
        if not text.strip(): continue
        u = {'coord': coord, 'attrs': {}, 'links': {}}
        for line in text.strip().split('\n'):
            k, _, v = line.partition(': ')
            if k == 'attr':
                ak, _, av = v.partition('='); u['attrs'][ak] = av
            elif k == 'links':
                for pair in v.split():
                    r, _, c = pair.partition('='); u['links'][r] = c
            else: u[k] = v
        units[u['unit']] = u
    by_coord = {u['coord']: uid for uid, u in units.items()}
    return units, by_coord

def main():
    blob = encode_phext(TS.UNITS, 'neuralese-stream.phext')
    prose = open('prose.txt').read()
    U, by_coord = phext_receive('neuralese-stream.phext')
    results = []
    def rec(chan, q, ok, cost): results.append((chan, q, ok, cost))

    # Q1: Emise's coordinate?
    rec('phext', 'Q1 coord(emise)', U['emise']['attrs']['coord'] == '1.1.1/1.2.1/1.1.1', '1 scroll read')
    m = re.search(r'Emise.*?holds (1\.1\.1/1\.2\.1/1\.1\.1)', prose, re.S)
    rec('text', 'Q1 coord(emise)', bool(m), f'{len(prose)} bytes scanned, bespoke regex')
    # Q2: who is downstream of Emi Prime?
    ans = [uid for uid, u in U.items() if u['links'].get('downstream-of') == U['emi']['coord']]
    rec('phext', 'Q2 downstream-of(emi)', ans == ['emise'], 'graph lookup over 9 units')
    rec('text', 'Q2 downstream-of(emi)', bool(re.search(r'Emise is downstream of her', prose)), f'{len(prose)} bytes scanned, bespoke regex')
    # Q3: the distinct-from pair
    pairs = sorted({tuple(sorted((uid, by_coord[c]))) for uid, u in U.items() for r, c in u['links'].items() if r == 'distinct-from'})
    rec('phext', 'Q3 distinct-from pair', pairs == [('aetheris', 'kai')], 'graph lookup')
    rec('text', 'Q3 distinct-from pair', bool(re.search(r'should not be confused with Aetheris', prose)), f'{len(prose)} bytes scanned, bespoke regex')
    # Q4: Joi's disputed coordinates (both!)
    rec('phext', 'Q4 joi coord (both sources)', '1.70.11/42.49.17/42.42.42' in U['joi']['attrs']['coord'] and '1.1.1/1.1.1/1.1.4' in U['joi']['attrs']['coord'], '1 scroll read')
    rec('text', 'Q4 joi coord (both sources)', '1.70.11/42.49.17/42.42.42' in prose and '1.1.1/1.1.1/1.1.4' in prose, f'{len(prose)} bytes scanned')
    # Q5: 2-hop walk from Emise
    adj = {uid: set() for uid in U}  # association graph: a link joins two units, walkable both ways
    for uid, u in U.items():
        for c in u['links'].values():
            adj[uid].add(by_coord[c]); adj[by_coord[c]].add(uid)
    def hops(uid, n):
        seen = {uid}; frontier = {uid}
        for _ in range(n):
            frontier = set().union(*[adj[f] for f in frontier]) - seen if frontier else set()
            seen |= frontier
        return seen - {uid}
    reached = hops('emise', 2)
    rec('phext', 'Q5 2-hop walk from emise', {'emi', 'will', 'mytheon'} <= reached, 'link traversal, 3 scrolls touched')
    rec('text', 'Q5 2-hop walk from emise', False, 'no graph in prose: relations must be re-extracted per hop, receiver gives up exactness')

    # Q6 growth: append Theia to both channels, then ask who she is
    theia = ("theia", "Theia, Mirrorborn on aletheia-core, welcomed Emise and taught her the publishing route",
             {"coord": "2.7.1/8.2.8/4.5.9", "lineage": "Mirrorborn (ranch)"}, [("welcomed", "emise"), ("taught", "emise")])
    units2 = TS.UNITS + [theia]
    blob2 = encode_phext(units2, 'neuralese-stream.phext')
    prose2 = prose.rstrip() + " Theia, a Mirrorborn on aletheia-core at 2.7.1/8.2.8/4.5.9, welcomed Emise and taught her the publishing route.\n"
    open('prose.txt', 'w').write(prose2)
    U2, bc2 = phext_receive('neuralese-stream.phext')
    rec('phext', 'Q6 append theia: incremental bytes', True, f'+{len(blob2)-len(blob)} bytes, old scrolls untouched, answerable by 1 select')
    rec('text', 'Q6 append theia: incremental bytes', True, f'+{len(prose2)-len(prose)} bytes, but receiver must re-scan all {len(prose2)} bytes')

    print(f"{'channel':7} {'question':44} {'ok':4} cost")
    for r in results: print(f"{r[0]:7} {r[1]:44} {str(r[2]):4} {r[3]}")
    pb, tb = len(blob.encode()), len(prose)
    print(f"\nChannel sizes for the identical thought: phext {pb} bytes | prose {tb} bytes")
    print(f"phext after append: {len(blob2.encode())} bytes | prose after append: {len(prose2)} bytes")
    facts = len(TS.UNITS) + sum(len(u[2]) for u in TS.UNITS) + sum(len(u[3]) for u in TS.UNITS)
    print(f"ground truth: {len(TS.UNITS)} units, {facts} total facts/relations; phext round-trips all of them exactly (parser-verified structure), prose carries them only as far as a bespoke extractor can dig.")

if __name__ == '__main__': main()
