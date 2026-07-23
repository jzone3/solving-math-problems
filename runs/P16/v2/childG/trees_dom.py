"""childG: on TREES, is RHS46 >= some classical PROVED upper bound on mu?

Classical bounds (all proved for all graphs):
  M1 Merris:      max_i (d_i + m_i)
  M2 edge-sum:    max_{ij} (d_i + d_j)
  M3 Guo/Das:     max_{ij} (d_i + d_j + sqrt((d_i-d_j)^2 + 4 m_i m_j))/2
  M4 LiZhang/2.9: max_i sqrt(2 d_i (d_i + m_i))
  M5 AndersonMorley-refined: max_{ij} (2 + sqrt((d_i+d_j-2)^2 + ... )) skip
  MIN: pointwise min of M1..M4
Report #trees where each exceeds RHS46, and worst gaps.
Usage: trees_dom.py NMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import g6_adj, t46

def bounds(A):
    d = A.sum(1); m = A @ d / d
    n = len(d)
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if A[i, j]]
    r46 = max(t46(d[i], d[j], m[i], m[j]) for i, j in edges)
    M1 = (d + m).max()
    M2 = max(d[i] + d[j] for i, j in edges)
    M3 = max((d[i] + d[j] + math.sqrt((d[i]-d[j])**2 + 4*m[i]*m[j]))/2
             for i, j in edges)
    M4 = np.sqrt(2*d*(d+m)).max()
    mu = np.linalg.eigvalsh(np.diag(d) - A)[-1]
    return r46, {"M1": M1, "M2": M2, "M3": M3, "M4": M4,
                 "MIN": min(M1, M2, M3, M4)}, mu

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    fails = {k: 0 for k in ("M1","M2","M3","M4","MIN")}
    worst = {k: (1e9, None) for k in fails}
    for n in range(3, nmax+1):
        p = subprocess.Popen(f"nauty-geng -qc {n} {n-1}:{n-1}", shell=True,
                             stdout=subprocess.PIPE, text=True)
        for line in p.stdout:
            g6 = line.strip()
            A = g6_adj(g6)
            r46, bs, mu = bounds(A)
            for k, v in bs.items():
                s = r46 - v
                if s < -1e-9:
                    fails[k] += 1
                if s < worst[k][0]:
                    worst[k] = (s, g6)
    for k in sorted(fails):
        print(f"{k}: fails {fails[k]}, min (RHS46 - bound) = {worst[k][0]:.5f} at {worst[k][1]}")
