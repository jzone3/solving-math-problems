"""Exact/high-precision Laplacian spectra toolkit for structured graph families.

A graph-with-spectrum is represented as a Spec object:
  n      : number of vertices
  m      : number of edges (exact int or Fraction)
  eigs   : list of (value, multiplicity) pairs, values are sympy-exact or Fraction/int.

Key closed forms used:
  * Join G v H:  L-spectrum = {0} u {mu_i(G)+nH : mu_i over nonzero-index eigs of G}
                 u {mu_j(H)+nG} u {nG+nH}   (standard result; removes one 0 from each,
                 adds nG+nH).
  * Complement: nonzero part maps mu -> n - mu; multiplicity of 0 adjusts by components.
    For a connected complement: spectrum(Gc) = {0} u {n - mu_i : mu_i over the n-1
    smallest-index... } -- we implement via: multiset of L(G) eigenvalues without one 0,
    mapped mu -> n-mu, plus a 0.
  * k-regular graph: L = kI - A, so L-eigs = k - A-eigs.
  * Kneser K(n,k): A-eigenvalues (-1)^i * C(n-k-i, k-i), multiplicity C(n,i)-C(n,i-1),
    degree C(n-k,k).
  * Threshold graph with degree sequence d: L-eigs = conjugate partition d* (Merris/Kelmans).
  * Complete multipartite K(a1..ap) = join of empty graphs.
"""

from fractions import Fraction
from math import comb


class Spec:
    __slots__ = ("n", "m", "eigs")

    def __init__(self, n, m, eigs):
        self.n = n
        self.m = m
        # normalize: merge equal values
        d = {}
        for v, mult in eigs:
            d[v] = d.get(v, 0) + mult
        self.eigs = sorted(d.items(), key=lambda x: -x[0])
        assert sum(mu for _, mu in self.eigs) == n, (n, self.eigs)

    def sorted_desc(self):
        return self.eigs  # already sorted descending

    def check_sum(self):
        s = sum(v * mult for v, mult in self.eigs)
        assert s == 2 * self.m, (s, self.m)


def empty_graph(n):
    return Spec(n, 0, [(Fraction(0), n)])


