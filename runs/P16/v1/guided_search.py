#!/usr/bin/env python3
"""P16: eigenvector-guided direct graph search for violations of bounds 44/46.
Moves proposed by mu-sensitivity (top Laplacian eigenvector) and RHS-edge relief."""
import math
import random
import sys

import numpy as np


def eval_state(which, A):
    n = A.shape[0]
    d = A.sum(axis=1)
    if d.min() < 1:
        return None
    m = (A @ d) / d
    L = np.diag(d) - A
    w, V = np.linalg.eigh(L)
    mu = w[-1]
    x = V[:, -1]
    rhs = -np.inf
    argmax = None
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
                v = 2 + math.sqrt(inner)
                if v > rhs:
                    rhs, argmax = v, (i, j)
    return mu - rhs, x, argmax


def connected(A):
    n = A.shape[0]
    seen = np.zeros(n, dtype=bool)
    stack = [0]
    seen[0] = True
    while stack:
        u = stack.pop()
        nb = np.nonzero(A[u])[0]
        for v in nb:
            if not seen[v]:
                seen[v] = True
                stack.append(int(v))
    return seen.all()


def run(which, n, seed, iters=30000):
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)
    h = n // 2
    A = np.zeros((n, n), dtype=np.int64)
    for i in range(h):
        for j in range(h, n):
            if rng.random() < 0.8:
                A[i, j] = A[j, i] = 1
    for _ in range(2 * n):
        i, j = rng.sample(range(n), 2)
        A[i, j] |= 0
    while not connected(A):
        i, j = rng.sample(range(n), 2)
        A[i, j] = A[j, i] = 1
    st = eval_state(which, A)
    while st is None:
        i, j = rng.sample(range(n), 2)
        A[i, j] = A[j, i] = 1
        if not connected(A):
            continue
        st = eval_state(which, A)
    cur, x, am = st
    best = cur
    T0, T1 = 0.4, 0.003
    for t in range(iters):
        T = T0 * (T1 / T0) ** (t / iters)
        r = rng.random()
        if r < 0.4:
            # add edge maximizing (x_u - x_v)^2 among a sample of non-edges
            cands = []
            for _ in range(30):
                u, v = rng.sample(range(n), 2)
                if not A[u, v]:
                    cands.append(((x[u] - x[v]) ** 2, u, v))
            if not cands:
                continue
            _, u, v = max(cands)
        elif r < 0.7 and am is not None:
            # perturb near the RHS-max edge: remove it or an incident edge
            u = am[rng.randrange(2)]
            nbrs = np.nonzero(A[u])[0]
            v = int(nbrs[rng.randrange(len(nbrs))])
        else:
            u, v = rng.sample(range(n), 2)
        A[u, v] ^= 1
        A[v, u] ^= 1
        st = eval_state(which, A) if connected(A) else None
        if st is not None and (st[0] > cur or rng.random() < math.exp((st[0] - cur) / T)):
            cur, x, am = st
            if cur > best:
                best = cur
                if best > 1e-9:
                    print(f"[{which}] VIOLATION n={n} seed={seed} t={t} margin={best}", flush=True)
                    print(A.tolist(), flush=True)
                    return best
        else:
            A[u, v] ^= 1
            A[v, u] ^= 1
    return best


if __name__ == "__main__":
    which = int(sys.argv[1])
    ns = [int(x) for x in sys.argv[2].split(",")]
    s0 = int(sys.argv[3])
    overall = -1e18
    for n in ns:
        for s in range(3):
            b = run(which, n, s0 + 31 * n + s)
            print(f"[{which}] n={n} seed={s} best={b:.6f}", flush=True)
            overall = max(overall, b)
    print(f"[{which}] GUIDED OVERALL {overall:.6f}")
