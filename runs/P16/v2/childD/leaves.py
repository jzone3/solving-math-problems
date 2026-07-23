"""childD: leaf-case candidates for Bound 46 (graphs with delta=1).
Tested claims over connected graphs with a leaf:
  (L1) mu(G) <= max over leaf edges of t46            [direct]
  (L2) mu(G) <= max(t46(leaf edges), Merris(core))     ...
  (L3) mu(G) <= max(max_{leaf e} t46(e), RHS46(G - all leaves at once?))
  (L4) induction: mu(G) <= max(t46 leaf edges of G, RHS46(G-v)) for v a leaf
  (L5) Merris(G) <= max_{leaf e} t46(e)
Usage: leaves.py NMAX
"""
import numpy as np, subprocess, sys, math

def graphs(n):
    p = subprocess.Popen(f"nauty-geng -qc {n}", shell=True,
                         stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        yield line.strip()

def g6_adj(g6):
    data = [ord(c) - 63 for c in g6]
    n = data[0]
    bits = []
    for v in data[1:]:
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    A = np.zeros((n, n))
    idx = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[idx]
            idx += 1
    return A

def t46(di, dj, mi, mj):
    a = 2*(di*di+dj*dj) - 16*di*dj/(mi+mj) + 4
    return 2 + math.sqrt(a) if a >= 0 else -math.inf

def data(A):
    d = A.sum(1); m = A @ d / d
    n = A.shape[0]
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if A[i, j]]
    L = np.diag(d) - A
    mu = np.linalg.eigvalsh(L)[-1]
    return d, m, edges, mu

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worst = {k: (1e9, None) for k in ("L1", "L4", "L5")}
    cnt = 0
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, edges, mu = data(A)
            if d.min() > 1: continue
            cnt += 1
            leafT = max(t46(d[i], d[j], m[i], m[j]) for i, j in edges
                        if d[i] == 1 or d[j] == 1)
            mer = (d + m).max()
            v = int(np.argmin(d))  # a leaf
            keep = [u for u in range(A.shape[0]) if u != v]
            B = A[np.ix_(keep, keep)]
            if B.sum(1).min() == 0:  # G-v has isolated vertex (K2 etc.)
                r46sub = -math.inf
                db = B.sum(1)
                if (db == 0).all() or len(keep) < 2:
                    r46sub = 0
            else:
                db, mb, eb, mub = data(B)
                r46sub = max(t46(db[i], db[j], mb[i], mb[j]) for i, j in eb)
            for k, val in (("L1", leafT - mu),
                           ("L4", max(leafT, r46sub) - mu),
                           ("L5", leafT - mer)):
                if val < worst[k][0]: worst[k] = (val, g6)
    print(f"graphs with a leaf: {cnt}")
    for k, (v, g) in worst.items():
        print(f"{k}: min slack {v:.6g} at {g}")
