"""Structure-seeded local search: start from equality/near-equality graphs
(K_a u K_a, best blow-ups) and hill-climb single edge flips on
score = l1^2 + l2^2 - 2m(1-1/w), with exact omega recomputed each step.
This probes whether the equality manifold can be crossed by irregular
perturbations (V2 'blowups of known near-misses').
"""
import random
import sys
import numpy as np
from common import graph_score, clique_number_np

random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 42)
TIME_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 600

import time


def two_cliques(a, b):
    n = a + b
    A = np.zeros((n, n), dtype=int)
    A[:a, :a] = 1
    A[a:, a:] = 1
    np.fill_diagonal(A, 0)
    return A


def full_score(A):
    n = A.shape[0]
    m = int(A.sum()) // 2
    if m == n * (n - 1) // 2:
        return None
    w = clique_number_np(A)
    return graph_score(A, w) + (w,)


def climb(A, iters, T0=0.15):
    cur = full_score(A)
    best = (cur[0], A.copy(), cur)
    n = A.shape[0]
    for it in range(iters):
        T = T0 * (1 - it / iters)
        i = random.randrange(n)
        j = random.randrange(n)
        if i == j:
            continue
        A[i, j] ^= 1
        A[j, i] ^= 1
        new = full_score(A)
        if new is not None and (new[0] >= cur[0] - 1e-12 or
                                random.random() < np.exp(min(0, (new[0] - cur[0]) / max(T, 1e-6)))):
            cur = new
            if cur[0] > best[0]:
                best = (cur[0], A.copy(), cur)
                if cur[0] > 1e-9:
                    print("VIOLATION", cur, flush=True)
                    np.save("violation.npy", A)
                    return best
        else:
            A[i, j] ^= 1
            A[j, i] ^= 1
    return best


def main():
    t0 = time.time()
    results = []
    seeds = []
    for a in (5, 8, 10, 12, 15, 18):
        seeds.append((f"K{a}uK{a}", two_cliques(a, a)))
        B = two_cliques(a, a)
        B[0, a] = B[a, 0] = 1
        seeds.append((f"K{a}uK{a}+e", B))
    ri = 0
    while time.time() - t0 < TIME_BUDGET:
        tag, S = seeds[ri % len(seeds)]
        ri += 1
        best = climb(S.copy(), 1500)
        results.append((best[0], tag, best[2]))
        print(f"[{time.time()-t0:7.0f}s] seed={tag} best={best[0]:+.6f} "
              f"(l1={best[2][1]:.4f} l2={best[2][2]:.4f} m={best[2][3]} w={best[2][4]})", flush=True)
    results.sort(key=lambda t: -t[0])
    print("\nTOP:")
    for r in results[:10]:
        print(r[0], r[1], r[2])


if __name__ == "__main__":
    main()
