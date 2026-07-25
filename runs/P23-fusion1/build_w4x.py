"""W_4 pool extended so that it contains the record's own halves exactly.

wt_4.pkl (radius-clipped) misses 19 of the record's 510 lattice points, so it
cannot be used as the universe for half-wise re-optimisation of the record.
Here A = P_4 u L374 and B = P_4 u S136, edges recomputed exactly (float
prefilter, exact integer confirmation).
"""
import pickle

import numpy as np

import lattice as L

pts4, _ = pickle.load(open('wt_4.pkl', 'rb'))
LS = pickle.load(open('/home/ubuntu/p23w16/LS.pkl', 'rb'))
P4 = [p for t, p in pts4 if t == 'A']
A = sorted(set(P4) | {tuple(x) for x in LS['L']})
B = sorted(set(P4) | {tuple(x) for x in LS['S']})
pts = [('A', p) for p in A] + [('B', p) for p in B]
nA = len(A)
print(f'|A|={nA} |B|={len(B)}', flush=True)

om = L.omega_t_complex(4)
zA = np.array([L.to_complex(p) for p in A])
zB = np.array([L.to_complex(p) * om for p in B])
e, s = L.squarefree_split(15)
edges = []


def within(pts_list, z, off):
    out = []
    for i in range(len(pts_list)):
        d = np.abs(z[i + 1:] - z[i])
        for k in np.nonzero(np.abs(d - 1.0) < 1e-6)[0]:
            j = i + 1 + int(k)
            if L.is_unit(pts_list[i], pts_list[j]):
                out.append((off + i, off + j))
    return out


edges += within(A, zA, 0)
print(f'A edges {len(edges)}', flush=True)
eb = within(B, zB, nA)
edges += eb
print(f'B edges {len(eb)}', flush=True)
cross = 0
for i in range(len(A)):
    d = np.abs(zB - zA[i])
    for k in np.nonzero(np.abs(d - 1.0) < 1e-6)[0]:
        j = int(k)
        if L.cross_is_unit(A[i], B[j], 4, (e, s)):
            edges.append((i, nA + j))
            cross += 1
print(f'cross {cross}; total {len(edges)}', flush=True)
pickle.dump((pts, edges), open('w4x.pkl', 'wb'))

idx = {p: i for i, p in enumerate(pts)}
rec = sorted({idx[('A', tuple(p))] for p in LS['L']}
             | {idx[('B', tuple(p))] for p in LS['S']})
pickle.dump(rec, open('rec_w4x.pkl', 'wb'))
print(f'record indices: {len(rec)}', flush=True)
