"""P06 core invariants (WoW 129/698), matched to refutationGBR Rust code.

Conjecture 129: std_dev(Laplacian eigenvalues) <= Randic index R(G),
where std_dev uses the population convention (divide by n).

KEY IDENTITY (makes dev degree-only, no eigensolve needed):
  trace(L)   = sum(mu_i)   = 2m
  trace(L^2) = sum(mu_i^2) = sum_v d_v^2 + 2m
  dev^2 = (sum d^2 + 2m)/n - (2m/n)^2

So dev(G) depends only on the degree sequence; R(G) depends on which
degrees are adjacent.

Padding reduction: append k isolated vertices (dev changes, R doesn't).
With A = sum_v d_v(d_v+1) and m edges, dev^2(n) = A/n - 4m^2/n^2 is
maximized over real n at n* = 8m^2/A with max value A^2/(16 m^2).
Hence a padded counterexample to 129 exists iff some H satisfies
  A(H)^2/(16 m^2) > R(H)^2   i.e.   A(H) > 4 m R(H)
(up to integer rounding of n*, checked explicitly).
Equality holds exactly for H = K_t (A = t^2(t-1), 4mR = t^2(t-1));
K_t plus (t-2) isolated vertices gives dev = R = t/2 exactly.
"""

from fractions import Fraction
from mpmath import mp, mpf, sqrt as msqrt

mp.dps = 60


def degrees_from_edges(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d


def dev2_exact(n, degs):
    """Exact Fraction: dev^2 of Laplacian eigenvalues via trace identity."""
    m2 = sum(degs)              # 2m
    s2 = sum(d * d for d in degs)
    return Fraction(s2 + m2, n) - Fraction(m2 * m2, n * n)


def randic_mp(edges, degs):
    """High-precision Randic index."""
    tot = mpf(0)
    for u, v in edges:
        tot += 1 / msqrt(mpf(degs[u]) * degs[v])
    return tot


def score(n, edges):
    """dev - R (positive => counterexample to 129)."""
    degs = degrees_from_edges(n, edges)
    dev = msqrt(mpf(dev2_exact(n, degs).numerator) / dev2_exact(n, degs).denominator)
    return dev - randic_mp(edges, degs)


def padded_score(edges, nH):
    """A/(4m) - R : positive => padded counterexample candidate (before
    integer-n check). Uses exact Fraction for A/(4m)."""
    degs = degrees_from_edges(nH, edges)
    m = sum(degs) // 2
    if m == 0:
        return None
    A = sum(d * (d + 1) for d in degs)
    lhs = mpf(A) / (4 * m)
    return lhs - randic_mp(edges, degs)


def best_padded_dev2_minus_R2(edges, nH):
    """Given H, choose integer padding k>=0 maximizing dev^2 - R^2 of
    H + k*K1; return (best n, dev2 - R2 as mpf)."""
    degs = degrees_from_edges(nH, edges)
    m = sum(degs) // 2
    A = sum(d * (d + 1) for d in degs)
    if A == 0:
        return None
    R2 = randic_mp(edges, degs) ** 2
    nstar = 8 * m * m / A
    best = None
    for n in {max(nH, int(nstar)), max(nH, int(nstar) + 1), nH}:
        dev2 = mpf(A) / n - mpf(4 * m * m) / (n * n)
        val = dev2 - R2
        if best is None or val > best[1]:
            best = (n, val)
    return best
