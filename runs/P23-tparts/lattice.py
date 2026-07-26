# Provenance: copied from origin/runs/P23-parts-gadgets:runs/P23-parts-gadgets/lattice.py
"""Exact arithmetic for Parts' base lattice (arXiv:2010.12665).

A point is a 4-tuple of Fractions (p,q,r,s) representing the complex number
    z = p + q*sqrt(33) + i*(r*sqrt(3) + s*sqrt(11)).
Parts' integer coordinates (a,b,c,d) with z = (a + b sqrt33 + i(c sqrt3 + d sqrt11))/12
correspond to (p,q,r,s) = (a/12, b/12, c/12, d/12), with the lattice condition
a-b+c+d = 0 mod 4.

Squared modulus:
    |z|^2 = (p^2 + 33 q^2 + 3 r^2 + 11 s^2) + 2*sqrt(33)*(p*q + r*s).
Since sqrt(33) is irrational, |z|^2 is rational iff pq + rs = 0, and for integer
tuples (a,b,c,d) two lattice points are at unit distance iff their difference
satisfies  a^2 + 33 b^2 + 3 c^2 + 11 d^2 = 144  AND  a*b + c*d = 0.
(Derivation: |z|^2 = [(a^2+33b^2+3c^2+11d^2) + 2 sqrt33 (ab+cd)]/144.)

All decisions are exact; floats are used only as an optional prefilter.
"""
from fractions import Fraction
from itertools import product

F = Fraction


def add(u, v):
    return (u[0] + v[0], u[1] + v[1], u[2] + v[2], u[3] + v[3])


def sub(u, v):
    return (u[0] - v[0], u[1] - v[1], u[2] - v[2], u[3] - v[3])


def neg(u):
    return (-u[0], -u[1], -u[2], -u[3])


def mul(u, v):
    """Exact complex multiplication in the basis (1, sqrt33, i sqrt3, i sqrt11).

    (p+q s33 + i r s3 + i s s11)(p'+q' s33 + i r' s3 + i s' s11):
      const :  pp' + 33qq' - 3rr' - 11ss'
      s33   :  pq' + qp' - rs' - sr'
      i s3  :  pr' + rp' + 11(qs' + sq')
      i s11 :  ps' + sp' + 3(qr' + rq')
    """
    p, q, r, s = u
    P, Q, R, S = v
    return (
        p * P + 33 * q * Q - 3 * r * R - 11 * s * S,
        p * Q + q * P - r * S - s * R,
        p * R + r * P + 11 * (q * S + s * Q),
        p * S + s * P + 3 * (q * R + r * Q),
    )


def conj(u):
    return (u[0], u[1], -u[2], -u[3])


def norm2(u):
    """|u|^2, exact. Returns (rational_part, sqrt33_part); modulus is rational
    iff the second component is 0."""
    p, q, r, s = u
    return (p * p + 33 * q * q + 3 * r * r + 11 * s * s, p * q + r * s)


def dist2(u, v):
    return norm2(sub(u, v))


def is_dist2(u, v, target):
    """Exact check |u-v|^2 == target (a Fraction/int)."""
    a, b = dist2(u, v)
    return b == 0 and a == target


def scale(u, c):
    """Multiply by a rational scalar c."""
    return (u[0] * c, u[1] * c, u[2] * c, u[3] * c)


def to_float(u):
    p, q, r, s = u
    return (float(p) + float(q) * 33 ** 0.5, float(r) * 3 ** 0.5 + float(s) * 11 ** 0.5)


# --- Parts lattice specifics -------------------------------------------------

# eta = (sqrt33 + i sqrt3)/6, |eta| = 1, eta^2 = 5/6 + i sqrt11/6
ETA = (F(0), F(1, 6), F(1, 6), F(0))
ETA_INV = conj(ETA)  # |eta|=1 so inverse is conjugate

# rho = 7/8 + i sqrt15/8 is NOT in this field (sqrt15, sqrt5); type-M rotation
# is handled elsewhere. Ring rotations available here: powers of eta and the
# 6th roots of unity  w6 = 1/2 + i sqrt3/2.
W6 = (F(1, 2), F(0), F(1, 2), F(0))

# 7-vertex hexagonal wheel H (unit hexagon + center), in Parts' integer coords /12:
# {(0,0,0,0), (+-12,0,0,0), (+-6,0,+-6,0)}
H_INT = [
    (0, 0, 0, 0),
    (12, 0, 0, 0), (-12, 0, 0, 0),
    (6, 0, 6, 0), (6, 0, -6, 0), (-6, 0, 6, 0), (-6, 0, -6, 0),
]


