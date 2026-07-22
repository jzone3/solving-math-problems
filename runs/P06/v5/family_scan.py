"""Targeted family scan (V5: literature/near-miss guided).

Families:
- 129: stars, stars+edges, double stars, spiders, complete split graphs.
- 698A: complete bipartite K_{a,b} (equality case!), K_{a,b} +/- edges,
  complete multipartite, complete split graphs.
Prints the top (closest-to-violation / violating) instances.
"""

import numpy as np
import itertools
from invariants import score_129_std, score_129_mad, score_698A, randic, s_minus, dev, laplacian_eigs


def star(n):
    A = np.zeros((n, n), dtype=int)
    A[0, 1:] = 1
    A[1:, 0] = 1
    return A


def star_plus_matching(n, k):
    """Star K_{1,n-1} plus a matching of k edges among the leaves."""
    A = star(n)
    for t in range(k):
        u, v = 1 + 2 * t, 2 + 2 * t
        if v >= n:
            break
        A[u, v] = A[v, u] = 1
    return A


def star_plus_clique(n, k):
    """Star plus a clique on the first k leaves."""
    A = star(n)
    for u, v in itertools.combinations(range(1, min(k + 1, n)), 2):
        A[u, v] = A[v, u] = 1
    return A


def double_star(a, b):
    """Two adjacent centers with a and b leaves."""
    n = a + b + 2
    A = np.zeros((n, n), dtype=int)
    A[0, 1] = A[1, 0] = 1
    for i in range(a):
        A[0, 2 + i] = A[2 + i, 0] = 1
    for i in range(b):
        A[1, 2 + a + i] = A[2 + a + i, 1] = 1
    return A


def complete_split(n, k):
    """Clique of size k joined completely to an independent set of size n-k."""
    A = np.ones((n, n), dtype=int) - np.eye(n, dtype=int)
    A[k:, k:] = 0
    return A


def complete_bipartite(a, b):
    n = a + b
    A = np.zeros((n, n), dtype=int)
    A[:a, a:] = 1
    A[a:, :a] = 1
    return A


def kab_plus_edge(a, b):
    A = complete_bipartite(a, b)
    if a >= 2:
        A[0, 1] = A[1, 0] = 1
    return A


def kab_minus_edge(a, b):
    A = complete_bipartite(a, b)
    A[0, a] = A[a, 0] = 0
    return A


def kab_plus_matching(a, b, k):
    A = complete_bipartite(a, b)
    for t in range(min(k, a // 2)):
        u, v = 2 * t, 2 * t + 1
        A[u, v] = A[v, u] = 1
    return A


def complete_multipartite(parts):
    n = sum(parts)
    A = np.ones((n, n), dtype=int) - np.eye(n, dtype=int)
    s = 0
    for p in parts:
        A[s:s + p, s:s + p] = 0
        s += p
    return A


def run():
    results_129, results_698 = [], []

    for n in list(range(4, 60)) + [80, 120, 200, 400]:
        results_129.append((score_129_std(star(n)), f"star({n})"))
        for k in [1, 2, 3, n // 4, n // 2]:
            results_129.append((score_129_std(star_plus_matching(n, k)), f"star+match({n},{k})"))
            results_129.append((score_129_std(star_plus_clique(n, min(k, 12))), f"star+clique({n},{min(k,12)})"))
        for a in [1, 2, 3, n // 2]:
            b = n - 2 - a
            if b >= 1:
                results_129.append((score_129_std(double_star(a, b)), f"dstar({a},{b})"))
        for k in [1, 2, 3, n // 3, n // 2]:
            if 1 <= k < n:
                results_129.append((score_129_std(complete_split(n, k)), f"csplit({n},{k})"))

    for a in range(1, 30):
        for b in range(a, 40):
            results_698.append((score_698A(complete_bipartite(a, b)), f"K({a},{b})"))
            if a >= 2:
                results_698.append((score_698A(kab_plus_edge(a, b)), f"K({a},{b})+e"))
                results_698.append((score_698A(kab_minus_edge(a, b)), f"K({a},{b})-e"))
            for k in [1, 2, a // 2]:
                if k >= 1:
                    results_698.append((score_698A(kab_plus_matching(a, b, k)), f"K({a},{b})+M{k}"))
    for parts in itertools.chain(
            itertools.combinations_with_replacement(range(1, 9), 3),
            itertools.combinations_with_replacement(range(1, 7), 4)):
        results_698.append((score_698A(complete_multipartite(list(parts))), f"Kmulti{parts}"))

    results_129.sort(reverse=True)
    results_698.sort(reverse=True)
    print("=== 129 (dev = std) top 15 (score = dev_L - R; >0 means violation) ===")
    for s, name in results_129[:15]:
        print(f"{s:+.6f}  {name}")
    print("=== 698A top 15 (score = s_minus - R) ===")
    for s, name in results_698[:15]:
        print(f"{s:+.6f}  {name}")


if __name__ == "__main__":
    run()
