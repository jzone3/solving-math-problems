"""P16 childC — continuous relaxation of the equitable-quotient search,
k = 4..8 cells (extends the k <= 3 analysis of ../continuous_opt2.py).

Parametrization (realizability-faithful): positive cell sizes n_i, symmetric
S_ij >= 0 supported on a chosen cell-graph; B = diag(n)^{-1} S. Constraint:
every present entry B_ij >= 1 (integer quotients have entries >= 1 on the
support). Cell degrees s_i = sum_j B_ij, m_i = (sum_j B_ij s_j)/s_i,
gap = lam_max(L_B) - RHS(bound). Integer quotients with the same support are a
subset of this feasible set, so a nonnegative infimum over it is strong
negative evidence for the whole support class (any entry size).

Supports: all nonisomorphic trees on k nodes (bipartite, always realizable)
plus tree+one-edge unicyclic patterns with even cycles, plus complete
bipartite cell patterns.

Optimizer: log-parametrized (entries e^u >= 1 via u >= 0 softplus shift)
Nelder-Mead / Powell multistart.
"""
import argparse
import itertools
import math
import sys
import time

import networkx as nx
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, "..")
import search_common  # noqa: E402

EDGE_FN = {44: search_common.rhs44_edge, 46: search_common.rhs46_edge}


def supports(k):
    sups = []
    for T in nx.nonisomorphic_trees(k):
        sups.append(sorted(T.edges()))
        # unicyclic with even cycle: add one edge creating an even cycle
        for (a, b) in itertools.combinations(range(k), 2):
            if T.has_edge(a, b):
                continue
            cyc_len = nx.shortest_path_length(T, a, b) + 1
            if cyc_len % 2 == 0:
                sups.append(sorted(list(T.edges()) + [(a, b)]))
    # complete bipartite supports
    for p in range(1, k // 2 + 1):
        sups.append([(i, j) for i in range(p) for j in range(p, k)])
    # dedupe
    uniq = {tuple(map(tuple, s)) for s in sups}
    return [list(map(list, s)) for s in uniq]


def make_gap(k, edges, bound):
    e_idx = [(a, b) for (a, b) in edges]
    ne = len(e_idx)
    fn = EDGE_FN[bound]

    def gap(theta):
        # theta = [log n_i (k), log S_e offsets (ne)]
        n = np.exp(theta[:k])
        S = np.zeros((k, k))
        for t, (a, b) in enumerate(e_idx):
            S[a, b] = S[b, a] = math.exp(theta[k + t])
        B = S / n[:, None]
        # enforce entries >= 1 via penalty
        pen = 0.0
        for (a, b) in e_idx:
            for (i, j) in ((a, b), (b, a)):
                if B[i, j] < 1.0:
                    pen += (1.0 - B[i, j]) ** 2 * 100.0
        s = B.sum(axis=1)
        if np.any(s <= 0):
            return 1e6
        m = (B @ s) / s
        LB = np.diag(s) - B
        lam = float(np.max(np.linalg.eigvals(LB).real))
        rhs = -math.inf
        for (a, b) in e_idx:
            v = fn(s[a], s[b], m[a], m[b])
            rhs = max(rhs, v)
        if rhs == -math.inf:
            return 1e6
        return rhs - lam + pen

    return gap


def run(k, bound, restarts, seed):
    rng = np.random.default_rng(seed)
    best = math.inf
    best_info = None
    sups = supports(k)
    for edges in sups:
        g = make_gap(k, edges, bound)
        dim = k + len(edges)
        for _ in range(restarts):
            x0 = rng.uniform(0.0, 5.0, size=dim)
            res = minimize(g, x0, method="Nelder-Mead",
                           options={"maxiter": 4000, "xatol": 1e-10, "fatol": 1e-12})
            if res.fun < best:
                best = res.fun
                best_info = (edges, res.x.copy())
                if best < -1e-6:
                    print(f"NEGATIVE k={k} bound={bound} edges={edges} "
                          f"gap={best:.6g} theta={res.x.tolist()}", flush=True)
    print(f"k={k} bound={bound}: {len(sups)} supports, min gap = {best:.6g} "
          f"(support {best_info[0] if best_info else None})", flush=True)
    return best, best_info


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bound", type=int, required=True)
    ap.add_argument("--kmin", type=int, default=4)
    ap.add_argument("--kmax", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    t0 = time.time()
    for k in range(args.kmin, args.kmax + 1):
        run(k, args.bound, args.restarts, args.seed + k)
    print(f"elapsed {time.time()-t0:.0f}s", flush=True)
