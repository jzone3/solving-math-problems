"""Exp 9: fully general first-order test. Optimize over a symmetric table
psi(p,q) > 0 on the point set P = {d_i} u {m_i}, with concavity in the second
argument (for each fixed first argument, as linear constraints over sorted P).
This is the most general (d,m)-local Jensen-type first-order edge-CW bound.
Minimize max_e [d_i psi(d_i,m_i) + d_j psi(d_j,m_j) - 2 psi(d_i,d_j)]/psi(d_i,d_j);
compare with target = sqrt(max arg44). Negative slack for the OPTIMUM => the
first-order method cannot prove Bound 44 for that graph.
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize

from common import g6_adj, graph_data, arg44

HARD = """H?`reQF H?ovE_N HCOf@pR HCQfRjF HCRdrrF HCpf`zF""".split()


def solve(g6, trials=20):
    A = g6_adj(g6)
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    target = math.sqrt(max(R, 0))
    pts = sorted(set(list(d) + list(m)))
    K = len(pts)
    idx = {p: k for k, p in enumerate(pts)}
    # symmetric table u[k,l] = log psi(pts[k], pts[l]); variables upper triangle
    iu = np.triu_indices(K)
    nv = len(iu[0])

    def table(u):
        T = np.zeros((K, K))
        T[iu] = u
        T = T + T.T - np.diag(np.diag(T))
        return np.exp(T)

    def F(u):
        P = table(u)
        return max((d[i] * P[idx[d[i]], idx[m[i]]] + d[j] * P[idx[d[j]], idx[m[j]]]
                    - 2 * P[idx[d[i]], idx[d[j]]]) / P[idx[d[i]], idx[d[j]]]
                   for i, j in E)

    cons = []
    for r in range(K):
        for k in range(1, K - 1):
            p1, p2, p3 = pts[k - 1], pts[k], pts[k + 1]

            def con(u, r=r, k=k, c1=(p3 - p2), c3=(p2 - p1), c2=(p3 - p1)):
                P = table(u)
                return c2 * P[r, k] - c1 * P[r, k - 1] - c3 * P[r, k + 1]

            cons.append({"type": "ineq", "fun": con})
    best = math.inf
    rng = np.random.default_rng(0)
    lp = np.log(pts)
    for _ in range(trials):
        a = rng.uniform(0, 1)
        b = rng.uniform(0, 1)
        U0 = a * lp[:, None] + b * lp[None, :]
        U0 = (U0 + U0.T) / 2 + rng.normal(0, 0.03, (K, K))
        r = minimize(F, U0[iu], constraints=cons, method="SLSQP",
                     options={"maxiter": 800, "ftol": 1e-12})
        if r.success or r.fun < best:
            best = min(best, r.fun)
    print(f"{g6}: general-psi slack = {target - best:+.5f} (target {target:.4f})")


if __name__ == "__main__":
    for g in (sys.argv[1:] or HARD):
        solve(g)
