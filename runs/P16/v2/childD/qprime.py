"""childD: identity  x^T K x = sum_e (arg_e-4)x_e^2 - 2 sum_i (d_i-2) X_i^2
                              + sum_{ij in E} (X_i - X_j)^2,   X = R x.
Test the stronger relaxation (drop the last nonneg term):
   Q' := diag(arg_e - 4) - B,  B_{ef} = sum_{i in e cap f} 2(d_i - 2)
   (including diagonal B_{ee} = 2(d_i-2)+2(d_j-2)).
Is Q' PSD for all connected delta>=2 graphs?  Usage: qprime.py NMAX
"""
import numpy as np, subprocess, sys

def graphs(n):
    p = subprocess.Popen(f"nauty-geng -qc -d2 {n}", shell=True,
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

def minim(g6):
    A = g6_adj(g6)
    n = A.shape[0]
    d = A.sum(1)
    m = A @ d / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    E = len(edges)
    arg = np.array([2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4 for i, j in edges])
    R = np.zeros((n, E))
    for e, (i, j) in enumerate(edges):
        R[i, e] = R[j, e] = 1
    B = sum(2*(d[i]-2)*np.outer(R[i], R[i]) for i in range(n))
    Qp = np.diag(arg - 4) - B
    return np.linalg.eigvalsh(Qp)[0]

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worst = (1e18, None); cnt = 0
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            lam = minim(g6); cnt += 1
            if lam < worst[0]: worst = (lam, g6)
    print(f"graphs={cnt} min_eig(Q')={worst[0]:.6g} at {worst[1]}")
