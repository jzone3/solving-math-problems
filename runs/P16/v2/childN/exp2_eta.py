"""childN exp2: test sufficient statement S1 for (B):
  for heavy e:  sum_{f~e} eta_f < z1_e - rho0(e),  eta_f = z1_f - rho1(f)
(valid since B1(f) subset B2(e) => rho0(e) >= rho1(f) => z1_f - rho0 <= eta_f).
Also the (W=) analog S1w: z1_e = rho0(e) => sum eta_f <= 0.
Also record eta_e distribution for heavy e and margins.
"""
import sys
from fractions import Fraction

sys.path.insert(0, ".")
from common import geng, gentreeg, g6_adj, edge_env

def scan(graphs, label):
    minS1 = None  # min of (z1_e - rho0) - sum eta_f over heavy
    minS1w = None
    violS1 = []
    violS1w = []
    cnt = 0
    for g6 in graphs:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ne = len(E)
        eta = [z1[a] - rho1[a] for a in range(ne)]
        for a in range(ne):
            nb = [b for b in range(ne) if AL[a][b]]
            se = sum(eta[b] for b in nb)
            if z1[a] > rho0[a]:
                cnt += 1
                marg = (z1[a] - rho0[a]) - se
                if minS1 is None or marg < minS1:
                    minS1 = marg
                if marg <= 0:
                    violS1.append((g6, a, marg))
            elif z1[a] == rho0[a]:
                if minS1w is None or -se < minS1w:
                    minS1w = -se
                if se > 0:
                    violS1w.append((g6, a, se))
    print(f"{label}: heavy={cnt} min S1 margin={minS1} min(-sum eta) at eq={minS1w} "
          f"violS1={len(violS1)} violS1w={len(violS1w)}")
    for v in violS1[:5]:
        print("  VIOL S1", v)
    for v in violS1w[:5]:
        print("  VIOL S1w", v)

if __name__ == "__main__":
    for n in range(3, 9):
        scan(geng(n), f"geng n={n}")
    for n in range(10, 15):
        scan(gentreeg(n), f"trees n={n}")
