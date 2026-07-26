"""Three-rotation universe: Parts' A u omega[15] B, plus an omega[11] copy.

`findrot.py` shows Heule's 553/610/633 use a *second* rotation on top of Parts'
omega[15] = (7 + i sqrt15)/8, namely omega[11] = (5 + i sqrt11)/6 (and its
square).  Every pool in this run has been A u omega[15] B only, so the
omega[11] copies are candidate vertices that no search here has ever been able
to use.  This builds the union exactly and computes all unit edges exactly
(floats prefilter only).

Env: ROTS (comma-separated labels from findrot.ROTS, plus 'id'), RAD, OUT.
"""
import os
import pickle

import numpy as np

import findrot as R
import mfield

F = R.F
RAD = float(os.environ.get('RAD', '2.0'))
LABELS = os.environ.get('ROTS', 'id,w[15],w[11],w[11]~').split(',')
OUT = os.environ.get('OUT', 'r3pool.pkl')

# base: Parts' own half-A points (the Minkowski-generated set -- the lattice
# *module* is dense in the plane, so it cannot be enumerated by a radius)
w4pts, _ = pickle.load(open('/home/ubuntu/p23w4/w4d.pkl', 'rb'))
lim = RAD + 1e-9
base = []
for tag, v in w4pts:
    if tag != 'A':
        continue
    x = (v[0] + v[1] * 33 ** 0.5) / 12
    y = (v[2] * 3 ** 0.5 + v[3] * 11 ** 0.5) / 12
    if x * x + y * y <= lim * lim:
        base.append(v)
print(f'base {len(base)} half-A points within radius {RAD}', flush=True)


def to_field(p):
    a, b, c, d = p
    from fractions import Fraction as Fr
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


pts = {}
for lbl in LABELS:
    rot = None if lbl == 'id' else R.ROTS[lbl]
    for p in base:
        q = to_field(p)
        if rot is not None:
            q = R.cmul(q, rot)
        pts.setdefault(q, lbl)
allp = sorted(pts, key=lambda q: (F.to_float(q[0]), F.to_float(q[1])))
print(f'{len(allp)} distinct points from {LABELS}', flush=True)

z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in allp])
order = np.argsort(z.real)
E = []
for ii in range(len(order)):
    i = order[ii]
    for jj in range(ii + 1, len(order)):
        j = order[jj]
        if z[j].real - z[i].real > 1.0000001:
            break
        if abs(abs(z[j] - z[i]) - 1.0) > 1e-7:
            continue
        dx = F.sub(allp[i][0], allp[j][0])
        dy = F.sub(allp[i][1], allp[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            E.append((min(i, j), max(i, j)))
E = sorted(set(E))
print(f'pool {len(allp)} vertices, {len(E)} exact edges', flush=True)
pickle.dump((allp, E), open(OUT, 'wb'))
