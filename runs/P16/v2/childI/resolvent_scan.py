"""Resolvent certificate h_alpha := (I - alpha P)^{-1} d = sum alpha^k P^k d
(positive whenever alpha < 1/rho; entrywise nonneg Neumann series).
Since (I-P) commutes with the resolvent, M h >= 0  <=>  (I-alpha P)^{-1}(d - Pd) >= 0.

Test fixed alphas and per-graph best alpha (grid).  Also Krylov-cone LP:
h = a*d + b*Pd + c*P2d, a,b,c >= 0 (h>0 automatic), Bh <= Th via LP.
Usage: resolvent_scan.py nmax
"""
import sys
import numpy as np
from scipy.optimize import linprog
from common import g6_to_adj, build, geng

ALPHAS = [0.5, 0.75, 0.9, 0.99]


def main(nmax):
    tot = 0
    fail_fixed = {a: 0 for a in ALPHAS}
    fail_best = 0
    fail_krylov = {2: 0, 3: 0, 4: 0}
    bad_best, bad_kry = [], []
    for n in range(3, nmax + 1):
        for g6 in geng(n):
            tot += 1
            G = build(g6_to_adj(g6))
            P = G["B"] / G["T"][:, None]
            d = G["d"]
            slack0 = d - P @ d
            n_ = G["n"]
            okbest = False
            for a in np.arange(0.05, 1.0, 0.05):
                try:
                    v = np.linalg.solve(np.eye(n_) - a * P, slack0)
                    h = np.linalg.solve(np.eye(n_) - a * P, d)
                except np.linalg.LinAlgError:
                    continue
                ok = (v >= -1e-9).all() and (h > 0).all()
                aa = min(ALPHAS, key=lambda x: abs(x - a))
                if abs(aa - a) < 1e-9 and not ok:
                    fail_fixed[aa] += 1
                if ok:
                    okbest = True
            for a in ALPHAS:
                if a not in np.arange(0.05, 1.0, 0.05):
                    try:
                        v = np.linalg.solve(np.eye(n_) - a * P, slack0)
                        h = np.linalg.solve(np.eye(n_) - a * P, d)
                        if (v >= -1e-9).all() and (h > 0).all():
                            pass
                        else:
                            fail_fixed[a] += 1
                    except np.linalg.LinAlgError:
                        fail_fixed[a] += 1
            if not okbest:
                fail_best += 1
                bad_best.append(g6)
            # Krylov cone LP
            vs = [d]
            for _ in range(4):
                vs.append(P @ vs[-1])
            for K in (2, 3, 4):
                Vs = np.array(vs[:K + 1]).T          # n x (K+1)
                Acon = (P @ Vs) - Vs                 # want Acon @ c <= 0
                res = linprog(np.zeros(K + 1), A_ub=Acon, b_ub=np.zeros(n_),
                              A_eq=np.ones((1, K + 1)), b_eq=[1.0],
                              bounds=[(0, None)] * (K + 1), method="highs")
                if not res.success:
                    fail_krylov[K] += 1
                    if K == 4:
                        bad_kry.append(g6)
    print(f"total {tot} n<={nmax}")
    for a in ALPHAS:
        print(f"  resolvent alpha={a}: fails {fail_fixed[a]}")
    print(f"  resolvent best-alpha grid: fails {fail_best}  {bad_best[:10]}")
    for K in (2, 3, 4):
        print(f"  Krylov cone K={K}: fails {fail_krylov[K]}")
    print("  Krylov4 bad:", bad_kry[:10])


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
