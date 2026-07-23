"""Exp 13: fine-parameter union certificate scan.
For each graph: minimize over c (sum family) and b (prod family) with dense grid;
count graphs where BOTH fail. Usage: exp13_fine.py nmax [res mod]
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44


def best_sum(d, m, E, target):
    delta = min(d)
    cs = np.concatenate([np.linspace(-2 * delta + 1e-3, 10, 1200),
                         np.linspace(10, 400, 250)])
    dd = np.array([d[i] for i, j in E])
    dj = np.array([d[j] for i, j in E])
    mi = np.array([m[i] for i, j in E])
    mj = np.array([m[j] for i, j in E])
    v = []
    for c in cs:
        den = dd + dj + c
        num = dd * (dd + mi + c) + dj * (dj + mj + c) - 2 * den
        v.append((num / den).max())
    return 2 + min(v)


def best_prod(d, m, E, target):
    bs = np.concatenate([np.linspace(0, 10, 1200), np.linspace(10, 400, 250)])
    dd = np.array([d[i] for i, j in E])
    dj = np.array([d[j] for i, j in E])
    mi = np.array([m[i] for i, j in E])
    mj = np.array([m[j] for i, j in E])
    v = []
    for b in bs:
        v.append((dd * (mi + b) / (dj + b) + dj * (mj + b) / (dd + b)).max())
    return min(v)


def run(nmax, res=0, mod=1):
    tot = 0
    fails = []
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
            if best_prod(d, m, E, target) <= target + 1e-9:
                continue
            if best_sum(d, m, E, target) <= target + 1e-9:
                continue
            fails.append(g6)
    print(f"n<={nmax} (res {res}/{mod}): graphs={tot} FAILURES={len(fails)}")
    print(fails[:60])


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    run(nmax, res, mod)