def complete_graph(n):
    if n == 1:
        return empty_graph(1)
    return Spec(n, n * (n - 1) // 2, [(Fraction(n), n - 1), (Fraction(0), 1)])


def path_graph_numeric(n):
    # numeric only (2-2cos(pi k / n)); handled in numeric pipeline instead
    raise NotImplementedError


def cycle_graph_exact(n):
    """Only exact for n in {3,4,6}; otherwise use numeric pipeline."""
    raise NotImplementedError


def join(a: Spec, b: Spec) -> Spec:
    nA, nB = a.n, b.n
    eigs = []
    # remove one zero from each spectrum
    def shifted(spec, shift):
        out = []
        zero_removed = False
        for v, mult in spec.eigs:
            if v == 0 and not zero_removed:
                mult -= 1
                zero_removed = True
            if mult > 0:
                out.append((v + shift, mult))
        assert zero_removed, "graph Laplacian must contain eigenvalue 0"
        return out

    eigs += shifted(a, Fraction(nB))
    eigs += shifted(b, Fraction(nA))
    eigs.append((Fraction(nA + nB), 1))
    eigs.append((Fraction(0), 1))
    m = a.m + b.m + nA * nB
    return Spec(nA + nB, m, eigs)


def complement(a: Spec) -> Spec:
    """Correct multiset identity: L(G) + L(Gc) = nI - J. Nonzero eigenvectors (orthogonal
    to all-ones) map mu -> n - mu; the all-ones vector stays eigenvalue 0 for both."""
    n = a.n
    eigs = []
    zero_removed = False
    for v, mult in a.eigs:
        if v == 0 and not zero_removed:
            mult -= 1
            zero_removed = True
        if mult > 0:
            eigs.append((Fraction(n) - v, mult))
    eigs.append((Fraction(0), 1))
    m = n * (n - 1) // 2 - a.m
    return Spec(n, m, eigs)


def regular_from_adj(n, degree, adj_eigs):
    """adj_eigs: list of (value, mult) for adjacency spectrum including degree."""
    eigs = [(Fraction(degree) - v, mult) for v, mult in adj_eigs]
    m = n * degree // 2
    return Spec(n, m, eigs)


def kneser(nn, k):
    n = comb(nn, k)
    deg = comb(nn - k, k)
    adj = []
    for i in range(k + 1):
        val = Fraction((-1) ** i * comb(nn - k - i, k - i))
        mult = comb(nn, i) - (comb(nn, i - 1) if i >= 1 else 0)
        adj.append((val, mult))
    return regular_from_adj(n, deg, adj)


def johnson(nn, k):
    n = comb(nn, k)
    deg = k * (nn - k)
    adj = []
    for j in range(k + 1):
        val = Fraction((k - j) * (nn - k - j) - j)
        mult = comb(nn, j) - (comb(nn, j - 1) if j >= 1 else 0)
        adj.append((val, mult))
    return regular_from_adj(n, deg, adj)


def hamming(d, q):
    n = q ** d
    deg = d * (q - 1)
    adj = []
    for i in range(d + 1):
        val = Fraction((q - 1) * (d - i) - i)  # = (q-1)d - qi
        mult = comb(d, i) * (q - 1) ** i
        adj.append((val, mult))
    return regular_from_adj(n, deg, adj)


def complete_multipartite(parts):
    s = empty_graph(parts[0])
    for p in parts[1:]:
        s = join(s, empty_graph(p))
    return s


def threshold_graph(creation_seq):
    """creation_seq: iterable of 0/1; start with single vertex; 1 = dominating vertex
    (join with K1), 0 = isolated vertex (disjoint union with K1)."""
    s = empty_graph(1)
    for b in creation_seq:
        if b:
            s = join(s, empty_graph(1))
        else:
            s = disjoint_union(s, empty_graph(1))
    return s


def disjoint_union(a: Spec, b: Spec) -> Spec:
    return Spec(a.n + b.n, a.m + b.m, list(a.eigs) + list(b.eigs))


def incidence_biregular(v_pts, b_blocks, r, k, lam):
    """Incidence graph of a 2-(v,k,lambda) design: bipartite (v,b), point-degree r,
    block-degree k. Adjacency eigenvalues: +-sqrt(rk) (mult 1 each),
    +-sqrt(r-lam) (mult v-1 each), 0 (mult b-v if b>v).
    Laplacian is NOT k - A here (biregular), so we use the singular-value identity:
    For biregular bipartite graph with degrees (r on one side, k on other) and
    B the incidence matrix, L eigenvalues are (r+k)/2 +- sqrt(((r-k)/2)^2 + sigma^2)?
    -- that identity is false in general; only valid relation is via normalized Laplacian.
    So we DON'T use closed form here; numeric pipeline handles incidence graphs.
    """
    raise NotImplementedError


def brouwer_deficits(spec: Spec):
    """Return list of (t, deficit) where deficit = m + t(t+1)/2 - S_t (exact).
    Negative deficit at any t = counterexample."""
    out = []
    t = 0
    S = Fraction(0)
    for v, mult in spec.eigs:
        for _ in range(mult):
            t += 1
            S += v
            out.append((t, spec.m + Fraction(t * (t + 1), 2) - S))
    return out


def worst(spec: Spec):
    """Return (min deficit, argmin t) by full scan."""
    ds = brouwer_deficits(spec)
    best = min(ds, key=lambda x: x[1])
    return best[1], best[0]


def worst_fast(spec: Spec):
    """Block-wise minimization: within a block of constant eigenvalue v spanning
    t in [t0+1, t0+mult], deficit(t) = m + t(t+1)/2 - S0 - v*(t - t0) is a convex
    quadratic in t; its unconstrained minimizer is t* = v - 1/2, so the block min is
    at t clipped to {t0+1, floor(t*), ceil(t*), t0+mult}. Exact arithmetic throughout.
    Handles huge-multiplicity spectra (e.g. Kneser) in O(#distinct eigenvalues)."""
    m = spec.m
    S0 = Fraction(0)
    t0 = 0
    best_d, best_t = None, None
    for v, mult in spec.eigs:
        cands = {t0 + 1, t0 + mult}
        # unconstrained minimizer of f(t) = t(t+1)/2 - v t  =>  t* = v - 1/2
        import math
        tstar = v - Fraction(1, 2)
        for tt in (math.floor(tstar), math.ceil(tstar)):
            if t0 + 1 <= tt <= t0 + mult:
                cands.add(tt)
        for t in cands:
            d = m + Fraction(t * (t + 1), 2) - (S0 + v * (t - t0))
            if best_d is None or d < best_d:
                best_d, best_t = d, t
        S0 += v * mult
        t0 += mult
    return best_d, best_t
