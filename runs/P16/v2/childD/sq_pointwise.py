"""childD: test the pointwise second-order strengthening of Bound 46:
  Conjecture D1: for connected G with delta>=2,
     rho( D^{-1/2} A_{L(G)}^2 D^{-1/2} ) <= 1,  D = diag(arg46(e)),
  which implies lambda_max(A_L)^2 <= max_e arg46(e) (via y = D^{1/2} CW vector)
  hence rho(Q) <= 2 + sqrt(max arg46) = RHS46 >= mu.
Also record min arg46 over edges (need > 0) and worst rho.
Usage: python3 sq_pointwise.py NMAX [d2|all]
"""
import numpy as np, subprocess, sys, math

def graphs(n, extra=""):
    p = subprocess.Popen(f"nauty-geng -qc {extra} {n}", shell=True,
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

def process(g6):
    A = g6_adj(g6)
    n = A.shape[0]
    d = A.sum(1)
    m = A @ d / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    E = len(edges)
    arg = np.array([2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4
                    for i, j in edges])
    if arg.min() <= 0:
        return None, arg.min()
    # line graph adjacency
    AL = np.zeros((E, E))
    for a in range(E):
        ia, ja = edges[a]
        for b in range(a+1, E):
            ib, jb = edges[b]
            if len({ia, ja} & {ib, jb}):
                AL[a, b] = AL[b, a] = 1
    B = AL @ AL
    s = 1/np.sqrt(arg)
    M = B * np.outer(s, s)
    return np.linalg.eigvalsh(M)[-1], arg.min()

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    extra = "-d2" if (len(sys.argv) < 3 or sys.argv[2] == "d2") else ""
    worst = (-1, None); minarg = (1e9, None); cnt = 0; negarg = 0
    for n in range(3, nmax + 1):
        for g6 in graphs(n, extra):
            rho, ma = process(g6)
            cnt += 1
            if ma < minarg[0]: minarg = (ma, g6)
            if rho is None:
                negarg += 1; continue
            if rho > worst[0]: worst = (rho, g6)
    print(f"graphs: {cnt}, nonpositive-arg graphs: {negarg}")
    print(f"max rho(M): {worst[0]:.12f} at {worst[1]}")
    print(f"min arg: {minarg[0]:.6g} at {minarg[1]}")
