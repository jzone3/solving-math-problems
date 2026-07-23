"""childJ exp9: extremal edge configurations of the pooled envelopes.

At each rho gridpoint, record the arg-extremal configurations:
 Lsup(rho) = max over edges f (2-ball arg44 <= rho, z1_f < rho) of L_f(rho)
 Uinf(rho) = min over edges e (2-ball arg44 <= rho, z1_e > rho) of U_e(rho)
and print the profiles (d_i,d_j,m_i,m_j,s,z1,zs,g6).

Usage: nmin nmax [trees] — pools graphs and trees classes together if 'both'.
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


def main():
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
    modes = ["scan", "trees"] if (len(sys.argv) > 3 and sys.argv[3] == "both") \
        else (["trees"] if len(sys.argv) > 3 else ["scan"])
    rho_grid = np.arange(1.0, 60.01, 0.5)
    Lsup = np.full(len(rho_grid), -np.inf)
    Uinf = np.full(len(rho_grid), np.inf)
    Larg = [None] * len(rho_grid)
    Uarg = [None] * len(rho_grid)
    for mode in modes:
        for n in range(nmin, nmax + 1):
            for g6 in gen(mode, n):
                if not g6:
                    continue
                A = g6_adj(g6)
                d, m, E = graph_data(A)
                ne = len(E)
                a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
                AL = line_graph_adj(E)
                s = np.array([d[i] + d[j] for i, j in E])
                z1 = AL @ (AL @ np.ones(ne))
                zs = AL @ (AL @ s)
                N1 = AL + np.eye(ne)
                N2 = N1 @ N1
                rho0 = np.array([a44[N2[a] > 0].max() for a in range(ne)])
                for a in range(ne):
                    i, j = E[a]
                    prof = (f"d=({int(d[i])},{int(d[j])}) m=({m[i]:.2f},{m[j]:.2f}) "
                            f"s={int(s[a])} z1={z1[a]:.0f} zs={zs[a]:.0f} {g6}")
                    mask = rho_grid >= rho0[a] - TOL
                    up = mask & (z1[a] > rho_grid + 1e-6)
                    dn = mask & (z1[a] < rho_grid - 1e-6)
                    if up.any():
                        Uv = (rho_grid[up] * s[a] - zs[a]) / (z1[a] - rho_grid[up])
                        idxs = np.where(up)[0]
                        better = Uv < Uinf[idxs] - 1e-12
                        for k, b in zip(idxs, better):
                            if b:
                                Uarg[k] = prof
                        Uinf[idxs] = np.minimum(Uinf[idxs], Uv)
                    if dn.any():
                        Lv = (rho_grid[dn] * s[a] - zs[a]) / (z1[a] - rho_grid[dn])
                        idxs = np.where(dn)[0]
                        better = Lv > Lsup[idxs] + 1e-12
                        for k, b in zip(idxs, better):
                            if b:
                                Larg[k] = prof
                        Lsup[idxs] = np.maximum(Lsup[idxs], Lv)
    for k in range(len(rho_grid)):
        c = "  CONFLICT" if Lsup[k] > Uinf[k] + 1e-7 else ""
        print(f"rho={rho_grid[k]:6.2f} L={Lsup[k]:9.4f} U={Uinf[k]:9.4f}{c}")
        print(f"    Larg: {Larg[k]}")
        print(f"    Uarg: {Uarg[k]}")


main()
