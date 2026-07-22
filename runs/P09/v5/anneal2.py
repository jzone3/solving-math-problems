"""Round-2 anneal, designed from the literature map: fix omega in {3,4,5},
reject flips that change the clique number, start from triangle-rich seeds
(Turan-union with cross edges = connected, irregular, many triangles).
Score = lam1^2 + lam2^2 - 2m(1-1/omega_target).

Usage: python3 anneal2.py <n> <omega> <restarts> <steps> <seed>
"""
import sys, json, time
import numpy as np
from core import turan_graph, union, top2, max_clique

def seed_graph(n, w, rng):
    k = max(1, n // (2 * w))
    A = union(turan_graph(k * w, w), turan_graph((n - k * w) // w * w if (n - k * w) >= w else w, w))
    s = A.shape[0]
    B = np.zeros((n, n)); B[:s, :s] = A; A = B
    # connect + roughen
    for _ in range(max(3, n // 4)):
        i, j = rng.integers(0, n, 2)
        if i != j:
            A[i, j] = A[j, i] = 1
    while max_clique(A) > w:
        # remove an edge from a max clique region: remove random edge in a K_{w+1}
        idx = np.transpose(np.nonzero(np.triu(A, 1)))
        i, j = idx[rng.integers(0, len(idx))]
        A[i, j] = A[j, i] = 0
    return A

def run(n, w, restarts, steps, seed):
    rng = np.random.default_rng(seed)
    gb = -1e9
    coef = 2 * (1 - 1 / w)
    for r in range(restarts):
        A = seed_graph(n, w, rng)
        def sc(A):
            l1, l2 = top2(A)
            return l1 * l1 + l2 * l2 - coef * (A.sum() / 2)
        s = sc(A); best = s; bestA = A.copy()
        T0, T1 = 0.8, 0.004
        for t in range(steps):
            T = T0 * (T1 / T0) ** (t / steps)
            i, j = rng.integers(0, n, 2)
            if i == j:
                continue
            A[i, j] = A[j, i] = 1 - A[i, j]
            if max_clique(A) != w:
                A[i, j] = A[j, i] = 1 - A[i, j]
                continue
            s2 = sc(A)
            if s2 >= s or rng.random() < np.exp((s2 - s) / T):
                s = s2
                if s > best:
                    best, bestA = s, A.copy()
            else:
                A[i, j] = A[j, i] = 1 - A[i, j]
        flag = " ***POSITIVE***" if best > 1e-9 else ""
        print(f"n={n} w={w} restart={r} best={best:+.6f} m={int(bestA.sum()//2)}{flag}", flush=True)
        if best > 1e-9:
            edges = [(int(i), int(j)) for i in range(n) for j in range(i + 1, n) if bestA[i, j]]
            json.dump({"n": n, "w": w, "edges": edges, "score": best},
                      open(f"witness2_n{n}_w{w}_seed{seed}.json", "w"))
        gb = max(gb, best)
    print(f"ROUND2 GLOBAL BEST n={n} w={w}: {gb:+.6f}")

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
