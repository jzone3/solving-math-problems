"""Closed-form named families check: Kneser graphs, complete multipartite
minus/plus perturbations, cones over unions of cliques, books, split graphs.
Direct numpy for perturbed ones, closed-form for Kneser.
"""
from math import comb
import numpy as np
from common import graph_score, clique_number_np, score_from


def kneser_check(nmax=28):
    rows = []
    for n in range(5, nmax + 1):
        for k in range(2, n // 2 + 1):
            N = comb(n, k)
            if N > 500000:
                continue
            d = comb(n - k, k)
            eigs = sorted((((-1) ** i) * comb(n - k - i, k - i) for i in range(k + 1)), reverse=True)
            l1, l2 = eigs[0], eigs[1]
            m = N * d // 2
            w = n // k  # omega(Kneser(n,k)) = floor(n/k)
            s = score_from(l1, l2, m, w)
            rows.append((s, f"Kneser({n},{k})", l1, l2, m, w))
    rows.sort(key=lambda t: -t[0])
    print("Kneser top 5:")
    for r in rows[:5]:
        print(r)


def perturbed_multipartite():
    # complete multipartite (equality-ish for balanced) + one edge inside a part
    rows = []
    for parts in [(3, 3, 3), (4, 4, 4), (5, 5, 5), (6, 6, 6), (2, 2, 2, 2), (4, 4, 4, 4),
                  (5, 5, 5, 5), (3, 3, 3, 3, 3), (6, 6), (10, 10), (8, 8, 8), (10, 10, 10)]:
        n = sum(parts)
        A = np.ones((n, n), dtype=int)
        np.fill_diagonal(A, 0)
        idx = np.cumsum((0,) + parts)
        for i in range(len(parts)):
            A[idx[i]:idx[i + 1], idx[i]:idx[i + 1]] = 0
        for tag, mod in [("", None), ("+e", ("add",)), ("-e", ("del",))]:
            B = A.copy()
            if mod == ("add",):
                if parts[0] < 2:
                    continue
                B[0, 1] = B[1, 0] = 1
            elif mod == ("del",):
                B[idx[1] - 1, idx[1]] = B[idx[1], idx[1] - 1] = 0
            m = int(B.sum()) // 2
            if m == n * (n - 1) // 2:
                continue
            w = clique_number_np(B)
            s, l1, l2, m = graph_score(B, w)
            rows.append((s, f"K_{parts}{tag}", l1, l2, m, w))
    rows.sort(key=lambda t: -t[0])
    print("\nperturbed multipartite top 10:")
    for r in rows[:10]:
        print(r)


def cones():
    # K_t joined to (K_a u K_b): quotient handled elsewhere, but check pendant
    # variants: (K_a u K_a) + apex adjacent to only part of each clique
    rows = []
    for a in range(4, 21):
        for p in range(1, a + 1):
            n = 2 * a + 1
            A = np.zeros((n, n), dtype=int)
            A[:a, :a] = 1
            A[a:2 * a, a:2 * a] = 1
            np.fill_diagonal(A, 0)
            v = 2 * a
            for i in range(p):
                A[v, i] = A[i, v] = 1
                A[v, a + i] = A[a + i, v] = 1
            w = clique_number_np(A)
            s, l1, l2, m = graph_score(A, w)
            rows.append((s, f"apex a={a} p={p}", l1, l2, m, w))
    rows.sort(key=lambda t: -t[0])
    print("\napex-over-two-cliques top 10:")
    for r in rows[:10]:
        print(r)


if __name__ == "__main__":
    kneser_check()
    perturbed_multipartite()
    cones()
