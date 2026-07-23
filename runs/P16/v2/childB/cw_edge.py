"""Line-graph Collatz-Wielandt with y_e = phi(d_i)phi(d_j), phi(x)=x^a (a<=1
for Jensen concavity). Gives valid bound:
  lambda_max(LG) <= max_{ij in E} [ d_i phi(m_i)/phi(d_j) + d_j phi(m_j)/phi(d_i) - 2 ]
  (for a=1 exact algebra, no Jensen needed: (Ay)_ij = d_i^2 m_i + d_j^2 m_j - 2 d_i d_j)
Test whether max_e sqrt(arg44/46(e)) >= max_e F_a(e), which would prove the bounds.
"""
import numpy as np, math, sys
from harness import graphs, g6_adj

def run(nmax, avals):
    worst44 = {a: (1e9, None) for a in avals}
    worst46 = {a: (1e9, None) for a in avals}
    sanity = {a: (1e9, None) for a in avals}
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            nn = A.shape[0]
            d = A.sum(1); m = A @ d / d
            E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
            a44 = [2 * ((d[i]-1)**2 + (d[j]-1)**2 + m[i]*m[j] - d[i]*d[j]) for i, j in E]
            a46 = [2*(d[i]**2 + d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4 for i, j in E]
            s44 = max(math.sqrt(x) if x >= 0 else -math.inf for x in a44)
            s46 = max(math.sqrt(x) if x >= 0 else -math.inf for x in a46)
            # line graph lambda for sanity
            ne = len(E)
            LA = np.zeros((ne, ne))
            for x in range(ne):
                for y in range(x+1, ne):
                    if len({*E[x]} & {*E[y]}): LA[x, y] = LA[y, x] = 1
            lam = np.linalg.eigvalsh(LA)[-1] if ne else 0.0
            for a in avals:
                F = max(d[i]*m[i]**a/d[j]**a + d[j]*m[j]**a/d[i]**a - 2 for i, j in E)
                if F - lam < sanity[a][0]: sanity[a] = (F - lam, g6)
                if s44 - F < worst44[a][0]: worst44[a] = (s44 - F, g6)
                if s46 - F < worst46[a][0]: worst46[a] = (s46 - F, g6)
    for a in avals:
        print(f"a={a}: sanity min(F-lam)={sanity[a][0]:+.4g} @{sanity[a][1]}  "
              f"min(s44-F)={worst44[a][0]:+.4g} @{worst44[a][1]}  "
              f"min(s46-F)={worst46[a][0]:+.4g} @{worst46[a][1]}")

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8,
        [0.0, 0.25, 0.5, 0.75, 1.0])
