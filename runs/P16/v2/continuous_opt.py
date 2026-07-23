"""Continuous relaxation: minimize gap(B) = RHS - lam_max(L_B) over CONTINUOUS
symmetrizable quotient matrices B = diag(n)^{-1} S (S symmetric >= 0, n > 0),
k cells.  Integer quotient matrices are a subset, so if the continuous infimum
is >= 0 (attained 0 only on the bipartite-regular equality manifold), then NO
equitable-partition certificate with k cells can refute the bound.
If a strictly negative continuous point is found, chase nearby integer points.

Usage: python3 continuous_opt.py <44|46> <k> <n_starts>
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize

from search_common import rhs44_edge, rhs46_edge

EPS = 1e-9


def unpack(theta, k):
    ns = np.exp(theta[:k])                     # cell sizes > 0
    Svals = np.exp(theta[k:])                  # upper-tri incl diag of S, > 0
    S = np.zeros((k, k))
    idx = np.triu_indices(k)
    S[idx] = Svals
    S = S + np.triu(S, 1).T
    B = S / ns[:, None]
    return ns, B


def gap(theta, k, edge_fn):
    ns, B = unpack(theta, k)
    s = B.sum(axis=1)
    if (s <= EPS).any():
        return 1e6
    m = (B @ s) / s
    L = np.diag(s) - B
    # L similar to symmetric via diag(sqrt(ns)); use eig on symmetrized
    Dh = np.sqrt(ns)
    Ls = (L * Dh[:, None]) / Dh[None, :]
    Ls = (Ls + Ls.T) / 2
    lam = np.linalg.eigvalsh(Ls)[-1]
    best = -math.inf
    for i in range(k):
        for j in range(i, k):
            if B[i, j] > 1e-8:
                best = max(best, edge_fn(s[i], s[j], m[i], m[j]))
    if best == -math.inf:
        return -lam  # all edge terms undefined: bound violated by lam
    return best - lam


def main():
    bound, k, n_starts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    edge_fn = rhs44_edge if bound == 44 else rhs46_edge
    rng = np.random.default_rng(0)
    nvar = k + k * (k + 1) // 2
    best = (math.inf, None)
    for t in range(n_starts):
        theta0 = rng.normal(0, 2, nvar) + np.concatenate(
            [np.zeros(k), rng.normal(3, 2) * np.ones(k * (k + 1) // 2)])
        res = minimize(gap, theta0, args=(k, edge_fn), method="Nelder-Mead",
                       options={"maxiter": 20000, "xatol": 1e-10, "fatol": 1e-12})
        if res.fun < best[0]:
            best = (res.fun, res.x.copy())
        if res.fun < -1e-6:
            ns, B = unpack(res.x, k)
            print(f"NEGATIVE continuous point bound {bound} k={k}: gap={res.fun}\nns={ns}\nB=\n{B}")
            np.save(f"cont_violation_{bound}_{k}.npy", res.x)
            return
    ns, B = unpack(best[1], k)
    print(f"bound {bound} k={k}: min continuous gap over {n_starts} starts = {best[0]:.3e}")
    print(f"ns={ns}\nB=\n{np.round(B,4)}")


if __name__ == "__main__":
    main()
