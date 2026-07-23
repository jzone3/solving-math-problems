"""Exp 3 (Route 1): first-order edge-CW with richer concave phi families.

Need per graph: max_e CW_phi(e) <= max_e t44(e), where
  CW_phi(e) = d_i phi(m_i)/phi(d_j) + d_j phi(m_j)/phi(d_i)   (must be <= 2+sqrt(R))
Families tested (all concave positive on [1, n-1]):
  P: phi(x) = x^a, a in [0,1]                         (known: 270 delta>=2 failures)
  S: phi(x) = x/(1+t x), t >= 0 grid                  (saturating)
  L: phi(x) = min(x, c + s(x-c)) one-breakpoint       (known fail)
  T: phi(x) = min(x - 1 + b, c + s(x-c), h) two-breakpoint grid (slope1 fixed by shift)
  M: phi(x) = min over grid lines a*x+b with a,b>=0 grids (concave = min of lines)
Count graphs where NO member of each family works; and the union.
"""
import itertools
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44


def cw_ok(d, m, E, phi, target):
    try:
        vals = {}
        pts = set(list(d) + list(m))
        for p in pts:
            v = phi(p)
            if v <= 0 or not np.isfinite(v):
                return False
            vals[p] = v
        return max(d[i] * vals[m[i]] / vals[d[j]] + d[j] * vals[m[j]] / vals[d[i]]
                   for i, j in E) <= target + 1e-9
    except (ValueError, ZeroDivisionError):
        return False


def run(nmax):
    tvals = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2, 2.0, 4.0]
    avals = [i / 20 for i in range(21)]
    fails = {"P": [], "S": [], "T": [], "U": []}
    tot = 0
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            target = 2 + math.sqrt(max(R, 0))
            tot += 1
            okP = any(cw_ok(d, m, E, lambda x, a=a: x ** a, target) for a in avals)
            okS = any(cw_ok(d, m, E, lambda x, t=t: x / (1 + t * x), target)
                      for t in tvals)
            okT = False
            for c in [1.5, 2, 2.5, 3, 4, 5, 6]:
                for s in [0, 0.2, 0.4, 0.6, 0.8]:
                    for h in [2, 3, 4, 6, 100]:
                        if cw_ok(d, m, E,
                                 lambda x, c=c, s=s, h=h: min(x, c + s * (x - c), h),
                                 target):
                            okT = True
                            break
                    if okT:
                        break
                if okT:
                    break
            if not okP:
                fails["P"].append(g6)
            if not okS:
                fails["S"].append(g6)
            if not okT:
                fails["T"].append(g6)
            if not (okP or okS or okT):
                fails["U"].append(g6)
    print(f"n<={nmax}: graphs={tot}")
    for k in fails:
        print(f"family {k}: {len(fails[k])} failures", fails[k][:8])


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
