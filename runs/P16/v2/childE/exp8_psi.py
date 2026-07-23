"""Exp 8: generalized edge-CW with y_e = psi(d_i, d_j), psi symmetric, positive,
concave in each variable. Bound: mu <= rho(Q) <= 2 + max_e
  [d_i psi(d_i, m_i) + d_j psi(d_j, m_j) - 2 psi(d_i, d_j)] / psi(d_i, d_j).
(Jensen in the second argument needs concavity in each variable.)

Families:
  Bilin: psi = xy + c(x+y) + e   (linear in each var => concave; need psi>0)
  Sum:   psi = x + y + c
Check the n=9 hard set and then full n<=8 / n<=9.
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44

HARD = """H?`reQF H?ovE_N HCOf@pR HCOf?zB HCOedPb HCOedHb HCOebIb HCOe`ZB
HCQf@oN HCQe`r` HCQdbPF HCQdar` HCQb`pw HCQbRbo HCQfRjF HCQerjF HCQfbjF
HCRdrrF HCpf`zF HCpdrjF""".split()

CGRID = [0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 6, 10, 20, 50, 1e3]
EGRID = [0, 0.5, 1, 2, 4, 8, 16, 40, 100, 1e3, 1e6]


def cw_psi(d, m, E, psi):
    vals = []
    for i, j in E:
        pe = psi(d[i], d[j])
        if pe <= 0:
            return math.inf
        pi = psi(d[i], m[i])
        pj = psi(d[j], m[j])
        if pi <= 0 or pj <= 0:
            return math.inf
        vals.append((d[i] * pi + d[j] * pj - 2 * pe) / pe)
    return 2 + max(vals)


def works(d, m, E, target):
    for c in CGRID:
        for e in EGRID:
            if cw_psi(d, m, E, lambda x, y, c=c, e=e: x * y + c * (x + y) + e) \
                    <= target + 1e-9:
                return True, ("bilin", c, e)
    for c in [0, 0.5, 1, 2, 4, 8, 20, 100]:
        if cw_psi(d, m, E, lambda x, y, c=c: x + y + c) <= target + 1e-9:
            return True, ("sum", c)
    return False, None


def run_hard():
    for g6 in HARD:
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        target = 2 + math.sqrt(max(R, 0))
        ok, w = works(d, m, E, target)
        print(g6, "OK" if ok else "FAIL", w)


def run_all(nmax):
    tot = 0
    fails = []
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            target = 2 + math.sqrt(max(R, 0))
            tot += 1
            ok, _ = works(d, m, E, target)
            if not ok:
                fails.append(g6)
    print(f"n<={nmax}: graphs={tot}, psi-family failures: {len(fails)}")
    print(fails[:30])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "hard":
        run_hard()
    else:
        run_all(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
