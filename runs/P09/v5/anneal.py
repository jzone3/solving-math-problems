"""Simulated annealing maximizing score = lam1^2 + lam2^2 - 2m(1-1/omega),
with exact clique number every step. Restricted to the genuinely open region:
we log the near-misses and track the max score seen (must stay < 0 if BN holds).

Usage: python3 anneal.py <n> <restarts> <steps> [seed] [init]
init in {random, turan-union, cliques}
"""
import sys, time, json
import numpy as np
from core import adj_from_edges, turan_graph, union, score, max_clique

def anneal(n, steps, rng, init="random", T0=1.0, T1=0.01):
    if init == "turan-union":
        r = int(rng.integers(3, 6))
        k = max(1, n // (2 * r))
        A = union(turan_graph(k * r, r), turan_graph(k * r, r))
        pad = n - A.shape[0]
        if pad > 0:
            B = np.zeros((n, n)); B[:A.shape[0], :A.shape[0]] = A; A = B
    elif init == "cliques":
        w = int(rng.integers(4, 8))
        Kw = np.ones((w, w)) - np.eye(w)
        A = union(Kw, Kw)
        pad = n - A.shape[0]
        B = np.zeros((n, n)); B[:A.shape[0], :A.shape[0]] = A; A = B
        # sprinkle random edges
        for _ in range(n):
            i, j = rng.integers(0, n, 2)
            if i != j: A[i, j] = A[j, i] = 1
    else:
        A = (rng.random((n, n)) < rng.uniform(0.2, 0.7)).astype(float)
        A = np.triu(A, 1); A = A + A.T
    s, w = score(A)
    if s is None: s = -1e9
    best_s, best_A = s, A.copy()
    for t in range(steps):
        T = T0 * (T1 / T0) ** (t / steps)
        i, j = rng.integers(0, n, 2)
        if i == j: continue
        A[i, j] = A[j, i] = 1 - A[i, j]
        s2, w2 = score(A)
        if s2 is None:
            s2 = -1e9
        if s2 >= s or rng.random() < np.exp((s2 - s) / T):
            s = s2
            if s > best_s:
                best_s, best_A = s, A.copy()
        else:
            A[i, j] = A[j, i] = 1 - A[i, j]
    return best_s, best_A

if __name__ == "__main__":
    n = int(sys.argv[1]); restarts = int(sys.argv[2]); steps = int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    init = sys.argv[5] if len(sys.argv) > 5 else "random"
    rng = np.random.default_rng(seed)
    global_best = -1e9
    t0 = time.time()
    for r in range(restarts):
        bs, bA = anneal(n, steps, rng, init=init)
        wf = max_clique(bA)
        mf = int(bA.sum() // 2)
        flag = " ***POSITIVE***" if bs > 1e-9 else ""
        print(f"n={n} init={init} restart={r} best={bs:+.6f} w={wf} m={mf} t={time.time()-t0:.0f}s{flag}", flush=True)
        if bs > global_best:
            global_best = bs
            if bs > 1e-9:
                edges = [(i, j) for i in range(n) for j in range(i+1, n) if bA[i, j]]
                with open(f"witness_n{n}_seed{seed}.json", "w") as f:
                    json.dump({"n": n, "edges": edges, "score": bs}, f)
    print(f"GLOBAL BEST n={n} init={init}: {global_best:+.6f}")
