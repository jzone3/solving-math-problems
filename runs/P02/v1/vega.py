#!/usr/bin/env python3
"""
Exact feasibility of the multiplication system {x > 0 : Ax = c*1} for the
Andrasfai graphs Gamma_i and all four Vega graph families Y^{mu,nu}_i
(definitions from Lamaison-Pehova-Reiher, "Strong Brandt-Thomasse Theorems",
arXiv:2406.10745, Section 4, Figure 4.1).

Motivation: by the Brandt-Thomasse theorem every maximal triangle-free graph
with delta > n/3 is a blow-up (vertex multiplication with positive classes,
up to taking the core) of an Andrasfai or Vega graph.  Hence verifying that
every Gamma_i and Y^{mu,nu}_i admits a positive rational solution of
Ax = c*1 verifies Brandt's Conjecture 4.1 for all graphs whose core is one of
these families -- for arbitrary n.

For each graph we check: triangle-free, maximal triangle-free, and
exact_max_t > 0 (rational simplex, no floats).
"""
import sys
from itertools import combinations
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from exactlp import exact_max_t


def andrasfai(i):
    """Gamma_i: Cayley graph on Z_{3i-1}, connection set {i,...,2i-1}."""
    n = 3 * i - 1
    adj = [0] * n
    for a in range(n):
        for d in range(i, 2 * i):
            b = (a + d) % n
            adj[a] |= 1 << b
            adj[b] |= 1 << a
    return n, adj


def vega(i, mu, nu):
    """Y^{mu nu}_i on 3i+7 - mu - nu vertices.
    Vertices 0..3i-2: Gamma_i.  red = 0..i-1, green = i..2i-1, blue = 2i..3i-2.
    Then hexagon a,v,c,u,b,w (cycle in this order) and x, y with edge xy,
    N(x) >= {a,b,c}, N(y) >= {u,v,w}; red = N(a) cap N(u),
    green = N(b) cap N(v), blue = N(c) cap N(w).
    mu = 1 deletes y; nu = 1 deletes vertex 2i-1 (a green Gamma vertex)."""
    ng = 3 * i - 1
    A, V, C, U, B, W, X, Y = (ng + k for k in range(8))
    n = ng + 8
    adj = [0] * n

    def add(p, q):
        adj[p] |= 1 << q
        adj[q] |= 1 << p

    _, gadj = andrasfai(i)
    for p in range(ng):
        adj[p] = gadj[p]
    for p, q in [(A, V), (V, C), (C, U), (U, B), (B, W), (W, A)]:
        add(p, q)
    for r in range(0, i):            # red
        add(r, A); add(r, U)
    for g in range(i, 2 * i):        # green
        add(g, B); add(g, V)
    for b in range(2 * i, 3 * i - 1):  # blue
        add(b, C); add(b, W)
    add(X, A); add(X, B); add(X, C)
    add(Y, U); add(Y, V); add(Y, W)
    add(X, Y)

    drop = []
    if mu:
        drop.append(Y)
    if nu:
        drop.append(2 * i - 1)
    keep = [v for v in range(n) if v not in drop]
    idx = {v: k for k, v in enumerate(keep)}
    m = len(keep)
    nadj = [0] * m
    for v in keep:
        for u in keep:
            if adj[v] >> u & 1:
                nadj[idx[v]] |= 1 << idx[u]
    return m, nadj


def check_mtf(n, adj):
    for u, v in combinations(range(n), 2):
        if adj[u] >> v & 1:
            assert not (adj[u] & adj[v]), (u, v, 'triangle')
        else:
            assert adj[u] & adj[v], (u, v, 'not maximal')


def main():
    imax = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    for i in range(2, imax + 1):
        n, adj = andrasfai(i)
        check_mtf(n, adj)
        t = exact_max_t(n, adj)
        assert t > 0, ('Gamma', i)
        print(f'Gamma_{i} (n={n}): MTF ok, max_t = {t} > 0', flush=True)
        for mu in (0, 1):
            for nu in (0, 1):
                m, vadj = vega(i, mu, nu)
                check_mtf(m, vadj)
                t = exact_max_t(m, vadj)
                assert t > 0, ('Vega', i, mu, nu, t)
                print(f'Vega_{i}^{mu}{nu} (n={m}): MTF ok, max_t = {t} > 0',
                      flush=True)


if __name__ == '__main__':
    main()
