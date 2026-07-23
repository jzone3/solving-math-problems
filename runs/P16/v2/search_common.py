"""P16 v2 — common utilities for searching counterexamples to BHS Bounds 44 and 46.

Exact statements (verified against arXiv:2606.14550v1, Table 2; NOT the catalog paraphrase):

  Bound 44:  mu(G) <= max_{ij in E} [ 2 + sqrt( 2*((d_i-1)^2 + (d_j-1)^2 + m_i*m_j - d_i*d_j) ) ]
  Bound 46:  mu(G) <= max_{ij in E} [ 2 + sqrt( 2*(d_i^2 + d_j^2) - 16*d_i*d_j/(m_i+m_j) + 4 ) ]

Convention (DHS Sec. 2): if the sqrt argument is negative the edge term is -inf
(edge excluded from the max). Graphs: finite simple, no isolated vertices
(disconnected allowed for search; a violating component gives a connected witness).

Floats are used HERE for search only. Any accepted witness must pass the exact
rational/Sturm verifier (verify_p16.py) before being claimed.
"""
import math
import numpy as np


def degrees_and_m(A):
    """A: 0/1 numpy adjacency. Returns (d, m) float arrays."""
    d = A.sum(axis=1).astype(float)
    m = (A @ d) / d
    return d, m


def rhs44_edge(di, dj, mi, mj):
    arg = 2.0 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
    if arg < 0:
        return -math.inf
    return 2.0 + math.sqrt(arg)


def rhs46_edge(di, dj, mi, mj):
    arg = 2.0 * (di ** 2 + dj ** 2) - 16.0 * di * dj / (mi + mj) + 4.0
    if arg < 0:
        return -math.inf
    return 2.0 + math.sqrt(arg)


def rhs_graph(A, edge_fn):
    d, m = degrees_and_m(A)
    n = len(d)
    best = -math.inf
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                v = edge_fn(d[i], d[j], m[i], m[j])
                if v > best:
                    best = v
    return best


def mu(A):
    d = A.sum(axis=1)
    L = np.diag(d) - A
    return float(np.linalg.eigvalsh(L)[-1])


# ---------- equitable-partition quotient machinery (DHS Sec. 4 style) ----------

def quotient_ok(B):
    """B: k x k nonneg integer matrix. Checks symmetrizability: b_ij>0 iff b_ji>0,
    and existence of positive cell sizes n_i with n_i b_ij = n_j b_ji (checked via
    spanning-tree ratio consistency). Returns None or a list of integer cell sizes
    (scaled to satisfy Lemma 2.3 parity/size constraints)."""
    from fractions import Fraction
    k = B.shape[0]
    for i in range(k):
        for j in range(k):
            if (B[i, j] > 0) != (B[j, i] > 0):
                return None
    # connectivity of the quotient support (else handle components separately; reject)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in range(k):
            if v not in seen and (B[u, v] > 0 or B[v, u] > 0):
                seen.add(v)
                stack.append(v)
    if len(seen) != k:
        return None
    # assign ratios n_j / n_0 by BFS; verify consistency
    r = [None] * k
    r[0] = Fraction(1)
    stack = [0]
    while stack:
        u = stack.pop()
        for v in range(k):
            if B[u, v] > 0:
                cand = r[u] * Fraction(int(B[u, v]), int(B[v, u]))
                if r[v] is None:
                    r[v] = cand
                    stack.append(v)
                elif r[v] != cand:
                    return None
    # scale to integers
    from math import lcm
    L = 1
    for x in r:
        L = lcm(L, x.denominator)
    n = [int(x * L) for x in r]
    # ensure Lemma 2.3: b_ii <= n_i - 1 with parity, b_ij <= n_j.  Scale by t (even t fixes parity).
    t = 2
    while True:
        ok = True
        for i in range(k):
            ni = n[i] * t
            if B[i, i] > ni - 1:
                ok = False
            for j in range(k):
                if B[i, j] > n[j] * t:
                    ok = False
        if ok:
            return [x * t for x in n]
        t += 2
        if t > 10 ** 6:
            return None


def quotient_data(B, n_sizes):
    """Given realizable quotient matrix B (k x k) with cell sizes, return
    (lam_max_LB, list of (s_i, m_i)) where s_i = degree of cell-i vertices and
    m_i = average neighbor degree.  All vertices in a cell share (d, m)."""
    k = B.shape[0]
    s = B.sum(axis=1).astype(float)
    m = (B @ s) / s
    LB = np.diag(s) - B.astype(float)
    lam = float(np.max(np.linalg.eigvals(LB).real))
    return lam, s, m


def quotient_rhs(B, s, m, edge_fn):
    k = B.shape[0]
    best = -math.inf
    for i in range(k):
        for j in range(k):
            if B[i, j] > 0 and (j > i or (j == i and B[i, i] > 0)):
                v = edge_fn(s[i], s[j], m[i], m[j])
                if v > best:
                    best = v
    return best
