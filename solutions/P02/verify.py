#!/usr/bin/env python3
"""Standalone verifier for a counterexample to Brandt's regular-supergraph
conjecture AS STATED on Douglas West's open problem page
(https://dwest.web.illinois.edu/openp/regsup.html):

    "If G is a maximal triangle-free graph and has minimum degree at least
     n(G)/3, then G has a regular supergraph obtainable by vertex
     multiplications."

A vertex multiplication replaces each vertex v by an independent set of
x_v >= 1 copies, each copy inheriting the neighborhood of v (copies of
adjacent vertices are fully joined; copies of the same or non-adjacent
vertices are non-adjacent).  The resulting graph H contains G (take one
copy of each vertex), is triangle-free whenever G is, and the degree of any
copy of v equals sum_{u in N_G(v)} x_u.  Hence G has a regular triangle-free
supergraph obtained by vertex multiplications  IFF  there exist integers
x_v >= 1 and d with

    (*)   sum_{u in N(v)} x_u = d      for every vertex v.

WITNESS.  G0 below has n = 9 vertices, is triangle-free, is maximal
triangle-free, and has minimum degree 3 = n/3.  Yet (*) has no solution:
even over the rationals, any x with A x = d*(1,...,1)  forces  x_8 = 0.

CERTIFICATE.  y = (0, 1, 1, 0, -1, -1, -1, -1, 2)  satisfies
    sum_v y_v = 0        and        yT A = (0,0,0,0,0,0,0,0,2)  (>= 0, != 0).
Then for ANY solution of (*):  0 = d * sum_v y_v = yT (A x) = 2 * x_8,
so x_8 = 0, contradicting x_8 >= 1.  (Integer arithmetic only.)

This script independently re-checks every claim and prints PASS.
No dependencies beyond the Python 3 standard library.
"""

N = 9
EDGES = [(0, 4), (0, 5), (0, 8), (1, 4), (1, 7), (1, 8), (2, 5), (2, 6),
         (2, 8), (3, 6), (3, 7), (3, 8), (4, 6), (5, 7)]
# graph6: H?q`qjo
Y = [0, 1, 1, 0, -1, -1, -1, -1, 2]


def main():
    adj = [[0] * N for _ in range(N)]
    for i, j in EDGES:
        assert 0 <= i < j < N
        adj[i][j] = adj[j][i] = 1

    # 1. triangle-free
    for i in range(N):
        for j in range(i + 1, N):
            for k in range(j + 1, N):
                assert not (adj[i][j] and adj[j][k] and adj[i][k]), \
                    f"triangle {i},{j},{k}"
    print("triangle-free: OK")

    # 2. maximal triangle-free: every non-adjacent pair has a common
    #    neighbour (so adding any edge creates a triangle)
    for i in range(N):
        for j in range(i + 1, N):
            if adj[i][j]:
                continue
            assert any(adj[i][k] and adj[j][k] for k in range(N)), \
                f"edge {i}{j} addable without creating a triangle"
    print("maximal triangle-free: OK")

    # 3. minimum degree >= n/3
    deg = [sum(row) for row in adj]
    assert min(deg) * 3 >= N, f"min degree {min(deg)} < n/3"
    print(f"min degree {min(deg)} >= n/3 = {N}/3: OK")

    # 4. certificate: sum(Y) == 0, (Y^T A) >= 0 and != 0
    assert sum(Y) == 0, "certificate: sum(Y) != 0"
    z = [sum(Y[u] * adj[u][v] for u in range(N)) for v in range(N)]
    assert all(zi >= 0 for zi in z), f"certificate: Y^T A has negative entry {z}"
    assert any(zi > 0 for zi in z), "certificate: Y^T A is zero"
    print(f"certificate: sum(Y)=0, Y^T A = {z} >= 0, nonzero: OK")

    # Consequence (pure logic, restated): if x_v >= 1 integers satisfied
    # sum_{u in N(v)} x_u = d for all v, then
    #   0 = d * sum(Y) = Y^T (A x) = (Y^T A) x = sum_v z_v x_v >= max(z) >= 1,
    # a contradiction.  Hence no regular supergraph by vertex multiplications.

    # 5. belt-and-braces: exhaustive search over small multiplicities
    #    (not a proof, the certificate above is the proof; this just guards
    #    against a mis-typed certificate) — check no solution with x_v <= 4.
    import itertools
    for x in itertools.product(range(1, 5), repeat=N):
        s = [sum(x[u] for u in range(N) if adj[v][u]) for v in range(N)]
        assert len(set(s)) > 1, f"unexpected solution {x}"
    print("no solution with all x_v in 1..4 (sanity sweep): OK")

    print("PASS: G0 (n=9, delta=3=n/3, maximal triangle-free) admits NO "
          "regular supergraph obtainable by vertex multiplications.")


if __name__ == "__main__":
    main()
