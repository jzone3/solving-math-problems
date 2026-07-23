"""childH exp4: does the FIXED weight y_e = s_e - 1 (c = -1) pass the ord2 test
   (A_L^2 y)_e <= R * y_e, R = max arg44, on ALL connected graphs?
Scan exhaustively; report failures and their feasible c-intervals.
"""
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj
from exp3_cvalues import interval

TOL = 1e-9
C = -1.0


def fixed_ok(A, c=C):
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    AL = line_graph_adj(E)
    y = np.array([d[i] + d[j] + c for i, j in E])
    return (AL @ (AL @ y) <= R * y + TOL).all()


if __name__ == "__main__":
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
    res = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    mod = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    tot, fails = 0, []
    for n in range(nmin, nmax + 1):
        suffix = f"{res}/{mod}" if mod > 1 and n >= 9 else ""
        if mod > 1 and n < 9 and res != 0:
            continue
        for g6 in graphs(n, suffix=suffix):
            A = g6_adj(g6)
            tot += 1
            if not fixed_ok(A):
                fails.append(g6)
    print(f"c={C}: n in [{nmin},{nmax}] res {res}/{mod}: graphs={tot} "
          f"fails={len(fails)}")
    for g in fails[:60]:
        lo, hi, ok, R = interval(g6_adj(g))
        print(f"FAIL {g}  c-interval [{lo:.4f},{hi:.4f}]")
