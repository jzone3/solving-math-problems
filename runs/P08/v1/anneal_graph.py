"""V1 annealing over general connected graphs, score = dev(D) - min(n+, n-).

Moves: toggle a random edge (keep connectivity). Eigensolve per eval (numpy).
Usage: python3 anneal_graph.py <n> <iters> [seed]
"""
import sys
import math
import random
import numpy as np
from collections import deque


def connected(A, n):
    seen = np.zeros(n, dtype=bool)
    q = deque([0])
    seen[0] = True
    cnt = 1
    while q:
        u = q.popleft()
        for v in np.nonzero(A[u])[0]:
            if not seen[v]:
                seen[v] = True
                cnt += 1
                q.append(v)
    return cnt == n


def score(A, n, tol=1e-4):
    # BFS APSP
    total = 0.0
    total_sq = 0.0
    diam = 0
    nbrs = [np.nonzero(A[u])[0] for u in range(n)]
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            du = dist[u]
            total += du
            total_sq += du * du
            if du > diam:
                diam = du
            for v in nbrs[u]:
                if dist[v] < 0:
                    dist[v] = du + 1
                    q.append(v)
    m = n * n
    mean = total / m
    var = total_sq / m - mean * mean
    dev = math.sqrt(max(var, 0.0))
    eig = np.linalg.eigvalsh(A)
    npos = int((eig > tol).sum())
    nneg = int((eig < -tol).sum())
    return dev - min(npos, nneg), dev, npos, nneg, diam


def main():
    n = int(sys.argv[1])
    iters = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rng = random.Random(seed)
    # start from a path (max dev)
    A = np.zeros((n, n))
    for i in range(n - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    cur, dev, npos, nneg, diam = score(A, n)
    best = cur
    best_info = (dev, npos, nneg, diam)
    T0, T1 = 0.5, 0.005
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / max(iters - 1, 1))
        i = rng.randrange(n)
        j = rng.randrange(n)
        if i == j:
            continue
        A[i, j] = A[j, i] = 1 - A[i, j]
        if not connected(A, n):
            A[i, j] = A[j, i] = 1 - A[i, j]
            continue
        s, dev, npos, nneg, diam = score(A, n)
        if s > cur or rng.random() < math.exp((s - cur) / T):
            cur = s
            if s > best:
                best = s
                best_info = (dev, npos, nneg, diam)
                if s > 1e-5:
                    print("VIOLATION", n, s, dev, npos, nneg, diam, flush=True)
                    np.save(f"violation_n{n}_seed{seed}.npy", A)
        else:
            A[i, j] = A[j, i] = 1 - A[i, j]
        if it % max(iters // 10, 1) == 0:
            print(f"n={n} it={it} cur={cur:.4f} best={best:.4f} info={best_info}", flush=True)
    print(f"FINAL n={n} best={best:.6f} dev={best_info[0]:.6f} npos={best_info[1]} "
          f"nneg={best_info[2]} diam={best_info[3]}", flush=True)


if __name__ == "__main__":
    main()
