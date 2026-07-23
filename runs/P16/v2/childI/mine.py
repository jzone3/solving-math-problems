"""Mine ground states: for all connected delta>=2 graphs n<=8, compute
rho = rho(diag(T)^{-1}B) and Perron h*; record hard graphs (h=d CW fails)
and near-equality graphs (rho > 0.99).  Also reproduce childF stats:
count of h=d failures and min eig of M.

Regression targets: express h*_i via local invariants d, m, sigma,
s_i = sum_{j~i} d_j = d*m, t_i = sum_{j~i}(sig_i+sig_j) w_ij, 2-step sums.
"""
import sys
import numpy as np
from common import g6_to_adj, build, perron_h, geng

nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8

hd_fail = 0
tot = 0
minmin = np.inf
hard = []      # (g6, rho) where h=d fails
neareq = []    # (g6, rho) rho>0.99 (excluding exact-equality regular graphs?)
for n in range(3, nmax + 1):
    for g6 in geng(n):
        tot += 1
        G = build(g6_to_adj(g6))
        Mh = G["M"] @ G["d"]
        if Mh.min() < -1e-9:
            hd_fail += 1
            rho, h = perron_h(G["B"], G["T"])
            hard.append((g6, rho))
        ev = np.linalg.eigvalsh(G["M"])[0]
        if ev < minmin:
            minmin = ev
        rho, h = perron_h(G["B"], G["T"])
        if rho > 0.99:
            neareq.append((g6, rho, ev))

print(f"total {tot} graphs n<=%d, h=d CW failures {hd_fail}, min eig M {minmin:.3e}" % nmax)
print(f"near-equality (rho>0.99): {len(neareq)}")
np.save("hard_g6.npy", np.array([g for g, r in hard]))
np.save("neareq_g6.npy", np.array([g for g, r, e in neareq]))
for g, r in hard[:10]:
    print("hard", g, r)
