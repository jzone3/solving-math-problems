#!/usr/bin/env python3
"""P16: systematic continuous optimization of violation margin over ALL
k=4 and k=5 quotient support patterns (connected cell graphs + loop subsets),
with feasibility floors (b_ij>=1 on support, b_ii>=2, n_i>=1, b_ij<=n_j).
Multi-start scipy optimization; report any support whose feasible sup > 0."""
import itertools
import sys

import numpy as np
from scipy.optimize import minimize

import networkx as nx

WHICH = int(sys.argv[1]) if len(sys.argv) > 1 else 44
K = int(sys.argv[2]) if len(sys.argv) > 2 else 4
NMAX = 500.0
BIG = 1e6


def connected_supports(k):
    nodes = list(range(k))
    seen = set()
    out = []
    edges = list(itertools.combinations(nodes, 2))
    for r in range(k - 1, len(edges) + 1):
        for es in itertools.combinations(edges, r):
            g = nx.Graph()
            g.add_nodes_from(nodes)
            g.add_edges_from(es)
            if not nx.is_connected(g):
                continue
            key = nx.weisfeiler_lehman_graph_hash(g)
            if key in seen:
                continue
            seen.add(key)
            out.append(es)
    return out


def margin(x, es, loops, k):
    n = np.exp(x[:k])  # n_i >= 1 via floor below
    n = 1.0 + n
    bv = 1.0 + np.exp(x[k:])
    B = np.zeros((k, k))
    p = 0
    for (i, j) in es:
        B[i, j] = bv[p]; p += 1
        # b_ji determined by n_i b_ij = n_j b_ji
        B[j, i] = n[i] * B[i, j] / n[j]
    for i in loops:
        B[i, i] = 1.0 + bv[p]; p += 1
    # feasibility penalties: b_ij <= n_j, b_ii <= n_i - 1, b_ji >= 1
    pen = 0.0
    for i in range(k):
        for j in range(k):
            if B[i, j] > 0:
                lim = n[j] - 1 if i == j else n[j]
                if B[i, j] > lim:
                    pen += (B[i, j] - lim) ** 2
                if i != j and B[i, j] < 1:
                    pen += (1 - B[i, j]) ** 2
    if n.max() > NMAX:
        pen += (n.max() - NMAX) ** 2
    d = B.sum(axis=1)
    if d.min() < 1e-9:
        return BIG
    m = B @ d / d
    S = np.diag(np.sqrt(n))
    Si = np.diag(1 / np.sqrt(n))
    LB = np.diag(d) - B
    sym = S @ LB @ Si
    sym = (sym + sym.T) / 2
    mu = np.linalg.eigvalsh(sym)[-1]
    r = -BIG
    for (i, j) in list(es) + [(i, i) for i in loops]:
        di, dj, mi, mj = d[i], d[j], m[i], m[j]
        if WHICH == 44:
            inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
        else:
            inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
        v = 2 + np.sqrt(inner) if inner >= 0 else -BIG
        r = max(r, v)
    return -(mu - r) + 10.0 * pen


def main():
    rng = np.random.default_rng(7)
    sups = connected_supports(K)
    print(f"which={WHICH} k={K} supports={len(sups)}", flush=True)
    best_overall = -1e18
    for es in sups:
        for loopmask in range(1 << K):
            loops = [i for i in range(K) if loopmask >> i & 1]
            nvar = K + len(es) + len(loops)
            best = -1e18
            for trial in range(12):
                x0 = rng.normal(0, 2, nvar)
                try:
                    res = minimize(margin, x0, args=(es, loops, K),
                                   method="Nelder-Mead",
                                   options={"maxiter": 4000, "fatol": 1e-12, "xatol": 1e-10})
                    val = -res.fun
                except Exception:
                    continue
                if val > best:
                    best = val
            if best > best_overall:
                best_overall = best
                print(f"support={es} loops={loops} best={best:.6f}", flush=True)
            if best > 1e-6:
                print(f"POSITIVE support={es} loops={loops} best={best:.6f}", flush=True)
    print(f"OVERALL which={WHICH} k={K} best={best_overall:.6f}", flush=True)


if __name__ == "__main__":
    main()
