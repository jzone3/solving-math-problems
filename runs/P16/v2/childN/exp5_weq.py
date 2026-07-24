"""childN exp5: (W=) via 1-ball lemmas.
 (a) W1B: z1_e >= max_{B1(e)} arg44  =>  w_e <= 0 ?     [would imply (W=)]
 (b) same premise, stronger: sum_{f~e} delta_f <= 0, delta_f=z1_f-arg44_f ?
 (c) V1-1ball: z1_e <= rho1(e) => zs_e <= rho1(e) s_e ?  (childJ verified)
"""
import sys
sys.path.insert(0, ".")
from common import geng, gentreeg, g6_adj, edge_env

def scan(graphs, label):
    va = vb = vc = 0
    cnta = cntc = 0
    maxa = maxb = maxc = None
    exa = exb = None
    for g6 in graphs:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ne = len(E)
        for a in range(ne):
            w = zs[a] - s[a] * z1[a]
            if z1[a] >= rho1[a]:
                cnta += 1
                if maxa is None or w > maxa:
                    maxa = w
                if w > 0:
                    va += 1
                    exa = exa or (g6, a, w)
                sd = sum(z1[b] - a44[b] for b in range(ne) if AL[a][b])
                if maxb is None or sd > maxb:
                    maxb = sd
                if sd > 0:
                    vb += 1
                    exb = exb or (g6, a, sd)
            if z1[a] <= rho1[a]:
                cntc += 1
                t = zs[a] - rho1[a] * s[a]
                if maxc is None or t > maxc:
                    maxc = t
                if t > 0:
                    vc += 1
    print(f"{label}: W1B cnt={cnta} max_w={maxa} viol={va} ex={exa} | "
          f"sum_delta max={maxb} viol={vb} ex={exb} | V1 cnt={cntc} max={maxc} viol={vc}")

if __name__ == "__main__":
    for n in range(3, 9):
        scan(geng(n), f"geng n={n}")
    for n in range(10, 16):
        scan(gentreeg(n), f"trees n={n}")
