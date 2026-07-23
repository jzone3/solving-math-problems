"""childJ exp3: do FIXED values of c work for all trees? (c=-2 <=> y = D_L).

Also reports, per tree, the exact feasible interval [lo,hi] to see its shape.
Usage: python3 exp3_trees_fixedc.py nmin nmax c1 c2 ...
"""
import subprocess
import sys

import numpy as np

from common import g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9


def trees(n):
    p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g", shell=True,
                         stdout=subprocess.PIPE, text=True)
    for l in p.stdout:
        yield l.strip()


def check(A, cs):
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    zs = AL @ (AL @ s)
    z1 = AL @ (AL @ np.ones(len(E)))
    smin = s.min()
    res = []
    for c in cs:
        if c <= -smin:
            res.append(False)
            continue
        lhs = zs + c * z1
        res.append(bool((lhs <= R * (s + c) + TOL).all()))
    # interval
    lo, hi = -smin, np.inf
    for a in range(len(E)):
        coef = z1[a] - R
        rhs = R * s[a] - zs[a]
        if coef > TOL:
            hi = min(hi, rhs / coef)
        elif coef < -TOL:
            lo = max(lo, rhs / coef)
    return res, lo, hi, smin


if __name__ == "__main__":
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
    cs = [float(x) for x in sys.argv[3:]]
    fails = {c: 0 for c in cs}
    tot = 0
    lo_max, hi_min = -np.inf, np.inf
    worst = None
    for n in range(nmin, nmax + 1):
        for g6 in trees(n):
            if not g6:
                continue
            tot += 1
            res, lo, hi, smin = check(g6_adj(g6), cs)
            for c, ok in zip(cs, res):
                if not ok:
                    fails[c] += 1
            if lo > lo_max:
                lo_max = lo
            if hi < hi_min:
                hi_min, worst = hi, g6
    print(f"trees [{nmin},{nmax}]: {tot}")
    for c in cs:
        print(f"  c={c}: fails={fails[c]}")
    print(f"  max lo over trees = {lo_max}, min hi = {hi_min} (at {worst})")
