"""childJ exp2: VERTEX-SPACE second-order certificate for Bound 44.

For delta>=2: N = Q - 2I = A + D - 2I is entrywise nonnegative, symmetric,
rho(N) = rho(Q) - 2 = lam (Perron). CW second order: lam^2 <= max_v (N^2 x)_v/x_v.
Family x = d + t (t > -delta). Test: exists t with (N^2(d+t))_v <= R(d_v+t)?
Linear in t per vertex => exact interval.

Also test the same for ALL graphs using beta-shift: N_b = Q - b I with
b = min(2, delta+1)... for delta=1 use b=1: rho(N_1)=lam+1, target (tau+1)^2.

Usage: scan nmin nmax [mindeg]  |  file <path>
"""
import sys
import numpy as np

from common import graphs, g6_adj, graph_data, arg44

TOL = 1e-9


def vertex_feasible(A, beta=None):
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    if R < 0:
        return False, None
    tau = np.sqrt(R)
    delta = d.min()
    if beta is None:
        beta = 2 if delta >= 2 else 1
    target = (tau + 2 - beta) ** 2   # need rho(N_b)^2 = (lam+2-b)^2 <= this
    N = A + np.diag(d - beta)
    if (d - beta).min() < 0:
        return None, None  # N not nonnegative; certificate unsound
    x0 = d.copy()
    one = np.ones(len(d))
    z0 = N @ (N @ x0)
    z1 = N @ (N @ one)
    # need z0 + t z1 <= target*(d + t); t > -delta + ... x>0: t > -min d
    lo, hi = -d.min() + 1e-12, np.inf
    for v in range(len(d)):
        coef = z1[v] - target
        rhs = target * d[v] - z0[v]
        if coef > TOL:
            hi = min(hi, rhs / coef)
        elif coef < -TOL:
            lo = max(lo, rhs / coef)
        else:
            if rhs < -TOL:
                return False, (lo, hi)
    return lo <= hi + TOL, (lo, hi)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "file":
        gs = [l.strip() for l in open(sys.argv[2]) if l.strip()]
        fails = skip = 0
        for g6 in gs:
            ok, _ = vertex_feasible(g6_adj(g6))
            if ok is None:
                skip += 1
            elif not ok:
                fails += 1
                print("FAIL", g6)
        print(f"file: {len(gs)} graphs, fails={fails}, skipped(nonneg)={skip}")
    else:
        nmin, nmax = int(sys.argv[2]), int(sys.argv[3])
        mindeg = sys.argv[4] if len(sys.argv) > 4 else ""
        extra = f"-d{mindeg}" if mindeg else ""
        tot = fails = skip = 0
        failset = []
        for n in range(nmin, nmax + 1):
            for g6 in graphs(n, extra=extra):
                tot += 1
                ok, _ = vertex_feasible(g6_adj(g6))
                if ok is None:
                    skip += 1
                elif not ok:
                    fails += 1
                    failset.append(g6)
        print(f"scan [{nmin},{nmax}] mindeg={mindeg or 1}: {tot} graphs, "
              f"fails={fails}, skipped={skip}")
        for g in failset[:100]:
            print("FAIL", g)
