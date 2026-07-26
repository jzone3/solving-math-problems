"""Exact check of a Heule .vtx graph: distinct points, exact unit edges, and
agreement with the published .edge file.  Floats are a prefilter only.
"""
import pickle
import sys

import mfield

VTX = sys.argv[1]
EDGE = sys.argv[2] if len(sys.argv) > 2 else None
OUT = sys.argv[3] if len(sys.argv) > 3 else None

F = mfield.MField([3, 5, 11])
pts = mfield.load_vtx(F, VTX)
n = len(pts)
zs = [(F.to_float(x), F.to_float(y)) for x, y in pts]
assert len({(round(a, 9), round(b, 9)) for a, b in zs}) == n, 'duplicate points'

E = []
for i in range(n):
    xi, yi = pts[i]
    ax, ay = zs[i]
    for j in range(i + 1, n):
        bx, by = zs[j]
        d = (ax - bx) ** 2 + (ay - by) ** 2
        if abs(d - 1.0) > 1e-6:
            continue
        dx = F.sub(xi, pts[j][0])
        dy = F.sub(yi, pts[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            E.append((i, j))
print(f'{n} distinct vertices, {len(E)} exact unit edges')

if EDGE:
    pub = set()
    for line in open(EDGE):
        if line.startswith('e '):
            a, b = line.split()[1:3]
            pub.add(tuple(sorted((int(a) - 1, int(b) - 1))))
    print(f'published {len(pub)} edges; identical: {pub == set(E)}')

if OUT:
    pickle.dump((pts, E), open(OUT, 'wb'))
