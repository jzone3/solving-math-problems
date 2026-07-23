"""SOUND resolvent certificate (Conjecture I1).

rho_0 := max_i (Bd)_i / (T_i d_i)  (crude CW upper bound: rho(P) <= rho_0).
alpha_G := kappa / max(rho_0, 1)   (kappa < 1 fixed; then alpha_G rho < 1).
h := (I - alpha P)^{-1} d  (convergent Neumann series, h >= d > 0).

Identity: (I-P) = (1/alpha)[(I-alpha P) - (1-alpha)I]  ==>
  (I-P)h = (1/alpha)(d - (1-alpha)h).
So  R(alpha):  (1-alpha) h <= d  entrywise
  ==>  Ph <= h with h > 0  ==>  rho(P) <= 1  ==>  M = diag(T)(I-P) ... PSD
(F2), since M symmetric = diag(T)^{1/2}(I - S)diag(T)^{1/2},
S = diag(T)^{-1/2} B diag(T)^{-1/2} similar to P.

Conjecture I1: R(alpha_G) holds for every connected delta>=2 graph
(kappa = 0.9 and 0.99 tested).  I1 ==> F2, and I1 is *equivalent* to F2 in
the limit kappa -> 1: if rho(P) > 1 then R(alpha) fails for EVERY
alpha in (0, 1/rho), in particular for alpha_G < 1/rho_0 <= 1/rho.

Usage: sound_resolvent.py n [res mod]
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng

n = int(sys.argv[1])
res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
KAPPAS = [0.9, 0.99]

tot = 0
fails = {k: 0 for k in KAPPAS}
bad = {k: [] for k in KAPPAS}
worst_margin = {k: np.inf for k in KAPPAS}
worst_g = {k: None for k in KAPPAS}
maxrho0 = -np.inf
for g6 in geng(n, res=res, mod=mod):
    tot += 1
    G = build(g6_to_adj(g6))
    P = G["B"] / G["T"][:, None]
    d = G["d"]
    rho0 = (P @ d / d).max()
    maxrho0 = max(maxrho0, rho0)
    I = np.eye(G["n"])
    for k in KAPPAS:
        a = k / max(rho0, 1.0)
        h = np.linalg.solve(I - a * P, d)
        margin = (d - (1 - a) * h).min()   # want >= 0
        if margin < worst_margin[k]:
            worst_margin[k] = margin
            worst_g[k] = g6
        if margin < -1e-9:
            fails[k] += 1
            if len(bad[k]) < 20:
                bad[k].append(g6)
print(f"I1 n={n} res={res}/{mod}: {tot} graphs, max rho0 {maxrho0:.6f}, "
      + ", ".join(f"kappa={k}: fails {fails[k]} worst_margin {worst_margin[k]:.3e} at {worst_g[k]}"
                  for k in KAPPAS))
for k in KAPPAS:
    for g in bad[k]:
        print(f"  BAD kappa={k}", g)
