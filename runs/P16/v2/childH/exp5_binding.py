"""childH exp5: structure of binding constraints in the ord2-sum c-interval on
the hard graphs (childE 190 @ n=10 + 8 n<=9 sum-failures).

Per edge, condition is sigma_e * c <= -kappa_e with
  sigma_e = M_e - 4 s_e + 4 - R        (slope; = (A_L^2 1)_e - R)
  kappa_e = (A_L M)_e - 2 M_e + 4 s_e - R s_e   (intercept)
L = max over sigma<0 of -kappa/sigma... (lower bds), U = min over sigma>0.
Report: binding edges' (d_i,d_j,s_e) vs (delta,Delta,max s), sign pattern.
"""
import numpy as np

from common import g6_adj, graph_data, arg44, line_graph_adj


def analyze(g6):
    A = g6_adj(g6)
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    M = np.array([d[i] * (d[i] + m[i]) + d[j] * (d[j] + m[j]) for i, j in E])
    zs = AL @ (AL @ s)
    z1 = AL @ (AL @ np.ones(len(E)))
    sigma = z1 - R
    kappa = zs - R * s
    lo, hi = -s.min(), np.inf
    elo = ehi = None
    for a in range(len(E)):
        if sigma[a] > 1e-9:
            u = -kappa[a] / sigma[a]
            if u < hi:
                hi, ehi = u, a
        elif sigma[a] < -1e-9:
            l = -kappa[a] / sigma[a]
            if l > lo:
                lo, elo = l, a
    def desc(a):
        if a is None:
            return "smin-constraint"
        i, j = E[a]
        return f"(d={int(d[i])},{int(d[j])} s={int(s[a])})"
    return (f"{g6} delta={int(d.min())} Delta={int(d.max())} smax={int(s.max())} "
            f"tau+2={2+np.sqrt(R):.3f} L@{desc(elo)} U@{desc(ehi)} "
            f"[{lo:.3f},{hi:.3f}]")


if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        for g6 in open(path):
            g6 = g6.strip()
            if g6:
                print(analyze(g6))
