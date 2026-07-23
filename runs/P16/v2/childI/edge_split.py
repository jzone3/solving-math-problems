"""Per-edge split test.  For x >= 0 (enough: M is a Z-matrix, so
x^T M x >= |x|^T M |x|), F2 follows from the per-edge inequality

  F_e(x_i, x_j) = c_i^e x_i^2 + c_j^e x_j^2 - 2 x_i x_j
                  - w_e (sig_i x_i + sig_j x_j)^2  >= 0,

with the allocation c_i^e := 1 + (2 d_j - 4)/d_i, which sums over edges at i
to the diagonal M_ii + sig_i^2 sum w = d_i + 2 m_i - 4 (identity:
sum_{j~i} (2d_j-4)/d_i = 2 m_i - 4).  On d-regular graphs
F_e = (2d-2)/d (x_i-x_j)^2 -- equality manifold preserved.

The 2x2 block has nonpositive off-diagonal, so copositive <=> PSD:
need c_i - w sig_i^2 >= 0 and det >= 0.  Check all edges of all connected
delta>=2 graphs up to n.
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng

nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
badcnt = 0
tot = 0
worst = (np.inf, None)
for n in range(3, nmax + 1):
    for g6 in geng(n):
        tot += 1
        G = build(g6_to_adj(g6))
        d, sig, w, edges = G["d"], G["sig"], G["w"], G["edges"]
        bad = False
        for k, (i, j) in enumerate(edges):
            ci = 1 + (2 * d[j] - 4) / d[i]
            cj = 1 + (2 * d[i] - 4) / d[j]
            a = ci - w[k] * sig[i] ** 2
            b = cj - w[k] * sig[j] ** 2
            o = -1 - w[k] * sig[i] * sig[j]
            det = a * b - o * o
            crit = min(a, b, det)
            if crit < worst[0]:
                worst = (crit, (g6, i, j))
            if crit < -1e-9:
                bad = True
        if bad:
            badcnt += 1
print(f"n<= {nmax}: {tot} graphs, per-edge-split failures on {badcnt} graphs; worst crit {worst}")
