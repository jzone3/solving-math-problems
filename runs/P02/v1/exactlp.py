#!/usr/bin/env python3
"""Exact rational simplex (two-phase, Bland's rule) used to certify the
multiplication-LP for P02.  Standalone: only stdlib (fractions).

LP solved:  maximize t
  s.t.  sum_{u in N(v)} x_u - lam = 0   for all v      (equalities)
        x_v - t >= 0                    for all v
        t <= 1
        x, lam, t >= 0
This LP is always feasible (all-zero).  Optimum > 0 iff there is x > 0 with
Ax constant, iff G has a regular vertex-multiplication supergraph (see
sweep.py docstring for the scaling argument).
"""
from fractions import Fraction

F = Fraction


def simplex_max(c, A, b):
    """Maximize c.x s.t. A x = b, x >= 0, exact Fractions.
    Assumes b >= 0. Returns (status, value) with status in {'opt','unbounded'}."""
    m = len(A)
    n = len(A[0])
    # add artificial vars, phase 1
    T = [[F(x) for x in row] + [F(1) if i == j else F(0) for j in range(m)] + [F(b[i])]
         for i, row in enumerate(A)]
    basis = [n + i for i in range(m)]
    N = n + m

    def pivot(T, basis, r, col):
        p = T[r][col]
        T[r] = [x / p for x in T[r]]
        for i in range(len(T)):
            if i != r and T[i][col] != 0:
                f = T[i][col]
                T[i] = [a - f * b2 for a, b2 in zip(T[i], T[r])]
        basis[r] = col

    def solve(T, basis, cost, N):
        # cost: list length N (objective to maximize)
        while True:
            # reduced costs
            z = [F(0)] * (N + 1)
            for i, bi in enumerate(basis):
                cb = cost[bi]
                if cb != 0:
                    for j in range(N + 1):
                        z[j] += cb * T[i][j]
            enter = -1
            for j in range(N):
                if cost[j] - z[j] > 0:
                    enter = j
                    break  # Bland
            if enter < 0:
                return 'opt', z[N]
            # ratio test (Bland: smallest basis index tie-break)
            leave, best = -1, None
            for i in range(len(T)):
                if T[i][enter] > 0:
                    ratio = T[i][N] / T[i][enter]
                    if best is None or ratio < best or \
                       (ratio == best and basis[i] < basis[leave]):
                        best, leave = ratio, i
            if leave < 0:
                return 'unbounded', None
            pivot(T, basis, leave, enter)

    # phase 1: minimize sum of artificials = maximize -sum
    cost1 = [F(0)] * n + [F(-1)] * m
    st, val = solve(T, basis, cost1, N)
    if val != 0:
        return 'infeasible', None
    # drive artificials out of basis if present (degenerate rows)
    for i in range(m):
        if basis[i] >= n:
            for j in range(n):
                if T[i][j] != 0:
                    pivot(T, basis, i, j)
                    break
    # drop artificial columns
    keep = list(range(n)) + [N]
    T = [[row[j] for j in keep] for row in T]
    # rows whose basis is still artificial are all-zero: drop them
    rows = [i for i in range(m) if basis[i] < n]
    T = [T[i] for i in rows]
    basis = [basis[i] for i in rows]
    cost2 = [F(x) for x in c]
    st, val = solve(T, basis, cost2, n)
    return st, val


def exact_max_t(n, adj):
    """adj: bitmask adjacency. Returns exact optimum t (Fraction) of the LP."""
    # vars: x_0..x_{n-1}, lam, t, s_0..s_{n-1} (x_v - t - s_v = 0), u (t + u = 1)
    nv = n + 2 + n + 1
    A, b = [], []
    for v in range(n):
        row = [F(0)] * nv
        for u2 in range(n):
            if adj[v] >> u2 & 1:
                row[u2] = F(1)
        row[n] = F(-1)
        A.append(row); b.append(F(0))
    for v in range(n):
        row = [F(0)] * nv
        row[v] = F(1); row[n + 1] = F(-1); row[n + 2 + v] = F(-1)
        A.append(row); b.append(F(0))
    row = [F(0)] * nv
    row[n + 1] = F(1); row[nv - 1] = F(1)
    A.append(row); b.append(F(1))
    c = [F(0)] * nv
    c[n + 1] = F(1)
    st, val = simplex_max(c, A, b)
    assert st == 'opt', st
    return val


if __name__ == '__main__':
    # self-test: C5 (Andrasfai graph), already regular -> t = 1
    n = 5
    adj = [0] * n
    for i in range(n):
        for j in (i + 1, i + 4):
            adj[i] |= 1 << (j % n)
    print('C5 opt t =', exact_max_t(n, adj))  # expect 1
    # star K_{1,3}: maximal TF, x_center appears in all leaf eqs;
    # leaf eq: x_center = lam; center eq: x_l1+x_l2+x_l3 = lam -> feasible? needs
    # x_center = lam and sum leaves = lam -> pick leaves 1,1,1 lam=3 center=3: t=1
    adj = [0b1110, 1, 1, 1]
    print('K13 opt t =', exact_max_t(4, adj))
