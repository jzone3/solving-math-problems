"""childJ exp1: exact (Fraction) interval structure for the ord2-sum test.

Per edge e: sigma_e * c <= -kappa_e, sigma_e = (A_L^2 1)_e - R,
kappa_e = (A_L^2 s)_e - R s_e; plus c > -min s.
Reports lo/hi, binding edges with full local data, slack, sign census.
Modes:
  file <path>      analyze g6 list, verbose per graph
  scan nmin nmax   census over connected graphs (silent unless infeasible)
  trees nmin nmax  census over trees
"""
import sys
from fractions import Fraction as Fr

import numpy as np

from common import graphs, g6_adj, graph_data, line_graph_adj


def exact_data(A):
    n = A.shape[0]
    Ai = A.astype(int)
    d = Ai.sum(1)
    nbr = [np.nonzero(Ai[i])[0] for i in range(n)]
    m = [Fr(int(sum(d[k] for k in nbr[i])), int(d[i])) for i in range(n)]
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if Ai[i, j]]
    return d, m, E


def arg44F(di, dj, mi, mj):
    return 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)


def interval(A):
    """Return (R, lo, hi, elo, ehi, E, d, m, s, sigma, kappa); lo/hi Fractions
    or None (elo None means the -min s constraint binds below)."""
    d, m, E = exact_data(A)
    R = max(arg44F(int(d[i]), int(d[j]), m[i], m[j]) for i, j in E)
    AL = line_graph_adj(E).astype(int)
    s = [Fr(int(d[i] + d[j])) for i, j in E]
    one = [Fr(1)] * len(E)

    def mul(x):
        return [sum(AL[a, b] * x[b] for b in np.nonzero(AL[a])[0]) for a in range(len(E))]

    z1 = mul(mul(one))
    zs = mul(mul(s))
    sigma = [z1[a] - R for a in range(len(E))]
    kappa = [zs[a] - R * s[a] for a in range(len(E))]
    lo, hi = -min(s), None
    elo = ehi = None
    infeas_eq = []
    for a in range(len(E)):
        if sigma[a] > 0:
            u = -kappa[a] / sigma[a]
            if hi is None or u < hi:
                hi, ehi = u, a
        elif sigma[a] < 0:
            l = -kappa[a] / sigma[a]
            if l > lo:
                lo, elo = l, a
        elif kappa[a] > 0:
            infeas_eq.append(a)
    return dict(R=R, lo=lo, hi=hi, elo=elo, ehi=ehi, E=E, d=d, m=m, s=s,
                sigma=sigma, kappa=kappa, infeas_eq=infeas_eq)


def feasible(A):
    r = interval(A)
    if r["infeas_eq"]:
        return False, r
    if r["hi"] is None:
        return True, r
    # need lo < hi allowed equality? constraint is c > -min s strictly when elo None
    if r["elo"] is None:
        return r["lo"] < r["hi"], r
    return r["lo"] <= r["hi"], r


def describe(g6):
    A = g6_adj(g6)
    ok, r = feasible(A)
    E, d, m, s = r["E"], r["d"], r["m"], r["s"]

    def desc(a, tag):
        if a is None:
            return f"{tag}=-mins"
        i, j = E[a]
        return (f"{tag}@(d={int(d[i])},{int(d[j])};m={m[i]},{m[j]};s={s[a]})")

    slack = None if r["hi"] is None else r["hi"] - r["lo"]
    return (f"{g6} n={A.shape[0]} feas={ok} R={r['R']} "
            f"smax={max(s)} tau+2~{2 + float(r['R']) ** .5:.3f} "
            f"{desc(r['elo'], 'L')} {desc(r['ehi'], 'U')} "
            f"lo={r['lo']} hi={r['hi']} slack={slack}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "file":
        for g6 in open(sys.argv[2]):
            g6 = g6.strip()
            if g6:
                print(describe(g6))
    else:
        import subprocess
        nmin, nmax = int(sys.argv[2]), int(sys.argv[3])
        tot = fails = 0
        for n in range(nmin, nmax + 1):
            if mode == "trees":
                p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g",
                                     shell=True, stdout=subprocess.PIPE, text=True)
                gen = (l.strip() for l in p.stdout)
            else:
                gen = graphs(n)
            for g6 in gen:
                tot += 1
                ok, _ = feasible(g6_adj(g6))
                if not ok:
                    fails += 1
                    print("FAIL", g6)
        print(f"{mode} [{nmin},{nmax}]: {tot} graphs, {fails} infeasible")
