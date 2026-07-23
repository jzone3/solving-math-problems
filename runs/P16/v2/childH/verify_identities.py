"""childH: machine verification of every identity used in PROOF44.md (childH).

H2 expansion, for y_e = s_e + c, e = ij:
  (A_L y)_e   = M_e + (c-2) s_e - 2c
  (A_L 1)_e   = s_e - 2
  (A_L s)_e   = M_e - 2 s_e
  (A_L M)_e   = (d_i-2) d_i (d_i+m_i) + (d_j-2) d_j (d_j+m_j) + P_i + P_j + W_i + W_j
  (A_L^2 y)_e = (A_L M)_e + (c-2)(M_e - 2 s_e) - 2c(s_e - 2)
with P_i = sum_{k~i} d_k^2, W_i = sum_{k~i} d_k m_k = (A^2 d)_i,
M_e = d_i(d_i+m_i) + d_j(d_j+m_j), s_e = d_i+d_j.

Also: Collatz-Wielandt sanity (lam <= max (A_L y)/y and lam^2 <= max (A_L^2 y)/y)
against true eigenvalues, on exhaustive n<=7 plus random graphs n<=30.
"""
import itertools
import random

import numpy as np

from common import graphs, g6_adj, graph_data, line_graph_adj

TOL = 1e-8


def check_graph(A, c):
    d, m, E = graph_data(A)
    n = A.shape[0]
    AL = line_graph_adj(E)
    ne = len(E)
    s = np.array([d[i] + d[j] for i, j in E])
    M = np.array([d[i] * (d[i] + m[i]) + d[j] * (d[j] + m[j]) for i, j in E])
    P = np.array([(A[i] * d**2).sum() for i in range(n)])
    W = A @ (d * m)
    y = s + c
    assert (y > 0).all()
    one = np.ones(ne)
    assert np.allclose(AL @ one, s - 2, atol=TOL)
    assert np.allclose(AL @ s, M - 2 * s, atol=TOL)
    assert np.allclose(AL @ y, M + (c - 2) * s - 2 * c, atol=TOL)
    ALM = np.array([(d[i] - 2) * d[i] * (d[i] + m[i])
                    + (d[j] - 2) * d[j] * (d[j] + m[j])
                    + P[i] + P[j] + W[i] + W[j] for i, j in E])
    assert np.allclose(AL @ M, ALM, atol=TOL)
    assert np.allclose(AL @ (AL @ y),
                       ALM + (c - 2) * (M - 2 * s) - 2 * c * (s - 2), atol=TOL)
    # W_i = (A^2 d)_i
    assert np.allclose(W, A @ A @ d, atol=TOL)
    # CW sanity
    lam = np.linalg.eigvalsh(AL)[-1] if ne > 0 else 0.0
    assert lam <= (AL @ y / y).max() + TOL
    assert lam * lam <= (AL @ (AL @ y) / y).max() + TOL


def rand_connected(n, p):
    while True:
        A = (np.random.rand(n, n) < p).astype(float)
        A = np.triu(A, 1)
        A = A + A.T
        # connectivity via BFS
        seen = {0}
        stack = [0]
        while stack:
            v = stack.pop()
            for u in np.nonzero(A[v])[0]:
                if u not in seen:
                    seen.add(u)
                    stack.append(int(u))
        if len(seen) == n and A.sum() > 0:
            return A


if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)
    cnt = 0
    for n in range(3, 8):
        for g6 in graphs(n):
            A = g6_adj(g6)
            for c in (-1.9, 0.0, 1.0, 7.5, 1000.0):
                check_graph(A, c)
            cnt += 1
    print(f"exhaustive n<=7: {cnt} graphs OK")
    for t in range(300):
        n = random.randint(5, 30)
        A = rand_connected(n, random.uniform(0.1, 0.7))
        smin = 2 * A.sum(1).min()
        for c in (-smin + 0.05, 0.0, 3.3, 100.0):
            check_graph(A, c)
    print("random graphs OK -- ALL IDENTITIES VERIFIED")
