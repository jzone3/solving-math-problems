"""Richer extended-field pool over Q(sqrt2,sqrt3,sqrt5,sqrt11): combine the sqrt2
45-degree rotation with the two native ring rotations used in v1
(u1=5/6+sqrt11/6 i, u2=1/2+sqrt3/2 i) and their products, to maximise the number
of cross unit-distances. Output pool_x2b.pkl (points, edges) for coremin/greedy."""
import pickle, time
from fractions import Fraction as F
import numpy as np
from mfield import MField, load_vtx

REC = '../../solutions/P23/v509e2442.vtx'
K = MField((2, 3, 5, 11))   # bit0=2,bit1=3,bit2=5,bit3=11


def fe(*pairs):
    t = [F(0)] * K.N
    for m, v in pairs:
        t[m] = F(v)
    return tuple(t)

# rotation generators (a,b), a^2+b^2=1
H = (fe((1, F(1, 2))), fe((1, F(1, 2))))                 # 45 deg  (sqrt2/2, sqrt2/2)
U1 = (fe((0, F(5, 6))), fe((8, F(1, 6))))                # 5/6, sqrt11/6  (mask 8 = sqrt11)
U2 = (fe((0, F(1, 2))), fe((2, F(1, 2))))                # 1/2, sqrt3/2   (mask 2 = sqrt3)


def rot(p, r):
    a, b = r; x, y = p
    return (K.sub(K.mul(a, x), K.mul(b, y)), K.add(K.mul(b, x), K.mul(a, y)))


def comp(r1, r2):
    a1, b1 = r1; a2, b2 = r2
    return (K.sub(K.mul(a1, a2), K.mul(b1, b2)), K.add(K.mul(a1, b2), K.mul(b1, a2)))


def main():
    t = time.time()
    pts = load_vtx(K, REC)
    gens = [H, U1, U2, comp(H, U1), comp(H, U2), comp(U1, U2),
            comp(H, comp(U1, U2)), comp(H, H)]
    seen = {p: i for i, p in enumerate(pts)}
    allp = list(pts)
    for r in gens:
        for p in pts:
            q = rot(p, r)
            if q not in seen:
                seen[q] = len(allp); allp.append(q)
    print('pool_x2b vertices:', len(allp), round(time.time()-t, 1), 's', flush=True)
    Af = np.array([(K.to_float(p[0]), K.to_float(p[1])) for p in allp])
    n = len(allp); E = []; CH = 700
    for s in range(0, n, CH):
        d2 = ((Af[s:s+CH, None, :] - Af[None, :, :]) ** 2).sum(-1)
        ii, jj = np.nonzero(np.abs(d2 - 1.0) < 1e-6)
        for a, b in zip(ii, jj):
            ga, gb = s + int(a), int(b)
            if ga < gb and K.norm2(allp[ga], allp[gb]) == K.ONE:
                E.append((ga, gb))
    pickle.dump((allp, E), open('pool_x2b.pkl', 'wb'))
    print('pool_x2b:', n, 'v', len(E), 'e', round(time.time()-t, 1), 's', flush=True)


if __name__ == '__main__':
    main()
