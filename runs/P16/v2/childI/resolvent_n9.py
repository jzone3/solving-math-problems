"""Exhaustive resolvent-certificate check at given n.

Certificate: with P = diag(1/T)B and fixed alpha, if the Neumann series
converges (alpha*rho(P) < 1) then h := (I-alpha P)^{-1} d > 0 and
    Mh >= 0  <=>  v := (I - alpha P)^{-1} (d - P d) >= 0,
which implies rho(P) <= 1 (F2).  We record, per graph:
  - v_min for alpha in {0.9, 0.99}
  - whether ANY alpha on a grid works
  - crude CW bound rho <= max (Pd)_i/d_i (to check rho < 1/alpha step)
Usage: resolvent_n9.py n [res mod] [alpha1,alpha2,...]
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng

n = int(sys.argv[1])
res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
alphas = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [0.9, 0.99]

tot = 0
fails = {a: 0 for a in alphas}
bad = {a: [] for a in alphas}
worst_cw = -np.inf
for g6 in geng(n, res=res, mod=mod):
    tot += 1
    G = build(g6_to_adj(g6))
    P = G["B"] / G["T"][:, None]
    d = G["d"]
    s0 = d - P @ d
    cw = 1.0 + max(0.0, -(s0 / d).min())  # max (Pd)_i/d_i
    worst_cw = max(worst_cw, cw)
    I = np.eye(G["n"])
    for a in alphas:
        try:
            v = np.linalg.solve(I - a * P, s0)
            ok = (v >= -1e-9).all()
        except np.linalg.LinAlgError:
            ok = False
        if not ok:
            fails[a] += 1
            if len(bad[a]) < 20:
                bad[a].append(g6)
print(f"resolvent n={n} res={res}/{mod}: {tot} graphs, "
      + ", ".join(f"alpha={a} fails {fails[a]}" for a in alphas)
      + f", max CW rho-bound {worst_cw:.6f}")
for a in alphas:
    for g in bad[a]:
        print(f"  BAD a={a}", g)
