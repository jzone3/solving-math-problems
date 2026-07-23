"""Exp 10: second-order CW certificate lam^2 <= max_e (A_L^2 y)_e / y_e <= max arg44
with weight families y_e = (d_i+b)(d_j+b) (affine) and (d_i d_j)^a (power).
Full scan n<=nmax; also ord4 fallback count. Parallel over geng res/mod.
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

BGRID = [0, 0.2, 0.5, 1, 1.5, 2, 3, 5, 8, 15, 40, 1e3]
AGRID = [i / 10 for i in range(11)]


def check(A):
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    AL = line_graph_adj(E)
    ok2 = ok4 = False
    for b in BGRID:
        y = np.array([(d[i] + b) * (d[j] + b) for i, j in E])
        z2 = AL @ (AL @ y)
        if (z2 / y).max() <= R + 1e-9:
            ok2 = True
            break
    if not ok2:
        for a in AGRID:
            y = np.array([(d[i] * d[j]) ** a for i, j in E])
            z2 = AL @ (AL @ y)
            if (z2 / y).max() <= R + 1e-9:
                ok2 = True
                break
    if not ok2:
        for b in BGRID:
            y = np.array([(d[i] + b) * (d[j] + b) for i, j in E])
            z4 = AL @ (AL @ (AL @ (AL @ y)))
            if (z4 / y).max() <= R * R + 1e-9:
                ok4 = True
                break
    return ok2, ok4


def run(nmax, res=0, mod=1):
    tot = 0
    f2 = []
    f24 = []
    for n in range(3, nmax + 1):
        suffix = f"{res}/{mod}" if mod > 1 and n >= 8 else ""
        if mod > 1 and n < 8 and res != 0:
            continue
        for g6 in graphs(n, suffix=suffix):
            A = g6_adj(g6)
            tot += 1
            ok2, ok4 = check(A)
            if not ok2:
                f2.append(g6)
                if not ok4:
                    f24.append(g6)
    print(f"n<={nmax} (res {res}/{mod}): graphs={tot}, ord2 fails={len(f2)}, "
          f"ord2+ord4 fails={len(f24)}")
    print("ord2 fails:", f2[:40])
    print("ord2+4 fails:", f24[:40])


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    run(nmax, res, mod)
