"""Exp 18: the additive-psi conjecture on ALL known hard graphs (8 from n<=9 +
190 from n=10 + 6 trees n<=14).

Family A_f: psi(x,y) = f(x)+f(y), f concave positive. Bound (Lemma, Jensen):
  rho(Q) <= 2 + max_e [d_i f(m_i) + d_j f(m_j) + (d_i-2) f(d_i) + (d_j-2) f(d_j)
                       - ... ] / (f(d_i)+f(d_j))   -- exact form below.
(A y)_e = (d_i-1)f(d_i) + S_i - f(d_j) + (d_j-1)f(d_j) + S_j - f(d_i),
S_i = sum_{k~i} f(d_k) <= d_i f(m_i).
CW_e = [ (d_i-2)f(d_i) + (d_j-2)f(d_j) + d_i f(m_i) + d_j f(m_j) ] / (f(d_i)+f(d_j))

Tests per graph:
  (1) one-breakpoint PL: f(x) = min(x, p + s(x-p)) + c  (grid p, s, c)
  (2) general concave f (SLSQP over point values, feasibility)
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize

from common import g6_adj, graph_data, arg44

HARD9 = ["GCOfBc", "H?`@fBP", "H?`@f@h", "H?`@db`", "H?`aeRS", "HCOcbQp",
         "HCOfBej", "HCOefDf"]
TREES = ['IhOK?E??G', 'KhH?GI??K??@', 'LhH?GI??G?o??@', 'MhCP?CAO??o??@??_',
         'MhH?GI??G?_A_???_', 'MhOK?C@?_?o??@?@?']


def cw_add(d, m, E, f):
    vals = {}
    for p in set(list(d) + list(m)):
        v = f(p)
        if v <= 0 or not np.isfinite(v):
            return math.inf
        vals[p] = v
    # returns the certified upper bound on rho(Q): 2 + max_e NUM4_e / y_e
    return 2 + max((d[i] * vals[m[i]] + d[j] * vals[m[j]]
                    + (d[i] - 2) * vals[d[i]] + (d[j] - 2) * vals[d[j]])
                   / (vals[d[i]] + vals[d[j]]) for i, j in E)


def pl_grid(d, m, E, target):
    for p in np.arange(1.0, max(d) + 0.51, 0.25):
        for s in np.arange(0, 1.01, 0.05):
            for c in [0, 0.25, 0.5, 1, 1.5, 2, 3, 5, 8, 15]:
                if cw_add(d, m, E,
                          lambda x, p=p, s=s, c=c: min(x, p + s * (x - p)) + c) \
                        <= target + 1e-9:
                    return (p, s, c)
    return None


def gen_f(d, m, E, target, trials=20):
    pts = sorted(set(list(d) + list(m)))
    K = len(pts)
    idx = {p: k for k, p in enumerate(pts)}

    def F(u):
        f = np.exp(u)
        return max((d[i] * f[idx[m[i]]] + d[j] * f[idx[m[j]]]
                    + (d[i] - 2) * f[idx[d[i]]] + (d[j] - 2) * f[idx[d[j]]])
                   / (f[idx[d[i]]] + f[idx[d[j]]]) for i, j in E)

    cons = []
    for k in range(1, K - 1):
        p1, p2, p3 = pts[k - 1], pts[k], pts[k + 1]

        def con(u, k=k, c1=(p3 - p2), c3=(p2 - p1), c2=(p3 - p1)):
            f = np.exp(u)
            return c2 * f[k] - c1 * f[k - 1] - c3 * f[k + 1]

        cons.append({"type": "ineq", "fun": con})
    best = math.inf
    rng = np.random.default_rng(7)
    for _ in range(trials):
        u0 = rng.uniform(0, 1) * np.log(pts) + rng.normal(0, 0.05, K)
        r = minimize(F, u0, constraints=cons, method="SLSQP",
                     options={"maxiter": 700, "ftol": 1e-12})
        if r.fun < best:
            best = r.fun
        if best <= target - 2 - 1e-9:
            break
    return 2 + best


def run():
    hard = HARD9 + TREES + open("n10_fails.txt").read().split()
    npl = 0
    ngen = 0
    bad = []
    for g6 in hard:
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        target = 2 + math.sqrt(max(R, 0))
        w = pl_grid(d, m, E, target)
        if w is not None:
            npl += 1
            continue
        v = gen_f(d, m, E, target)
        if v <= target + 1e-7:
            ngen += 1
        else:
            bad.append((g6, v - target))
    print(f"hard graphs: {len(hard)}; PL-1-breakpoint OK: {npl}; "
          f"general-f OK (extra): {ngen}; NEITHER: {len(bad)}")
    for g, dv in bad:
        print("  ", g, f"{dv:+.5f}")


if __name__ == "__main__":
    run()
