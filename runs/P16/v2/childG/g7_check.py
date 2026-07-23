"""childG: Lemma G7 numeric check.

For every vertex v (any degree) and u = a minimum-degree neighbour of v:
  arg46(uv) - (2 d_v^2 - 16 d_v + 6) >= 0
over all connected graphs n <= NMAX (and trees up to TMAX with the weaker
+4 form against RHS46 directly).
Usage: g7_check.py NMAX TMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import graphs, g6_adj
from explore5 import rhs46_A

if __name__ == "__main__":
    nmax, tmax = int(sys.argv[1]), int(sys.argv[2])
    worst = (1e9, None)
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6); d = A.sum(1); m = A @ d / d
            for v in range(n):
                nb = np.where(A[v] > 0)[0]
                u = nb[np.argmin(d[nb])]
                arg = 2*(d[v]**2 + d[u]**2) - 16*d[v]*d[u]/(m[v]+m[u]) + 4
                s = arg - (2*d[v]**2 - 16*d[v] + 6)
                if s < worst[0]:
                    worst = (s, g6)
    print(f"per-vertex arg46 slack (n<={nmax}): min {worst[0]:.6g} at {worst[1]}")
    worst = (1e9, None)
    for n in range(3, tmax+1):
        p = subprocess.Popen(f"nauty-geng -qc {n} {n-1}:{n-1}", shell=True,
                             stdout=subprocess.PIPE, text=True)
        for line in p.stdout:
            A = g6_adj(line.strip()); D = A.sum(1).max()
            f = 2 + math.sqrt(max(2*D*D - 16*D + 4, 0))
            s = rhs46_A(A) - f
            if s < worst[0]:
                worst = (s, line.strip())
    print(f"trees RHS46 vs 2+sqrt((2D^2-16D+4)^+) (n<={tmax}): min gap {worst[0]:.6g} at {worst[1]}")
