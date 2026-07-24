"""Dump full local data of edges where the exp6 certificate residual R > 0
(premise satisfied), n<=8 + trees<=14, to identify the resisting pattern."""
import sys
from fractions import Fraction
sys.path.insert(0, ".")
from common import geng, gentreeg, g6_adj, edge_env

def scan(graphs, label):
    for g6 in graphs:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        dd = A.sum(1)
        n = len(dd)
        eidx = {fr: a for a, fr in enumerate(E)}
        for a, (i, j) in enumerate(E):
            w = zs[a] - s[a] * z1[a]
            R = Fraction(w)
            prem = z1[a] >= a44[a]
            for k in range(n):
                for (u, v) in ((i, j), (j, i)):
                    if A[u, k] and k != v:
                        b = eidx[(min(u, k), max(u, k))]
                        R += Fraction(int(dd[k]), 2) / m[u] * (z1[a] - a44[b])
                        if a44[b] > z1[a]:
                            prem = False
            if prem and R > 0:
                x, y = int(dd[i]), int(dd[j])
                dks = sorted(int(dd[k]) for k in range(n) if A[i, k] and k != j)
                dls = sorted(int(dd[k]) for k in range(n) if A[j, k] and k != i)
                print(f"{label} {g6} e={E[a]} R={R} x={x} y={y} mi={m[i]} mj={m[j]} "
                      f"dk={dks} dl={dls} z1={z1[a]} a44={a44[a]} w={w}")

if __name__ == "__main__":
    for n in range(4, 9):
        scan(geng(n), f"geng{n}")
    for n in range(9, 15):
        scan(gentreeg(n), f"tree{n}")
