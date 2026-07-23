"""childG exploration 2: edge-class refinements (all terms computed with G's own d,m).

Edge classes in G (connected, has a leaf):
  leaf edge: an endpoint has degree 1
  core edge: both endpoints in 2-core(G)
  branch edge: everything else (inside pendant trees, no leaf endpoint)

Candidates:
  B1: mu(G) <= max(leaf terms, core terms)        [drop branch edges]
  B2: mu(G) <= max(leaf terms, branch terms)      [trees have no core]
  B3: mu(G) <= max(leaf terms, core terms) for graphs WITH nonempty core
  B4 (trees): mu <= leaf terms  (= A4, rerun for reference)
Usage: explore2.py NMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import graphs, g6_adj, t46, data, two_core

def core_vertices(A):
    n = A.shape[0]
    B = A.copy()
    alive = np.ones(n, bool)
    while True:
        d = B.sum(1)
        low = [i for i in range(n) if alive[i] and d[i] <= 1]
        if not low:
            break
        for i in low:
            alive[i] = False
            B[i, :] = 0
            B[:, i] = 0
    return set(np.where(alive)[0])

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worst = {k: (1e9, None) for k in ("B1","B2","B3","B4")}
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, edges, mu, rq = data(A)
            if d.min() > 1:
                continue
            cv = core_vertices(A)
            leaf, core, branch = [], [], []
            for i, j in edges:
                tt = t46(d[i], d[j], m[i], m[j])
                if d[i] == 1 or d[j] == 1:
                    leaf.append(tt)
                elif i in cv and j in cv:
                    core.append(tt)
                else:
                    branch.append(tt)
            lt = max(leaf)
            ct = max(core, default=-math.inf)
            bt = max(branch, default=-math.inf)
            is_tree = len(edges) == n-1
            checks = {
                "B1": max(lt, ct) - mu,
                "B2": max(lt, bt) - mu,
                "B3": (max(lt, ct) - mu) if core else 1e9,
                "B4": (lt - mu) if is_tree else 1e9,
            }
            for k, val in checks.items():
                if val < worst[k][0]:
                    worst[k] = (val, g6)
    for k in sorted(worst):
        v, g = worst[k]
        print(f"{k}: min slack {v:.6g} at {g}")
