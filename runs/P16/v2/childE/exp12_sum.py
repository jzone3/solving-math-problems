"""Exp 12: two 1-param families, union test:
  SUM_c:  y_e = d_i + d_j + c, c in (-2*delta, inf)   (f(x)=x+c/2 affine)
  PROD_b: y_e = (d_i+b)(d_j+b), b >= 0
CW bound (first-order, Jensen exact since f affine for SUM):
  CW(e) = [d_i psi(d_i,m_i) + d_j psi(d_j,m_j) - 2 psi_e]/psi_e + 2 <= 2+sqrt(max arg44)
Full scan; parallelizable via res/mod at n>=9.
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44


def cw_sum(d, m, E, c):
    return 2 + max((d[i] * (d[i] + m[i] + c) + d[j] * (d[j] + m[j] + c)
                    - 2 * (d[i] + d[j] + c)) / (d[i] + d[j] + c) for i, j in E)


def cw_prod(d, m, E, b):
    return 2 + max(d[i] * (m[i] + b) / (d[j] + b) + d[j] * (m[j] + b) / (d[i] + b) - 2
                   for i, j in E)


def certify(d, m, E, target):
    delta = min(d)
    for c in np.concatenate([np.linspace(-2 * delta + 0.05, 8, 160),
                             [12, 20, 50, 200]]):
        if cw_sum(d, m, E, c) <= target + 1e-9:
            return "sum", c
    for b in [0, 0.2, 0.5, 1, 1.5, 2, 3, 5, 8, 15, 40, 1e3]:
        if cw_prod(d, m, E, b) <= target + 1e-9:
            return "prod", b
    return None, None


def run(nmax, res=0, mod=1):
    tot = 0
    fails = []
    nsum = nprod = 0
    for n in range(3, nmax + 1):
        suffix = f"{res}/{mod}" if mod > 1 and n >= 9 else ""
        if mod > 1 and n < 9 and res != 0:
            continue
        for g6 in graphs(n, suffix=suffix):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            target = 2 + math.sqrt(max(R, 0))
            tot += 1
            kind, _ = certify(d, m, E, target)
            if kind == "sum":
                nsum += 1
            elif kind == "prod":
                nprod += 1
            else:
                fails.append(g6)
    print(f"n<={nmax} (res {res}/{mod}): graphs={tot} sum={nsum} prod={nprod} "
          f"FAILURES={len(fails)}")
    print(fails[:50])


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    run(nmax, res, mod)
