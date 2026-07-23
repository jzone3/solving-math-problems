"""Exp 1: which cheap Collatz-Wielandt certificates prove lam^2 <= max arg44 on n<=8?

Certificates tested per graph (R = max_e arg44; y_e = (d_i d_j)^a or phi powers):
  ord1[a]: max_e (A_L y)_e / y_e  <= sqrt(R)   (first-order CW; childB family shifted)
  ord2[a]: max_e (A_L^2 y)_e / y_e <= R        (second-order CW)
  ord4[a]: max_e (A_L^4 y)_e / y_e <= R^2      (fourth-order CW)
Report per-certificate failure counts and whether the per-graph BEST-a variant fails.
"""
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, max_arg44, line_graph_adj

AVALS = [i / 10 for i in range(11)]


def run(nmax):
    fail1 = 0
    fail2 = 0
    fail4 = 0
    tot = 0
    worst2 = []
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max_arg44(d, m, E)
            if R < 0:
                print("NEG R", g6)
                continue
            AL = line_graph_adj(E)
            tot += 1
            ok1 = ok2 = ok4 = False
            for a in AVALS:
                y = np.array([(d[i] * d[j]) ** a for i, j in E])
                z1 = AL @ y
                z2 = AL @ z1
                z4 = AL @ (AL @ z2)
                if not ok1 and (z1 / y).max() <= np.sqrt(R) + 1e-9:
                    ok1 = True
                if not ok2 and (z2 / y).max() <= R + 1e-9:
                    ok2 = True
                if not ok4 and (z4 / y).max() <= R * R + 1e-9:
                    ok4 = True
                if ok1 and ok2 and ok4:
                    break
            fail1 += not ok1
            fail2 += not ok2
            fail4 += not ok4
            if not ok2 and len(worst2) < 20:
                worst2.append(g6)
    print(f"n<= {nmax}: graphs={tot}")
    print(f"ord1 (best power a) failures: {fail1}")
    print(f"ord2 (best power a) failures: {fail2}")
    print(f"ord4 (best power a) failures: {fail4}")
    print("sample ord2 failures:", worst2)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
