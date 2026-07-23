"""Annealing wave 2: seeds at OTHER points of the equality manifold —
double Turán unions T(n,w) u T(n,w) (w=3..6) and complete split graphs — with
single-edge-flip annealing and exact omega. Parallel over 8 workers.
"""
import random
import sys
import time
import numpy as np
import multiprocessing as mp
from common import graph_score, clique_number_np

TIME_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 3600


def turan(parts):
    n = sum(parts)
    A = np.ones((n, n), dtype=int)
    np.fill_diagonal(A, 0)
    idx = np.cumsum((0,) + tuple(parts))
    for i in range(len(parts)):
        A[idx[i]:idx[i + 1], idx[i]:idx[i + 1]] = 0
    return A


def dturan(w, t):
    A1 = turan((t,) * w)
    n1 = A1.shape[0]
    n = 2 * n1
    A = np.zeros((n, n), dtype=int)
    A[:n1, :n1] = A1
    A[n1:, n1:] = A1
    return A


def csplit(s, t):
    n = s + t
    A = np.zeros((n, n), dtype=int)
    A[:s, :] = 1
    A[:, :s] = 1
    np.fill_diagonal(A, 0)
    return A


def full_score(A):
    n = A.shape[0]
    m = int(A.sum()) // 2
    if m == n * (n - 1) // 2:
        return None
    w = clique_number_np(A)
    return graph_score(A, w) + (w,)


def worker(seed_idx):
    rng = random.Random(seed_idx)
    seeds = ([(f"2xT w={w} t={t}", dturan(w, t)) for w in (3, 4, 5, 6) for t in (3, 4, 5)]
             + [(f"split {s}+{t}", csplit(s, t)) for s, t in ((5, 10), (8, 8), (10, 20), (12, 6))])
    t0 = time.time()
    best_overall = (-1e18, None, None)
    while time.time() - t0 < TIME_BUDGET:
        tag, S = seeds[rng.randrange(len(seeds))]
        A = S.copy()
        cur = full_score(A)
        n = A.shape[0]
        for it in range(1200):
            T = 0.12 * (1 - it / 1200)
            i, j = rng.randrange(n), rng.randrange(n)
            if i == j:
                continue
            A[i, j] ^= 1
            A[j, i] ^= 1
            new = full_score(A)
            if new is not None and (new[0] >= cur[0] - 1e-12 or
                                    rng.random() < np.exp(min(0, (new[0] - cur[0]) / max(T, 1e-6)))):
                cur = new
                if cur[0] > best_overall[0]:
                    best_overall = (cur[0], tag, cur)
                if cur[0] > 1e-9:
                    print("VIOLATION", cur, tag, flush=True)
                    np.save(f"violation_ls2_{seed_idx}.npy", A)
                    return best_overall
            else:
                A[i, j] ^= 1
                A[j, i] ^= 1
    return best_overall


if __name__ == "__main__":
    with mp.Pool(4) as pool:
        res = pool.map(worker, range(4))
    for r in sorted(res, key=lambda t: -t[0]):
        print(f"best={r[0]:+.8f} seed={r[1]} detail={r[2]}")
