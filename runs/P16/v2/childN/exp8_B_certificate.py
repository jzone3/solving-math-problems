"""childN exp8: certificate for (B).
(B) <=> w_e + (s_e-3)(z1_e-rho0) < 0 for heavy e.
Bound w_e <= w_e + sum_k lam_k (rho - arg44_ik) + sum_l lam_l (rho - arg44_jl)
with lam_k = d_k/(2 m_i) (m_k cancels).  Define
  Q_e(rho) = [that bound] + (s_e-3)(z1_e - rho).
Report max Q_e(rho0) over heavy edges; also with extra slack mu*(rho-arg44_e)
for mu in {0, 1/2, 1}; also Q at rho=z1 (the W-case sanity).
"""
import sys
from fractions import Fraction
sys.path.insert(0, ".")
from common import geng, gentreeg, g6_adj, edge_env

def scan(graphs, label):
    best = {}
    ex = {}
    for g6 in graphs:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        dd = A.sum(1)
        n = len(dd)
        eidx = {fr: a for a, fr in enumerate(E)}
        for a, (i, j) in enumerate(E):
            if z1[a] <= rho0[a]:
                continue
            rho = rho0[a]
            w = Fraction(zs[a] - s[a] * z1[a])
            slack = Fraction(0)
            for k in range(n):
                for (u, v) in ((i, j), (j, i)):
                    if A[u, k] and k != v:
                        b = eidx[(min(u, k), max(u, k))]
                        slack += Fraction(int(dd[k]), 2) / m[u] * (rho - a44[b])
            base = w + slack + (s[a] - 3) * (z1[a] - rho)
            for mu in (Fraction(0), Fraction(1, 2), Fraction(1)):
                q = base + mu * (rho - a44[a])
                key = f"mu={mu}"
                if key not in best or q > best[key]:
                    best[key] = q
                    ex[key] = (g6, E[a])
    print(label, {k: (str(v), ex[k]) for k, v in best.items()})

if __name__ == "__main__":
    for n in range(5, 9):
        scan(geng(n), f"geng n={n}")
    for n in range(9, 15):
        scan(gentreeg(n), f"trees n={n}")
