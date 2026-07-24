"""EXACT (rational arithmetic) verification that F2 fails on windmill F_k.

Builds M(F_k) over Fractions and exhibits an explicit rational vector x with
x^T M x < 0 (exact). By symmetry use the 3-dim quotient (hub, one per-triangle
pair symmetric coordinate): x = a on hub, b on all 2k outer vertices.
Actually use x from float eigenvector, rationalized, then verify exactly.

Also exact check of D1's K = diag(arg46) - A_L^2 on F_k and Bound 46 itself.
"""
from fractions import Fraction as F
import numpy as np
from common import build
from windmill import windmill


def exact_M_windmill(k):
    """M for F_k over exact rationals, using the vertex set {hub} + 2k outer."""
    n = 2 * k + 1
    A = [[0] * n for _ in range(n)]
    for t in range(k):
        u, v = 1 + 2 * t, 2 + 2 * t
        A[0][u] = A[u][0] = 1
        A[0][v] = A[v][0] = 1
        A[u][v] = A[v][u] = 1
    d = [F(sum(row)) for row in A]
    m = [F(sum(d[j] for j in range(n) if A[i][j])) / d[i] for i in range(n)]
    sig = [d[i] + m[i] - 4 for i in range(n)]
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i][j]]
    w = {}
    for (i, j) in edges:
        a4 = 2 * (d[i] ** 2 + d[j] ** 2) - F(16) * d[i] * d[j] / (m[i] + m[j])
        w[(i, j)] = 0 if a4 == 0 else 1 / a4
    # M_ii = 2 sig_i + 4 - d_i - sig_i^2 * sum_{e ni i} w_e
    # M_ij = -(1 + sig_i sig_j w_ij) on edges
    M = [[F(0)] * n for _ in range(n)]
    for i in range(n):
        Wi = sum(w[e] for e in edges if i in e)
        M[i][i] = 2 * sig[i] + 4 - d[i] - sig[i] ** 2 * Wi
    for (i, j) in edges:
        M[i][j] = M[j][i] = -(1 + sig[i] * sig[j] * w[(i, j)])
    return M, d, sig, w, edges


def quad_form(M, x):
    n = len(x)
    return sum(M[i][j] * x[i] * x[j] for i in range(n) for j in range(n))


for k in [16, 17, 18, 25]:
    # float eigenvector -> rational witness
    bd = build(windmill(k))
    ev, V = np.linalg.eigh(bd["M"])
    xf = V[:, 0]
    # rationalize with denominator 10^4
    x = [F(round(t * 10000), 10000) for t in xf]
    M, d, sig, w, edges = exact_M_windmill(k)
    val = quad_form(M, x)
    print(f"k={k}: float mineig={ev[0]:.6f}  EXACT x^T M x = {val} "
          f"= {float(val):.6f}  -> F2 {'VIOLATED' if val < 0 else 'ok'}",
          flush=True)

# where does the reduction chain stand on windmills? Check D1's K and Bound 46
import numpy.linalg as la

for k in [5, 12, 17, 25, 40, 80]:
    A = windmill(k)
    n = A.shape[0]
    d = A.sum(1)
    m = (A @ d) / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    E = len(edges)
    # line graph adjacency
    AL = np.zeros((E, E))
    for a in range(E):
        for b in range(a + 1, E):
            if len(set(edges[a]) & set(edges[b])) == 1:
                AL[a, b] = AL[b, a] = 1
    arg = np.array([2 * (d[i] ** 2 + d[j] ** 2) - 16 * d[i] * d[j] / (m[i] + m[j]) + 4
                    for (i, j) in edges])
    K = np.diag(arg) - AL @ AL
    evK = la.eigvalsh(K)
    # Bound 46: rho(Q)^2 <= max_e arg46(e)?  (childD chain: D1 => bound46)
    Q = np.diag(d) + A
    rhoQ = max(la.eigvalsh(Q))
    print(f"k={k}: min eig K = {evK[0]:.6f} ({'D1 ok' if evK[0] > -1e-9 else 'D1 FAILS'});"
          f" rho(Q)^2={rhoQ**2:.3f} max arg46={arg.max():.3f} "
          f"bound46 {'ok' if rhoQ**2 <= arg.max() + 1e-9 else 'FAILS'}", flush=True)
