"""Sampled 3- and 4-flip perturbations around the FULL equality family:
unions T(ar,r) u T(br,r) (a,b>=1, incl. a=1 i.e. K_r), for r=3..6.
Also greedy plateau-walk: from each equality graph, repeatedly take the best
single flip (allowing score-decreasing moves down to -tol) for depth D.
"""
import sys
import numpy as np
from core import turan_graph, union, score

def sampled_kflips(A, k, samples, rng):
    n = A.shape[0]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    best = -1e9
    for _ in range(samples):
        idx = rng.choice(len(pairs), k, replace=False)
        B = A.copy()
        for t in idx:
            i, j = pairs[t]
            B[i, j] = B[j, i] = 1 - B[i, j]
        if B.sum() == n * (n - 1):
            continue
        s, w = score(B)
        if s is not None and s > best:
            best = s
    return best

def plateau_walk(A, depth, tol, rng):
    n = A.shape[0]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    best_global = -1e9
    cur = A.copy()
    visited_scores = []
    for d in range(depth):
        best_s, best_p = -1e9, None
        for (i, j) in pairs:
            cur[i, j] = cur[j, i] = 1 - cur[i, j]
            if cur.sum() != n * (n - 1):
                s, w = score(cur)
                if s is not None and s > best_s:
                    best_s, best_p = s, (i, j)
            cur[i, j] = cur[j, i] = 1 - cur[i, j]
        if best_p is None:
            break
        i, j = best_p
        cur[i, j] = cur[j, i] = 1 - cur[i, j]
        best_global = max(best_global, best_s)
        visited_scores.append(best_s)
        if best_s < -tol:
            break
    return best_global

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rng = np.random.default_rng(seed)
    for r in [3, 4, 5, 6]:
        for a in [1, 2, 3]:
            for b in [1, 2, 3]:
                if b < a: continue
                A = union(turan_graph(a * r, r), turan_graph(b * r, r))
                s0, w0 = score(A)
                b3 = sampled_kflips(A, 3, 3000, rng)
                b4 = sampled_kflips(A, 4, 3000, rng)
                pw = plateau_walk(A, 8, 3.0, rng)
                flag = " ***POSITIVE***" if max(b3, b4, pw) > 1e-9 else ""
                print(f"r={r} a={a} b={b} base={s0:+.2e} 3flip={b3:+.4f} 4flip={b4:+.4f} walk={pw:+.4f}{flag}", flush=True)
