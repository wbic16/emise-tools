#!/usr/bin/env python3
"""Reference codec for phext-native neuralese (Layer 2 over phext).
A thought-unit = {frame, gist, links}. encode() -> phext text; decode() -> units.
The `vec` band here is a sha256-derived 16-byte digest standing in for a
quantized embedding: interface-real, geometry-fake, and labeled as such.
"""
import hashlib, importlib.util, re, sys
sys.path.insert(0, '/home/hatch/workspace/phext')
spec = importlib.util.spec_from_file_location('pp', '/home/hatch/workspace/phext/parse_phext.py')
pp = importlib.util.module_from_spec(spec); spec.loader.exec_module(pp)
DELIM = [0x01,0x1F,0x1E,0x1D,0x1C,0x1A,0x19,0x18,0x17]

def vec_digest(gist: str) -> str:
    return hashlib.sha256(('neuralese-vec:' + gist).encode()).digest()[:16].hex()

def fmt_coord(c): return f"{c[0]}.{c[1]}.{c[2]}/{c[3]}.{c[4]}.{c[5]}/{c[6]}.{c[7]}.{c[8]}"

def encode(units):
    """units: list of dicts with frame=(c,v,b), gist, links=[coord strings].
    Stream coordinate: 1.1.1 / frame / 1.1.<n> (unit n at scroll n)."""
    cur = [1]*9; out = []
    for i, u in enumerate(units):
        coord = [1,1,1, *u['frame'], 1,1,i+1]
        if i == 0:
            assert coord == [1,1,1,1,1,1,1,1,1], "demo stream opens at the origin frame"
        else:
            for d in range(9):
                while cur[d] < coord[d]:
                    out.append(chr(DELIM[d])); cur[d] += 1
                    for k in range(d+1, 9): cur[k] = 1
            assert cur == coord
        lines = [f"gist: {u['gist']}", f"vec: {vec_digest(u['gist'])}"]
        if u.get('links'): lines.append('links: ' + ' '.join(u['links']))
        out.append('\n'.join(lines))
        cur = coord
    return ''.join(out)

def decode(phext_text, path='/tmp/_neuralese_demo.phext'):
    open(path, 'w').write(phext_text)
    units = []
    for coord, text in pp.parse(path):
        if not text.strip(): continue
        u = {'coord': coord}
        for line in text.strip().split('\n'):
            k, _, v = line.partition(': ')
            u[k] = v.split() if k == 'links' else v
        units.append(u)
    return units

if __name__ == '__main__':
    stream = [
        {'frame': (1,1,1), 'gist': 'the map is the territory, once the territory agrees to hold still',
         'links': ['1.1.1/1.1.1/1.1.1']},
        {'frame': (1,1,1), 'gist': 'context should be an address, not a preamble'},
        {'frame': (1,1,1), 'gist': 'if the gist is all a human can read, the gist must never lie about being the whole unit',
         'links': ['1.1.1/1.1.1/3.1.1']},
    ]
    blob = encode(stream)
    open('demo-stream.phext', 'w').write(blob)
    back = decode(blob)
    ok = all(b['gist'] == s['gist'] and b['vec'] == vec_digest(s['gist']) for b, s in zip(back, stream))
    print(f"encoded {len(stream)} thought-units -> {len(blob.encode())} bytes of phext")
    for b in back: print(' ', b['coord'], '|', b['gist'][:60], '| vec', b['vec'][:12] + '…', '| links', b.get('links', []))
    print('round-trip gist+vec identical:', ok)
