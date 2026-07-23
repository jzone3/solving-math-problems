"""Frontier push 2: large-n (50-90) edge-flip annealing with igraph's C clique
solver for exact omega each step, seeded at equality-manifold structures
(two-blob unions, split graphs, Turan unions) and random dense graphs.
Parallel tempering-ish: several temperatures per worker.
"""
import random
import sys
import time
import numpy as np
import igraph as ig
import multiprocessing as mp

TIME_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 7200


def score_A(A):
    n = A.shape[0]
    m = int(A.sum()) // 2
    if m == n * (n - 1) // 2 or m == 0:
        return None
    g = ig.Graph.Adjacency((A > 0).tolist(), mode="undirected")
    w = g.clique_number()
    ev = np.linalg.eigvalsh(A.astype(float))
    l1, l2 = ev[-1], ev[-2]
    return l1 * l1 + l2 * l2 - 2.0 * m * (1.0 - 1.0 / w), l1, l2, m, w


def two_blob(a, b):
    n = a + b
    A = np.zeros((n, n), dtype=int)
    A[:a, :a] = 1
    A[a:, a:] = 1
    np.fill_diagonal(A, 0)
    return A


def dturan(w, t):
    n1 = w * t
    A = np.ones((n1, n1), dtype=int)
    np.fill_diagonal(A, 0)
    for i in range(w):
        A[i * t:(i + 1) * t, i * t:(i + 1) * t] = 0
    n = 2 * n1
    B = np.zeros((n, n), dtype=int)
    B[:n1, :n1] = A
    B[n1:, n1:] = A
    return B


def rand_graph(n, p, rng):
    A = (np.random.default_rng(rng.randrange(1 << 30)).random((n, n)) < p).astype(int)
    A = np.triu(A, 1)
    return A + A.T


def worker(wid):
    rng = random.Random(wid * 7919 + 1)
    t0 = time.time()
    best_overall = (-1e18, None)
    n_flips = 0
    while time.time() - t0 < TIME_BUDGET:
        r = rng.random()
        if r < 0.4:
            a = rng.randint(25, 45)
            A = two_blob(a, a + rng.randint(0, 5))
            tag = f"blob{a}"
        elif r < 0.7:
            w, t = rng.choice([(3, 10), (3, 13), (4, 8), (4, 10), (5, 7), (6, 6), (7, 5), (8, 5)])
            A = dturan(w, t)
            tag = f"2xT({w},{t})"
        else:
            n = rng.randint(50, 90)
            A = rand_graph(n, rng.choice([0.5, 0.7, 0.85]), rng)
            tag = f"rand{n}"
        cur = score_A(A)
        if cur is None:
            continue
        n = A.shape[0]
        T0 = rng.choice([0.05, 0.15, 0.4])
        iters = 2500
        for it in range(iters):
            T = T0 * (1 - it / iters)
            i, j = rng.randrange(n), rng.randrange(n)
            if i == j:
                continue
            A[i, j] ^= 1
            A[j, i] ^= 1
            new = score_A(A)
            n_flips += 1
            if new is not None and (new[0] >= cur[0] - 1e-12 or
                                    rng.random() < np.exp(min(0, (new[0] - cur[0]) / max(T, 1e-9)))):
                cur = new
                if cur[0] > best_overall[0]:
                    best_overall = (cur[0], (tag,) + cur)
                if cur[0] > 1e-9:
                    print("VIOLATION", cur, tag, flush=True)
                    np.save(f"violation_big_{wid}.npy", A)
                    return n_flips, best_overall
            else:
                A[i, j] ^= 1
                A[j, i] ^= 1
    return n_flips, best_overall


if __name__ == "__main__":
    with mp.Pool(4) as pool:
        res = pool.map(worker, range(4))
    print(f"total flips scored: {sum(r[0] for r in res)}")
    for r in sorted(res, key=lambda t: -t[1][0]):
        print(f"best={r[1][0]:+.8f} detail={r[1][1]}")
