"""Deduplicate the W_4 pool as a *point set*.

The two halves both contain the origin (rho*0 = 0), so w4x.pkl carries the same
plane point twice with identical neighbourhoods -- the record's 510 pool
indices are only 509 distinct points.  Any search over the pool should run on
the merged point set, otherwise a witness can silently pay twice for one point.
"""
import pickle

import numpy as np

import lattice as L

pts, E = pickle.load(open('w4x.pkl', 'rb'))
om = L.omega_t_complex(4)
z = np.array([L.to_complex(p) * (om if t == 'B' else 1) for t, p in pts])

merge = {}
for i in range(len(pts)):
    if pts[i][0] != 'A':
        continue
    for j in np.nonzero(np.abs(z - z[i]) < 1e-9)[0]:
        j = int(j)
        if j > i:
            merge[j] = i
print(f'coincident duplicates: {len(merge)}')

keep = [i for i in range(len(pts)) if i not in merge]
new = {v: k for k, v in enumerate(keep)}


def m(x):
    return new[merge.get(x, x)]


E2 = sorted({tuple(sorted((m(u), m(v)))) for u, v in E if m(u) != m(v)})
pts2 = [pts[i] for i in keep]
pickle.dump((pts2, E2), open('w4d.pkl', 'wb'))
rec = sorted({m(v) for v in pickle.load(open('rec_w4x.pkl', 'rb'))})
pickle.dump(rec, open('rec_w4d.pkl', 'wb'))
print(f'{len(pts2)} vertices, {len(E2)} edges, record {len(rec)}')
