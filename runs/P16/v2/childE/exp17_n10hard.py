"""Exp 17: collect the n=10 two-family failures into n10_fails.txt, then test:
  (a) ord2 certificate (affine + power weights) on them;
  (b) 3-param bilinear psi = xy + c(x+y) + e (first-order, exact since linear
      in each variable) with fine grids;
  (c) sum-family with general concave f via SLSQP (additive psi).
"""
import glob
import math
import re
import sys

import numpy as np

from common import g6_adj, graph_data, arg44, line_graph_adj
from exp15_exact import sum_feasible, prod_feasible


def collect():
    g6s = []
    for fn in glob.glob("exp15_n10_*.log"):
        txt = open(fn).read()
        m = re.search(r"\[(.*)\]", txt, re.S)
        if m and m.group(1).strip():
            g6s += [s.strip().strip("'") for s in m.group(1).split(",")]
    still = []
    for g6 in g6s:
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        di = np.array([d[i] for i, j in E])
        dj = np.array([d[j] for i, j in E])
        mi = np.array([m[i] for i, j in E])
        mj = np.array([m[j] for i, j in E])
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        tau = math.sqrt(max(R, 0))
        if not (sum_feasible(di, dj, mi, mj, tau, min(d))
                or prod_feasible(di, dj, mi, mj, tau)):
            still.append(g6)
    with open("n10_fails.txt", "w") as f:
        f.write("\n".join(still))
    print("collected", len(still))
    return still


def test(still):
    okord2 = okbilin = 0
    bad = []
    for g6 in still:
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        tau = math.sqrt(max(R, 0))
        AL = line_graph_adj(E)
        o2 = False
        for b in np.concatenate([np.linspace(0, 10, 101), [20, 50, 1e3]]):
            y = np.array([(d[i] + b) * (d[j] + b) for i, j in E])
            if ((AL @ (AL @ y)) / y).max() <= R + 1e-9:
                o2 = True
                break
        if not o2:
            for a in np.linspace(0, 1, 21):
                y = np.array([(d[i] * d[j]) ** a for i, j in E])
                if ((AL @ (AL @ y)) / y).max() <= R + 1e-9:
                    o2 = True
                    break
        okord2 += o2
        bl = False
        for c in np.concatenate([np.linspace(-1, 8, 46), [12, 25, 60]]):
            for e in np.concatenate([np.linspace(-8, 20, 57), [50, 200]]):
                y = np.array([d[i] * d[j] + c * (d[i] + d[j]) + e for i, j in E])
                if (y <= 0).any():
                    continue
                yi = np.array([d[i] * m[i] + c * (d[i] + m[i]) + e for i, j in E])
                yj = np.array([d[j] * m[j] + c * (d[j] + m[j]) + e for i, j in E])
                di = np.array([d[i] for i, j in E])
                dj = np.array([d[j] for i, j in E])
                cw = (di * yi + dj * yj - 2 * y) / y
                if cw.max() <= tau + 1e-9:
                    bl = True
                    break
            if bl:
                break
        okbilin += bl
        if not (o2 or bl):
            bad.append(g6)
    print(f"of {len(still)}: ord2 OK {okord2}, bilinear OK {okbilin}, "
          f"neither: {len(bad)}")
    print(bad[:30])


if __name__ == "__main__":
    still = collect()
    test(still)
