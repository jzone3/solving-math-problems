"""Inspect the Na-violating tree :L`EKIS`]{LY and tight n=8 graphs GCpb`o etc."""
import sys
sys.path.insert(0, ".")
from common import g6_adj, edge_env

for g6 in [":L`EKIS`]{LY", "GCpb`o", "GCXecW", "G?ovF?"]:
    A = g6_adj(g6)
    d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
    ne = len(E)
    eta = [z1[a] - rho1[a] for a in range(ne)]
    print("=" * 60)
    print(g6, "deg=", list(map(int, A.sum(1))))
    for a in range(ne):
        if z1[a] >= rho0[a]:
            nb = [b for b in range(ne) if AL[a][b]]
            se = sum(eta[b] for b in nb)
            print(f" edge {E[a]} s={s[a]} z1={z1[a]} zs={zs[a]} a44={a44[a]} "
                  f"rho0={rho0[a]} rho1={rho1[a]} D={rho0[a]*(s[a]-3)+3*z1[a]-zs[a]}"
                  f" sum_eta={se}")
            for b in nb:
                print(f"    nbr {E[b]} s={s[b]} z1={z1[b]} a44={a44[b]} "
                      f"rho1={rho1[b]} eta={eta[b]}")
