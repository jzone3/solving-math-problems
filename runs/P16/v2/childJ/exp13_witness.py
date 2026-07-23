"""childJ exp13: find the pooled-envelope conflict witnesses at given rho,
and record the 3-ball max arg44 (to test whether radius-3 locality separates).

Scans: all connected n<=9 + trees n<=16. Prints every edge config with
L_f(rho) > THRESH_L or U_e(rho) < THRESH_U at rho.
Usage: exp13_witness.py rho threshL threshU [n9]
"""
import subprocess
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9


def gens(include_n9):
    for n in range(3, 9):
        yield from graphs(n)
    for n in range(3, 17):
        p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g",
                             shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        for l in p.stdout:
            yield l.strip()
    if include_n9:
        yield from graphs(9)


def main():
    rho = float(sys.argv[1])
    thL, thU = float(sys.argv[2]), float(sys.argv[3])
    inc9 = len(sys.argv) > 4
    for g6 in gens(inc9):
        if not g6:
            continue
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        ne = len(E)
        a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
        R = a44.max()
        AL = line_graph_adj(E)
        s = np.array([d[i] + d[j] for i, j in E])
        z1 = AL @ (AL @ np.ones(ne))
        zs = AL @ (AL @ s)
        N1 = AL + np.eye(ne)
        N2 = N1 @ N1
        N3 = N2 @ N1
        for a in range(ne):
            rho2 = a44[N2[a] > 0].max()
            if rho2 > rho + TOL:
                continue
            rho3 = a44[N3[a] > 0].max()
            i, j = E[a]
            if z1[a] < rho - 1e-6:
                Lv = (rho * s[a] - zs[a]) / (z1[a] - rho)
                if Lv > thL - 1e-9:
                    print(f"L {Lv:.4f} {g6} R={R:.3f} rho3={rho3:.3f} "
                          f"d=({int(d[i])},{int(d[j])}) m=({m[i]:.3f},{m[j]:.3f}) "
                          f"s={int(s[a])} z1={z1[a]:.0f} zs={zs[a]:.0f}")
            elif z1[a] > rho + 1e-6:
                Uv = (rho * s[a] - zs[a]) / (z1[a] - rho)
                if Uv < thU + 1e-9:
                    print(f"U {Uv:.4f} {g6} R={R:.3f} rho3={rho3:.3f} "
                          f"d=({int(d[i])},{int(d[j])}) m=({m[i]:.3f},{m[j]:.3f}) "
                          f"s={int(s[a])} z1={z1[a]:.0f} zs={zs[a]:.0f}")


main()
