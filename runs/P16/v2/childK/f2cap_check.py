"""Exhaustive check of F2'' (capped sigma) at n = 9 (and any n via args).

sigma_c := d - 4 + min(m, d + c),  M(sigma_c) = 2D+4I-Q-DHD  (H unchanged).
Usage: python3 f2cap_check.py <n> <cap> [res mod]
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng

n = int(sys.argv[1])
cap = float(sys.argv[2])
res, mod = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 1)

bad, tot, worst, wg = [], 0, 1e18, None
for g6 in geng(n, res=res, mod=mod):
    A = g6_to_adj(g6)
    bd = build(A)
    d, m = bd["d"], bd["m"]
    s = np.maximum(d - 4 + np.minimum(m, d + cap), 0.0)
    D = np.diag(s)
    Ms = 2 * D + 4 * np.eye(bd["n"]) - bd["Q"] - D @ bd["H"] @ D
    e = np.linalg.eigvalsh(Ms)[0]
    tot += 1
    if e < worst:
        worst, wg = e, g6
    if e < -1e-8:
        bad.append((g6, e))
print(f"n={n} cap={cap} res={res}/{mod}: tot={tot} bad={len(bad)} "
      f"worst={worst:.3e} ({wg})")
if bad:
    print("FAILURES:", bad[:50])
