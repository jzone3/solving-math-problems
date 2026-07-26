"""Candidate universe for region trades: Parts' record + translated copies.

Every trade search so far drew replacement vertices from Parts' own universe
(A u omega A) or, latterly, from the omega[11] copy.  E43 found translations T
for which A u (T + omega A) is *also* non-4-colorable, i.e. a supply of
candidate points that couple to the record's own geometry and that no previous
search in this run could reach.  This builds

    record(509)  u  A_r  u  omega A_r  u  (T63 + omega A_r)  u  (T65 + omega A_r)

within radius R of the record's centroid, with every unit edge recomputed
exactly.

Env: RAD, OUT.
"""
import os
import pickle
from collections import Counter
from fractions import Fraction as Fr

import numpy as np

import findrot as R
import mfield

F = R.F
W = R.ROTS['w[15]']
RAD = float(os.environ.get('RAD', '1.9'))
OUT = os.environ.get('OUT', 'tradepool.pkl')

rec = mfield.load_vtx(
    F, '/home/ubuntu/solving-math-problems/solutions/P23/v509e2442.vtx')
w4pts, _ = pickle.load(open('/home/ubuntu/p23w4/w4d.pkl', 'rb'))
base = []
for tag, v in w4pts:
    if tag != 'A':
        continue
    x = (v[0] + v[1] * 33 ** 0.5) / 12
    y = (v[2] * 3 ** 0.5 + v[3] * 11 ** 0.5) / 12
    if x * x + y * y <= (RAD + 1e-9) ** 2:
        base.append((R.elt({0: Fr(v[0], 12), 5: Fr(v[1], 12)}),
                     R.elt({1: Fr(v[2], 12), 4: Fr(v[3], 12)})))

T63 = pickle.load(open('tscan.pkl', 'rb'))[0][1]
T65 = pickle.load(open('tscan2.pkl', 'rb'))[0][1]
ZERO = (R.elt({}), R.elt({}))

pts = {}
for p in rec:
    pts[p] = 'rec'
for p in base:
    pts.setdefault(p, 'A')
for lbl, T in (('wA', ZERO), ('T63', T63), ('T65', T65)):
    for q in base:
        r = R.cmul(q, W)
        p = (F.add(r[0], T[0]), F.add(r[1], T[1]))
        pts.setdefault(p, lbl)

allp = sorted(pts, key=lambda p: F.to_float(p[0]))
lab = [pts[p] for p in allp]
z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in allp])
print(f'{len(allp)} distinct points {Counter(lab)}', flush=True)

E = []
for i in range(len(allp)):
    for k in np.nonzero(np.abs(np.abs(z[i + 1:] - z[i]) - 1.0) < 1e-7)[0]:
        j = i + 1 + int(k)
        dx = F.sub(allp[i][0], allp[j][0])
        dy = F.sub(allp[i][1], allp[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            E.append((i, j))
print(f'pool {len(allp)} vertices, {len(E)} exact edges', flush=True)
print('edges by class', Counter(tuple(sorted((lab[a], lab[b])))
                                for a, b in E), flush=True)

pickle.dump((allp, E), open(OUT, 'wb'))
idx = {p: i for i, p in enumerate(allp)}
start = sorted(idx[p] for p in rec)
assert len(start) == 509
pickle.dump(start, open(OUT.replace('.pkl', '_rec.pkl'), 'wb'))
print(f'saved {OUT} and the 509 start set', flush=True)
