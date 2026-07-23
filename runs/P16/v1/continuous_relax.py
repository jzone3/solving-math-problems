#!/usr/bin/env python3
"""P16 v1 escalation: continuous relaxation of the quotient-margin problem.

Variables (per support pattern on k cells): real cell sizes n_i > 0 and edge
weights e_ij >= eps on the support (e_ij = n_i b_ij = n_j b_ji; e_ii = # internal
edges). Objective: maximize margin = rho(L_B) - max_{support edges} f_bound.
Realizability relaxed to 0 <= b_ij <= n_j, 0 <= b_ii <= n_i - 1 (penalty).
If the continuous supremum over this family is <= 0, no integer quotient point
of that support can violate the bound via the rho(L_B) lower bound.
"""
import itertools
import math
import sys

import numpy as np
from scipy.optimize import minimize


def make_eval(which, k, support):
    sup = list(support)

    def margin(x):
        n = np.exp(x[:k])  # positive
        e = np.exp(x[k:])  # positive weights per support edge
        B = np.zeros((k, k))
        for t, (i, j) in enumerate(sup):
            if i == j:
                B[i, i] = 2 * e[t] / n[i]
            else:
                B[i, j] = e[t] / n[i]
                B[j, i] = e[t] / n[j]
        d = B.sum(axis=1)
        if d.min() <= 1e-12:
            return -1e6
        m = (B @ d) / d
        # penalty for violated realizability, incl. integrality floor b >= 1 on support
        pen = 0.0
        for i in range(k):
            pen += max(0.0, B[i, i] - (n[i] - 1)) ** 2
            pen += max(0.0, 1.0 - n[i]) ** 2
            for j in range(k):
                if i != j:
                    pen += max(0.0, B[i, j] - n[j]) ** 2
        for (i, j) in sup:
            if i == j:
                pen += max(0.0, 1.0 - B[i, i]) ** 2
            else:
                pen += max(0.0, 1.0 - B[i, j]) ** 2 + max(0.0, 1.0 - B[j, i]) ** 2
        # rho(L_B) via symmetrization
        M = np.diag(d) - np.diag(np.sqrt(n)) @ B @ np.diag(1 / np.sqrt(n))
        M = (M + M.T) / 2
        if not np.all(np.isfinite(M)):
            return -1e6
        try:
            mu = np.max(np.linalg.eigvalsh(M))
        except np.linalg.LinAlgError:
            return -1e6
        rhs = -np.inf
        for (i, j) in sup:
            di, dj, mi, mj = d[i], d[j], m[i], m[j]
            if which == 44:
                inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
            else:
                inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
            if inner < 0:
                return -1e6
            rhs = max(rhs, 2 + math.sqrt(inner))
        return mu - rhs - 100.0 * pen

    return margin


def supports(k):
    """connected support patterns over k cells (off-diag edges + optional loops)."""
    offd = list(itertools.combinations(range(k), 2))
    for r in range(k - 1, len(offd) + 1):
        for oset in itertools.combinations(offd, r):
            # connectivity
            seen = {0}
            stack = [0]
            adj = {i: [] for i in range(k)}
            for (i, j) in oset:
                adj[i].append(j)
                adj[j].append(i)
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            if len(seen) != k:
                continue
            for loops in itertools.chain.from_iterable(
                    itertools.combinations(range(k), s) for s in range(0, k + 1)):
                yield list(oset) + [(i, i) for i in loops]


def optimize(which, kmax=4, restarts=6, seed=0):
    rng = np.random.default_rng(seed)
    best = (-1e18, None, None)
    for k in range(2, kmax + 1):
        for sup in supports(k):
            f = make_eval(which, k, sup)
            for r in range(restarts):
                x0 = np.concatenate([rng.uniform(0.5, 4.0, k),
                                     rng.uniform(0.5, 6.0, len(sup))])
                res = minimize(lambda x: -f(x), x0, method="Nelder-Mead",
                               options={"maxiter": 4000, "xatol": 1e-10, "fatol": 1e-12})
                v = -res.fun
                if v > best[0]:
                    best = (v, k, sup)
                    if v > 1e-7:
                        n = np.exp(res.x[:k])
                        e = np.exp(res.x[k:])
                        print(f"[{which}] POSITIVE k={k} sup={sup} margin={v:.8f} n={n} e={e}", flush=True)
        print(f"[{which}] k={k} done; best so far {best[0]:.8f} (k={best[1]}, sup={best[2]})", flush=True)
    print(f"[{which}] CONTINUOUS OVERALL best margin {best[0]:.8f} at k={best[1]} sup={best[2]}")


if __name__ == "__main__":
    optimize(int(sys.argv[1]), kmax=int(sys.argv[2]) if len(sys.argv) > 2 else 4)
