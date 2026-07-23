"""childD: Conjecture D1 (PSD form): for connected G with delta(G)>=2,
    K(G) := diag(arg46(e)) - A_{L(G)}^2  is positive semidefinite.
Implies Bound 46 (and rho(Q) <= RHS46): with z the unit Perron vector of A_L,
lambda^2 = z^T A^2 z <= z^T D z <= max_e arg46.

Also machine-checks the quadratic form identity
  x^T K x = sum_e (arg_e - 4) x_e^2 + 4 sum_i X_i^2 - sum_{ij in E} (X_i+X_j)^2,
  X = R x  (vertex sums), using A_L = R^T R - 2I.

Usage: python3 psd_check.py N RES MOD   (geng -d2 res/mod)
Prints min eigenvalue of K over all graphs (want >= -1e-9).
"""
import numpy as np, subprocess, sys

def graphs(n, res, mod):
    p = subprocess.Popen(f"nauty-geng -qc -d2 {n} {res}/{mod}", shell=True,
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

def K_of(g6, check_identity=False):
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
    AL = R.T @ R - 2*np.eye(E)
    K = np.diag(arg) - AL @ AL
    if check_identity:
        rng = np.random.default_rng(0)
        for _ in range(5):
            x = rng.standard_normal(E)
            X = R @ x
            q1 = x @ K @ x
            q2 = ((arg - 4) * x**2).sum() + 4*(X**2).sum() \
                 - sum((X[i]+X[j])**2 for i, j in edges)
            assert abs(q1 - q2) < 1e-8 * max(1, abs(q1)), (g6, q1, q2)
    return np.linalg.eigvalsh(K)[0]

if __name__ == "__main__":
    n, res, mod = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    check = len(sys.argv) > 4
    worst = (1e18, None); cnt = 0
    for g6 in graphs(n, res, mod):
        lam = K_of(g6, check)
        cnt += 1
        if lam < worst[0]: worst = (lam, g6)
    print(f"n={n} {res}/{mod}: graphs={cnt} min_eig={worst[0]:.3e} at {worst[1]}")
