"""childD: L4 check at n=9 (sharded): for every connected graph with a leaf,
mu(G) <= max( max_{leaf edge e} t46(e),  RHS46(G-v) )  for v = some leaf
(checked for the min-degree argmin leaf, as in leaves.py L4).
Usage: leaves9.py N RES MOD
"""
import numpy as np, subprocess, sys, math
from leaves import g6_adj, t46, data

def graphs(n, res, mod):
    p = subprocess.Popen(f"nauty-geng -qc {n} {res}/{mod}", shell=True,
                         stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        yield line.strip()

if __name__ == "__main__":
    n, res, mod = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    worst = (1e9, None); cnt = 0
    for g6 in graphs(n, res, mod):
        A = g6_adj(g6)
        d = A.sum(1)
        if d.min() != 1: continue
        cnt += 1
        d, m, edges, mu = data(A)
        leafT = max(t46(d[i], d[j], m[i], m[j]) for i, j in edges
                    if d[i] == 1 or d[j] == 1)
        # best over ALL leaves (exists-version)
        best = -1e9
        N = A.shape[0]
        for v in range(N):
            if d[v] != 1: continue
            keep = [u for u in range(N) if u != v]
            B = A[np.ix_(keep, keep)]
            if len(keep) < 2 or B.sum(1).min() == 0:
                sub = 2.0
            else:
                db, mb, eb, mub = data(B)
                sub = max(t46(db[i], db[j], mb[i], mb[j]) for i, j in eb)
            best = max(best, max(leafT, sub) - mu)
        if best < worst[0]: worst = (best, g6)
    print(f"n={n} {res}/{mod}: leafy graphs={cnt} min L4 slack {worst[0]:.6g} at {worst[1]}")
