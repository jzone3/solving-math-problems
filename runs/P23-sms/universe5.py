"""Richer universe over Q(sqrt3,sqrt5,sqrt11): the Moser-ball direction set
(hexagonal omega + Moser rotation rho = 5/6+sqrt11/6 i) AUGMENTED with a sqrt5
unit rotation sigma = (1+2i)/sqrt5 = sqrt5/5 + 2 sqrt5/5 i (angle arctan 2, an
irrational multiple of pi) and its conjugate, so the universe reaches genuinely
new sqrt5 geometry (the extra generator in Parts' field beyond the Moser ball).

Same exact-arithmetic pipeline as universe.py; just more generators / bigger field.
"""
import sys, pickle, math
from fractions import Fraction as F
from mfield import MField
import universe as U  # reuse compute_edges / build_ball


def build_field():
    return MField((3, 5, 11))  # basis masks: 0:1 1:s3 2:s5 3:s15 4:s11 5:s33 6:s55 7:s165


def directions(fld):
    def el(*pairs):
        v = [F(0)] * fld.N
        for m, c in pairs:
            v[m] = F(c)
        return tuple(v)

    def cmul(a, b):
        ax, ay = a; bx, by = b
        return (fld.sub(fld.mul(ax, bx), fld.mul(ay, by)),
                fld.add(fld.mul(ax, by), fld.mul(ay, bx)))

    one, zero = fld.ONE, fld.ZERO
    omega = (el((0, F(1, 2))), el((1, F(1, 2))))            # 1/2 + s3/2 i
    rho = (el((0, F(5, 6))), el((4, F(1, 6))))             # 5/6 + s11/6 i
    rhob = (el((0, F(5, 6))), el((4, F(-1, 6))))
    sig = (el((2, F(1, 5))), el((2, F(2, 5))))             # s5/5 + 2 s5/5 i = (1+2i)/s5
    sigb = (el((2, F(1, 5))), el((2, F(-2, 5))))
    e0 = (one, zero)

    def orbit(seed):
        out, cur = [], seed
        for _ in range(6):
            out.append(cur); cur = cmul(cur, omega)
        return out

    dirs = []
    for s in (e0, rho, rhob, sig, sigb):
        dirs += orbit(s)
    seen, uniq = set(), []
    for d in dirs:
        if d not in seen:
            seen.add(d); uniq.append(d)
    for d in uniq:
        assert fld.add(fld.mul(d[0], d[0]), fld.mul(d[1], d[1])) == fld.ONE, d
    return uniq


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    out = sys.argv[2] if len(sys.argv) > 2 else f"U5_k{k}.pkl"
    fld = build_field()
    dirs = directions(fld)
    print(f"[universe5] primes=(3,5,11) |D|={len(dirs)} k={k}")
    pts = U.build_ball(fld, dirs, k)
    print(f"[universe5] |U_{k}| = {len(pts)} points")
    edges = U.compute_edges(fld, pts)
    print(f"[universe5] {len(edges)} exact unit edges "
          f"(avg deg {2*len(edges)/max(1,len(pts)):.2f})")
    with open(out, "wb") as f:
        pickle.dump({"points": pts, "edges": edges, "perms": [],
                     "primes": (3, 5, 11), "k": k}, f)
    print(f"[universe5] wrote {out}")


if __name__ == "__main__":
    main()
