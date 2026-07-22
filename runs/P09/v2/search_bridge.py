"""Perturbations of the equality case K_a u K_b: add sparse bridge patterns
(matching, star, random bipartite, double-kite paths), plus pendant paths.
Exact clique number via branch-and-bound; eigenvalues via numpy.
"""
import itertools
import random
import numpy as np
from common import graph_score, clique_number_np

random.seed(1)


def two_cliques(a, b):
    n = a + b
    A = np.zeros((n, n), dtype=int)
    A[:a, :a] = 1
    A[a:, a:] = 1
    np.fill_diagonal(A, 0)
    return A


def report(tag, A):
    n = A.shape[0]
    m = int(A.sum()) // 2
    if m == n * (n - 1) // 2:  # complete graph: excluded by conjecture
        return (-1e18, tag + " (complete,skip)", 0, 0, m, n)
    w = clique_number_np(A)
    s, l1, l2, m = graph_score(A, w)
    return s, tag, l1, l2, m, w


def main():
    results = []
    for a in range(3, 31):
        for b in range(a, 31):
            base = two_cliques(a, b)
            n = a + b
            # matching bridges of size t
            for t in range(0, min(a, b) + 1):
                A = base.copy()
                for i in range(t):
                    A[i, a + i] = A[a + i, i] = 1
                results.append(report(f"match a={a} b={b} t={t}", A))
            # star bridge: vertex 0 of clique A joined to first t of clique B
            for t in range(1, b + 1):
                A = base.copy()
                A[0, a:a + t] = A[a:a + t, 0] = 1
                results.append(report(f"star a={a} b={b} t={t}", A))
            # random bipartite bridges
            for e in (1, 2, 3, 5, 8, 13, min(a * b // 4, 40)):
                A = base.copy()
                pairs = [(i, a + j) for i in range(a) for j in range(b)]
                for (i, j) in random.sample(pairs, min(e, len(pairs))):
                    A[i, j] = A[j, i] = 1
                results.append(report(f"rand a={a} b={b} e={e}", A))
    # double kites: two K_a's connected by a path of length L
    for a in range(3, 26):
        for L in range(1, 8):
            n = 2 * a + (L - 1)
            A = np.zeros((n, n), dtype=int)
            A[:a, :a] = 1
            A[a + L - 1:, a + L - 1:] = 1
            np.fill_diagonal(A, 0)
            chain = [0] + list(range(a, a + L - 1)) + [a + L - 1]
            for u, v in zip(chain, chain[1:]):
                A[u, v] = A[v, u] = 1
            results.append(report(f"kite a={a} L={L}", A))
    # clique + pendant clique overlapping in s vertices (clique sunflowers)
    for a in range(3, 26):
        for s in range(1, a):
            n = 2 * a - s
            A = np.zeros((n, n), dtype=int)
            A[:a, :a] = 1
            A[a - s:, a - s:] = 1
            np.fill_diagonal(A, 0)
            results.append(report(f"overlap a={a} s={s}", A))
    results.sort(key=lambda t: -t[0])
    viol = [r for r in results if r[0] > 1e-9]
    print(f"searched {len(results)} graphs; violations: {len(viol)}")
    for r in results[:25]:
        print(f"score={r[0]:+.6f} {r[1]} l1={r[2]:.4f} l2={r[3]:.4f} m={r[4]} w={r[5]}")


if __name__ == "__main__":
    main()
