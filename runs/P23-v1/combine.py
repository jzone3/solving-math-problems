"""Combined pool: pool_mink (47,621) + pool2 (5,825, union+apex) deduped exactly,
with G509 as indices 0..508. Edges recomputed exactly (float prefilter).
Output: pool_comb.pkl + list of 'fresh' candidate indices (in pool2 but not mink).
"""
import pickle
import numpy as np
from field import to_float, norm2, ONE

mpts, mE = pickle.load(open('pool_mink.pkl', 'rb'))
p2pts, _ = pickle.load(open('pool2.pkl', 'rb'))
seen = {p: i for i, p in enumerate(mpts)}
allp = list(mpts)
fresh = []
for p in p2pts:
    if p not in seen:
        seen[p] = len(allp)
        fresh.append(len(allp))
        allp.append(p)
print('mink', len(mpts), '+ fresh from pool2:', len(fresh), '=', len(allp))

A = np.array([(to_float(p[0]), to_float(p[1])) for p in allp])
N = len(allp)
E = []
CH = 1500
for s in range(0, N, CH):
    d2 = ((A[s:s+CH, None, :] - A[None, :, :]) ** 2).sum(-1)
    ii, jj = np.nonzero(np.abs(d2 - 1.0) < 1e-6)
    for a, b in zip(ii, jj):
        ga, gb = s + a, b
        if ga < gb and norm2(allp[ga], allp[gb]) == ONE:
            E.append((ga, gb))
    print('chunk', s, 'edges so far', len(E), flush=True)
pickle.dump((allp, E), open('pool_comb.pkl', 'wb'))
pickle.dump(fresh, open('fresh_idx.pkl', 'wb'))
print('FINAL combined pool:', N, 'vertices,', len(E), 'edges')
