#!/usr/bin/env python3
"""Standalone verifier for a counterexample to Graffiti (WoW) conjecture 154.

Conjecture 154: for every connected graph G,
    stdev(adjacency eigenvalues) <= n / mu(D)
where mu(D) is the average inter-vertex distance.

Since trace(A) = 0 and sum(lambda_i^2) = trace(A^2) = 2m, the population
standard deviation of the adjacency spectrum is EXACTLY sqrt(2m/n).
So the conjecture is equivalent to  2*m*mu^2 <= n^3, checkable in exact
integer arithmetic (no eigensolver, no floats needed).

Witness: lollipop graph L(50, 70) = clique K_50 with a path of 70 edges
attached to one clique vertex.  n = 120, m = 1295, sum of pairwise
distances S = 186060.

Both conventions for mu are refuted:
  mu_pairs = S / C(n,2)      -> violation iff 2*m*S^2 > n^3 * C(n,2)^2
  mu_full  = 2S / n^2        -> violation iff 8*m*S^2 > n^7
(mu_full is the convention in the Roucairol-Cazenave 2025 Rust code, which
averages the full n x n distance matrix including the zero diagonal.)

Run: python3 verify.py   (prints PASS on success; pure stdlib)
"""
from collections import deque
from math import comb, sqrt

CLIQUE = 50
PATH = 70


def build_lollipop(a, l):
    n = a + l
    adj = [set() for _ in range(n)]
    for i in range(a):
        for j in range(i + 1, a):
            adj[i].add(j)
            adj[j].add(i)
    # path attached to clique vertex 0: 0 - a - a+1 - ... - a+l-1
    chain = [0] + list(range(a, n))
    for x, y in zip(chain, chain[1:]):
        adj[x].add(y)
        adj[y].add(x)
    return adj


def main():
    adj = build_lollipop(CLIQUE, PATH)
    n = len(adj)
    m = sum(len(s) for s in adj) // 2

    # all-pairs BFS: connectivity + exact sum of pairwise distances
    twice_S = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        assert all(d >= 0 for d in dist), "graph not connected"
        twice_S += sum(dist)
    assert twice_S % 2 == 0
    S = twice_S // 2

    print(f"lollipop(K_{CLIQUE}, P_{PATH}): n={n}, m={m}, S={S}")

    # exact integer checks (violation means conjecture is FALSE)
    viol_pairs = 2 * m * S * S > n ** 3 * comb(n, 2) ** 2
    viol_full = 8 * m * S * S > n ** 7

    mu_pairs = S / comb(n, 2)
    mu_full = 2 * S / n ** 2
    sd = sqrt(2 * m / n)
    print(f"stdev(eigenvalues) = sqrt(2m/n) = {sd:.6f}")
    print(f"mu_pairs = {mu_pairs:.6f}, n/mu_pairs = {n / mu_pairs:.6f}, "
          f"violated: {viol_pairs}")
    print(f"mu_full  = {mu_full:.6f}, n/mu_full  = {n / mu_full:.6f}, "
          f"violated: {viol_full}")

    assert viol_pairs, "no violation under pairs convention"
    assert viol_full, "no violation under full-matrix convention"
    print("PASS: conjecture 154 (2*m*mu^2 <= n^3) is FALSE for this graph "
          "under both mu conventions")


if __name__ == "__main__":
    main()
