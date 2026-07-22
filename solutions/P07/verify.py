#!/usr/bin/env python3
"""Independent verifier for a counterexample to Graffiti conjecture 154 (WoW 154).

Conjecture (as encoded by Roucairol-Cazenave 2025, GenerateGraph.rs, CONJECTURE == 154):
    for every connected graph G: stdev(adjacency eigenvalues) <= n / mean_dist
where stdev is the population standard deviation of the n adjacency eigenvalues and
mean_dist is the mean of ALL n^2 entries of the distance matrix (diagonal included).

Since trace(A)=0 and trace(A^2)=2m, stdev = sqrt(2m/n) exactly, so with S = the sum of
distances over ordered pairs (mean_dist = S/n^2) the conjecture is equivalent to the
integer inequality
    2 * m * S^2 <= n^7.
Under the more common convention mu = S/(n(n-1)) it is equivalent to
    2 * m * S^2 <= n^3 * (n*(n-1))^2.
This script checks the witness violates BOTH, using only integer arithmetic + BFS.

Witness: lollipop L(50, 70) = clique K_50 with a pendant path of 70 vertices (n = 120).

Only the Python standard library is used. Prints PASS on success.
"""
from collections import deque

A_CLIQUE = 50
PATH_LEN = 70


def build_lollipop(a, ell):
    n = a + ell
    adj = [set() for _ in range(n)]
    for i in range(a):
        for j in range(i + 1, a):
            adj[i].add(j)
            adj[j].add(i)
    prev = 0  # attach path at clique vertex 0
    for k in range(ell):
        v = a + k
        adj[prev].add(v)
        adj[v].add(prev)
        prev = v
    return n, adj


def all_pairs_distance_sum(n, adj):
    total = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    q.append(v)
        assert all(d >= 0 for d in dist), "graph is not connected"
        total += sum(dist)
    return total  # sum over ordered pairs (u, v), u != v


def main():
    n, adj = build_lollipop(A_CLIQUE, PATH_LEN)
    m = sum(len(s) for s in adj) // 2
    S = all_pairs_distance_sum(n, adj)

    assert n == 120
    assert m == A_CLIQUE * (A_CLIQUE - 1) // 2 + PATH_LEN == 1295
    assert S == 372120, S

    lhs = 2 * m * S * S  # = 2 m S^2

    # Roucairol-Cazenave convention: mu = S / n^2 ; conjecture <=> 2 m S^2 <= n^7
    rhs_rc = n ** 7
    assert lhs > rhs_rc, (lhs, rhs_rc)

    # standard convention: mu = S / (n(n-1)) ; conjecture <=> 2 m S^2 <= n^3 (n(n-1))^2
    rhs_std = n ** 3 * (n * (n - 1)) ** 2
    assert lhs > rhs_std, (lhs, rhs_std)

    # float sanity mirror of the R-C check: stdev - n/mean_dist > 1e-5
    stdev = (2 * m / n) ** 0.5
    mean_dist_rc = S / n ** 2
    assert stdev - n / mean_dist_rc > 1e-5

    print("witness: lollipop L(%d,%d), n=%d, m=%d, S=%d" % (A_CLIQUE, PATH_LEN, n, m, S))
    print("2*m*S^2 = %d" % lhs)
    print("n^7     = %d  (R-C convention rhs; exceeded by %d)" % (rhs_rc, lhs - rhs_rc))
    print("n^3*(n(n-1))^2 = %d  (standard convention rhs; exceeded by %d)" % (rhs_std, lhs - rhs_std))
    print("stdev(eigs) = sqrt(2m/n) = %.6f > n/mu = %.6f" % (stdev, n / mean_dist_rc))
    print("PASS")


if __name__ == "__main__":
    main()
