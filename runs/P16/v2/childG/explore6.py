"""childG exploration 6: leaf-extension constructions G* with G subgraph of G*,
delta(G*)>=2, support vertices' degrees unchanged.  Then Hyp D (Bound 46,
delta>=2) gives mu(G) <= mu(G*) <= RHS46(G*); need RHS46(G*) <= RHS46(G).

  H2: per leaf v: attach a pendant triangle via edge (add u,w1,w2; edges
      v-u, u-w1, u-w2, w1-w2).  d_v -> 2.
  H6: per leaf v: add u,w and triangle v-u-w.  d_v -> 3.
  H5: one new vertex z adjacent to all leaves (needs >=2 leaves), plus, if
      only ... skip when <2 leaves; also z-w helper when z would be leaf:
      exactly: if #leaves>=3, z has deg>=3, leaves deg 2. If #leaves==2, z
      is degree 2. ok. If 1 leaf: fall back to H2 on it.
Usage: explore6.py NMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import graphs, g6_adj, t46, data
from explore5 import rhs46_A

def extend(A, kind):
    n = A.shape[0]
    d = A.sum(1)
    leaves = [i for i in range(n) if d[i] == 1]
    if kind == "H2":
        add = 3*len(leaves)
        B = np.zeros((n+add, n+add)); B[:n, :n] = A
        k = n
        for v in leaves:
            u, w1, w2 = k, k+1, k+2; k += 3
            for a, b in ((v,u),(u,w1),(u,w2),(w1,w2)):
                B[a,b]=B[b,a]=1
        return B
    if kind == "H6":
        add = 2*len(leaves)
        B = np.zeros((n+add, n+add)); B[:n, :n] = A
        k = n
        for v in leaves:
            u, w = k, k+1; k += 2
            for a, b in ((v,u),(v,w),(u,w)):
                B[a,b]=B[b,a]=1
        return B
    if kind == "H5":
        if len(leaves) < 2:
            return extend(A, "H2")
        B = np.zeros((n+1, n+1)); B[:n, :n] = A
        for v in leaves:
            B[v, n] = B[n, v] = 1
        return B
    raise ValueError

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worst = {k: (1e9, None) for k in ("H2","H6","H5")}
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            if A.sum(1).min() > 1:
                continue
            r46 = rhs46_A(A)
            for k in worst:
                s = r46 - rhs46_A(extend(A, k))
                if s < worst[k][0]:
                    worst[k] = (s, g6)
    for k in sorted(worst):
        v, g = worst[k]
        print(f"{k}: min (RHS46(G)-RHS46(G*)) = {v:.6g} at {g}")
