"""childG exploration 7: anatomy of the leaf-deletion induction.

For each connected leafy G:
  S3: does there EXIST a leaf v with RHS46(G-v) <= RHS46(G)?  ("good leaf")
  For good leaves, is the step mu(G) <= max(leafT(G), RHS46(G-v)) true?
      (stronger than L4 which allowed any leaf)
  For graphs with NO good leaf ("stubborn"): is mu(G) <= leafT(G)?
  W1 := [exists good leaf v with step-inequality] OR [mu <= leafT]:
      if W1 holds for all leafy graphs, the induction closes modulo proving
      (i) the step for good leaves and (ii) mu <= leafT for stubborn graphs.
Also record: for good-leaf graphs, min over good leaves of step slack;
stubborn graphs' structure.
Usage: explore7.py NMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import graphs, g6_adj, t46, data
from explore5 import rhs46_A

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worst_step = (1e9, None)   # best-good-leaf step slack, min over graphs
    worst_stub = (1e9, None)   # leafT - mu over stubborn graphs
    n_stub = 0; cnt = 0; w1fail = 0
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, edges, mu, rq = data(A)
            if d.min() > 1:
                continue
            cnt += 1
            r46 = rhs46_A(A)
            lt = max(t46(d[i], d[j], m[i], m[j]) for i, j in edges
                     if d[i] == 1 or d[j] == 1)
            leaves = [i for i in range(int(A.shape[0])) if d[i] == 1]
            best = -1e18  # best (i.e. max) step slack over good leaves
            has_good = False
            for v in leaves:
                keep = [u for u in range(A.shape[0]) if u != v]
                B = A[np.ix_(keep, keep)]
                if B.sum() == 0:
                    rsub = 0.0
                elif B.sum(1).min() == 0:
                    continue  # disconnected-ish (only for K2-like); skip
                else:
                    rsub = rhs46_A(B)
                if rsub <= r46 + 1e-9:
                    has_good = True
                    slack = max(lt, rsub) - mu
                    if slack > best:
                        best = slack
            if has_good:
                if best < worst_step[0]:
                    worst_step = (best, g6)
                if best < -1e-9 and lt - mu < -1e-9:
                    w1fail += 1
                    print(f"W1 FAIL (good) {g6} step={best:.4f} lt-mu={lt-mu:.4f}")
            else:
                n_stub += 1
                s = lt - mu
                if s < worst_stub[0]:
                    worst_stub = (s, g6)
                if s < -1e-9:
                    w1fail += 1
                    print(f"W1 FAIL (stubborn) {g6} lt-mu={s:.4f}")
    print(f"leafy: {cnt}, stubborn (no good leaf): {n_stub}, W1 failures: {w1fail}")
    print(f"min step slack over good-leaf graphs: {worst_step[0]:.6g} at {worst_step[1]}")
    print(f"min (leafT-mu) over stubborn graphs: {worst_stub[0]:.6g} at {worst_stub[1]}")
