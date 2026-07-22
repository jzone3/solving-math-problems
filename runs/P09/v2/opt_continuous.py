"""Continuous relaxation over blow-up weights: for each pattern F on <=6
vertices and each type assignment, maximize score over REAL weights x_i >= 1
(sum <= N) using multistart Nelder-Mead. The discrete optimum is bounded by
grid points near the continuous one; a strictly negative continuous max over
many starts is strong (non-rigorous) evidence the whole pattern class fails.
"""
import itertools
import sys
import numpy as np
import networkx as nx
from scipy.optimize import minimize
from common import score_from

N = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
KMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 6
rng = np.random.default_rng(0)


def cont_score(F, types, x):
    k = len(x)
    x = 1.0 + np.abs(x)
    if x.sum() > N:
        return -1e9 + (N - x.sum())
    Q = np.zeros((k, k))
    m = 0.0
    for i in range(k):
        if types[i] == 'K':
            Q[i, i] = x[i] - 1
            m += x[i] * (x[i] - 1) / 2
        for j in range(k):
            if i != j and F[i][j]:
                Q[i, j] = x[j]
                if i < j:
                    m += x[i] * x[j]
    d = np.sqrt(x)
    S = (Q * (d[:, None] / d[None, :]))
    S = (S + S.T) / 2
    ev = np.sort(np.linalg.eigvalsh(S))
    l1 = ev[-1]
    l2 = ev[-2] if k >= 2 else -1.0
    if any(t == 'K' and x[i] >= 2 for i, t in enumerate(types)) and l2 < -1.0:
        l2 = -1.0
    if any(t == 'I' and x[i] >= 2 for i, t in enumerate(types)) and l2 < 0.0:
        l2 = 0.0
    # omega: max over cliques of F of sum(x_i for K) + count(I)
    best = 0.0
    nodes = range(k)
    for r in range(1, k + 1):
        for C in itertools.combinations(nodes, r):
            if all(F[a][b] for a, b in itertools.combinations(C, 2)):
                best = max(best, sum(x[i] if types[i] == 'K' else 1.0 for i in C))
    w = best
    ntot = x.sum()
    if m >= ntot * (ntot - 1) / 2 - 0.499:  # only complete graphs round to this
        return -1e9
    return score_from(l1, l2, m, w)


def main():
    atlas = nx.graph_atlas_g()
    worst = []
    for G in atlas:
        k = G.number_of_nodes()
        if k < 2 or k > KMAX:
            continue
        F = [[0] * k for _ in range(k)]
        for u, v in G.edges():
            F[u][v] = F[v][u] = 1
        for types in itertools.product('KI', repeat=k):
            bestv = -1e18
            bx = None
            for _ in range(8):
                x0 = rng.uniform(0, 40, size=k)
                r = minimize(lambda x: -cont_score(F, types, x), x0,
                             method='Nelder-Mead',
                             options={'maxiter': 2000, 'xatol': 1e-6, 'fatol': 1e-10})
                if -r.fun > bestv:
                    bestv, bx = -r.fun, 1.0 + np.abs(r.x)
            worst.append((bestv, k, tuple(G.edges()), types, tuple(np.round(bx, 3))))
            if bestv > 1e-7:
                print("POSITIVE cont max!", bestv, k, list(G.edges()), types, bx, flush=True)
    worst.sort(key=lambda t: -t[0])
    print("top 20 continuous maxima:")
    for r in worst[:20]:
        print(r)


if __name__ == "__main__":
    main()
