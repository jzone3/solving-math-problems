#!/usr/bin/env python3
"""V4 (proof attempt -> extremal structure) search for Graffiti 154.

Conjecture 154 (Roucairol-Cazenave encoding, GenerateGraph.rs CONJECTURE==154):
    std(adjacency eigenvalues) <= n / mean(distance-matrix entries over all n^2 cells)
Since eigenvalues sum to 0 and sum of squares is 2m, std = sqrt(2m/n) exactly, so
the conjecture is equivalent (RC form, mu1 = 2*S/n^2 with S = sum over unordered pairs):
    2m * mu1^2 <= n^3   <=>   8*m*S^2 <= n^7.
Unordered-pairs form (mu2 = 2S/(n(n-1)), the classical average distance):
    8*m*S^2 <= n^5*(n-1)^2.
mu2 > mu1, so violating the RC (n^7) form implies violating the pairs form.

Dumbbell(a, l, b): cliques K_a, K_b joined by a path with l edges (l-1 internal
vertices). n = a + b + l - 1, m = C(a,2) + C(b,2) + l.

All arithmetic exact (Python ints).
"""

def C2(x):
    return x * (x - 1) // 2

def dumbbell_S_m_n(a, l, b):
    """Exact sum of distances over unordered pairs, edge count, vertex count."""
    assert a >= 1 and b >= 1 and l >= 1
    n = a + b + l - 1
    m = C2(a) + C2(b) + l
    S = C2(a) + C2(b)
    # A side to internal path vertices u_i, i=1..l-1:
    #   (a-1) non-attachment vertices at distance i+1, attachment at distance i
    for i in range(1, l):
        S += (a - 1) * (i + 1) + i
        S += (b - 1) * (l - i + 1) + (l - i)
    # A to B
    S += (a - 1) * (b - 1) * (l + 2) + (a - 1) * (l + 1) + (b - 1) * (l + 1) + l
    # internal-internal: sum_{1<=i<j<=l-1} (j-i)
    L = l - 1
    S += sum((L - d) * d for d in range(1, L))
    return S, m, n

def bfs_S_m_n(a, l, b):
    """Independent brute-force check via adjacency + BFS."""
    from collections import deque
    # vertices: 0..a-1 clique A (0 = attachment), path internals a..a+l-2,
    # clique B: a+l-1 .. a+l-1+b-1 (a+l-1 = attachment)
    n = a + b + l - 1
    adj = [set() for _ in range(n)]
    for i in range(a):
        for j in range(i + 1, a):
            adj[i].add(j); adj[j].add(i)
    off = a + l - 1
    for i in range(b):
        for j in range(i + 1, b):
            adj[off + i].add(off + j); adj[off + j].add(off + i)
    path = [0] + list(range(a, a + l - 1)) + [off]
    for u, v in zip(path, path[1:]):
        adj[u].add(v); adj[v].add(u)
    m = sum(len(s) for s in adj) // 2
    S = 0
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
        S += sum(dist)
    assert S % 2 == 0
    return S // 2, m, n

def check(a, l, b):
    S, m, n = dumbbell_S_m_n(a, l, b)
    lhs = 8 * m * S * S
    return lhs, n ** 7, n ** 5 * (n - 1) ** 2, S, m, n

if __name__ == "__main__":
    import sys
    # 1) validate closed form against BFS on small cases
    for a in range(1, 7):
        for b in range(1, 7):
            for l in range(1, 8):
                assert dumbbell_S_m_n(a, l, b) == bfs_S_m_n(a, l, b), (a, l, b)
    print("closed form validated against BFS on all a,b<=6, l<=7")

    # 2) scan n, for each n optimize a=b (by symmetry) and also asymmetric
    best = None
    first_rc = None
    first_pairs = None
    for n in range(20, 3001):
        for a in range(2, (n + 1) // 2 + 1):
            for b in (a, a - 1):  # near-balanced (convexity; asymmetric scan below confirms)
                l = n + 1 - a - b
                if l < 1 or b < 2:
                    continue
                lhs, rc_rhs, pairs_rhs, S, m, nn = check(a, l, b)
                ratio = lhs / rc_rhs
                if best is None or ratio > best[0]:
                    best = (ratio, a, l, b, n)
                if lhs > pairs_rhs and first_pairs is None:
                    first_pairs = (a, l, b, n)
                    print("FIRST pairs-form violation:", first_pairs)
                if lhs > rc_rhs and first_rc is None:
                    first_rc = (a, l, b, n)
                    print("FIRST RC-form violation:", first_rc)
        if n % 500 == 0:
            print(f"n={n} best ratio so far {best[0]:.6f} at a,l,b,n={best[1:]}" )
    print("best:", best)
    print("first RC violation:", first_rc)
    print("first pairs violation:", first_pairs)
