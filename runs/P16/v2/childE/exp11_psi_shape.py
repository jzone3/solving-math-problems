"""Exp 11: (a) print optimal general-psi table for hard graphs (normalized);
(b) test additive family psi(x,y) = f(x)+f(y) with general concave f (SLSQP over
values of f at point set) on the hard graphs.
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize

from common import g6_adj, graph_data, arg44

HARD = "H?`reQF H?ovE_N HCOf@pR HCQfRjF HCRdrrF HCpf`zF".split()


def solve_general(g6, trials=24):
    A = g6_adj(g6)
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    target = math.sqrt(max(R, 0))
    pts = sorted(set(list(d) + list(m)))
    K = len(pts)
    idx = {p: k for k, p in enumerate(pts)}
    iu = np.triu_indices(K)

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
    best, bu = math.inf, None
    rng = np.random.default_rng(0)
    lp = np.log(pts)
    for _ in range(trials):
        a, b = rng.uniform(0, 1, 2)
        U0 = a * lp[:, None] + b * lp[None, :]
        U0 = (U0 + U0.T) / 2 + rng.normal(0, 0.03, (K, K))
        r = minimize(F, U0[iu], constraints=cons, method="SLSQP",
                     options={"maxiter": 800, "ftol": 1e-12})
        if r.fun < best:
            best, bu = r.fun, r.x
    P = table(bu)
    P = P / P[0, 0]
    print(f"{g6}: slack={target - best:+.5f}")
    print("   pts:", [f"{p:.3g}" for p in pts])
    for r in range(K):
        print("   ", " ".join(f"{P[r, k]:7.3f}" for k in range(K)))
    # rank-1 check: is P approx outer(f, f)? and additive check P ~ f+g?
    w, V = np.linalg.eigh(P)
    print(f"   top-2 eig of table: {w[-1]:.4f}, {w[-2]:+.4f} (rank-1-ness)")
    return d, m, E, target


def solve_additive(g6, trials=24):
    A = g6_adj(g6)
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    target = math.sqrt(max(R, 0))
    pts = sorted(set(list(d) + list(m)))
    K = len(pts)
    idx = {p: k for k, p in enumerate(pts)}

    def F(u):
        f = np.exp(u)

        def psi(a, b):
            return f[idx[a]] + f[idx[b]]

        return max((d[i] * psi(d[i], m[i]) + d[j] * psi(d[j], m[j])
                    - 2 * psi(d[i], d[j])) / psi(d[i], d[j]) for i, j in E)

    cons = []
    for k in range(1, K - 1):
        p1, p2, p3 = pts[k - 1], pts[k], pts[k + 1]

        def con(u, k=k, c1=(p3 - p2), c3=(p2 - p1), c2=(p3 - p1)):
            f = np.exp(u)
            return c2 * f[k] - c1 * f[k - 1] - c3 * f[k + 1]

        cons.append({"type": "ineq", "fun": con})
    best, bu = math.inf, None
    rng = np.random.default_rng(1)
    for _ in range(trials):
        u0 = rng.uniform(0, 1) * np.log(pts) + rng.normal(0, 0.05, K)
        r = minimize(F, u0, constraints=cons, method="SLSQP",
                     options={"maxiter": 800, "ftol": 1e-12})
        if r.fun < best:
            best, bu = r.fun, r.x
    f = np.exp(bu)
    print(f"{g6}: ADDITIVE slack={target - best:+.5f} "
          f"f={[f'{v / f[0]:.4f}' for v in f]}")


if __name__ == "__main__":
    for g in HARD:
        solve_general(g)
        solve_additive(g)
