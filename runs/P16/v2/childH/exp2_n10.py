"""childH exp2: full n=10 scan of the ord2-sum conjecture.

Fast path: first-order sum certificate (exact interval, childE exp15) -- if it
holds with weight y = s + c then the ord2 test holds with the same y
(A_L(A_L y) <= tau A_L y <= tau^2 y), so no need to build the line graph.
Fallback: exact ord2-sum interval test (exp1).
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44
from exp1_ord2sum import ord2_sum_feasible

EPS = 1e-9


def sum_feasible(di, dj, mi, mj, tau):
    T = tau + 2
    s = di + dj
    alpha = di * (di + mi) + dj * (dj + mj) - T * s
    beta = s - T
    lo = -float(s.min()) + 1e-9
    hi = math.inf
    for a, b in zip(alpha, beta):
        if abs(b) < 1e-12:
            if a > EPS:
                return False
        elif b < 0:
            lo = max(lo, a / (-b))
        else:
            hi = min(hi, -a / b)
    return lo <= hi + EPS


def run(n, res, mod):
    tot = ord1 = ord2 = 0
    fails = []
    for g6 in graphs(n, suffix=f"{res}/{mod}"):
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        di = np.array([d[i] for i, j in E])
        dj = np.array([d[j] for i, j in E])
        mi = np.array([m[i] for i, j in E])
        mj = np.array([m[j] for i, j in E])
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        tau = math.sqrt(max(R, 0))
        tot += 1
        if sum_feasible(di, dj, mi, mj, tau):
            ord1 += 1
        elif ord2_sum_feasible(A):
            ord2 += 1
        else:
            fails.append(g6)
    print(f"n={n} res {res}/{mod}: graphs={tot} ord1={ord1} ord2={ord2} "
          f"FAILS={len(fails)}")
    for g in fails[:100]:
        print("FAIL", g)


if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
