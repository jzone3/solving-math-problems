#!/usr/bin/env python3
"""Standalone verifier for a counterexample to Graffiti (WoW) conjecture 143
(the sibling of conjecture 154, listed open in Roucairol-Cazenave 2025).

Conjecture 143: for every connected graph G,
    Var(positive adjacency eigenvalues) <= m / mu(D)
where Var is the population variance and mu(D) the average inter-vertex
distance.

Witness: dumbbell(20, 13, 7) = clique K_20 and clique K_7 joined by a path
with 13 edges (12 internal vertices) between one vertex of each clique.
n = 39, m = 224.

Rigor: the positive eigenvalues are algebraic numbers; we compute the
characteristic polynomial EXACTLY (integer coefficients, sympy), isolate its
real roots exactly (sympy real_roots -> CRootOf, certified isolating
intervals), take the strictly positive ones, and evaluate the variance to
40 significant digits. The violation margin (~0.08) exceeds the numerical
error (~1e-35) by >30 orders of magnitude. m and the distance sum S are
exact integers from BFS.

Both mu conventions are refuted:
  mu_pairs = S / C(n,2)  and  mu_full = S_ordered / n^2 (Roucairol-Cazenave
  Rust convention: mean of the full n x n distance matrix incl. diagonal).

Run: python3 verify143.py   (prints PASS; needs sympy + mpmath)
"""
from collections import deque
from fractions import Fraction

import mpmath as mp
import sympy as sp

A_CLQ, PATH, B_CLQ = 20, 13, 7


def build_dumbbell(a, l, b):
    n = a + b + l - 1
    adj = [set() for _ in range(n)]

    def add(x, y):
        adj[x].add(y)
        adj[y].add(x)

    for i in range(a):
        for j in range(i + 1, a):
            add(i, j)
    for i in range(b):
        for j in range(i + 1, b):
            add(a + l - 1 + i, a + l - 1 + j)
    chain = [0] + list(range(a, a + l - 1)) + [a + l - 1]
    for x, y in zip(chain, chain[1:]):
        add(x, y)
    return adj


def main():
    adj = build_dumbbell(A_CLQ, PATH, B_CLQ)
    n = len(adj)
    m = sum(len(s) for s in adj) // 2

    # exact ordered distance sum via BFS
    S_ord = 0
    for s0 in range(n):
        dist = [-1] * n
        dist[s0] = 0
        q = deque([s0])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        assert all(d >= 0 for d in dist), "not connected"
        S_ord += sum(dist)

    print(f"dumbbell({A_CLQ},{PATH},{B_CLQ}): n={n}, m={m}, S_ordered={S_ord}")

    # exact characteristic polynomial + certified real roots
    M = sp.zeros(n)
    for i, s in enumerate(adj):
        for j in s:
            M[i, j] = 1
    charpoly = M.charpoly()
    roots = charpoly.real_roots()
    assert len(roots) == n, "adjacency matrix must have n real eigenvalues"
    pos = [r for r in roots if r.is_positive]
    print(f"positive eigenvalues: {len(pos)}")

    mp.mp.dps = 50
    vals = [mp.mpf(str(sp.N(r, 45))) for r in pos]
    k = len(vals)
    mean = sum(vals) / k
    var = sum((v - mean) ** 2 for v in vals) / k

    bound_full = Fraction(m * n * n, S_ord)
    bound_pairs = Fraction(m * n * (n - 1), S_ord)
    print(f"Var(positive eigenvalues) = {mp.nstr(var, 20)}")
    print(f"m/mu_full  = {float(bound_full):.10f}")
    print(f"m/mu_pairs = {float(bound_pairs):.10f}")

    margin_full = var - mp.mpf(bound_full.numerator) / bound_full.denominator
    margin_pairs = var - mp.mpf(bound_pairs.numerator) / bound_pairs.denominator
    print(f"margins: full={mp.nstr(margin_full, 10)}, "
          f"pairs={mp.nstr(margin_pairs, 10)}")
    assert margin_full > mp.mpf("1e-20"), "no violation (full convention)"
    assert margin_pairs > mp.mpf("1e-20"), "no violation (pairs convention)"
    print("PASS: conjecture 143 (Var+ <= m/mu) is FALSE for this graph "
          "under both mu conventions")


if __name__ == "__main__":
    main()
