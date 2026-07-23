"""Line graph reformulation: rho(Q) = 2 + lambda_max(A(L(G))).
Bound 44 <=> lam2 := lambda_max(L(G))^2 <= max_e arg44(e) where
arg44(ij) = 2((d_i-1)^2+(d_j-1)^2+m_i m_j - d_i d_j),
arg46(ij) = 2(d_i^2+d_j^2) - 16 d_i d_j/(m_i+m_j) + 4.
Valid line-graph bounds tested for dominance:
  S_e = sum of line-degrees of line-neighbors of e  (lam^2 <= max_e S_e)
  P_ef = D_e D_f over line-edges                    (lam^2 <= max P_ef)
"""
import numpy as np, math, sys
from harness import graphs, g6_adj

def run(nmax):
    worst = {}
    def upd(key, val, g6):
        if key not in worst or val < worst[key][0]:
            worst[key] = (val, g6)
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            nn = A.shape[0]
            d = A.sum(1); m = A @ d / d
            E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
            ne = len(E)
            # line graph adjacency
            LA = np.zeros((ne, ne))
            for a in range(ne):
                for b in range(a + 1, ne):
                    if len({*E[a]} & {*E[b]}):
                        LA[a, b] = LA[b, a] = 1
            lam = np.linalg.eigvalsh(LA)[-1] if ne > 0 else 0.0
            lam2 = lam * lam
            arg44 = [2 * ((d[i]-1)**2 + (d[j]-1)**2 + m[i]*m[j] - d[i]*d[j]) for i, j in E]
            arg46 = [2*(d[i]**2 + d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4 for i, j in E]
            D = [d[i] + d[j] - 2 for i, j in E]
            S = []
            for a, (i, j) in enumerate(E):
                S.append(sum(D[b] for b in range(ne) if LA[a, b]))
            maxS = max(S)
            maxP = max((D[a]*D[b] for a in range(ne) for b in range(a+1, ne) if LA[a, b]), default=0)
            upd("lam2 vs max arg44 (bound validity)", max(arg44) - lam2, g6)
            upd("lam2 vs max arg46 (bound validity)", max(arg46) - lam2, g6)
            upd("maxarg44 - maxS", max(arg44) - maxS, g6)
            upd("maxarg46 - maxS", max(arg46) - maxS, g6)
            upd("maxarg44 - maxP", max(arg44) - maxP, g6)
            upd("maxarg46 - maxP", max(arg46) - maxP, g6)
            upd("maxarg44 - min(maxS,maxP)", max(arg44) - min(maxS, maxP), g6)
            upd("maxarg46 - min(maxS,maxP)", max(arg46) - min(maxS, maxP), g6)
            upd("sanity maxS - lam2", maxS - lam2, g6)
            upd("sanity maxP - lam2", maxP - lam2, g6)
    for k, (v, g) in worst.items():
        print(f"{k:38s} min = {v:+.6g}  @ {g}")

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
