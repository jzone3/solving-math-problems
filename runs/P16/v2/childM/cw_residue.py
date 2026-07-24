"""h = d Collatz-Wielandt residue for sigma-hat (c=2,4) vs old sigma, plus
sound resolvent certificate I1 (childI) rerun with sigma-hat.

Condition (h=d): (Bd)_i <= T_i d_i for all i, where B = Q + S H S, T = 2s+4.
Equivalent per-vertex: s_i sum_j w_ij (s_i d_i + s_j d_j) <= d_i (2 s_i - sig_i)
with sig = d+m-4 (since (Qd)_i = d_i(d_i+m_i)).

Also: I1 with kappa=0.99, alpha = 0.99/max(rho0,1), rho0 = max (Bd)_i/(T_i d_i);
R(alpha): (1-alpha)(I-alpha P)^{-1} d <= d.

Usage: python3 cw_residue.py <n> [res mod]
"""
import sys
import numpy as np
from common import build_base, with_diag, sigma_cap, geng, g6_to_adj

n = int(sys.argv[1])
res, mod = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)

stats = {c: dict(tot=0, cw_fail=0, i1_fail=0, max_rho0=0.0, worst_i1=-1e18)
         for c in (2.0, 4.0, None)}   # None = old sigma

for g6 in geng(n, res=res, mod=mod):
    A = g6_to_adj(g6)
    b = build_base(A)
    d, m = b["d"], b["m"]
    for c in stats:
        s = (d + m - 4.0) if c is None else sigma_cap(d, m, c)
        bd = with_diag(b, s)
        B, T = bd["B"], bd["T"]
        st = stats[c]
        st["tot"] += 1
        r = (B @ d) / (T * d)
        rho0 = r.max()
        st["max_rho0"] = max(st["max_rho0"], rho0)
        if rho0 > 1 + 1e-12:
            st["cw_fail"] += 1
        alpha = 0.99 / max(rho0, 1.0)
        P = B / T[:, None]
        h = np.linalg.solve(np.eye(b["n"]) - alpha * P, d)
        viol = np.max((1 - alpha) * h - d)
        st["worst_i1"] = max(st["worst_i1"], viol)
        if viol > 1e-9:
            st["i1_fail"] += 1

for c, st in stats.items():
    lbl = "old" if c is None else f"cap{int(c)}"
    print(f"n={n} res={res}/{mod} {lbl}: tot={st['tot']} cw(h=d)fail={st['cw_fail']} "
          f"I1fail={st['i1_fail']} max_rho0={st['max_rho0']:.4f} "
          f"worstI1viol={st['worst_i1']:.3e}")
