"""Continuous relaxation v2 with the REALIZABILITY-faithful constraint that
every present entry of the quotient matrix is >= 1 (integer quotients have
entries in {0} u {1,2,...}).  For each symmetric support pattern on k cells,
minimize gap = RHS - lam_max(L_B) over B = diag(n)^{-1} S with S_ij >= 1 on
support (S symmetric), n_i > 0.  Integer quotient certificates are a subset,
so a nonnegative infimum here rules out ALL k-cell equitable-partition
refutations (of any cell sizes / entry magnitudes).

Usage: python3 continuous_opt2.py <44|46> <k> <starts_per_pattern>
"""
import itertools
import math
import sys

import numpy as np
from scipy.optimize import minimize

from search_common import rhs44_edge, rhs46_edge


def patterns(k):
    pairs = [(i, j) for i in range(k) for j in range(i, k)]
    for mask in range(1, 2 ** len(pairs)):
        sup = [pairs[t] for t in range(len(pairs)) if mask >> t & 1]
        # connectivity over k cells
        adj = {i: set() for i in range(k)}
        for i, j in sup:
            adj[i].add(j)
            adj[j].add(i)
        seen = {0}
        st = [0]
        while st:
            u = st.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    st.append(v)
        if len(seen) == k and all(adj[i] for i in range(k)):
            yield sup


def make_gap(sup, k, edge_fn):
    ne = len(sup)

    def gap(theta):
        ns = np.exp(np.clip(theta[:k], -30, 30))
        vals = 1.0 + np.exp(np.clip(theta[k:k + ne], -30, 30))  # entries >= 1
        S = np.zeros((k, k))
        for t, (i, j) in enumerate(sup):
            S[i, j] = vals[t]
            S[j, i] = vals[t]
        B = S / ns[:, None]
        # realizability: every present entry of B (both orientations) must be >= 1
        pen = 0.0
        for (i, j) in sup:
            pen += max(0.0, 1.0 - B[i, j]) ** 2 + max(0.0, 1.0 - B[j, i]) ** 2
        s = B.sum(axis=1)
        m = (B @ s) / s
        Dh = np.sqrt(ns)
        L = np.diag(s) - B
        Ls = (L * Dh[:, None]) / Dh[None, :]
        Ls = (Ls + Ls.T) / 2
        try:
            lam = np.linalg.eigvalsh(Ls)[-1]
        except np.linalg.LinAlgError:
            return 1e6
        best = -math.inf
        for (i, j) in sup:
            best = max(best, edge_fn(s[i], s[j], m[i], m[j]))
        if best == -math.inf:
            return -lam + 100.0 * pen
        return best - lam + 100.0 * pen
    return gap


def main():
    bound, k, nst = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    edge_fn = rhs44_edge if bound == 44 else rhs46_edge
    rng = np.random.default_rng(1)
    best = (math.inf, None, None)
    for sup in patterns(k):
        ne = len(sup)
        for t in range(nst):
            theta0 = rng.normal(0, 2, k + ne)
            theta0[k:] += rng.normal(2, 2)
            res = minimize(make_gap(sup, k, edge_fn), theta0, method="Nelder-Mead",
                           options={"maxiter": 8000, "fatol": 1e-13, "xatol": 1e-9})
            if res.fun < best[0]:
                best = (res.fun, sup, res.x.copy())
            if res.fun < -1e-6:
                g = make_gap(sup, k, edge_fn)
                ns = np.exp(res.x[:k])
                vals = 1 + np.exp(res.x[k:k + ne])
                print(f"NEGATIVE bound {bound} k={k} sup={sup} gap={res.fun}")
                print("ns=", ns, "entries=", vals)
                np.save(f"cont2_violation_{bound}_{k}.npy", res.x)
                return
    print(f"bound {bound} k={k}: min gap = {best[0]:.4e} at sup={best[1]}")
    ns = np.exp(best[2][:k])
    vals = 1 + np.exp(best[2][k:])
    print("ns=", np.round(ns, 5), "entries=", np.round(vals, 5))


if __name__ == "__main__":
    main()
