#!/usr/bin/env python3
"""Independent exact verifier for P17 (WoW 20 & 21), no floats on the
accept path.

For each test graph G it certifies, with exact arithmetic only:
  (a) n+(G) <= S and n-(G) <= S, where S = sum of positive adjacency
      eigenvalues, via Sturm root counting (with multiplicity through
      square-free factorization) and rational isolation intervals for a
      certified rational lower bound on S;
  (b) the inertia-bound link n - alpha(G) >= max{n+, n-} with alpha computed
      exactly by branch and bound.
Prints PASS if every graph satisfies both, FAIL otherwise.

This is a *consequence checker* for the Kumar-Pragada theorem
(arXiv:2607.19817) on a finite corpus; the theorem itself is a general
proof, verified by hand and spot-checked in runs/P17/v1.
"""
import itertools
import sympy as sp

x = sp.Symbol('x')

def inertia_and_S_cert(A, n):
    """Return (npos, nneg, cert) where cert(c) certifies exactly whether
    S >= c for integer c, with S = sum of positive roots of charpoly."""
    poly = sp.Poly(sp.Matrix(A).charpoly(x).as_expr(), x)
    npos = nneg = 0
    factors = poly.factor_list()[1]
    for fac, mult in factors:
        fp = sp.Poly(fac, x)
        if fp.degree() == 1 and fp.nth(0) == 0:
            continue  # factor x: zero eigenvalues (count_roots includes endpoints)
        npos += mult * fp.count_roots(0, sp.oo)
        nneg += mult * fp.count_roots(-sp.oo, 0)

    def cert(c):
        # exact fast path: all positive roots rational (from linear factors)
        nonlin_pos = sum(mult * sp.Poly(fac, x).count_roots(0, sp.oo)
                         for fac, mult in factors if sp.Poly(fac, x).degree() > 1)
        if nonlin_pos == 0:
            S = sp.Integer(0)
            for fac, mult in factors:
                fp = sp.Poly(fac, x)
                if fp.degree() == 1:
                    r = sp.Rational(-fp.nth(0), fp.nth(1))
                    if r > 0:
                        S += mult * r
            return S >= c
        for k in range(6, 120, 6):
            dx = sp.Rational(1, 10 ** k)
            lo = sp.Integer(0); hi = sp.Integer(0); ok = True
            for (a, b), mult in poly.intervals(eps=dx, sqf=False):
                if b <= 0 or a == b == 0:
                    continue
                if a <= 0:
                    ok = False; break
                lo += mult * a; hi += mult * b
            if not ok:
                continue
            if lo >= c:
                return True
            if hi < c:
                return False
        raise RuntimeError("undecided: S vs %s" % c)
    return npos, nneg, cert

def alpha_exact(adj, n):
    best = 0
    def bb(cand, cur):
        nonlocal best
        if cur + len(cand) <= best:
            return
        if not cand:
            best = max(best, cur); return
        v = cand[0]
        bb([u for u in cand[1:] if not adj[v][u]], cur + 1)
        bb(cand[1:], cur)
    bb(list(range(n)), 0)
    return best

def graphs():
    # equality cases and structured corpus
    def from_edges(n, E):
        A = [[0] * n for _ in range(n)]
        for i, j in E:
            A[i][j] = A[j][i] = 1
        return n, A
    yield from_edges(8, [(0, 1), (2, 3), (4, 5), (6, 7)])          # matching
    yield from_edges(6, [(0,1),(0,2),(1,2),(3,4),(3,5),(4,5)])     # 2K3
    yield from_edges(5, [(0,1),(1,2),(2,3),(3,4),(4,0)])           # C5
    yield from_edges(10, [(i, j) for i in range(5) for j in range(i+1, 5)]
                        + [(i+5, j+5) for i in range(5) for j in range(i+1, 5) if True]
                        + [(0, 5)])                                # 2K5+bridge
    # all graphs on 5 vertices
    pairs = list(itertools.combinations(range(5), 2))
    for mask in range(1 << len(pairs)):
        E = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
        yield from_edges(5, E)

def main():
    bad = 0
    for n, A in graphs():
        npos, nneg, cert = inertia_and_S_cert(A, n)
        al = alpha_exact(A, n)
        m = max(npos, nneg)
        ok_a = cert(m)          # WoW 20 & 21: max{n+, n-} <= S, exact
        ok_b = (n - al) >= m    # Cvetkovic inertia bound consequence
        if not (ok_a and ok_b):
            print("FAIL candidate:", n, npos, nneg, al, ok_a, ok_b)
            bad += 1
    print("PASS" if bad == 0 else f"FAIL ({bad})")

if __name__ == '__main__':
    main()
