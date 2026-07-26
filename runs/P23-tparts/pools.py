# Provenance: copied from origin/runs/P23-parts-gadgets:runs/P23-parts-gadgets/pools.py
"""Base-graph pools and gadget placements on Parts' lattice."""
from fractions import Fraction as F
from itertools import product
import sys

from lattice import (H, Hm, minkowski, unit_edges, add, sub, mul, neg, norm2,
                     to_float, frac_to_int, int_to_frac, tau1, orbit, is_dist2)


def oplus(n, m):
    """(+)^n H^m"""
    g = Hm(m)
    base = Hm(m)
    for _ in range(n - 1):
        g = minkowski(g, base)
    return g


def clip(points, r2max, center=None):
    """Keep points with |z - center|^2 <= r2max exactly (rational part; sqrt33
    part bounded via float check then exact compare)."""
    out = []
    fr = float(r2max)
    if center is None:
        center = (F(0), F(0), F(0), F(0))
    cx, cy = to_float(center)
    for p in points:
        x, y = to_float(p)
        x -= cx
        y -= cy
        if x * x + y * y <= fr + 1e-9:
            a, b = norm2(sub(p, center))
            # |z|^2 = a + b*sqrt33 ; compare exactly: a + b*sqrt33 <= r2max
            # <=> b*sqrt33 <= r2max - a ; square carefully by sign
            rhs = r2max - a
            if b == 0:
                if a <= r2max:
                    out.append(p)
            elif b > 0:
                if rhs > 0 and 33 * b * b <= rhs * rhs:
                    out.append(p)
            else:
                if rhs >= 0 or 33 * b * b >= rhs * rhs:
                    out.append(p)
    return out


def find_radius_points(r2, bound=40):
    """Integer tuples (a,b,c,d), a-b+c+d=0 mod 4, with |z|^2 == r2 (Fraction).
    Searches |a|,... <= bound with a^2+33b^2+3c^2+11d^2 = 144*r2, ab+cd=0."""
    target = 144 * r2
    assert target.denominator == 1
    target = int(target)
    out = []
    for b in range(-bound // 5, bound // 5 + 1):
        rb = target - 33 * b * b
        if rb < 0:
            continue
        for d in range(-bound // 3, bound // 3 + 1):
            rd = rb - 11 * d * d
            if rd < 0:
                continue
            for c in range(-bound // 1, bound + 1):
                rc = rd - 3 * c * c
                if rc < 0:
                    continue
                a2 = rc
                a = int(round(a2 ** 0.5))
                for aa in (a, -a):
                    if aa * aa == a2 and aa * b + c * d == 0 and (aa - b + c + d) % 4 == 0:
                        out.append((aa, b, c, d))
                    if a == 0:
                        break
    return sorted(set(out))


def equilateral_triples(r2):
    """Centered equilateral triples: point t with |t|^2==r2 such that tau1(t)
    is a lattice point; triple = (t, tau1 t, tau1^2 t), side^2 = 3 r2."""
    triples = []
    for t in find_radius_points(r2):
        a, b, c, d = t
        if (a + 3 * c) % 2 or (b + d) % 2 or (a - c) % 2 or (3 * b - d) % 2:
            continue
        t2 = tau1(t)
        t3 = tau1(t2)
        p1, p2, p3 = int_to_frac(t), int_to_frac(t2), int_to_frac(t3)
        s2 = 3 * r2
        if is_dist2(p1, p2, s2) and is_dist2(p2, p3, s2) and is_dist2(p1, p3, s2):
            triples.append((t, t2, t3))
    return triples


def axis_pair(d):
    """Pair (+-d/2, 0) as lattice tuples if representable: a = 6d must be
    integral -> use tuple (6d,0,0,0). Returns None if not lattice-valid."""
    a = F(6) * d
    if a.denominator != 1:
        return None
    a = int(a)
    if (a - 0 + 0 + 0) % 4 != 0:
        return None
    return ((a, 0, 0, 0), (-a, 0, 0, 0))


def vert_pair(d):
    """Pair (0, +-d/2) with imaginary part c*sqrt3/12: c = 6d/sqrt3 -> c=2d*sqrt3... 
    use c such that (c sqrt3)/12 = d/2  =>  c = 2 sqrt3 d -> only if d = k/sqrt3.
    Instead accept d^2 rational with d = c*sqrt3/6: c = sqrt(12 d^2)/... 
    Direct: need integer c with 3 c^2 = 36 d^2  (i.e. c^2 = 12 d^2)."""
    c2 = 12 * d * d
    if c2.denominator != 1:
        return None
    c = int(round(int(c2) ** 0.5))
    if c * c != c2:
        return None
    if (c % 4) != 0 and ((0 - 0 + c + 0) % 4) != 0:
        return None
    return ((0, 0, c, 0), (0, 0, -c, 0))


def build_pool(extra_pts, r2max, n=2, m=2, degmin=None, center=None):
    """Pool = clip((+)^n H^m, r2max) union extra points; exact unit edges.
    Returns (points, edges, ids of extra_pts)."""
    pool = clip(oplus(n, m), r2max, center=center)
    seen = {p: i for i, p in enumerate(pool)}
    for p in extra_pts:
        if p not in seen:
            seen[p] = len(pool)
            pool.append(p)
    edges = unit_edges(pool)
    if degmin:
        keep = set(seen[p] for p in extra_pts)
        pts, edges = iter_degfilter(pool, edges, degmin, keep)
        seen = {p: i for i, p in enumerate(pts)}
        pool = pts
    return pool, edges, [seen[p] for p in extra_pts]


def iter_degfilter(points, edges, degmin, keep):
    """Iteratively remove vertices with degree < degmin (never in keep)."""
    import collections
    pts = list(points)
    while True:
        deg = collections.Counter()
        for a, b in edges:
            deg[a] += 1
            deg[b] += 1
        drop = [i for i in range(len(pts)) if deg[i] < degmin and i not in keep]
        if not drop:
            return pts, edges
        alive = set(range(len(pts))) - set(drop)
        order = sorted(alive)
        idx = {v: i for i, v in enumerate(order)}
        keep = {idx[v] for v in keep}
        edges = [(idx[a], idx[b]) for a, b in edges if a in idx and b in idx]
        pts = [pts[v] for v in order]


if __name__ == "__main__":
    for (n, m) in [(2, 1), (2, 2), (3, 1), (3, 2)]:
        g = oplus(n, m)
        print("oplus^%d H^%d: %d vertices" % (n, m, len(g)))
