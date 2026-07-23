"""childH exp3: which fixed c work for the ord2-sum test? Probe c in
{-2, 0, 2, 5, 10, inf} on the hard sets (childE n10_fails + first-order-sum
failures at n<=9) and report per-graph feasible c-intervals.
c = inf limit: condition (A_L^2 1)_e = M_e - 4 s_e + 4 <= R for all e.
"""
import sys

import numpy as np

from common import g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9


def interval(A):
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    zs = AL @ (AL @ s)
    z1 = AL @ (AL @ np.ones(len(E)))
    lo, hi = -s.min(), np.inf
    ok = True
    for a in range(len(E)):
        coef = z1[a] - R
        rhs = R * s[a] - zs[a]
        if coef > TOL:
            hi = min(hi, rhs / coef)
        elif coef < -TOL:
            lo = max(lo, rhs / coef)
        elif rhs < -TOL:
            ok = False
    return (lo, hi, ok, R)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(f"== {path}")
        for g6 in open(path):
            g6 = g6.strip()
            if not g6:
                continue
            lo, hi, ok, R = interval(g6_adj(g6))
            print(f"{g6}  c in [{lo:.4f}, {hi:.4f}] ok={ok and lo <= hi + TOL} R={R:.3f}")
