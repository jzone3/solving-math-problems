"""For each candidate counterexample graph, extract an integer Farkas certificate y:
    A y >= 0 (componentwise),  1^T y = 0,  1^T A y > 0.
Such y proves: no x > 0 with A x = lambda*1 (take y^T A x = lambda * 1^T y = 0,
but (Ay)^T x > 0 unless Ay = 0, and 1^T Ay > 0 forces Ay != 0). Hence no vertex
multiplication of G is regular => counterexample to Brandt's conjecture (West form).

Certificate found by exact rational LP: max 1^T A y s.t. Ay >= 0, 1^T y = 0, |y| <= 1,
then scaled to integers.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p02lib import parse_graph6, degrees, simplex_max, _simplex_core, _pivot
from fractions import Fraction
F = Fraction

def farkas_certificate(n, adj):
    deg = degrees(n, adj)
    nv = 5 * n  # p, q, s, pslack, qslack ; y = p - q
    rows = []; rhs = []
    def newrow(): return [F(0)] * nv
    for v in range(n):
        r = newrow()
        for u in range(n):
            if (adj[v] >> u) & 1:
                r[u] = F(1); r[n + u] = F(-1)
        r[2 * n + v] = F(-1)
        rows.append(r); rhs.append(F(0))
    r = newrow()
    for u in range(n):
        r[u] = F(1); r[n + u] = F(-1)
    rows.append(r); rhs.append(F(0))
    for v in range(n):
        r = newrow(); r[v] = F(1); r[3 * n + v] = F(1); rows.append(r); rhs.append(F(1))
        r = newrow(); r[n + v] = F(1); r[4 * n + v] = F(1); rows.append(r); rhs.append(F(1))
    c = [F(0)] * nv
    for v in range(n):
        c[v] = F(deg[v]); c[n + v] = F(-deg[v])
    val, sol = simplex_max_with_solution(rows, rhs, c)
    if val is None or val <= 0:
        return None
    y = [sol[v] - sol[n + v] for v in range(n)]
    from math import lcm
    L = lcm(*[fy.denominator for fy in y]) if any(fy.denominator != 1 for fy in y) else 1
    return [int(fy * L) for fy in y]

def simplex_max_with_solution(A, b, c):
    m = len(A); n = len(A[0])
    A = [row[:] for row in A]; b = b[:]
    for i in range(m):
        if b[i] < 0:
            A[i] = [-x for x in A[i]]; b[i] = -b[i]
    N = n + m
    T = [A[i] + [F(1) if j == i else F(0) for j in range(m)] + [b[i]] for i in range(m)]
    basis = [n + i for i in range(m)]
    obj = [F(0)] * (N + 1)
    for i in range(m):
        for j in range(N + 1):
            obj[j] -= T[i][j]
    _simplex_core(T, obj, basis, N)
    if -obj[N] > 0:
        return None, None
    for i in range(m):
        if basis[i] >= n:
            for j in range(n):
                if T[i][j] != 0:
                    _pivot(T, basis, i, j, N); break
    obj2 = [-c[j] for j in range(n)] + [F(0)] * m + [F(0)]
    for i in range(m):
        bj = basis[i]
        if bj < n and obj2[bj] != 0:
            coef = obj2[bj]
            for j in range(N + 1):
                obj2[j] -= coef * T[i][j]
    _simplex_core(T, obj2, basis, N, forbid=set(range(n, N)))
    sol = [F(0)] * n
    for i in range(m):
        if basis[i] < n:
            sol[basis[i]] = T[i][N]
    return obj2[N], sol

if __name__ == '__main__':
    for g6 in sys.argv[1:]:
        n, adj = parse_graph6(g6)
        y = farkas_certificate(n, adj)
        print(g6, y)
