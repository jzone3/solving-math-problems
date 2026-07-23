"""Diagonal-splitting sufficient condition for D1 (route a).

If exists diagonal Dt > 0 with  H <= Dt  and  Q - 4I <= Dt^{-1}  then
  H^{1/2}(Q-4I)H^{1/2} <= H^{1/2} Dt^{-1} H^{1/2}  and
  lam_max(H^{1/2} Dt^{-1} H^{1/2}) = lam_max(Dt^{-1/2} H Dt^{-1/2}) <= 1,
hence K >= 0 (via the exact spectral reformulation, arg>4 case).

On bipartite d-regular graphs Dt = 2(d-2) I works with equality both sides.

This script tests, for each connected delta>=2 graph:
  phi(theta) := max( lam_max(e^{-th/2} H e^{-th/2}), lam_max(e^{th/2}(Q-4I)e^{th/2}) )
  minimized over theta (BFGS, several starts).  Feasible iff min phi <= 1.
"""
import sys
import numpy as np
from scipy.optimize import minimize
from vertex_cert import graphs, g6_adj
from shifted_scan import data

def test_graph(A):
    d,m,edges,R,arg,AL = data(A)
    nn = len(d)
    if np.min(arg-4) < 1e-9:
        return None   # degenerate edge; handled separately
    w = 1.0/(arg-4)
    H = R @ np.diag(w) @ R.T
    Q = np.diag(d) + A
    QM = Q - 4*np.eye(nn)
    def phi(th):
        th = np.clip(th, -30, 30)
        s = np.exp(th/2)
        M1 = H / np.outer(s, s)
        M2 = QM * np.outer(s, s)
        return max(np.linalg.eigvalsh(M1)[-1], np.linalg.eigvalsh(M2)[-1])
    best = np.inf
    for th0 in [np.zeros(nn), np.log(np.maximum(2*(d-2),1.0)),
                np.log(d), -np.log(d)]:
        r = minimize(phi, th0, method="Nelder-Mead",
                     options={"maxiter": 4000, "fatol":1e-12, "xatol":1e-10})
        best = min(best, r.fun)
    return best

if __name__ == "__main__":
    n_lo, n_hi = int(sys.argv[1]), int(sys.argv[2])
    worst = -np.inf; worst_g = None; count=0; fails=[]
    for n in range(n_lo, n_hi+1):
        for g6 in graphs(n):
            count += 1
            b = test_graph(g6_adj(g6))
            if b is None: continue
            if b > worst: worst, worst_g = b, g6
            if b > 1 + 1e-7: fails.append((g6, round(b,6)))
    print(f"n={n_lo}..{n_hi}: {count} graphs; worst min-phi = {worst:.9f} at {worst_g}")
    print(f"infeasible (>1): {len(fails)}  {fails[:10]}")
