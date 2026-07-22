#!/usr/bin/env python3
"""V1: exact integer search over dumbbell(a, l, b) graphs for Graffiti 154.

Dumbbell(a, l, b): clique A on a vertices, clique B on b vertices, joined by a
path with l edges (l-1 internal vertices) between u in A and v in B.
n = a + b + l - 1, m = C(a,2) + C(b,2) + l.

Conjecture 154: stdev(adjacency eigenvalues) <= n / mu(D).
Since trace A = 0 and sum lambda_i^2 = 2m, stdev = sqrt(2m/n), so the
conjecture is equivalent to 2*m*mu^2 <= n^3 -- pure integer arithmetic given
S = sum of all pairwise distances.

Two mu definitions are checked:
  mu_pairs = S / C(n,2)            (average over unordered pairs, WoW-style)
  mu_full  = 2S / n^2              (mean over full n x n distance matrix,
                                    incl. diagonal zeros; used by the
                                    Roucairol-Cazenave Rust code)

Violation of 2*m*mu^2 > n^3 in exact integers:
  pairs: 2*m*S^2 > n^3 * C(n,2)^2
  full:  2*m*(2S)^2 > n^3 * (n^2)^2  i.e.  8*m*S^2 > n^7
"""
from math import comb


def dumbbell_m(a, l, b):
    return comb(a, 2) + comb(b, 2) + l


def dumbbell_S(a, l, b):
    """Exact sum of pairwise distances of dumbbell(a,l,b). O(l) integer loop."""
    # within cliques
    S = comb(a, 2) + comb(b, 2)
    # A-B pairs: u-v = l; u-other B = l+1 (b-1 pairs); other A-v = l+1 (a-1);
    # other A - other B = l+2
    S += l + (b - 1) * (l + 1) + (a - 1) * (l + 1) + (a - 1) * (b - 1) * (l + 2)
    # path internal vertices p_i, i = 1..l-1 (dist i from u, l-i from v)
    for i in range(1, l):
        S += i + (a - 1) * (i + 1)          # to A
        S += (l - i) + (b - 1) * (l - i + 1)  # to B
    # path-path pairs: sum_{1<=i<j<=l-1} (j-i)
    k = l - 1
    S += sum(d * (k - d) for d in range(1, k))
    return S


def check(a, l, b):
    n = a + b + l - 1
    m = dumbbell_m(a, l, b)
    S = dumbbell_S(a, l, b)
    lhs_pairs = 2 * m * S * S
    rhs_pairs = n ** 3 * comb(n, 2) ** 2
    lhs_full = 8 * m * S * S
    rhs_full = n ** 7
    return n, m, S, lhs_pairs > rhs_pairs, lhs_full > rhs_full, \
        lhs_pairs / rhs_pairs, lhs_full / rhs_full


def brute_verify_S(a, l, b):
    """Independent BFS check of dumbbell_S."""
    from collections import deque
    n = a + b + l - 1
    adj = [[] for _ in range(n)]
    def add(x, y):
        adj[x].append(y); adj[y].append(x)
    # A = 0..a-1 (u = 0), path = a..a+l-2, B = a+l-1..n-1 (v = a+l-1)
    for i in range(a):
        for j in range(i + 1, a):
            add(i, j)
    for i in range(b):
        for j in range(i + 1, b):
            add(a + l - 1 + i, a + l - 1 + j)
    chain = [0] + list(range(a, a + l - 1)) + [a + l - 1]
    for x, y in zip(chain, chain[1:]):
        add(x, y)
    S = 0
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
        S += sum(dist)
    assert S % 2 == 0
    return S // 2


if __name__ == "__main__":
    import sys
    # sanity: closed form vs BFS on assorted small cases
    for (a, l, b) in [(3, 2, 3), (5, 4, 4), (10, 7, 8), (2, 1, 2), (4, 1, 4)]:
        assert dumbbell_S(a, l, b) == brute_verify_S(a, l, b), (a, l, b)
    print("closed-form S verified against BFS on small cases")

    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    best = []
    first_pairs = first_full = None
    for n in range(10, nmax + 1):
        best_ratio = (0, None)
        # asymptotic optimum a=b~3n/8, l~n/4; search a window
        a0 = round(3 * n / 8)
        for a in range(max(2, a0 - 15), a0 + 16):
            for b in range(max(2, a - 3), a + 4):  # near-symmetric
                l = n + 1 - a - b
                if l < 1:
                    continue
                r = check(a, l, b)
                if r[6] > best_ratio[0]:
                    best_ratio = (r[6], (a, l, b), r)
        if best_ratio[1]:
            r = best_ratio[2]
            if r[3] and first_pairs is None:
                first_pairs = (n, best_ratio[1])
                print(f"FIRST pairs-violation at n={n}: (a,l,b)={best_ratio[1]}")
            if r[4] and first_full is None:
                first_full = (n, best_ratio[1])
                print(f"FIRST full-matrix violation at n={n}: (a,l,b)={best_ratio[1]}")
            if n % 100 == 0 or n in (50, 150):
                print(f"n={n}: best (a,l,b)={best_ratio[1]} ratio_full={r[6]:.4f} ratio_pairs={r[5]:.4f}")
    if first_pairs and first_full:
        print("done:", first_pairs, first_full)
