"""P16 childE common utilities: Bound 44 proof attempt.

Bound 44: mu(G) <= max_{ij in E} [2 + sqrt(arg44)] with
  arg44 = 2((d_i-1)^2 + (d_j-1)^2 + m_i m_j - d_i d_j),
negative arg => term -inf.

Strengthened target used throughout (verified true for all connected n<=10 by
parent/childB): lam := rho(Q) - 2 = lam_max(A(L(G))) satisfies lam^2 <= max_e arg44.
"""
import math
import subprocess

import numpy as np


def graphs(n, extra="", suffix=""):
    p = subprocess.Popen(f"nauty-geng -qc {extra} {n} {suffix}", shell=True,
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


def graph_data(A):
    """degrees d, avg-neighbor-degrees m, edge list."""
    n = A.shape[0]
    d = A.sum(1)
    m = A @ d / d
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    return d, m, E


def arg44(di, dj, mi, mj):
    return 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)


def max_arg44(d, m, E):
    return max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)


def line_graph_lambda(A, d=None, E=None):
    """lam_max of A(L(G)) = rho(Q) - 2, via Q eigenvalue (fast, n x n)."""
    Q = np.diag(A.sum(1)) + A
    return np.linalg.eigvalsh(Q)[-1] - 2


def mu(A):
    d = A.sum(1)
    L = np.diag(d) - A
    return np.linalg.eigvalsh(L)[-1]


def line_graph_adj(E):
    ne = len(E)
    AL = np.zeros((ne, ne))
    for a in range(ne):
        ia, ja = E[a]
        for b in range(a + 1, ne):
            ib, jb = E[b]
            if ia in (ib, jb) or ja in (ib, jb):
                AL[a, b] = AL[b, a] = 1
    return AL
