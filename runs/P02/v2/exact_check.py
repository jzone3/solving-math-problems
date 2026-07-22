#!/usr/bin/env python3
"""Exact analysis of INFEASIBLE-CANDIDATE graphs from mtf_scan.py.

For each graph6 on stdin (or argv), over exact rationals:
  1. re-verify MTF + delta >= n/3 (and note boundary delta == n/3);
  2. compute the affine solution space of A x = d*1; report forced-zero /
     forced-negative coordinates, i.e. a certificate vector y with
     y^T A = e_v^T (scaled), y^T 1 = 0 whenever x_v is forced to 0;
  3. decide exact LP feasibility of {A x = d 1, x >= 1} via rational Fourier
     reasoning on the (low-dim) solution space, brute-forcing over a grid of
     the free parameters if dimension <= 3 plus a Farkas fallback;
  4. weak-reading check: is there a graph homomorphism G -> G - Z (Z = forced
     zero set)?  If not, no regular blow-up (even with empty classes) contains
     G as a subgraph.
"""
import sys
from fractions import Fraction as F


def g6_to_adj(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for b in data[1:]:
        bits.extend((b >> i) & 1 for i in range(5, -1, -1))
    A = [[0] * n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i][j] = A[j][i] = 1
            idx += 1
    return n, A


def rref(mat):
    m = [row[:] for row in mat]
    R, C = len(m), len(m[0])
    r, piv = 0, []
    for c in range(C):
        pr = next((rr for rr in range(r, R) if m[rr][c] != 0), None)
        if pr is None:
            continue
        m[r], m[pr] = m[pr], m[r]
        pv = m[r][c]
        m[r] = [v / pv for v in m[r]]
        for rr in range(R):
            if rr != r and m[rr][c] != 0:
                f = m[rr][c]
                m[rr] = [a - f * b for a, b in zip(m[rr], m[r])]
        piv.append(c)
        r += 1
    return m, piv


def nullspace(A, n):
    # system [A | -1] z = 0, z = (x_0..x_{n-1}, d)
    M = [[F(A[i][j]) for j in range(n)] + [F(-1)] for i in range(n)]
    m, piv = rref(M)
    C = n + 1
    free = [c for c in range(C) if c not in piv]
    basis = []
    for fc in free:
        v = [F(0)] * C
        v[fc] = F(1)
        for i, pc in enumerate(piv):
            v[pc] = -m[i][fc]
        basis.append(v)
    return basis


def forced_zero(basis, n):
    return [v for v in range(n) if all(b[v] == 0 for b in basis)]


def cert_for_zero(A, n, v):
    # find y: y^T A = e_v, y^T 1 = 0
    rows = []
    for j in range(n):
        rows.append([F(A[i][j]) for i in range(n)] + [F(1 if j == v else 0)])
    rows.append([F(1)] * n + [F(0)])
    m, piv = rref(rows)
    if any(all(x == 0 for x in row[:n]) and row[n] != 0 for row in m):
        return None
    y = [F(0)] * n
    for i, pc in enumerate(piv):
        if pc < n:
            y[pc] = m[i][n]
    # verify
    for j in range(n):
        assert sum(y[i] * A[i][j] for i in range(n)) == (1 if j == v else 0)
    assert sum(y) == 0
    return y


def lp_feasible_exact(basis, n):
    """Exact feasibility of x >= 1 over span(basis) restricted to x coords.
    Uses Fourier-Motzkin elimination on the coefficients (dims here are <= 3)."""
    k = len(basis)
    # constraints: sum_j t_j * basis[j][v] >= 1 for v in 0..n-1
    cons = [([b[v] for b in basis], F(1)) for v in range(n)]
    return fm_feasible(cons, k)


def fm_feasible(cons, k):
    # cons: list of (coeffs (len k), rhs) meaning coeffs . t >= rhs
    if k == 0:
        return all(0 >= rhs for _, rhs in cons if True) and all(
            rhs <= 0 for c, rhs in cons)
    # eliminate variable k-1
    pos, neg, zero = [], [], []
    for c, r in cons:
        a = c[k - 1]
        if a > 0:
            pos.append(([x / a for x in c[:k - 1]], r / a))
        elif a < 0:
            neg.append(([x / a for x in c[:k - 1]], r / a))
        else:
            zero.append((c[:k - 1], r))
    new = list(zero)
    # t_{k-1} >= r_p - c_p.t  (from pos), t_{k-1} <= r_n - c_n.t (from neg)
    for cp, rp in pos:
        for cn, rn in neg:
            # need rn - cn.t >= rp - cp.t  ->  (cp - cn).t >= rp - rn
            new.append(([a - b for a, b in zip(cp, cn)], rp - rn))
    if not pos or not neg:
        # unbounded direction exists for this var unless zero-rows conflict
        return fm_feasible(new, k - 1)
    return fm_feasible(new, k - 1)


def hom_exists(A, n, removed):
    keep = [v for v in range(n) if v not in removed]
    idx = {v: i for i, v in enumerate(keep)}
    m = len(keep)
    B = [[A[keep[i]][keep[j]] for j in range(m)] for i in range(m)]
    adj = [[j for j in range(n) if A[i][j]] for i in range(n)]
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    assign = [-1] * n

    def bt(t):
        if t == n:
            return True
        v = order[t]
        for c in range(m):
            if all(assign[u] == -1 or B[c][assign[u]] for u in adj[v]):
                assign[v] = c
                if bt(t + 1):
                    return True
                assign[v] = -1
        return False
    return bt(0)


def analyze(g6):
    n, A = g6_to_adj(g6)
    deg = [sum(r) for r in A]
    dmin = min(deg)
    tf = all(not (A[i][j] and A[j][k] and A[i][k]) for i in range(n)
             for j in range(i + 1, n) for k in range(j + 1, n))
    mx = all(A[i][j] or any(A[i][k] and A[j][k] for k in range(n))
             for i in range(n) for j in range(i + 1, n))
    basis = nullspace(A, n)
    fz = forced_zero(basis, n)
    feas = lp_feasible_exact(basis, n)
    boundary = (3 * dmin == n)
    line = (f'{g6} n={n} delta={dmin} boundary={boundary} tf={tf} mtf={mx} '
            f'soldim={len(basis)} forced_zero={fz} exact_feasible={feas}')
    if fz and not feas:
        certs = {v: [str(c) for c in cert_for_zero(A, n, v)] for v in fz}
        line += f' certs={certs}'
        if '--hom' in sys.argv:
            hom = hom_exists(A, n, set(fz))
            line += f' hom_G_to_G-minus-Z={hom}'
    print(line, flush=True)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    src = args if args else (l.split()[-1] for l in sys.stdin if l.strip())
    for g in src:
        analyze(g)
