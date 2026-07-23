"""childJ exp8: envelope of feasible c-intervals as a function of R.

For each graph record (R, lo, hi). If sup{lo : R'<=R} <= inf{hi : R'>=R} ...
More precisely a universal c(R) exists iff for every pair of graphs G1,G2 with
R1 = R2 = R: lo(G1) <= hi(G2). Practically: bucket by R value and check
max lo <= min hi per bucket; and print the envelope curves sorted by R.

Decoupled per-edge version: for EVERY edge f (any graph) with z1_f < R:
L_f(R) <= phi(R), and every edge e with z1_e > R: phi(R) <= U_e(R), where R
ranges over [local rho0, ...] — here we record per-edge curves at the graph's
own R only (plus the pooled per-rho envelope from all edges, sweeping rho).

Usage: pooled nmin nmax [trees]  -> per-edge pooled envelope over rho grid
       graphs nmin nmax [trees]  -> per-graph (R, lo, hi) buckets
"""
import subprocess
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9


def gen(mode, n):
    if mode == "trees":
        p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g",
                             shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        return (l.strip() for l in p.stdout)
    return graphs(n)


def edge_data(A):
    d, m, E = graph_data(A)
    ne = len(E)
    a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    z1 = AL @ (AL @ np.ones(ne))
    zs = AL @ (AL @ s)
    return a44, s, z1, zs


def main():
    mode2 = sys.argv[1]
    nmin, nmax = int(sys.argv[2]), int(sys.argv[3])
    mode = "trees" if len(sys.argv) > 4 else "scan"
    if mode2 == "graphs":
        buckets = {}
        for n in range(nmin, nmax + 1):
            for g6 in gen(mode, n):
                if not g6:
                    continue
                a44, s, z1, zs = edge_data(g6_adj(g6))
                R = a44.max()
                lo, hi = -s.min(), np.inf
                for a in range(len(s)):
                    coef = z1[a] - R
                    rhs = R * s[a] - zs[a]
                    if coef > TOL:
                        hi = min(hi, rhs / coef)
                    elif coef < -TOL:
                        lo = max(lo, rhs / coef)
                key = round(R, 6)
                cur = buckets.get(key, (-np.inf, np.inf, None, None))
                buckets[key] = (max(cur[0], lo), min(cur[1], hi),
                                g6 if lo > cur[0] else cur[2],
                                g6 if hi < cur[1] else cur[3])
        bad = 0
        for R in sorted(buckets):
            lo, hi, glo, ghi = buckets[R]
            flag = ""
            if lo > hi + TOL:
                bad += 1
                flag = f"  <-- CONFLICT lo@{glo} hi@{ghi}"
            print(f"R={R:10.4f} maxlo={lo:9.4f} minhi={hi:9.4f}{flag}")
        print(f"buckets={len(buckets)}, conflicts={bad}")
    else:
        # pooled per-edge envelope on a rho grid
        rho_grid = np.arange(0.5, 80.01, 0.25)
        Lsup = np.full(len(rho_grid), -np.inf)
        Uinf = np.full(len(rho_grid), np.inf)
        for n in range(nmin, nmax + 1):
            for g6 in gen(mode, n):
                if not g6:
                    continue
                a44, s, z1, zs = edge_data(g6_adj(g6))
                AL = line_graph_adj(s.__len__() and [(0,0)]) if False else None
                # local rho0: 2-ball max arg44 per edge
                A = g6_adj(g6)
                d, m, E = graph_data(A)
                ALm = line_graph_adj(E)
                N2 = (ALm + np.eye(len(E))) @ (ALm + np.eye(len(E)))
                rho0 = np.array([a44[N2[a] > 0].max() for a in range(len(E))])
                for a in range(len(E)):
                    mask = rho_grid >= rho0[a] - TOL
                    up = mask & (z1[a] > rho_grid + 1e-6)
                    dn = mask & (z1[a] < rho_grid - 1e-6)
                    if up.any():
                        Uv = (rho_grid[up] * s[a] - zs[a]) / (z1[a] - rho_grid[up])
                        Uinf[up] = np.minimum(Uinf[up], Uv)
                    if dn.any():
                        Lv = (rho_grid[dn] * s[a] - zs[a]) / (z1[a] - rho_grid[dn])
                        Lsup[dn] = np.maximum(Lsup[dn], Lv)
        bad = (Lsup > Uinf + 1e-7).sum()
        print(f"grid pts={len(rho_grid)}, conflicts={bad}")
        for k in range(0, len(rho_grid), 8):
            print(f"rho={rho_grid[k]:7.2f} Lsup={Lsup[k]:9.4f} Uinf={Uinf[k]:9.4f}"
                  + ("  CONFLICT" if Lsup[k] > Uinf[k] + 1e-7 else ""))


main()
