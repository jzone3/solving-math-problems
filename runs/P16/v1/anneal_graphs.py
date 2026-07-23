#!/usr/bin/env python3
"""P16 v1: secondary screen — simulated annealing directly on graphs
(edge flips, keeping connectivity) maximizing mu(G) - RHS(bound)."""
import math
import random
import sys

import numpy as np


def margin(which, A):
    n = A.shape[0]
    d = A.sum(axis=1)
    if d.min() < 1:
        return None
    m = (A @ d) / d
    L = np.diag(d) - A
    mu = np.max(np.linalg.eigvalsh(L.astype(float)))
    r = -np.inf
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                di, dj, mi, mj = float(d[i]), float(d[j]), m[i], m[j]
                if which == 44:
                    inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
                else:
                    inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
                if inner < 0:
                    return None
                r = max(r, 2 + math.sqrt(inner))
    return mu - r


def connected(A):
    n = A.shape[0]
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in np.nonzero(A[u])[0]:
            if v not in seen:
                seen.add(int(v))
                stack.append(int(v))
    return len(seen) == n


def anneal(which, n, seed, iters=60000):
    rng = random.Random(seed)
    # start from a random connected graph (path + random edges)
    A = np.zeros((n, n), dtype=np.int64)
    for i in range(n - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    for _ in range(n):
        i, j = rng.sample(range(n), 2)
        A[i, j] = A[j, i] = 1
    cur = margin(which, A)
    while cur is None:
        i, j = rng.sample(range(n), 2)
        A[i, j] = A[j, i] = 1
        cur = margin(which, A)
    best = (cur, A.copy())
    T0, T1 = 0.5, 0.005
    for t in range(iters):
        i, j = rng.sample(range(n), 2)
        A[i, j] ^= 1
        A[j, i] ^= 1
        v = margin(which, A) if connected(A) else None
        T = T0 * (T1 / T0) ** (t / iters)
        if v is not None and (v > cur or rng.random() < math.exp((v - cur) / T)):
            cur = v
            if v > best[0]:
                best = (v, A.copy())
                if v > -0.2:
                    print(f"[{which}] n={n} seed={seed} t={t} margin={v:.6f}", flush=True)
        else:
            A[i, j] ^= 1
            A[j, i] ^= 1
    return best


if __name__ == "__main__":
    which = int(sys.argv[1])
    overall = (-1e18, None)
    for n in (10, 14, 18, 24, 30, 40):
        for seed in range(3):
            v, A = anneal(which, n, seed * 1000 + n)
            print(f"[{which}] n={n} seed={seed} BEST margin={v:.6f}", flush=True)
            if v > overall[0]:
                overall = (v, A)
    v, A = overall
    print(f"[{which}] OVERALL best margin={v:.6f}")
    if v > 1e-9:
        print("VIOLATION adjacency:")
        print(A.tolist())
