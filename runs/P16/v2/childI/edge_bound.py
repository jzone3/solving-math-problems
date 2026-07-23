"""Per-edge quantity q_e(i) := w_ij (sig_i d_i + sig_j d_j), so that
tau_i = (1/d_i) sum_{j~i} q_ij <= max_j q_ij and rho(P) <= max(1, max_i tau_i)
... actually rho(P) <= max_i (Bd)_i/(T_i d_i) = max_i (d_i+m_i+sig_i tau_i)/T_i
with T_i = 2 sig_i + 4, so rho <= max_i (1 + sig_i(tau_i - 1)/T_i).

Empirically find sup q over exhaustive n<=8 + random graphs + parametric
local configurations, to conjecture a universal constant C with q <= C
(then tau <= C and rho(P) <= 1 + max sig (C-1)/(2 sig+4) <= (C+1)/2 for C>=1).
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng

nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
maxq = -np.inf
argmax = None
maxtau = -np.inf
argtau = None
for n in range(3, nmax + 1):
    for g6 in geng(n):
        G = build(g6_to_adj(g6))
        d, sig, w, edges = G["d"], G["sig"], G["w"], G["edges"]
        tau = np.zeros(G["n"])
        for k, (i, j) in enumerate(edges):
            q = w[k] * (sig[i] * d[i] + sig[j] * d[j])
            tau[i] += q / d[i]
            tau[j] += q / d[j]
            if q > maxq:
                maxq, argmax = q, (g6, i, j, d[i], d[j], G["m"][i], G["m"][j])
        tt = tau.max()
        if tt > maxtau:
            maxtau, argtau = tt, g6
print(f"n<={nmax}: max per-edge q = {maxq:.6f} at {argmax}")
print(f"          max tau = {maxtau:.6f} at {argtau}")

# parametric probe: edge (i,j) with degrees D1,D2 and extreme m's
# constraints: m_i d_i >= d_j + 2(d_i-1), m_i <= Delta; scan freely
best = -np.inf
barg = None
for D1 in range(2, 40):
    for D2 in range(2, 40):
        for m1x in np.linspace(max(2, (D2 + 2 * (D1 - 1)) / D1), 40, 60):
            for m2x in np.linspace(max(2, (D1 + 2 * (D2 - 1)) / D2), 40, 60):
                s1 = D1 + m1x - 4
                s2 = D2 + m2x - 4
                a4 = 2 * (D1**2 + D2**2) - 16 * D1 * D2 / (m1x + m2x)
                if a4 <= 1e-9:
                    continue
                q = (s1 * D1 + s2 * D2) / a4
                if q > best:
                    best, barg = q, (D1, D2, m1x, m2x)
print(f"parametric sup q ~ {best:.6f} at (d_i,d_j,m_i,m_j)={barg}")
