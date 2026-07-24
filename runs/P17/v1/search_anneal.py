#!/usr/bin/env python3
"""Simulated annealing search for counterexamples to WoW 20/21.

WoW 20: n+(G) <= sum of positive eigenvalues (= E/2).  Violation iff
    score20(G) := sum_{lambda>0} (1 - lambda) > 0.
WoW 21: n-(G) <= sum of positive eigenvalues.  Violation iff
    score21(G) := sum_{lambda<0} (1 - |lambda|) > 0.
(Both use trace 0 => sum_pos = sum |neg| = E/2.)

Float search only; any candidate with score > -TOL_REPORT is re-checked
exactly by verify_exact.py.
"""
import numpy as np, itertools, random, sys, json, time

ZTOL = 1e-8          # eigenvalues within ZTOL of 0 treated as zero
REPORT = -0.02       # report graphs with score above this

def scores(A):
    ev = np.linalg.eigvalsh(A)
    pos = ev[ev > ZTOL]
    neg = ev[ev < -ZTOL]
    s = pos.sum()
    return len(pos) - s, len(neg) - s   # score20, score21

def ncomp(A):
    n = len(A); seen = [False]*n; c = 0
    for s in range(n):
        if seen[s]: continue
        c += 1; stack = [s]; seen[s] = True
        while stack:
            u = stack.pop()
            for v in np.nonzero(A[u])[0]:
                if not seen[v]: seen[v] = True; stack.append(v)
    return c

def rand_graph(n, p, rng):
    U = np.triu((rng.random((n, n)) < p).astype(float), 1)
    return U + U.T

def anneal(n, objective, iters, rng, T0=0.6, T1=0.005, p0=None):
    p = p0 if p0 is not None else rng.uniform(0.05, 0.5)
    A = rand_graph(n, p, rng)
    def val(A):
        s20, s21 = scores(A)
        raw = s20 if objective == 20 else s21
        return raw - 1e-3 * (ncomp(A) - 1), raw
    cur, curraw = val(A)
    best, bestraw, bestA = cur, curraw, A.copy()
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        i = rng.integers(0, n); j = rng.integers(0, n)
        while j == i: j = rng.integers(0, n)
        A[i, j] = A[j, i] = 1 - A[i, j]
        new, newraw = val(A)
        if new >= cur or rng.random() < np.exp((new - cur) / T):
            cur, curraw = new, newraw
            if cur > best:
                best, bestraw, bestA = cur, curraw, A.copy()
        else:
            A[i, j] = A[j, i] = 1 - A[i, j]
    return bestraw, bestA

def edges_of(A):
    n = len(A)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]

if __name__ == '__main__':
    obj = int(sys.argv[1])            # 20 or 21
    ns = [int(x) for x in sys.argv[2].split(',')]
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    iters = int(sys.argv[4]) if len(sys.argv) > 4 else 30000
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    rng = np.random.default_rng(seed)
    overall = []
    for n in ns:
        bn, bA = -1e9, None
        for r in range(restarts):
            b, A = anneal(n, obj, iters, rng)
            if b > bn: bn, bA = b, A
        e = edges_of(bA)
        print(f"obj={obj} n={n} best_score={bn:.6f} m={len(e)}", flush=True)
        overall.append((n, bn, e))
        if bn > REPORT:
            print("NEAR-MISS/CANDIDATE:", json.dumps({"n": n, "score": bn, "edges": e}), flush=True)
    top = max(overall, key=lambda t: t[1])
    print("TOP:", json.dumps({"obj": obj, "n": top[0], "score": top[1], "edges": top[2]}))
