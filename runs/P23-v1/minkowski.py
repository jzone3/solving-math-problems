"""Minkowski-sum pool: new exact vertices p+q (p,q in V509), clipped to the
record's radius, deduped exactly, unioned with V509, unit edges recomputed
exactly (float prefilter), then degree-filtered. Output: pool_mink.pkl."""
import pickle, math
import numpy as np
from field import add, sub, mul, to_float, ONE, norm2

pts509 = pickle.load(open('g509.pkl', 'rb'))[0]
n0 = len(pts509)
print('V509:', n0)

fl = [(to_float(p[0]), to_float(p[1])) for p in pts509]
R = max(math.hypot(x, y) for x, y in fl)
print('radius', R)

seen = {}
for p in pts509:
    seen[p] = True
new = {}
for i in range(n0):
    xi, yi = fl[i]
    for j in range(i, n0):
        x = xi + fl[j][0]; y = yi + fl[j][1]
        if x * x + y * y > (R * 1.02) ** 2:
            continue
        q = (add(pts509[i][0], pts509[j][0]), add(pts509[i][1], pts509[j][1]))
        if q not in seen and q not in new:
            new[q] = True
print('new Minkowski points (clipped, deduped):', len(new))

allp = pts509 + list(new.keys())
A = np.array([(to_float(p[0]), to_float(p[1])) for p in allp])
N = len(allp)
print('pool size before degree filter:', N)

# iterative degree filter with exact confirmation of candidate edges
alive = np.ones(N, dtype=bool)
alive_idx = np.arange(N)
while True:
    idx = np.nonzero(alive)[0]
    B = A[idx]
    deg = np.zeros(len(idx), dtype=np.int32)
    edges = []
    CH = 2000
    for s in range(0, len(idx), CH):
        d2 = ((B[s:s+CH, None, :] - B[None, :, :]) ** 2).sum(-1)
        ii, jj = np.nonzero(np.abs(d2 - 1.0) < 1e-6)
        for a, b in zip(ii, jj):
            ga, gb = s + a, b
            if ga < gb:
                pa, pb = allp[idx[ga]], allp[idx[gb]]
                if norm2(pa, pb) == ONE:
                    deg[ga] += 1; deg[gb] += 1
                    edges.append((ga, gb))
    keep = (deg >= 5) | (idx < n0)   # never drop record vertices
    print('alive', len(idx), 'edges', len(edges), 'dropping', int((~keep).sum()))
    if keep.all():
        remap = {int(g): k for k, g in enumerate(idx)}
        pts = [allp[int(g)] for g in idx]
        E = [(remap[int(idx[a])] if False else a, b) for a, b in edges]
        E = [(a, b) for a, b in edges]
        pickle.dump((pts, E), open('pool_mink.pkl', 'wb'))
        pickle.dump(list(range(n0)), open('seed_g509_mink.pkl', 'wb'))
        print('FINAL pool:', len(pts), 'vertices,', len(E), 'edges -> pool_mink.pkl')
        break
    alive2 = np.zeros(N, dtype=bool)
    alive2[idx[keep]] = True
    alive = alive2
