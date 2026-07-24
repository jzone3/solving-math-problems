"""childN exp1: baseline re-verification of (B) and (W=) on small graphs,
plus structural probes:
  - where in B2(e) is rho0 attained (self / first shell / second shell)?
  - unified form: for z1_e >= rho0(e), D_e(rho0) = (z1_e-rho0) - sum_{f~e}(z1_f-rho0) >= 0
    (>0 when heavy); record min margins.
"""
import sys
from fractions import Fraction

sys.path.insert(0, ".")
from common import geng, gentreeg, g6_adj, edge_env

def scan(graphs, label):
    minB = None
    minW = None
    nheavy = nEq = 0
    attain = {"self": 0, "shell1": 0, "shell2only": 0}
    viol = []
    for g6 in graphs:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ne = len(E)
        for a in range(ne):
            if z1[a] > rho0[a]:
                nheavy += 1
                D = rho0[a] * (s[a] - 3) + 3 * z1[a] - zs[a]
                if minB is None or D < minB:
                    minB = D
                if D <= 0:
                    viol.append(("B", g6, a, D))
                # where attained
                if a44[a] == rho0[a]:
                    attain["self"] += 1
                elif any(AL[a][b] and a44[b] == rho0[a] for b in range(ne)):
                    attain["shell1"] += 1
                else:
                    attain["shell2only"] += 1
            elif z1[a] == rho0[a]:
                nEq += 1
                w = zs[a] - s[a] * z1[a]
                if minW is None or -w < minW:
                    minW = -w
                if w > 0:
                    viol.append(("W", g6, a, w))
    print(f"{label}: heavy={nheavy} minD={minB} eq={nEq} min(-w)={minW} "
          f"attain={attain} viol={len(viol)}")
    for v in viol[:10]:
        print("  VIOL", v)

if __name__ == "__main__":
    for n in range(3, 9):
        scan(geng(n), f"geng n={n}")
    for n in range(10, 15):
        scan(gentreeg(n), f"trees n={n}")
