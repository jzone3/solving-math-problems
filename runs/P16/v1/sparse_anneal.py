#!/usr/bin/env python3
"""P16: large-n sparse-graph annealing (adjacency dict + scipy eigsh) for
bounds 44/46 — covers sparse structures out of reach of dense search."""
import math
import random
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl


def build(n, edges):
    r = [e[0] for e in edges] + [e[1] for e in edges]
    c = [e[1] for e in edges] + [e[0] for e in edges]
    A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(n, n))
    return A


def evaluate(which, n, edges):
    A = build(n, edges)
    d = np.asarray(A.sum(axis=1)).ravel()
    if d.min() < 1:
        return None
    m = (A @ d) / d
    L = sp.diags(d) - A
    try:
        mu = spl.eigsh(L, k=1, which="LA", return_eigenvectors=False, maxiter=5000)[0]
    except Exception:
        return None
    rhs = -np.inf
    for (i, j) in edges:
        di, dj, mi, mj = d[i], d[j], m[i], m[j]
        if which == 44:
            inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
        else:
            inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
        if inner < 0:
            return None
        rhs = max(rhs, 2 + math.sqrt(inner))
    return mu - rhs


def is_connected(n, edges):
    adj = [[] for _ in range(n)]
    for (i, j) in edges:
        adj[i].append(j)
        adj[j].append(i)
    seen = [False] * n
    seen[0] = True
    st = [0]
    cnt = 1
    while st:
        u = st.pop()
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                cnt += 1
                st.append(v)
    return cnt == n


def seed_edges(n, rng, style):
    edges = set()
    if style == 0:  # spanning tree + random
        for i in range(1, n):
            edges.add((rng.randrange(i), i))
        for _ in range(n):
            i, j = rng.sample(range(n), 2)
            edges.add((min(i, j), max(i, j)))
    elif style == 1:  # hub + matching cloud
        h = 0
        for i in range(1, n - 1, 2):
            edges.add((i, i + 1))
            edges.add((h, i))
    else:  # two hubs + cloud
        for i in range(2, n - 1, 2):
            edges.add((i, i + 1))
            edges.add((0, i))
            edges.add((1, i))
        edges.add((0, 1))
    return edges


def run(which, n, seed, iters=8000):
    rng = random.Random(seed)
    edges = seed_edges(n, rng, seed % 3)
    if not is_connected(n, list(edges)):
        for i in range(1, n):
            edges.add((rng.randrange(i), i))
    cur = evaluate(which, n, list(edges))
    tries = 0
    while cur is None and tries < 50:
        i, j = rng.sample(range(n), 2)
        edges.add((min(i, j), max(i, j)))
        cur = evaluate(which, n, list(edges))
        tries += 1
    if cur is None:
        return -1e18
    best = cur
    T0, T1 = 0.3, 0.003
    for t in range(iters):
        i, j = rng.sample(range(n), 2)
        e = (min(i, j), max(i, j))
        if e in edges:
            edges.discard(e)
        else:
            edges.add(e)
        v = evaluate(which, n, list(edges)) if is_connected(n, list(edges)) else None
        T = T0 * (T1 / T0) ** (t / iters)
        if v is not None and (v > cur or rng.random() < math.exp((v - cur) / T)):
            cur = v
            if v > best:
                best = v
                if v > 1e-9:
                    print(f"[{which}] VIOLATION n={n} seed={seed} margin={v}", flush=True)
                    print(sorted(edges), flush=True)
                    return best
        else:
            if e in edges:
                edges.discard(e)
            else:
                edges.add(e)
    return best


if __name__ == "__main__":
    which = int(sys.argv[1])
    n = int(sys.argv[2])
    s0 = int(sys.argv[3])
    overall = -1e18
    for s in range(3):
        b = run(which, n, s0 + s)
        print(f"[{which}] n={n} seed={s0 + s} best={b:.6f}", flush=True)
        overall = max(overall, b)
    print(f"[{which}] SPARSE n={n} OVERALL {overall:.6f}")
