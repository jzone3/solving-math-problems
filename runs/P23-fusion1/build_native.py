"""Rich NATIVE-field pool over the Parts ring Q(sqrt3,sqrt5,sqrt11).

v1 built Minkowski/apex pools in this field but only ever ran *small-move*
searches on them (greedy deletion, -2+1 / -3+2 swaps). The LNS ruin&recreate
engine (lns508.py) has never been run over the native ring -- which is the only
place where working substitutions for record vertices are known to exist
(v1 found 9 single swaps here, none in the sqrt2 extension).

Pool = record
     u Minkowski sums p+q (clipped to the record radius)
     u apex points: for every pair p,q at distance <= 2, the two third vertices
       of the unit-side triangles on (p,q) -- these are the canonical UDG
       extension points and the natural substitutes for a record vertex.
Edges recomputed exactly (float prefilter + exact confirmation), then a degree
filter keeps only vertices with >= MINDEG unit neighbours (record kept always).

Env: RCLIP (1.02), MINDEG (5), APEXMAX (max apex points), CAPMINK.
Output pool_native.pkl
"""
import pickle, time, os, math
from fractions import Fraction as F
import numpy as np
from mfield import MField, load_vtx

REC = '../../solutions/P23/v509e2442.vtx'
K = MField((3, 5, 11))


_SQ = {}


def _scale(d2):
    """s with apex = mid +- s*(-dy, dx);  s = sqrt((4-d2)/(4 d2)).  Cached."""
    if d2 in _SQ:
        return _SQ[d2]
    t = K.mul(K.sub(K.scal(4, K.ONE), d2), K.inv(K.scal(4, d2)))
    s = K.field_sqrt(t)
    _SQ[d2] = s
    return s


def apexes(p, q):
    """Third vertices of the two unit triangles on segment pq (exact, or [])."""
    d2 = K.norm2(p, q)
    fd = K.to_float(d2)
    if fd <= 1e-12 or fd > 4.0:
        return []
    s = _scale(d2)
    if s is None:
        return []                                # apex not in this field
    mx = K.scal(F(1, 2), K.add(p[0], q[0]))
    my = K.scal(F(1, 2), K.add(p[1], q[1]))
    dx, dy = K.sub(q[0], p[0]), K.sub(q[1], p[1])
    ox, oy = K.mul(K.scal(-1, dy), s), K.mul(dx, s)
    return [(K.add(mx, ox), K.add(my, oy)), (K.sub(mx, ox), K.sub(my, oy))]


def main():
    t0 = time.time()
    rclip = float(os.environ.get('RCLIP', '1.02'))
    mindeg = int(os.environ.get('MINDEG', '5'))
    apexmax = int(os.environ.get('APEXMAX', '40000'))
    capmink = int(os.environ.get('CAPMINK', '40000'))
    pts = load_vtx(K, REC)
    n0 = len(pts)
    ptsf = [(K.to_float(p[0]), K.to_float(p[1])) for p in pts]
    rmax = max(math.hypot(x, y) for x, y in ptsf)
    lim = (rclip * rmax) ** 2
    print(f'record {n0} rmax={rmax:.3f}', flush=True)

    seen = {p: i for i, p in enumerate(pts)}
    allp = list(pts)

    added = 0
    for i in range(n0):
        px, py = ptsf[i]
        for j in range(i, n0):
            sx, sy = px + ptsf[j][0], py + ptsf[j][1]
            if sx*sx + sy*sy > lim:
                continue
            s = (K.add(pts[i][0], pts[j][0]), K.add(pts[i][1], pts[j][1]))
            if s not in seen:
                seen[s] = len(allp); allp.append(s); added += 1
        if added >= capmink:
            break
    print(f'minkowski added {added} -> {len(allp)} ({round(time.time()-t0)}s)', flush=True)

    # apexes over close pairs of record vertices
    A = np.array(ptsf)
    aadd = 0
    for i in range(n0):
        d2row = ((A - A[i]) ** 2).sum(-1)
        for j in np.nonzero((d2row > 1e-9) & (d2row <= 4.0))[0]:
            j = int(j)
            if j <= i:
                continue
            for s in apexes(pts[i], pts[j]):
                if s not in seen:
                    seen[s] = len(allp); allp.append(s); aadd += 1
            if aadd >= apexmax:
                break
        if aadd >= apexmax:
            break
        if i % 50 == 0:
            print(f'  apex {i}/{n0} added {aadd} ({round(time.time()-t0)}s)', flush=True)
    print(f'apex added {aadd} -> {len(allp)} ({round(time.time()-t0)}s)', flush=True)

    # exact edges
    Af = np.array([(K.to_float(x), K.to_float(y)) for x, y in allp])
    n = len(allp); E = []; CH = 500
    for s in range(0, n, CH):
        d2 = ((Af[s:s+CH, None, :] - Af[None, :, :]) ** 2).sum(-1)
        ii, jj = np.nonzero(np.abs(d2 - 1.0) < 1e-6)
        for a, b in zip(ii, jj):
            ga, gb = s + int(a), int(b)
            if ga < gb and K.norm2(allp[ga], allp[gb]) == K.ONE:
                E.append((ga, gb))
        if s % 5000 == 0:
            print(f'  edge scan {s}/{n} edges {len(E)} ({round(time.time()-t0)}s)', flush=True)

    # degree filter (record always kept)
    while True:
        deg = [0] * n
        for a, b in E:
            deg[a] += 1; deg[b] += 1
        keep = [i for i in range(n) if i < n0 or deg[i] >= mindeg]
        if len(keep) == n:
            break
        ks = set(keep)
        remap = {g: k for k, g in enumerate(keep)}
        allp = [allp[g] for g in keep]
        E = [(remap[a], remap[b]) for a, b in E if a in ks and b in ks]
        n = len(allp)
        print(f'  degree filter -> {n} v {len(E)} e', flush=True)

    pickle.dump((allp, E), open('pool_native.pkl', 'wb'))
    print(f'pool_native: {n} v {len(E)} e ({round(time.time()-t0)}s)', flush=True)


if __name__ == '__main__':
    main()
