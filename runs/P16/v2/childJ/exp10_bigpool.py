"""childJ exp10: large-scale pooled envelope computation, saved to .npy.

Grid rho in [1,200] step 0.25. For each class, computes Lsup/Uinf arrays and
saves; combine.py merges all and checks pointwise separation.
Usage: exp10_bigpool.py scan n res mod out.npz | trees n out.npz | file path out.npz
"""
import subprocess
import sys

import numpy as np

from common import g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9
RHO = np.arange(1.0, 200.01, 0.25)


def process(g6, Lsup, Uinf):
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
    for a in range(ne):
        rho0 = a44[N2[a] > 0].max()
        mask = RHO >= rho0 - TOL
        up = mask & (z1[a] > RHO + 1e-6)
        dn = mask & (z1[a] < RHO - 1e-6)
        if up.any():
            Uv = (RHO[up] * s[a] - zs[a]) / (z1[a] - RHO[up])
            Uinf[up] = np.minimum(Uinf[up], Uv)
        if dn.any():
            Lv = (RHO[dn] * s[a] - zs[a]) / (z1[a] - RHO[dn])
            Lsup[dn] = np.maximum(Lsup[dn], Lv)


def main():
    mode = sys.argv[1]
    Lsup = np.full(len(RHO), -np.inf)
    Uinf = np.full(len(RHO), np.inf)
    if mode == "file":
        it = (l.strip() for l in open(sys.argv[2]))
        out = sys.argv[3]
    elif mode == "trees":
        n = int(sys.argv[2])
        out = sys.argv[3]
        p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g",
                             shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        it = (l.strip() for l in p.stdout)
    else:
        n, res, mod = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        out = sys.argv[5]
        suffix = f"{res}/{mod}" if mod > 1 else ""
        p = subprocess.Popen(f"nauty-geng -qc {n} {suffix}", shell=True,
                             stdout=subprocess.PIPE, text=True)
        it = (l.strip() for l in p.stdout)
    tot = 0
    for g6 in it:
        if not g6:
            continue
        tot += 1
        process(g6, Lsup, Uinf)
    np.savez(out, L=Lsup, U=Uinf, rho=RHO)
    print(f"{out}: {tot} graphs done")


if __name__ == "__main__":
    main()
