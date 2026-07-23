"""childH exp1: SECOND-ORDER test with SHIFTED-SUM weights y_e = s_e + c.

Condition (Lemma H1): lam^2 <= max_e (A_L^2 y)_e / y_e.  Certifies Bound 44 iff
exists c > -min_e s_e with (A_L^2 y)_e <= R * y_e for all e, R = max_e arg44
(= tau^2 with tau = RHS44 - 2; NOT RHS44 -- childE pitfall).

Since y = s + c*1, A_L^2 y = A_L^2 s + c A_L^2 1: per-edge LINEAR in c =>
exact interval intersection feasibility (same style as childE exp15).
"""
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9


def ord2_sum_feasible(A, order=2):
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    if R < 0:
        return False
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    one = np.ones(len(E))
    zs, z1 = s.copy(), one.copy()
    for _ in range(order):
        zs, z1 = AL @ zs, AL @ z1
    # need: zs[e] + c*z1[e] <= R*(s[e] + c)  for all e;  c > -min s
    lo, hi = -s.min() + 1e-12, np.inf
    for a in range(len(E)):
        coef = z1[a] - R
        rhs = R * s[a] - zs[a]
        if coef > TOL:
            hi = min(hi, rhs / coef)
        elif coef < -TOL:
            lo = max(lo, rhs / coef)
        else:
            if rhs < -TOL:
                return False
    return lo <= hi + TOL


def scan(nmin, nmax, res=0, mod=1):
    tot, fails = 0, []
    for n in range(nmin, nmax + 1):
        suffix = f"{res}/{mod}" if mod > 1 and n >= 9 else ""
        if mod > 1 and n < 9 and res != 0:
            continue
        for g6 in graphs(n, suffix=suffix):
            A = g6_adj(g6)
            tot += 1
            if not ord2_sum_feasible(A):
                fails.append(g6)
    print(f"n in [{nmin},{nmax}] (res {res}/{mod}): graphs={tot}, "
          f"ord2-sum fails={len(fails)}")
    for g in fails[:200]:
        print("FAIL", g)


if __name__ == "__main__":
    if sys.argv[1] == "file":
        fails = []
        with open(sys.argv[2]) as f:
            gs = [l.strip() for l in f if l.strip()]
        for g6 in gs:
            if not ord2_sum_feasible(g6_adj(g6)):
                fails.append(g6)
        print(f"file {sys.argv[2]}: {len(gs)} graphs, ord2-sum fails={len(fails)}")
        for g in fails[:200]:
            print("FAIL", g)
    else:
        scan(int(sys.argv[1]), int(sys.argv[2]),
             int(sys.argv[3]) if len(sys.argv) > 3 else 0,
             int(sys.argv[4]) if len(sys.argv) > 4 else 1)
