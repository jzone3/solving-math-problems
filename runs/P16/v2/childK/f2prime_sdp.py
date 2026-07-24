"""Conjecture F2' (exists-D rescue): for every connected delta>=2 graph there
is a diagonal s >= 0 with M(s) = 2 diag(s) + 4I - Q - diag(s) H diag(s) >= 0.

Feasibility is an SDP via the Schur complement LMI (childF section 5(ii)):
  N(s) = [[2 diag(s) + 4I - Q,  diag(s) R diag(sqrt(w))],
          [ .T,                 I_E                    ]] >= 0.
(Schur: N >= 0 and I_E > 0  <=>  2D+4I-Q - D R w R^T D = M(s) >= 0.)

Exhaustive n <= 7 (583 graphs) + all failing families + windmills/wheels.
Solve: maximize t s.t. N(s) - t*I >= 0, s >= 0. Feasible iff opt t >= 0.
"""
import sys
import numpy as np
import cvxpy as cp
from common import g6_to_adj, build, geng
from graphs import windmill, wheel, hub_plus_cycles, hub_plus_cliques


def sdp_margin(A, solver="SCS"):
    bd = build(A)
    n, Q, w, edges = bd["n"], bd["Q"], bd["w"], bd["edges"]
    E = len(edges)
    R = np.zeros((n, E))
    for kk, (i, j) in enumerate(edges):
        R[i, kk] = R[j, kk] = 1
    Rw = R * np.sqrt(w)
    s = cp.Variable(n, nonneg=True)
    t = cp.Variable()
    top = 2 * cp.diag(s) + 4 * np.eye(n) - Q
    off = cp.diag(s) @ Rw
    N = cp.bmat([[top, off], [off.T, np.eye(E)]])
    prob = cp.Problem(cp.Maximize(t), [N - t * np.eye(n + E) >> 0])
    try:
        prob.solve(solver=solver, verbose=False)
        return t.value
    except Exception as ex:
        return None


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "small"
    if mode == "families":
        for name, A in [("F_14", windmill(14)), ("F_25", windmill(25)),
                        ("F_60", windmill(60)), ("W_40", wheel(40)),
                        ("W_100", wheel(100)), ("hub15C4", hub_plus_cycles(15, 4)),
                        ("hub25K3", hub_plus_cliques(25, 3))]:
            print(name, "sdp margin:", sdp_margin(A), flush=True)
    else:
        nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        bad, tot = [], 0
        worst = 1e18
        for n in range(3, nmax + 1):
            for g6 in geng(n):
                A = g6_to_adj(g6)
                v = sdp_margin(A)
                tot += 1
                if v is None or v < -1e-6:
                    bad.append((g6, v))
                if v is not None:
                    worst = min(worst, v)
            print(f"n={n} done tot={tot} bad={len(bad)} worst_margin={worst:.3e}",
                  flush=True)
        print("bad:", bad[:30])
