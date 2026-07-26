"""Candidate pool around Heule's 510-vertex graph, inside Q(sqrt3,sqrt5,sqrt11).

Heule's 510 is a *different* 5-chromatic unit-distance graph from Parts' 509 --
same field, different construction -- and it is vertex-critical (checked: all
510 single deletions are 4-colorable).  Everything this run has tried lives in
Parts' basin; this builds the analogous candidate universe around Heule's graph
so the swap and exact region-trade machinery can work in a second basin, where a
two-vertex improvement would land on 508.

Candidates are the field-exact translates p + (q - r) for edges (q, r), which
stay in the field automatically; floats are used only to prefilter by radius and
by degree, and every accepted candidate's edges are confirmed exactly.

Env: RMAX (radius), DMIN (min degree into the graph), OUT.
"""
import os
import pickle

import numpy as np

import mfield

RMAX = float(os.environ.get('RMAX', '2.5'))
DMIN = int(os.environ.get('DMIN', '3'))
OUT = os.environ.get('OUT', 'hpool.pkl')

F = mfield.MField([3, 5, 11])
pts, E = pickle.load(open('h510e.pkl', 'rb'))
n = len(pts)
Z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in pts])
c = Z.mean()

U = []
for u, v in E:
    for a, b in ((u, v), (v, u)):
        U.append((F.sub(pts[a][0], pts[b][0]), F.sub(pts[a][1], pts[b][1])))
zU = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in U])
print(f'{len(U)} edge vectors', flush=True)

# float pass: which (p, u) land inside the disk and touch >= DMIN graph vertices
cand = []
for i in range(n):
    W = Z[i] + zU
    inside = np.nonzero(np.abs(W - c) <= RMAX)[0]
    if len(inside) == 0:
        continue
    D = np.abs(W[inside][:, None] - Z[None, :])
    deg = (np.abs(D - 1.0) < 1e-7).sum(axis=1)
    for k, dg in zip(inside, deg):
        if dg >= DMIN:
            cand.append((i, int(k)))
print(f'{len(cand)} float-surviving candidates', flush=True)

seen = {(x, y) for x, y in pts}
new = []
for i, k in cand:
    p = (F.add(pts[i][0], U[k][0]), F.add(pts[i][1], U[k][1]))
    if p in seen:
        continue
    seen.add(p)
    new.append(p)
print(f'{len(new)} distinct new points', flush=True)

allp = list(pts) + new
zz = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in allp])
edges = []
for i in range(len(allp)):
    d = np.abs(zz[i + 1:] - zz[i])
    for k in np.nonzero(np.abs(d - 1.0) < 1e-7)[0]:
        j = i + 1 + int(k)
        dx = F.sub(allp[i][0], allp[j][0])
        dy = F.sub(allp[i][1], allp[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            edges.append((i, j))
print(f'pool: {len(allp)} vertices, {len(edges)} exact edges', flush=True)
pickle.dump((allp, edges), open(OUT, 'wb'))