def int_to_frac(t):
    return (F(t[0], 12), F(t[1], 12), F(t[2], 12), F(t[3], 12))


def frac_to_int(u):
    """Return Parts integer tuple (a,b,c,d) = 12*u if integral, else None."""
    out = []
    for x in u:
        y = 12 * x
        if y.denominator != 1:
            return None
        out.append(int(y))
    return tuple(out)


H = [int_to_frac(t) for t in H_INT]


def rot(points, m):
    """Multiply all points by eta^m (m may be negative)."""
    r = ETA if m >= 0 else ETA_INV
    out = list(points)
    for _ in range(abs(m)):
        out = [mul(p, r) for p in out]
    return out


def Hm(m):
    """H^m = union_{alpha=-m..m} eta^alpha H (deduped)."""
    seen = {}
    for a in range(-m, m + 1):
        for p in rot(H, a):
            seen[p] = True
    return list(seen)


def minkowski(A, B):
    seen = {}
    for a in A:
        for b in B:
            seen[add(a, b)] = True
    return list(seen)


def unit_edges(points):
    """All unit-distance pairs (indices), exact. Float prefilter + exact check."""
    import math
    pts = list(points)
    n = len(pts)
    fl = [to_float(p) for p in pts]
    edges = []
    # grid prefilter
    cell = {}
    for i, (x, y) in enumerate(fl):
        cell.setdefault((int(x // 1), int(y // 1)), []).append(i)
    for (cx, cy), idxs in cell.items():
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                other = cell.get((cx + dx, cy + dy))
                if not other:
                    continue
                for i in idxs:
                    xi, yi = fl[i]
                    for j in other:
                        if j <= i:
                            continue
                        xj, yj = fl[j]
                        d2 = (xi - xj) ** 2 + (yi - yj) ** 2
                        if abs(d2 - 1.0) < 1e-9 and is_dist2(pts[i], pts[j], 1):
                            edges.append((i, j))
    return edges


def pairs_at_dist2(points, target):
    """All pairs (i,j) with exact |pi-pj|^2 == target (Fraction)."""
    pts = list(points)
    tf = float(target)
    fl = [to_float(p) for p in pts]
    out = []
    n = len(pts)
    for i in range(n):
        xi, yi = fl[i]
        for j in range(i + 1, n):
            xj, yj = fl[j]
            d2 = (xi - xj) ** 2 + (yi - yj) ** 2
            if abs(d2 - tf) < 1e-9 and is_dist2(pts[i], pts[j], target):
                out.append((i, j))
    return out


# --- base-orbit machinery (Parts' tau transforms, on integer tuples) --------

def tau1(t):
    a, b, c, d = t
    return ((-a - 3 * c) // 2, (-b - d) // 2, (a - c) // 2, (3 * b - d) // 2)


def tau2(t):
    a, b, c, d = t
    return ((-a + 3 * c) // 2, (-b + d) // 2, (-a - c) // 2, (-3 * b - d) // 2)


def tau3(t):
    a, b, c, d = t
    return (-a, -b, c, d)


def tau4(t):
    a, b, c, d = t
    return (a, b, -c, -d)


def tau5(t):
    a, b, c, d = t
    return (a, -b, c, -d)


def orbit(t):
    """Full symmetry orbit (order <= 24) of an integer tuple."""
    seen = {t}
    frontier = [t]
    while frontier:
        nxt = []
        for u in frontier:
            for f in (tau1, tau2, tau3, tau4, tau5):
                v = f(u)
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        frontier = nxt
    return sorted(seen)


if __name__ == "__main__":
    # sanity checks
    assert norm2(ETA) == (1, 0)
    e2 = mul(ETA, ETA)
    assert e2 == (F(5, 6), F(0), F(0), F(1, 6)), e2  # eta^2 = 5/6 + i sqrt11/6
    h1 = Hm(1)
    h2 = Hm(2)
    assert len(h1) == 19, len(h1)   # 3 wheels sharing center: 1 + 6*3 = 19
    assert len(h2) == 31, len(h2)   # V31
    e31 = unit_edges(h2)
    print("H^2:", len(h2), "vertices,", len(e31), "unit edges")
    # all H^2 points are integral in Parts coords
    assert all(frac_to_int(p) is not None for p in h2)
    # lattice congruence a-b+c+d = 0 mod 4
    assert all(sum(frac_to_int(p)[k] * (1, -1, 1, 1)[k] for k in range(4)) % 4 == 0 for p in h2)
    print("sanity OK")
