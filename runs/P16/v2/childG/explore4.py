"""childG exploration 4: Perron localization on Q.

For leafy connected G: y = Perron(Q), u = argmax y_i/d_i, so rho(Q) <= d_u+m_u.
  C1: d_u + m_u <= RHS46(G)?
  C2: d_u + m_u <= max leaf t46, when u is a support vertex?
  C3: is u always a support vertex / leaf?  (classify)
  C4: mu <= d_u + m_u  (sanity)
Also, trees only:
  C5: d_u + m_u <= max leaf t46?
Usage: explore4.py NMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import graphs, g6_adj, t46, data

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worst = {k: (1e9, None) for k in ("C1","C2","C5")}
    uclass = {}
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, edges, mu, rq = data(A)
            if d.min() > 1:
                continue
            Q = np.diag(d) + A
            w, V = np.linalg.eigh(Q)
            y = np.abs(V[:, -1])
            u = int(np.argmax(y / d))
            merr = d[u] + m[u]
            r46 = max(t46(d[i], d[j], m[i], m[j]) for i, j in edges)
            lt = max(t46(d[i], d[j], m[i], m[j]) for i, j in edges
                     if d[i] == 1 or d[j] == 1)
            is_supp = d[u] > 1 and any(d[v] == 1 for v in np.where(A[u] > 0)[0])
            is_leaf = d[u] == 1
            key = "leaf" if is_leaf else ("support" if is_supp else "other")
            uclass[key] = uclass.get(key, 0) + 1
            is_tree = len(edges) == n-1
            checks = {"C1": r46 - merr,
                      "C2": (lt - merr) if is_supp else 1e9,
                      "C5": (lt - merr) if is_tree else 1e9}
            for k, val in checks.items():
                if val < worst[k][0]:
                    worst[k] = (val, g6)
    print("u classes:", uclass)
    for k in sorted(worst):
        v, g = worst[k]
        print(f"{k}: min slack {-v if k=='C1' else v:.6g} at {g}"
              if False else f"{k}: min slack {v:.6g} at {g}")
