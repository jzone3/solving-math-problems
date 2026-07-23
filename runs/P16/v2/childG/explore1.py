"""childG exploration 1: which reduction shapes are TRUE for leafy graphs.

For all connected graphs with a leaf, n <= NMAX, test:
  A1: mu(G) <= max_{leaf edges} t46(e)                       [direct, expect fails]
  A2: mu(G) <= max(leafT, RHS46(2core(G)))                   [2-core reduction]
  A3: RHS46(2core(G)) <= RHS46(G)                            [core monotonicity]
  A4 (trees only): mu(T) <= leafT(T)                         [trees direct]
  A5: mu(G) <= max(leafT, rho(Q(2core)))                     [core spectral]
  A6: rhoQ(G) <= RHS46(G)                                    [sanity, known true n<=10]
Usage: explore1.py NMAX
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
    Q = np.diag(d) + A
    mu = np.linalg.eigvalsh(L)[-1]
    rq = np.linalg.eigvalsh(Q)[-1]
    return d, m, edges, mu, rq

def rhs46(d, m, edges):
    return max((t46(d[i], d[j], m[i], m[j]) for i, j in edges), default=-math.inf)

def two_core(A):
    A = A.copy()
    keep = list(range(A.shape[0]))
    while True:
        d = A.sum(1)
        low = [i for i in range(A.shape[0]) if d[i] <= 1]
        if not low:
            break
        sel = [i for i in range(A.shape[0]) if i not in low]
        A = A[np.ix_(sel, sel)]
        keep = [keep[i] for i in sel]
        if A.shape[0] == 0:
            break
    return A

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worst = {k: (1e9, None) for k in ("A1","A2","A3","A4","A5","A6")}
    cnt = 0; ntrees = 0
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, edges, mu, rq = data(A)
            if d.min() > 1:
                continue
            cnt += 1
            leafT = max(t46(d[i], d[j], m[i], m[j]) for i, j in edges
                        if d[i] == 1 or d[j] == 1)
            r46 = rhs46(d, m, edges)
            C = two_core(A)
            if C.shape[0] >= 2 and C.sum() > 0:
                dc, mc, ec, muc, rqc = data(C)
                r46c = rhs46(dc, mc, ec)
            else:
                r46c = -math.inf; rqc = -math.inf
            is_tree = (len(edges) == n-1)
            if is_tree: ntrees += 1
            checks = {
                "A1": leafT - mu,
                "A2": max(leafT, r46c) - mu,
                "A3": (r46 - r46c) if r46c > -math.inf else 1e9,
                "A4": (leafT - mu) if is_tree else 1e9,
                "A5": max(leafT, rqc) - mu,
                "A6": r46 - rq,
            }
            for k, val in checks.items():
                if val < worst[k][0]:
                    worst[k] = (val, g6)
    print(f"leafy connected graphs n<={nmax}: {cnt} (trees: {ntrees})")
    for k in sorted(worst):
        v, g = worst[k]
        print(f"{k}: min slack {v:.6g} at {g}")
