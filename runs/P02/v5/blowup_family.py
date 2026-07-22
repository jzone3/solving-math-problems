#!/usr/bin/env python3
"""Infinite family of counterexamples: blow-ups G0(t) of the n=9 witness G0.

Lemma A (multiplication preserves the hypotheses): if G is maximal
triangle-free with delta(G) = n/3, then the blow-up G(t) (every vertex ->
t twins) is triangle-free, has diameter <= 2 (copies of the same or
non-adjacent vertices share a common neighbour inherited from G), hence is
maximal triangle-free, has n(G(t)) = tn and delta = t*delta(G) = n(G(t))/3.

Lemma B (infeasibility lifts): if G(t) had integers x'_w >= 1 with all
multiplied-neighbourhood sums equal, then X_v := sum of x' over the t
copies of v (X_v >= t >= 1) solves the system for G. So G infeasible =>
G(t) infeasible for all t >= 1.

This script machine-checks both lemmas' conclusions for t = 1..4
(n = 9, 18, 27, 36) directly, using the exact rational LP from search.py.
"""
from search import g6_to_adj, is_maximal_tf, check_graph

G0 = 'H?q`qjo'

def blowup(adj, t):
    n = len(adj)
    N = n * t
    return [[adj[i // t][j // t] for j in range(N)] for i in range(N)]

def main():
    n, adj = g6_to_adj(G0)
    for t in range(1, 5):
        A = blowup(adj, t)
        N = len(A)
        deg = [sum(r) for r in A]
        assert not any(A[i][j] and A[j][k] and A[i][k]
                       for i in range(N) for j in range(i + 1, N)
                       for k in range(j + 1, N)), "triangle!"
        assert is_maximal_tf(N, A), "not maximal"
        assert min(deg) * 3 == N, "delta != n/3"
        assert check_graph(N, A) is None, "unexpectedly feasible"
        print(f"t={t}: n={N}, delta={min(deg)}=n/3, maximal TF, system INFEASIBLE  OK")
    print("PASS: G0(t) is a counterexample for every checked t")

if __name__ == "__main__":
    main()
