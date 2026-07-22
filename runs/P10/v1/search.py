#!/usr/bin/env python3
"""P10 V1: annealed edge-flip counterexample search for Brouwer's conjecture.

Score(G) = max_t ( sum_{i<=t} mu_i  -  m  -  t(t+1)/2 ),  mu_i Laplacian eigenvalues desc.
Brouwer's conjecture <=> Score(G) <= 0 for all graphs. We anneal edge flips to maximize
Score over n-vertex graphs. Equality (score = 0) is attained by threshold graphs, so the
search reports best scores and whether any strictly positive score (violation) is found.

Usage: search.py N_MIN N_MAX SECONDS_PER_N SEED [OUTFILE]
"""
import sys, time, math, json
import numpy as np

def score_graph(A):
    """Return (best_score, best_t). A: symmetric 0/1 adjacency matrix."""
    n = A.shape[0]
    d = A.sum(axis=1)
    L = np.diag(d) - A
    mu = np.linalg.eigvalsh(L)[::-1]          # descending
    m = d.sum() / 2.0
    cs = np.cumsum(mu)
    t = np.arange(1, n + 1)
    vals = cs - m - t * (t + 1) / 2.0
    i = int(np.argmax(vals))
    return float(vals[i]), i + 1

def random_threshold(n, rng):
    """Random threshold graph: sequence of dominating/isolated vertex additions."""
    A = np.zeros((n, n))
    for k in range(1, n):
        if rng.random() < 0.5:
            A[k, :k] = 1; A[:k, k] = 1
    return A

def anneal(n, seconds, rng, T0=0.5, Tmin=1e-4, report=None, init="random"):
    if init == "threshold":
        A = random_threshold(n, rng)
    else:
        p = rng.uniform(0.15, 0.9)
        A = (rng.random((n, n)) < p).astype(float)
        A = np.triu(A, 1); A = A + A.T
    cur, cur_t = score_graph(A)
    best, best_t, best_A = cur, cur_t, A.copy()
    start = time.time()
    it = 0
    while True:
        el = time.time() - start
        if el > seconds: break
        frac = el / seconds
        T = T0 * (Tmin / T0) ** frac
        i = rng.integers(0, n); j = rng.integers(0, n)
        if i == j: continue
        A[i, j] = 1 - A[i, j]; A[j, i] = A[i, j]
        new, new_t = score_graph(A)
        if new >= cur or rng.random() < math.exp((new - cur) / T):
            cur, cur_t = new, new_t
            if cur > best:
                best, best_t, best_A = cur, cur_t, A.copy()
                if best > 1e-9 and report:
                    report(n, best, best_t, best_A)
        else:
            A[i, j] = 1 - A[i, j]; A[j, i] = A[i, j]
        it += 1
    return best, best_t, best_A, it

def edges_of(A):
    n = A.shape[0]
    return [[i, j] for i in range(n) for j in range(i + 1, n) if A[i, j]]

def main():
    n_min, n_max, secs, seed = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    outfile = sys.argv[5] if len(sys.argv) > 5 else None
    init = sys.argv[6] if len(sys.argv) > 6 else "random"
    rng = np.random.default_rng(seed)
    def report(n, s, t, A):
        rec = {"VIOLATION": True, "n": n, "t": t, "score": s, "edges": edges_of(A)}
        print(json.dumps(rec), flush=True)
        if outfile:
            with open(outfile, "a") as f: f.write(json.dumps(rec) + "\n")
    for n in range(n_min, n_max + 1):
        best, bt, bA, it = anneal(n, secs, rng, report=report, init=init)
        m = int(bA.sum() // 2)
        rec = {"n": n, "best_score": best, "t": bt, "m": m, "iters": it, "seed": seed}
        print(json.dumps(rec), flush=True)
        if outfile:
            with open(outfile, "a") as f: f.write(json.dumps(rec) + "\n")

if __name__ == "__main__":
    main()
