"""Large extended-field pool over Q(sqrt2,sqrt3,sqrt5,sqrt11).

Genuinely new geometry beyond v1 (which did Minkowski sums only inside the Parts
field) and beyond E2/E3 (small rotation-only pools):

  * rotation orbit of the record under generators {45deg (sqrt2), 30/60deg (sqrt3),
    ring u1=5/6+sqrt11/6 i, u2=1/2+sqrt3/2 i, 90deg} -- several copies;
  * a MINKOWSKI-sum layer  {p + R45(q) : p,q in record}  clipped to a radius, which
    mixes the sqrt2 direction into every record vertex -> dense new unit distances.

Output pool_x2big.pkl (points, edges) for coremin.py / greedy.py.
Env knobs: RCLIP (radius factor, default 1.03), CAPMINK (max minkowski pts).
"""
import pickle, time, os, math
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

H = (fe((1, F(1, 2))), fe((1, F(1, 2))))          # 45 deg
U1 = (fe((0, F(5, 6))), fe((8, F(1, 6))))          # 5/6, sqrt11/6
U2 = (fe((0, F(1, 2))), fe((2, F(1, 2))))          # 1/2, sqrt3/2  (30/60 family)
NINETY = (fe(), fe((0, F(1))))                     # (0,1)


def rot(p, r):
    a, b = r; x, y = p
    return (K.sub(K.mul(a, x), K.mul(b, y)), K.add(K.mul(b, x), K.mul(a, y)))


def comp(r1, r2):
    a1, b1 = r1; a2, b2 = r2
    return (K.sub(K.mul(a1, a2), K.mul(b1, b2)), K.add(K.mul(a1, b2), K.mul(b1, a2)))


def main():
    t0 = time.time()
    rclip = float(os.environ.get('RCLIP', '1.03'))
    capmink = int(os.environ.get('CAPMINK', '30000'))
    pts = load_vtx(K, REC)
    ptsf = [(K.to_float(p[0]), K.to_float(p[1])) for p in pts]
    rmax = max(math.hypot(x, y) for x, y in ptsf)
    lim = (rclip * rmax) ** 2
    print(f'record rmax={rmax:.3f} clip r2<={lim:.3f}', flush=True)

    seen = {p: i for i, p in enumerate(pts)}
    allp = list(pts)

    # rotation orbit
    gens = [H, U2, comp(H, U2), NINETY, comp(NINETY, H), U1, comp(H, U1)]
    for r in gens:
        for p in pts:
            q = rot(p, r)
            if q not in seen:
                seen[q] = len(allp); allp.append(q)
    print('after rotation orbit:', len(allp), round(time.time()-t0, 1), 's', flush=True)

    # Minkowski layer: p + R45(q), clipped
    Rq = [rot(p, H) for p in pts]
    Rqf = [(K.to_float(a), K.to_float(b)) for a, b in Rq]
    added = 0
    for i, p in enumerate(pts):
        px, py = ptsf[i]
        for j, q in enumerate(Rq):
            sx, sy = px + Rqf[j][0], py + Rqf[j][1]
            if sx*sx + sy*sy > lim:
                continue
            s = (K.add(p[0], q[0]), K.add(p[1], q[1]))
            if s not in seen:
                seen[s] = len(allp); allp.append(s); added += 1
                if added >= capmink:
                    break
        if added >= capmink:
            break
    print('after minkowski layer:', len(allp), 'added', added, round(time.time()-t0, 1), 's', flush=True)

    # edges: float prefilter (blocked) then exact confirm
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
            print('  edge scan', s, '/', n, 'edges', len(E), round(time.time()-t0, 1), 's', flush=True)
    pickle.dump((allp, E), open('pool_x2big.pkl', 'wb'))
    print('pool_x2big:', n, 'v', len(E), 'e', round(time.time()-t0, 1), 's', flush=True)


if __name__ == '__main__':
    main()
