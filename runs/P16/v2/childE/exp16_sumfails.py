"""Exp 16: collect all n<=9 graphs where the SUM family fails; characterize them
(bipartite? leaves? degree structure? which pair (e,f) blocks feasibility?).
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44
from exp15_exact import sum_feasible, prod_feasible


def is_bipartite(A):
    n = A.shape[0]
    col = [None] * n
    stack = [0]
    col[0] = 0
    while stack:
        v = stack.pop()
        for u in range(n):
            if A[v, u]:
                if col[u] is None:
                    col[u] = 1 - col[v]
                    stack.append(u)
                elif col[u] == col[v]:
                    return False
    return True


def run(nmax):
    fails = []
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            di = np.array([d[i] for i, j in E])
            dj = np.array([d[j] for i, j in E])
            mi = np.array([m[i] for i, j in E])
            mj = np.array([m[j] for i, j in E])
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            tau = math.sqrt(max(R, 0))
            if not sum_feasible(di, dj, mi, mj, tau, min(d)):
                pf = prod_feasible(di, dj, mi, mj, tau)
                dd = np.asarray(d)
                bip = is_bipartite(A)
                # blocking data
                T = tau + 2
                s = di + dj
                alpha = di * (di + mi) + dj * (dj + mj) - T * s
                beta = s - T
                lo = -np.inf
                hi = np.inf
                for a, b in zip(alpha, beta):
                    if b < -1e-12:
                        lo = max(lo, a / (-b))
                    elif b > 1e-12:
                        hi = min(hi, -a / b)
                nbeta0bad = int(np.sum((np.abs(beta) <= 1e-12) & (alpha > 1e-9)))
                fails.append((g6, n, pf, bip, dd.min(), dd.max(), lo, hi,
                              nbeta0bad))
    print(f"total sum-failures: {len(fails)}")
    npf = sum(1 for f in fails if not f[2])
    print(f"...of which prod ALSO fails: {npf}")
    nbip = sum(1 for f in fails if f[3])
    print(f"...bipartite: {nbip}")
    nleaf = sum(1 for f in fails if f[4] == 1)
    print(f"...with leaves (delta=1): {nleaf}")
    from collections import Counter
    print("delta,Delta histogram:", Counter((f[4], f[5]) for f in fails))
    print("beta0-blocked count:", sum(1 for f in fails if f[8] > 0))
    for f in fails[:25]:
        print(f"  {f[0]} n={f[1]} prodOK={f[2]} bip={f[3]} delta={f[4]:.0f} "
              f"Delta={f[5]:.0f} c-window=({f[6]:.3f},{f[7]:.3f}) beta0bad={f[8]}")


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
