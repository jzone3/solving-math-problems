"""Exp 4 (Route 1): mine the shape of per-graph feasible concave phi.

For hard graphs (where simple families fail), find a concave phi minimizing
max_e CW_phi(e) (SLSQP, multistart), normalize phi(min pt)=1, and report:
  - phi values at the sorted point set
  - slack: best F vs target 2+sqrt(R)
  - is phi nondecreasing? which concavity constraints are active (kinks)?
  - location of kinks relative to graph stats (delta, Delta, mbar, davg)
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize

from common import graphs, g6_adj, graph_data, arg44


def solve_phi(d, m, E, trials=16, seed=0):
    pts = sorted(set(list(d) + list(m)))
    idx = {p: k for k, p in enumerate(pts)}
    K = len(pts)

    def F(u):
        phi = np.exp(u)
        return max(d[i] * phi[idx[m[i]]] / phi[idx[d[j]]]
                   + d[j] * phi[idx[m[j]]] / phi[idx[d[i]]] for i, j in E)

    cons = []
    for k in range(1, K - 1):
        p1, p2, p3 = pts[k - 1], pts[k], pts[k + 1]

        def con(u, k=k, c1=(p3 - p2), c3=(p2 - p1), c2=(p3 - p1)):
            phi = np.exp(u)
            return c2 * phi[k] - c1 * phi[k - 1] - c3 * phi[k + 1]

        cons.append({"type": "ineq", "fun": con})
    best, bu = math.inf, None
    rng = np.random.default_rng(seed)
    for _ in range(trials):
        u0 = rng.uniform(0, 1) * np.log(pts) + rng.normal(0, 0.05, K)
        r = minimize(F, u0, constraints=cons, method="SLSQP",
                     options={"maxiter": 600, "ftol": 1e-12})
        if r.fun < best:
            best, bu = r.fun, r.x
    return pts, np.exp(bu - bu[0]), best


def analyze(g6, verbose=True):
    A = g6_adj(g6)
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    target = 2 + math.sqrt(max(R, 0))
    pts, phi, F = solve_phi(d, m, E)
    K = len(pts)
    mono = all(phi[k + 1] >= phi[k] - 1e-7 for k in range(K - 1))
    kinks = []
    for k in range(1, K - 1):
        p1, p2, p3 = pts[k - 1], pts[k], pts[k + 1]
        val = (p3 - p1) * phi[k] - (p3 - p2) * phi[k - 1] - (p2 - p1) * phi[k + 1]
        if val > 1e-6 * phi[k]:
            kinks.append(pts[k])
    if verbose:
        dd = np.array(d)
        print(f"{g6}: slack={target - F:+.4f} target={target:.4f} "
              f"delta={dd.min():.0f} Delta={dd.max():.0f} "
              f"davg={dd.mean():.2f} mono={mono} kinks={kinks}")
        print("   pts:", [f"{p:.3g}" for p in pts])
        print("   phi:", [f"{v:.4f}" for v in phi])
    return target - F, mono, kinks


if __name__ == "__main__":
    hard = ['EUZ_', 'FCOf?', 'FCZfG', 'FCZbg', 'FCY[w', 'FCdcg', 'FCvcw', 'FEhd_',
            'EEj_', 'EQjO', 'GCpb`o', 'GCXecW', 'GCzn^[', 'G?ovF?']
    for g in hard:
        analyze(g)
