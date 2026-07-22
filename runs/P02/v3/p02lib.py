"""P02 V3 (ILP-duality) toolkit.

Problem: G maximal triangle-free (MTF), delta(G) >= n/3.  Conjecture (Brandt 2002):
exists integer multiplicities x_v >= 1 with sum_{u in N(v)} x_u = d for all v
(the vertex-multiplication blowup is regular; blowups of TF graphs stay TF).

Key reduction (scaling): integer feasibility for SOME d  <=>  rational LP
feasibility of {x > 0, A x = lambda*1}.  Since (Ax)_v > 0 whenever x > 0 and
delta >= 1, we may normalize lambda = 1.  Define

    m*(G) = max { m : exists x with A x = 1, x >= m*1 }   (LP; may be infeasible)

Then G is a COUNTEREXAMPLE  iff  m*(G) <= 0 or the LP is infeasible.
Farkas certificate of infeasibility of {x >= 1, Ax = lambda*1, lambda free}:
    y in Q^n with  A y >= 0 (componentwise),  1^T y = 0,  deg^T y > 0.
m* is used as the continuous LP-duality score guiding local search (minimize it).
"""
from fractions import Fraction
import itertools, random

# ---------- graph6 ----------
def parse_graph6(s):
    s = s.strip()
    data = [ord(c) - 63 for c in s]
    n = data[0]
    assert 0 <= n <= 62
    bits = []
    for b in data[1:]:
        bits.extend(((b >> k) & 1) for k in range(5, -1, -1))
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj

def to_graph6(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (adj[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k+6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return ''.join(out)

# ---------- properties ----------
def is_triangle_free(n, adj):
    for v in range(n):
        nb = adj[v]
        u = nb
        while u:
            w = u & -u
            i = w.bit_length() - 1
            u ^= w
            if adj[i] & nb & ~((1 << (i+1)) - 1):
                return False
    return True

def is_maximal_tf(n, adj):
    # TF + every non-adjacent pair (incl. requirement of no isolated twins issue)
    # has a common neighbor
    for u in range(n):
        for v in range(u+1, n):
            if not (adj[u] >> v) & 1:
                if not (adj[u] & adj[v]):
                    return False
    return True

def degrees(n, adj):
    return [bin(a).count('1') for a in adj]

# ---------- exact rational LP: m*(G) ----------
# maximize m  s.t.  A x - 1*m_shift ... we solve: exists x: Ax = 1, x >= m.
# Variables x_1..x_n, m.  max m s.t. Ax = 1, x_v - m >= 0.
# Small exact simplex over Fractions (n <= ~40).

def exact_mstar(n, adj):
    """Return (status, mstar) with exact Fractions.
    status: 'ok' (mstar computed), 'infeasible' (Ax=1 has no solution)."""
    # Solve with simplex on: max m ; s.t. sum_{u~v} x_u = 1 ; x_v - m = s_v >= 0
    # Substitute x_v = m + s_v: sum_{u~v}(m+s_u)=1 -> deg(v)*m + sum_{u~v}s_u = 1.
    # LP: max m s.t. deg(v)*m + sum_{u~v} s_u = 1, s >= 0, m free.
    # m free: m = mp - mn, mp,mn >= 0.
    deg = degrees(n, adj)
    # columns: s_0..s_{n-1}, mp, mn ; rows: n equalities, rhs 1
    A = []
    for v in range(n):
        row = [Fraction(1) if (adj[v] >> u) & 1 else Fraction(0) for u in range(n)]
        row.append(Fraction(deg[v]))
        row.append(Fraction(-deg[v]))
        A.append(row)
    b = [Fraction(1)] * n
    c = [Fraction(0)] * n + [Fraction(1), Fraction(-1)]  # maximize m
    res = simplex_max(A, b, c)
    if res is None:
        return 'infeasible', None
    return 'ok', res

def simplex_max(A, b, c):
    """Exact two-phase simplex: max c^T z s.t. A z = b, z >= 0 (b >= 0 assumed).
    Returns optimal value, None if infeasible, raises if unbounded."""
    m = len(A); n = len(A[0])
    # ensure b >= 0
    A = [row[:] for row in A]; b = b[:]
    for i in range(m):
        if b[i] < 0:
            A[i] = [-x for x in A[i]]; b[i] = -b[i]
    # phase 1: add artificials
    N = n + m
    T = [A[i] + [Fraction(1) if j == i else Fraction(0) for j in range(m)] + [b[i]]
         for i in range(m)]
    basis = [n + i for i in range(m)]
    # phase-1 objective: minimize sum artificials = maximize -sum
    obj = [Fraction(0)] * (N + 1)
    for i in range(m):
        for j in range(N + 1):
            obj[j] -= T[i][j]
    _simplex_core(T, obj, basis, N)
    if -obj[N] > 0:  # optimal phase-1 value = obj[N]... check residual
        return None
    # drive artificials out of basis if present (pivot on any nonzero orig col)
    for i in range(m):
        if basis[i] >= n:
            piv = None
            for j in range(n):
                if T[i][j] != 0:
                    piv = j; break
            if piv is not None:
                _pivot(T, basis, i, piv, N)
        # else row is redundant; leave (artificial stays 0)
    # phase 2
    obj2 = [-c[j] for j in range(n)] + [Fraction(0)] * m + [Fraction(0)]
    for i in range(m):
        bj = basis[i]
        if bj < n and obj2[bj] != 0:
            coef = obj2[bj]
            for j in range(N + 1):
                obj2[j] -= coef * T[i][j]
    # forbid artificials re-entering: mark their reduced costs
    _simplex_core(T, obj2, basis, N, forbid=set(range(n, N)))
    return obj2[N]

def _simplex_core(T, obj, basis, N, forbid=frozenset()):
    m = len(T)
    while True:
        # Bland's rule
        enter = None
        for j in range(N):
            if j in forbid:
                continue
            if obj[j] < 0:
                enter = j; break
        if enter is None:
            return
        ratio = None; leave = None
        for i in range(m):
            if T[i][enter] > 0:
                r = T[i][N] / T[i][enter]
                if ratio is None or r < ratio or (r == ratio and basis[i] < basis[leave]):
                    ratio = r; leave = i
        if leave is None:
            raise ArithmeticError('unbounded')
        _pivot(T, basis, leave, enter, N)
        coef = obj[enter]
        if coef != 0:
            for j in range(N + 1):
                obj[j] -= coef * T[leave][j]

def _pivot(T, basis, r, col, N):
    piv = T[r][col]
    T[r] = [x / piv for x in T[r]]
    for i in range(len(T)):
        if i != r and T[i][col] != 0:
            coef = T[i][col]
            T[i] = [T[i][j] - coef * T[r][j] for j in range(N + 1)]
    basis[r] = col

def is_counterexample_exact(n, adj):
    st, ms = exact_mstar(n, adj)
    if st == 'infeasible':
        return True, None
    return (ms <= 0), ms
