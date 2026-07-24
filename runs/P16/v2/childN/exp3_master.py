"""childN exp3: candidate master lemma variants.
eta_g = z1_g - rho1(g)   (1-ball heaviness)
  N-a: z1_e >= rho0(e)  =>  sum_{f~e} eta_f <= 0
  N-b: z1_e >= rho1(e) (eta_e >= 0)  =>  sum_{f~e} eta_f <= 0
Also record: max sum eta over all edges regardless of premise (control).
"""
import sys
sys.path.insert(0, ".")
from common import geng, gentreeg, g6_adj, edge_env

def scan(graphs, label):
    maxNa = maxNb = maxAll = None
    violNa, violNb = [], []
    cntA = cntB = 0
    for g6 in graphs:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ne = len(E)
        eta = [z1[a] - rho1[a] for a in range(ne)]
        for a in range(ne):
            se = sum(eta[b] for b in range(ne) if AL[a][b])
            if maxAll is None or se > maxAll:
                maxAll = se
            if z1[a] >= rho0[a]:
                cntA += 1
                if maxNa is None or se > maxNa:
                    maxNa = se
                if se > 0:
                    violNa.append((g6, a, se))
            if z1[a] >= rho1[a]:
                cntB += 1
                if maxNb is None or se > maxNb:
                    maxNb = se
                if se > 0:
                    violNb.append((g6, a, se))
    print(f"{label}: cntA={cntA} max_sum_eta|Na={maxNa} violNa={len(violNa)} | "
          f"cntB={cntB} max|Nb={maxNb} violNb={len(violNb)} | max_all={maxAll}")
    for v in violNa[:5]:
        print("  VIOL Na", v)
    for v in violNb[:3]:
        print("  VIOL Nb", v)

if __name__ == "__main__":
    for n in range(3, 9):
        scan(geng(n), f"geng n={n}")
    for n in range(10, 15):
        scan(gentreeg(n), f"trees n={n}")
