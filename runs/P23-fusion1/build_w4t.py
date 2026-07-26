"""Smallest known non-4-colorable type-M universe, built exactly.

`genscan.py` found that three Minkowski layers of the 30 unit vectors of Parts'
ring, clipped to radius 2, already give a non-4-colorable union at 3997
vertices -- smaller than the 5677 of `w4s.pkl` and far smaller than the 18517 of
the full W_4 pool.  Here the same set is rebuilt with exact integer unit tests
(float prefilter, exact confirmation) so it can be used as the universe for the
exact hitting-set and region-trade searches.
"""
import pickle

import numpy as np

import genscan as G
import lattice as L

P, Q, M, R, LAYERS = 3, 11, 12, 2.0, 3
U = [u for u in G.units(P, Q, M) if any(u)]
base = G.build(P, Q, M, U, R, LAYERS)
print(f'{len(U)} unit vectors, base {len(base)}', flush=True)

om = L.omega_t_complex(4)
A = sorted(base)
B = [p for p in A if p != (0, 0, 0, 0)]
pts = [('A', p) for p in A] + [('B', p) for p in B]
nA = len(A)
zA = np.array([L.to_complex(p) for p in A])
zB = np.array([L.to_complex(p) * om for p in B])
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


edges += within(A, zA, 0)
edges += within(B, zB, nA)
cross = 0
for i in range(len(A)):
    for k in np.nonzero(np.abs(np.abs(zB - zA[i]) - 1.0) < 1e-6)[0]:
        j = int(k)
        if L.cross_is_unit(A[i], B[j], 4, (e, s)):
            edges.append((i, nA + j))
            cross += 1
print(f'{len(pts)} vertices, {len(edges)} edges ({cross} cross)', flush=True)
pickle.dump((pts, edges), open('w4t.pkl', 'wb'))
