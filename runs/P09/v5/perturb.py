"""Exhaustive 1- and 2-flip neighborhoods of the equality graphs.

Equality graphs (score=0): Turan T(n,r) with r|n, and unions of two equal Turan graphs.
If the conjecture were locally false, some flip combo would give score > 0.
Records the best (max) score over each neighborhood.
"""
import itertools, sys
import numpy as np
from core import *

def flips(A):
    n = A.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            yield (i, j)

def apply(A, fl):
    B = A.copy()
    for i, j in fl:
        B[i, j] = B[j, i] = 1 - B[i, j]
    return B

def scan(name, A, depth2_sample=4000, seed=0):
    rng = np.random.default_rng(seed)
    n = A.shape[0]
    best, bestfl = -1e9, None
    fl_list = list(flips(A))
    for f in fl_list:
        B = apply(A, [f])
        if B.sum() == n * (n - 1):
            continue
        s, w = score(B)
        if s is not None and s > best:
            best, bestfl = s, [f]
    # sampled 2-flips
    for _ in range(depth2_sample):
        f1, f2 = rng.choice(len(fl_list), 2, replace=False)
        B = apply(A, [fl_list[f1], fl_list[f2]])
        if B.sum() == n * (n - 1):
            continue
        s, w = score(B)
        if s is not None and s > best:
            best, bestfl = s, [fl_list[f1], fl_list[f2]]
    print(f"{name:30s} best neighborhood score = {best:+.6f}  via {bestfl}")
    return best

if __name__ == "__main__":
    for r in [3, 4, 5]:
        for k in [2, 3, 4]:
            n = k * r
            scan(f"T({n},{r}) 1+2 flips", turan_graph(n, r))
    for r in [3, 4]:
        for k in [2, 3]:
            n = k * r
            A = turan_graph(n, r)
            scan(f"2xT({n},{r}) 1+2 flips", union(A, A))
    for w in [4, 5, 6]:
        Kw = np.ones((w, w)) - np.eye(w)
        scan(f"2K{w} 1+2 flips", union(Kw, Kw))
