"""Sufficient condition C1 for F2:

  M = diag(d+2m-4) - A - DHD  (identity: 2sig+4-d = d+2m-4)
  x^T DHD x = sum_e w_e (sig_i x_i + sig_j x_j)^2 <= 2 sum_i sig_i^2 W_i x_i^2,
      W_i := sum_{e ni i} w_e
  A = diag(d) - L  ==>  M >= diag(2m - 4 - 2 sig^2 W) + L.

So (C1):  sig_i^2 W_i <= m_i - 2 for all i  ==>  F2.  Equality on d-regular
graphs (sig^2 W = (2d-4)^2 * d/(4d(d-2)) = d-2 = m-2).  Check exhaustively.
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng

nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
tot = fails = 0
worst = (-np.inf, None)
for n in range(3, nmax + 1):
    for g6 in geng(n):
        tot += 1
        G = build(g6_to_adj(g6))
        sig, w, edges, m = G["sig"], G["w"], G["edges"], G["m"]
        W = np.zeros(G["n"])
        for k, (i, j) in enumerate(edges):
            W[i] += w[k]; W[j] += w[k]
        viol = sig ** 2 * W - (m - 2)
        vmax = viol.max()
        if vmax > worst[0]:
            worst = (vmax, g6)
        if vmax > 1e-9:
            fails += 1
print(f"n<={nmax}: {tot} graphs, C1 failures {fails}, worst excess {worst}")
