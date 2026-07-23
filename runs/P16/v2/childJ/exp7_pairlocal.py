"""childJ exp7: LOCAL-rho pairwise conjecture (the H-local reduction).

For every pair e,f with z1_e > z1_f and every rho in
  I = [max(rho0(e,f), z1_f), z1_e],  rho0 = max arg44 over N[e] u N[f],
require q(rho) = (rho*s_f - zs_f)(z1_e - rho) - (rho*s_e - zs_e)(z1_f - rho) >= 0.
(q >= 0 <=> L_f(rho) <= U_e(rho); at rho = z1_e it degenerates to kappa_e<=0.)

Also positivity-pair: p(rho) = (rho*s_e - zs_e) + s_f*(z1_e - rho) >= 0 on
  [max(rho0, z1_f... any f), z1_e)  (i.e. U_e >= -s_f).

If these hold for all graphs, Conjecture H follows from a purely 2-local
statement (since global R >= rho0 and R in the required range whenever the
pair (e,f) is sign-active under R).
Usage: scan nmin nmax | trees nmin nmax | file <path>
"""
import subprocess
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-7


def gen(mode, n):
    if mode == "trees":
        p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g",
                             shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        return (l.strip() for l in p.stdout)
    return graphs(n)


def quad_min(a, b, c, lo, hi):
    """min of a*r^2 + b*r + c on [lo, hi]"""
    vals = [a * lo * lo + b * lo + c, a * hi * hi + b * hi + c]
    if abs(a) > 1e-15:
        r = -b / (2 * a)
        if lo < r < hi and a > 0:
            vals.append(a * r * r + b * r + c)
    return min(vals)


def check(A):
    d, m, E = graph_data(A)
    ne = len(E)
    a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    z1 = AL @ (AL @ np.ones(ne))
    zs = AL @ (AL @ s)
    N1 = AL + np.eye(ne)
    viols = []
    for e in range(ne):
        for f in range(ne):
            if e == f or z1[e] <= z1[f]:
                continue
            rho0 = a44[(N1[e] > 0) | (N1[f] > 0)].max()
            lo = max(rho0, z1[f])
            hi = z1[e]
            if lo > hi:
                continue
            # q(rho) = (rho s_f - zs_f)(z1_e - rho) - (rho s_e - zs_e)(z1_f - rho)
            aq = -s[f] + s[e]
            bq = s[f] * z1[e] + zs[f] - s[e] * z1[f] - zs[e]
            cq = -zs[f] * z1[e] + zs[e] * z1[f]
            if quad_min(aq, bq, cq, lo, hi) < -TOL:
                viols.append(("q", e, f))
            # positivity pair: p(rho) = rho(s_e - s_f) - zs_e + s_f z1_e
            pl = lambda r: r * (s[e] - s[f]) - zs[e] + s[f] * z1[e]
            if min(pl(lo), pl(hi)) < -TOL:
                viols.append(("p", e, f))
    return viols


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "file":
        src = [("file", [l.strip() for l in open(sys.argv[2]) if l.strip()])]
    else:
        nmin, nmax = int(sys.argv[2]), int(sys.argv[3])
        src = [(n, gen(mode, n)) for n in range(nmin, nmax + 1)]
    tot = badg = 0
    for tag, it in src:
        for g6 in it:
            if not g6:
                continue
            tot += 1
            v = check(g6_adj(g6))
            if v:
                badg += 1
                if badg <= 20:
                    print("VIOL", g6, v[:4])
    print(f"total={tot}, graphs with local-pair violations={badg}")
