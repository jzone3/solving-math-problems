#!/usr/bin/env python3
"""Standalone verifier for the refutation of Graffiti conjecture 154 (WoW 154).

Conjecture 154: for every connected graph G, std(adjacency eigenvalues) <= n / mu(D),
where mu(D) is the average inter-vertex distance.

Because adjacency eigenvalues sum to 0 and their squares sum to 2m, we have
std = sqrt(2m/n) EXACTLY, so the conjecture is equivalent to 2m * mu^2 <= n^3.
No eigensolve is needed; everything below is exact integer arithmetic.

Two standard readings of mu (S = sum of distances over unordered pairs):
  (a) Roucairol-Cazenave 2025 code (GenerateGraph.rs, CONJECTURE==154):
      mu = mean over all n^2 distance-matrix entries (diagonal included) = 2S/n^2.
      Conjecture <=> 8*m*S^2 <= n^7.
  (b) classical average distance over unordered pairs: mu = 2S/(n(n-1)).
      Conjecture <=> 8*m*S^2 <= n^5*(n-1)^2.
Note mu_(b) > mu_(a), so RHS_(a) >= RHS_(b): a violation of (a) implies one of (b).

Witness: dumbbell(2, 69, 50) = a K_50 and a K_2 joined by a path with 69 edges.
(Equivalently a lollipop: K_50 with a pendant path of 70 edges.)
n = 120, m = 1295. It violates BOTH forms, as does dumbbell(36, 64, 36) (n = 135),
the smallest balanced example. Margins are thin at these sizes (std - n/mu ~ 2e-3)
but exact integer arithmetic below leaves no doubt; the violation ratio
8mS^2/n^7 grows linearly in n along the family (≈ 6.8 at n = 1000, ≈ 20 at n = 3000).

Run: python3 verify.py   ->  prints PASS if the refutation checks out.
"""
from collections import deque


def dumbbell_adj(a, l, b):
    """Cliques K_a and K_b joined by a path with l edges (l-1 internal vertices).
    Vertex 0 is the K_a attachment; vertex a+l-1 is the K_b attachment."""
    n = a + b + l - 1
    adj = [set() for _ in range(n)]

    def add(u, v):
        adj[u].add(v)
        adj[v].add(u)

    for i in range(a):
        for j in range(i + 1, a):
            add(i, j)
    off = a + l - 1
    for i in range(b):
        for j in range(i + 1, b):
            add(off + i, off + j)
    path = [0] + list(range(a, a + l - 1)) + [off]
    for u, v in zip(path, path[1:]):
        add(u, v)
    return adj


def graph_stats(adj):
    """(n, m, S) with S = sum of shortest-path distances over unordered pairs.
    Raises if the graph is disconnected."""
    n = len(adj)
    m = sum(len(s) for s in adj) // 2
    total = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        seen = 1
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    seen += 1
                    q.append(v)
        if seen != n:
            raise ValueError("graph not connected")
        total += sum(dist)
    assert total % 2 == 0
    return n, m, total // 2


def main():
    ok = True
    for (a, l, b) in [(2, 69, 50), (36, 64, 36)]:
        adj = dumbbell_adj(a, l, b)
        n, m, S = graph_stats(adj)
        lhs = 8 * m * S * S           # = 2m * (2S)^2, compare scaled RHS below
        rhs_rc = n ** 7               # RC / diagonal-included mean form
        rhs_pairs = n ** 5 * (n - 1) ** 2  # unordered-pairs mean form
        viol_rc = lhs > rhs_rc
        viol_pairs = lhs > rhs_pairs
        print(f"dumbbell({a},{l},{b}): n={n} m={m} S={S}")
        print(f"  8*m*S^2 = {lhs}")
        print(f"  n^7           = {rhs_rc}   violated: {viol_rc}")
        print(f"  n^5*(n-1)^2   = {rhs_pairs}   violated: {viol_pairs}")
        ok = ok and viol_rc and viol_pairs
    if ok:
        print("PASS: Graffiti 154 (std(eig) <= n/mu(D), i.e. 2m*mu^2 <= n^3) is refuted "
              "under both definitions of mu.")
    else:
        print("FAIL")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
