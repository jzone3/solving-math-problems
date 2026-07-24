"""Extended-field pool: Q(sqrt2, sqrt3, sqrt5, sqrt11).

The prompt's explicit lever is "different field extensions". v1 stayed inside
Q(sqrt3,sqrt5,sqrt11). Here we adjoin sqrt2 and use the 45-degree unit rotation
r = (sqrt2/2)(1+i) (and its powers 135/225/315 deg) applied to the 509 record,
producing genuinely new vertices that are NOT expressible in the Parts field.
90/180/270 deg rotations are rational and add nothing new, so only the odd
multiples of 45 deg are used. Output pool_x2.pkl is (points, edges) for coremin.
"""
import pickle, time
from fractions import Fraction as F
import numpy as np
import mfield
from mfield import MField, load_vtx

REC = '../../solutions/P23/v509e2442.vtx'
K = MField((2, 3, 5, 11))   # primes bit0=2,bit1=3,bit2=5,bit3=11 ; N=16


def fe(*pairs):
    t = [F(0)] * K.N
    for m, v in pairs:
        t[m] = F(v)
    return tuple(t)

# sqrt2/2 has mask {2}=bit0 -> mask index 1, coeff 1/2
H = fe((1, F(1, 2)))          # sqrt2/2
NEG_H = fe((1, F(-1, 2)))     # -sqrt2/2
ONE_F = K.ONE


def rot(p, a, b):
    x, y = p
    return (K.sub(K.mul(a, x), K.mul(b, y)), K.add(K.mul(b, x), K.mul(a, y)))


def main():
    t = time.time()
    pts = load_vtx(K, REC)
    print('loaded record into Q(v2,v3,v5,v11):', len(pts), 'pts', round(time.time()-t,1),'s', flush=True)
    # odd multiples of 45 deg: (a,b) = (cos,sin)
    rots = [(H, H),          # 45
            (NEG_H, H),      # 135
            (NEG_H, NEG_H),  # 225
            (H, NEG_H)]      # 315
    seen = {p: i for i, p in enumerate(pts)}
    allp = list(pts)
    for (a, b) in rots:
        for p in pts:
            q = rot(p, a, b)
            if q not in seen:
                seen[q] = len(allp); allp.append(q)
    print('pool_x2 vertices:', len(allp), round(time.time()-t,1),'s', flush=True)
    # edges: float prefilter then exact norm2 in the 16-dim field
    Af = np.array([(K.to_float(p[0]), K.to_float(p[1])) for p in allp])
    n = len(allp); E = []; CH = 800
    for s in range(0, n, CH):
        d2 = ((Af[s:s+CH, None, :] - Af[None, :, :]) ** 2).sum(-1)
        ii, jj = np.nonzero(np.abs(d2 - 1.0) < 1e-6)
        for a, b in zip(ii, jj):
            ga, gb = s + int(a), int(b)
            if ga < gb and K.norm2(allp[ga], allp[gb]) == ONE_F:
                E.append((ga, gb))
    pickle.dump((allp, E), open('pool_x2.pkl', 'wb'))
    print('pool_x2:', n, 'v', len(E), 'e', round(time.time()-t,1),'s', flush=True)


if __name__ == '__main__':
    main()
