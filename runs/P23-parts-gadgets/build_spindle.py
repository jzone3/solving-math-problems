"""Type-J spindle assembly from a minimized mono-pair gadget, in exact
arithmetic over the multi-quadratic field Q(sqrt3,sqrt11,sqrt13,sqrt19).

Take the mono-pair-8/3 gadget M with pair (b=0, a=P), |P| = 8/3. Rotate M
about 0 by theta = arccos(119/128) (sin theta = 3*sqrt247/128, 247=13*19 --
provably OUTSIDE Q(sqrt3,sqrt11), so the two copies share ONLY the pivot).
Then |P - rP| = 2*(8/3)*sin(theta/2) = 1, the closing unit edge. The union
G = M cup rM (+ the closing edge arises automatically as a unit distance)
is non-4-colorable: color(a)=color(b)=color(rP) but |a - rP| = 1.

Verifies: exact unit-edge recomputation over the field, exact overlap count,
kissat UNSAT + drat-trim on the 4-coloring CNF of the union.
"""
import os
import pickle
import subprocess
import sys
import tempfile
from fractions import Fraction as F

from mfield import MField
from gadget import build_cnf, write_cnf, KISSAT, DRAT

K = MField((3, 11, 13, 19))


def m(**kw):
    """element from {radicand: Fraction} dict, e.g. m(r1=F(1,2), r33=...)"""
    coefs = [F(0)] * K.N
    for k, v in kw.items():
        rad = int(k[1:])
        mask = 0
        rem = rad
        for i, p in enumerate(K.primes):
            if rem % p == 0:
                mask |= 1 << i
                rem //= p
        assert rem == 1, rad
        coefs[mask] = F(v)
    return tuple(coefs)


def lat_to_xy(t):
    """Parts fraction 4-tuple (p,q,r,s) -> (x,y) MField pair."""
    p, q, r, s = t
    return (K.add(m(r1=p), m(r33=q)), K.add(m(r3=r), m(r11=s)))


def rotate(xy, c, s):
    x, y = xy
    return (K.sub(K.mul(c, x), K.mul(s, y)), K.add(K.mul(s, x), K.mul(c, y)))


def d2(u, v):
    dx = K.sub(u[0], v[0])
    dy = K.sub(u[1], v[1])
    return K.add(K.mul(dx, dx), K.mul(dy, dy))


def main(pkl):
    with open(pkl, "rb") as f:
        d = pickle.load(f)
    assert d["kind"] == "mono"
    pts = d["points"]
    g0, g1 = d["gadget"]
    # translate so the pair is (0, P)
    b = pts[g0]
    pts = [tuple(x - y for x, y in zip(p, b)) for p in pts]
    P = pts[g1]
    xy = [lat_to_xy(p) for p in pts]
    ct = m(r1=F(119, 128))
    st = m(r247=F(3, 128))
    assert K.mul(st, st) == m(r1=F(2223, 128 * 128))
    assert K.add(K.mul(ct, ct), K.mul(st, st)) == K.ONE
    rxy = [rotate(p, ct, st) for p in xy]
    # exact overlap
    s1 = set(xy)
    overlap = [p for p in rxy if p in s1]
    print("overlap of the two copies: %d vertices (expect exactly 1: the pivot)"
          % len(overlap))
    union = list(s1) + [p for p in rxy if p not in s1]
    print("spindle union: %d vertices (= 2*%d - %d)" % (len(union), len(xy), len(overlap)))
    # closing distance |P - rP| must be exactly 1
    Pxy = lat_to_xy(P)
    rP = rotate(Pxy, ct, st)
    assert d2(Pxy, rP) == K.ONE, "closing edge is not unit length!"
    print("closing edge |P - rP| = 1 exactly")
    # exact unit edges over the union (float prefilter)
    fl = [(K.to_float(x), K.to_float(y)) for (x, y) in union]
    edges = []
    n = len(union)
    for i in range(n):
        for j in range(i + 1, n):
            dd = (fl[i][0] - fl[j][0]) ** 2 + (fl[i][1] - fl[j][1]) ** 2
            if abs(dd - 1.0) < 1e-9 and d2(union[i], union[j]) == K.ONE:
                edges.append((i, j))
    print("union: %d exact unit edges" % len(edges))
    cls = build_cnf(n, edges, [])
    with tempfile.TemporaryDirectory() as td:
        cnf = os.path.join(td, "f.cnf")
        proof = os.path.join(td, "f.drat")
        write_cnf(cls, 4 * n, cnf)
        r = subprocess.run([KISSAT, "-q", cnf, proof], capture_output=True, text=True)
        print("kissat:", {10: "SAT", 20: "UNSAT"}.get(r.returncode, r.returncode))
        if r.returncode == 20:
            r2 = subprocess.run([DRAT, cnf, proof], capture_output=True, text=True)
            print("drat-trim:", "s VERIFIED" if "s VERIFIED" in r2.stdout
                  else r2.stdout[-300:])
            with open("spindle_union.pkl", "wb") as f:
                pickle.dump({"points": union, "edges": edges,
                             "primes": K.primes}, f)
            print("saved spindle_union.pkl (%d-vertex 5-chromatic UDG)" % n)


if __name__ == "__main__":
    main(sys.argv[1])
