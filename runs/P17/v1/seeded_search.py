#!/usr/bin/env python3
"""Low-temperature local search seeded at the best-known near-equality
family (two cliques joined by a bridge) for score21, and C5+matching for
score20. Usage: seeded_search.py <20|21> <n> <restarts> <iters> <seed>"""
import numpy as np, sys, json
from search_anneal import scores, ncomp, edges_of

def two_cliques_bridge(a, b):
    n = a + b; A = np.zeros((n, n))
    A[:a, :a] = 1 - np.eye(a); A[a:, a:] = 1 - np.eye(b)
    A[0, a] = A[a, 0] = 1
    return A

def c5_plus_matching(n):
    A = np.zeros((n, n))
    for i in range(5): A[i, (i + 1) % 5] = A[(i + 1) % 5, i] = 1
    for k in range(5, n - 1, 2): A[k, k + 1] = A[k + 1, k] = 1
    return A

def local(A, objective, iters, rng, T0=0.08, T1=0.002):
    n = len(A)
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
            if cur > best: best, bestraw, bestA = cur, curraw, A.copy()
        else:
            A[i, j] = A[j, i] = 1 - A[i, j]
    return bestraw, bestA

if __name__ == '__main__':
    obj = int(sys.argv[1]); n = int(sys.argv[2])
    restarts = int(sys.argv[3]); iters = int(sys.argv[4]); seed = int(sys.argv[5])
    rng = np.random.default_rng(seed)
    bb, bA = -1e18, None
    for r in range(restarts):
        A0 = two_cliques_bridge(n // 2, n - n // 2) if obj == 21 else c5_plus_matching(n)
        b, A = local(A0, obj, iters, rng)
        if b > bb: bb, bA = b, A
    e = edges_of(bA)
    print(f"seeded obj={obj} n={n} best={bb:.8f} m={len(e)}")
    if bb > 1e-7:
        print("CANDIDATE:", json.dumps({"n": n, "score": bb, "edges": e}))
