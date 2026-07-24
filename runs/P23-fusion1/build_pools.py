"""Build new-geometry candidate pools around the 509 record.

v1 only used ring rotations u=5/6+sqrt11/6 i and u=1/2+sqrt3/2 i (both native to
Q(sqrt3,sqrt5,sqrt11)). Here we try genuinely different unit rotations that v1 did
NOT use:
  * RATIONAL Pythagorean rotations (3/5,4/5),(5/13,12/13),(8/17,15/17),(20/29,21/29)
    and inverses -- irrational angle multiples of pi, stay inside the field, new geometry;
  * a sqrt2-based 45-degree rotation (sqrt2/2)(1+i) -- a genuine field EXTENSION
    Q(sqrt2,sqrt3,sqrt5,sqrt11) (the "different field extension" lever from the prompt).

Output pools are (points, edges) pickles compatible with coremin.py / greedy.py.
"""
import pickle, sys, time
from fractions import Fraction as F
import numpy as np
import field  # native Q(sqrt3,sqrt5,sqrt11), 8-dim, fast
from field import load_vtx

REC = '../../solutions/P23/v509e2442.vtx'


def exact_edges(K, pts, tol=1e-6):
    Af = np.array([(K.to_float(p[0]), K.to_float(p[1])) for p in pts])
    n = len(pts)
    E = []
    CH = 1200
    for s in range(0, n, CH):
        d2 = ((Af[s:s+CH, None, :] - Af[None, :, :]) ** 2).sum(-1)
        ii, jj = np.nonzero(np.abs(d2 - 1.0) < tol)
        for a, b in zip(ii, jj):
            ga, gb = s + int(a), int(b)
            if ga < gb and K.norm2(pts[ga], pts[gb]) == K.ONE:
                E.append((ga, gb))
    return E


# ---- adapter so field.py (module of functions) looks like an MField ----
class NativeK:
    ONE = field.ONE
    add = staticmethod(field.add)
    sub = staticmethod(field.sub)
    mul = staticmethod(field.mul)
    to_float = staticmethod(field.to_float)
    norm2 = staticmethod(field.norm2)
    N = field.N


def fe_native(*pairs):
    t = [F(0)] * field.N
    for idx, val in pairs:
        t[idx] = F(val)
    return tuple(t)


def rot(K, p, a, b):
    x, y = p
    return (K.sub(K.mul(a, x), K.mul(b, y)), K.add(K.mul(b, x), K.mul(a, y)))


def build_rational():
    K = NativeK()
    pts = load_vtx(REC)
    # rational unit rotations (a,b) with a^2+b^2=1
    rats = [(F(3,5),F(4,5)), (F(4,5),F(3,5)), (F(5,13),F(12,13)),
            (F(8,17),F(15,17)), (F(20,29),F(21,29))]
    rots = []
    for a,b in rats:
        rots.append((fe_native((0,a)), fe_native((0,b))))
        rots.append((fe_native((0,a)), fe_native((0,-b))))  # inverse
    seen = {p: i for i, p in enumerate(pts)}
    allp = list(pts)
    for (a,b) in rots:
        for p in pts:
            q = rot(K, p, a, b)
            if q not in seen:
                seen[q] = len(allp); allp.append(q)
    print('rational-rotation pool:', len(allp), 'vertices', flush=True)
    E = exact_edges(K, allp)
    pickle.dump((allp, E), open('pool_rat.pkl', 'wb'))
    print('pool_rat:', len(allp), 'v', len(E), 'e', flush=True)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'rational'
    t = time.time()
    if which == 'rational':
        build_rational()
    print('done in', round(time.time()-t,1), 's')
