"""Universe with translated rotated copies: A u wA u (T + wA) u (-T + wA).

`tshift.py` extracts the translation de Grey/Heule's earlier graphs use,
T = (-19 + 11 i sqrt15)/96 (up to sign), applied to the omega[15]-rotated copy.
Parts' universe pins the rotation centre at the origin, so translated copies are
candidate vertices no pool in this run has contained.  Exact edges throughout;
floats prefilter only.

Env: RAD, COPIES (comma-separated: 'id', 'w', 'w+T', 'w-T', 'w11'), OUT.
"""
import os
import pickle
from fractions import Fraction as Fr

import numpy as np

import findrot as R

F = R.F
RAD = float(os.environ.get('RAD', '2.6'))
COPIES = os.environ.get('COPIES', 'id,w,w+T,w-T').split(',')
OUT = os.environ.get('OUT', 'tpool.pkl')

W = R.ROTS['w[15]']
W11 = R.ROTS['w[11]']
T = pickle.load(open('tshift.pkl', 'rb'))['803']
NEGT = (tuple(-c for c in T[0]), tuple(-c for c in T[1]))

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
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


def add(p, q):
    return (F.add(p[0], q[0]), F.add(p[1], q[1]))


SPEC = {'id': (None, None), 'w': (W, None), 'w+T': (W, T), 'w-T': (W, NEGT),
        'w11': (W11, None), 'w11+T': (W11, T)}

pts = {}
for lbl in COPIES:
    rot, sh = SPEC[lbl]
    for p in base:
        q = to_field(p)
        if rot is not None:
            q = R.cmul(q, rot)
        if sh is not None:
            q = add(q, sh)
        pts.setdefault(q, lbl)
allp = sorted(pts, key=lambda q: (F.to_float(q[0]), F.to_float(q[1])))
tags = [pts[q] for q in allp]
print(f'{len(allp)} distinct points from {COPIES}', flush=True)

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
from collections import Counter
print('copy sizes', Counter(tags))
print('cross edges', Counter(tuple(sorted((tags[a], tags[b]))) for a, b in E))
pickle.dump((allp, E), open(OUT, 'wb'))
pickle.dump(tags, open(OUT + '.tags', 'wb'))
