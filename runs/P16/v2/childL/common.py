"""P16 childL common utilities (Conjecture J attack).

Definitions (see childJ/PROOF_H.md):
  s_e = d_i + d_j, z1_e = (A_L^2 1)_e, zs_e = (A_L^2 s)_e,
  arg44_e = 2((d_i-1)^2 + (d_j-1)^2 + m_i m_j - d_i d_j),
  B2(e) = edges at line-graph distance <= 2 from e (incl. e),
  rho0(e) = max_{g in B2(e)} arg44_g,
  rho1(e) = max_{g in B1(e)} arg44_g  (1-ball version).
"""
from fractions import Fraction
import subprocess

import numpy as np


def geng(n, extra=""):
    p = subprocess.Popen(f"nauty-geng -qc {extra} {n}", shell=True,
                         stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        yield line.strip()


def gentreeg(n):
    p = subprocess.Popen(f"nauty-gentreeg -q {n}", shell=True,
                         stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        yield line.strip()


def s6_adj(s6):
    assert s6.startswith(":")
    data = [ord(c) - 63 for c in s6[1:]]
    n = data[0]
    assert n < 63
    bits = []
    for v in data[1:]:
        bits += [(v >> t) & 1 for t in range(5, -1, -1)]
    k = max(1, (n - 1).bit_length())
    A = np.zeros((n, n), dtype=np.int64)
    v = 0
    pos = 0
    while pos + 1 + k <= len(bits):
        b = bits[pos]
        xval = 0
        for t in bits[pos + 1:pos + 1 + k]:
            xval = (xval << 1) | t
        pos += 1 + k
        if b:
            v += 1
        if xval >= n or v >= n:
            break
        if xval > v:
            v = xval
        else:
            A[xval, v] = A[v, xval] = 1
    return A


def g6_adj(g6):
    if g6.startswith(":"):
        return s6_adj(g6)
    data = [ord(c) - 63 for c in g6]
    n = data[0]
    bits = []
    for v in data[1:]:
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    A = np.zeros((n, n), dtype=np.int64)
    idx = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[idx]
            idx += 1
    return A


def edge_env(A):
    """Return per-edge exact data as lists of Fractions/ints:
    E, s, z1, zs, arg44, rho0, rho1."""
    n = A.shape[0]
    d = A.sum(1)
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    ne = len(E)
    m = [Fraction(int((A[i] * d).sum()), int(d[i])) for i in range(n)]
    s = [int(d[i] + d[j]) for i, j in E]
    a44 = [2 * ((d[i] - 1) ** 2 + (d[j] - 1) ** 2 + m[i] * m[j] - d[i] * d[j])
           for i, j in E]
    AL = np.zeros((ne, ne), dtype=np.int64)
    for a in range(ne):
        ia, ja = E[a]
        for b in range(a + 1, ne):
            ib, jb = E[b]
            if ia in (ib, jb) or ja in (ib, jb):
                AL[a, b] = AL[b, a] = 1
    AL2 = AL @ AL
    z1 = (AL2 @ np.ones(ne, dtype=np.int64)).tolist()
    zs = (AL2 @ np.array(s, dtype=np.int64)).tolist()
    # B1/B2 membership (incl. self)
    B1 = AL + np.eye(ne, dtype=np.int64)
    B2 = B1 + AL2
    rho0 = [max(a44[b] for b in range(ne) if B2[a, b] > 0) for a in range(ne)]
    rho1 = [max(a44[b] for b in range(ne) if B1[a, b] > 0) for a in range(ne)]
    return d, m, E, s, z1, zs, a44, rho0, rho1, AL
