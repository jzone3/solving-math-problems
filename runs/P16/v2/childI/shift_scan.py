"""childH-style shifted-weight certificates for F2.

Family h = d + c*u (u a fixed local vector, c a per-graph free constant).
CW condition B h <= T*h is LINEAR in c per vertex:

  (B d - T*d)_i + c (B u - T*u)_i <= 0,

so per-graph feasibility is an exact interval intersection
(also require h > 0: c > -min d_i/u_i for u > 0, etc.).

Count graphs with empty interval, for u in {1, m, sigma, m-2, d(no-op),
t, d*(t-1), Pd-d}.  Usage: shift_scan.py nmax
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng


def feasible(Bd_Td, Bu_Tu, d, u):
    """exists c with Bd_Td + c*Bu_Tu <= 0 and d + c*u > 0?"""
    lo, hi = -np.inf, np.inf
    for a, b in zip(Bd_Td, Bu_Tu):
        # a + c b <= 0
        if abs(b) < 1e-12:
            if a > 1e-9:
                return False
        elif b > 0:
            hi = min(hi, -a / b)
        else:
            lo = max(lo, -a / b)
    # positivity: d_i + c u_i > 0
    for di, ui in zip(d, u):
        if abs(ui) < 1e-12:
            continue
        if ui > 0:
            lo = max(lo, -di / ui + 1e-12)
        else:
            hi = min(hi, di / (-ui) - 1e-12)
    return lo <= hi + 1e-12


def main(nmax):
    fails = {}
    tot = 0
    for n in range(3, nmax + 1):
        for g6 in geng(n):
            tot += 1
            G = build(g6_to_adj(g6))
            B, T, d, m, sig = G["B"], G["T"], G["d"], G["m"], G["sig"]
            n_ = G["n"]
            P = B / T[:, None]
            t = np.zeros(n_)
            for k, (i, j) in enumerate(G["edges"]):
                s = (sig[i] + sig[j]) * G["w"][k]
                t[i] += s; t[j] += s
            us = {
                "1": np.ones(n_), "m": m, "sig": sig, "m-2": m - 2,
                "t": t, "d*(t-1)": d * (t - 1), "Pd-d": P @ d - d,
                "P2d-d": P @ (P @ d) - d,
            }
            Bd_Td = B @ d - T * d
            for k, u in us.items():
                ok = feasible(Bd_Td, B @ u - T * u, d, u)
                if not ok:
                    fails[k] = fails.get(k, 0) + 1
    print(f"total {tot} graphs n<={nmax}; empty-interval counts:")
    for k in sorted(fails, key=lambda k: fails[k]):
        print(f"  u={k:10s} fails {fails[k]}")
    for k in us:
        if k not in fails:
            print(f"  u={k:10s} fails 0  <-- UNIVERSAL so far")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
