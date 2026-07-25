"""Smallest non-4-colorable type-M universe found by `basescan.py`.

Parts uses B = (+)^4 H^2 clipped at radius 2 (9259 points, 18517 in the union).
The scan shows (+)^3 H^2 at the same radius -- 2839 points, 5677 in the union --
is *already* non-4-colorable, while every smaller (n, r) in the family is
4-colorable.  That universe does not contain Parts' 509 (it misses 19 of his
points), so its own minimal witness is a different graph, and worth minimising
on its own terms.

Edges: float prefilter, exact integer confirmation; the shared origin is merged.
"""
import pickle

import numpy as np

import lattice as L

R = 2.0
N = 3
lim = 144.0 * (R + 1e-9) ** 2
H2 = L.Hm(2)
cur = {(0, 0, 0, 0)}
for k in range(N):
    slack = N - (k + 1)
    klim = 144.0 * (R + slack) ** 2 + 1e-6
    cur = {L.add(p, q) for p in cur for q in H2
           if min(L.radius2_144(L.add(p, q))) <= klim}
P = sorted(p for p in cur if min(L.radius2_144(p)) <= lim)
print(f'base {len(P)}', flush=True)

om = L.omega_t_complex(4)
pts = [('A', p) for p in P] + [('B', p) for p in P if p != (0, 0, 0, 0)]
nA = len(P)
zA = np.array([L.to_complex(p) for p in P])
zB = np.array([L.to_complex(p) * om for _, p in pts[nA:]])
B = [p for _, p in pts[nA:]]
e, s = L.squarefree_split(15)
edges = []


def within(pl, z, off):
    out = []
    for i in range(len(pl)):
        d = np.abs(z[i + 1:] - z[i])
        for k in np.nonzero(np.abs(d - 1.0) < 1e-6)[0]:
            j = i + 1 + int(k)
            if L.is_unit(pl[i], pl[j]):
                out.append((off + i, off + j))
    return out


edges += within(P, zA, 0)
edges += within(B, zB, nA)
cross = 0
for i in range(len(P)):
    for k in np.nonzero(np.abs(np.abs(zB - zA[i]) - 1.0) < 1e-6)[0]:
        j = int(k)
        if L.cross_is_unit(P[i], B[j], 4, (e, s)):
            edges.append((i, nA + j))
            cross += 1
print(f'{len(pts)} vertices, {len(edges)} edges ({cross} cross)', flush=True)
pickle.dump((pts, edges), open('w4s.pkl', 'wb'))
