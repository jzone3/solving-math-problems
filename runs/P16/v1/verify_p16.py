#!/usr/bin/env python3
"""P16 exact verifier for candidate counterexamples to BHS bounds 44/46.

Input: cell sizes n, quotient matrix B (nonnegative integers), bound number.
Accept path is fully exact (Python ints / Fractions only; no floats):
  1. realizability of (n, B) per DHS arXiv:2606.14550 Lemma 2.3
     (b_ii <= n_i - 1; b_ii or n_i even; b_ij <= n_j; n_i b_ij = n_j b_ji),
     plus connectivity of the cell graph => a connected graph G on
     sum(n_i) >= 2 vertices with this equitable partition exists;
  2. mu(G) >= rho(L_B) (quotient eigenvalues interlace: standard lifting);
     a rational lower bound lam on rho(L_B) is certified via the exact
     characteristic polynomial of L_B (Faddeev-LeVerrier over Fractions)
     and Sturm-sequence sign counting: #roots > lam >= 1;
  3. RHS(bound) is computed per cell-edge with exact rational arithmetic;
     comparisons against "2 + sqrt(inner)" are done by exact squaring:
     lam > 2 + sqrt(inner)  <=>  lam > 2 and (lam-2)^2 > inner.
Prints PASS iff mu(G) > RHS is certified, i.e. the bound is refuted.

Exact bound forms (from DHS LaTeX source, Table 2; "2 +" outside sqrt):
  44: 2 + sqrt(2((d_i-1)^2 + (d_j-1)^2 + m_i m_j - d_i d_j))
  46: 2 + sqrt(2(d_i^2 + d_j^2) - 16 d_i d_j / (m_i + m_j) + 4)
"""
import sys
from fractions import Fraction


def realizable(n, B):
    k = len(n)
    if k < 1 or any(x < 1 for x in n):
        return False
    if sum(n) < 2:
        return False
    for i in range(k):
        if not (0 <= B[i][i] <= n[i] - 1):
            return False
        if B[i][i] % 2 == 1 and n[i] % 2 == 1:
            return False
        for j in range(k):
            if i != j:
                if not (0 <= B[i][j] <= n[j]):
                    return False
                if n[i] * B[i][j] != n[j] * B[j][i]:
                    return False
    if k == 1:
        return B[0][0] >= 1
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in range(k):
            if v not in seen and u != v and B[u][v] > 0:
                seen.add(v)
                stack.append(v)
    return len(seen) == k


def charpoly(M):
    """Faddeev-LeVerrier: coefficients of det(xI - M), exact Fractions.
    Returns list c with c[0]=1: p(x) = sum c[i] x^(k-i)."""
    k = len(M)
    M = [[Fraction(x) for x in row] for row in M]
    c = [Fraction(1)]
    N = [[Fraction(0)] * k for _ in range(k)]
    for m in range(1, k + 1):
        # N = M @ N + c[m-1] * I
        MN = [[sum(M[i][l] * N[l][j] for l in range(k)) for j in range(k)]
              for i in range(k)]
        for i in range(k):
            MN[i][i] += c[m - 1]
        N = MN
        tr = sum(sum(M[i][l] * N[l][i] for l in range(k)) for i in range(k))
        c.append(-tr / m)
    return c


def poly_eval(p, x):
    r = Fraction(0)
    for c in p:
        r = r * x + c
    return r


def poly_deriv(p):
    d = len(p) - 1
    return [p[i] * (d - i) for i in range(d)]


def poly_mod(a, b):
    a = a[:]
    while len(a) >= len(b) and any(x != 0 for x in a):
        if a[0] == 0:
            a.pop(0)
            continue
        f = a[0] / b[0]
        for i in range(len(b)):
            a[i] -= f * b[i]
        a.pop(0)
    while a and a[0] == 0:
        a.pop(0)
    return a


def sturm_chain(p):
    chain = [p, poly_deriv(p)]
    while len(chain[-1]) > 1 or (chain[-1] and chain[-1][0] != 0):
        r = poly_mod(chain[-2], chain[-1])
        if not r:
            break
        chain.append([-c for c in r])
    return chain


def sign_changes(chain, x):
    signs = []
    for p in chain:
        v = poly_eval(p, x)
        if v != 0:
            signs.append(1 if v > 0 else -1)
    return sum(1 for a, b in zip(signs, signs[1:]) if a != b)


def roots_gt(p, x, ub):
    """Number of real roots of p in (x, ub], via Sturm."""
    ch = sturm_chain(p)
    return sign_changes(ch, x) - sign_changes(ch, ub)


def certify_mu_lower(n, B, lam):
    """Certify rho(L_B) > lam (lam Fraction) exactly."""
    k = len(n)
    LB = [[Fraction(-B[i][j]) for j in range(k)] for i in range(k)]
    for i in range(k):
        LB[i][i] += sum(B[i])
    p = charpoly(LB)
    ub = Fraction(2 * max(sum(B[i]) for i in range(k)) + 1)  # mu <= 2*Delta
    return roots_gt(p, lam, ub) >= 1


def rhs_edges(n, B, which):
    """Return list of exact 'inner' values (Fractions) per cell-edge."""
    k = len(n)
    s = [Fraction(sum(B[i])) for i in range(k)]
    assert all(x >= 1 for x in s), "isolated vertices"
    m = [sum(B[i][j] * s[j] for j in range(k)) / s[i] for i in range(k)]
    inners = []
    for i in range(k):
        for j in range(i, k):
            if (i == j and B[i][i] > 0) or (i != j and B[i][j] > 0):
                di, mi, dj, mj = s[i], m[i], s[j], m[j]
                if which == 44:
                    inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
                elif which == 46:
                    inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
                else:
                    raise ValueError(which)
                inners.append(inner)
    return inners


def find_certifying_lambda(n, B, inners):
    """Binary-search (exact rationals) for lam with rho(L_B) > lam and
    lam > 2 + sqrt(inner) for all edges. Returns lam or None."""
    # need lam s.t. certify_mu_lower and for all inner: inner < 0 is not
    # allowed (bound not real) -- caller checks; else (lam-2)^2 > inner, lam>2
    lo = Fraction(2)
    hi = Fraction(2 * max(sum(row) for row in B) + 1)
    for _ in range(200):
        mid = (lo + hi) / 2
        if certify_mu_lower(n, B, mid):
            lo = mid
            if all((lo - 2) ** 2 > inner for inner in inners):
                return lo
        else:
            hi = mid
        if hi - lo < Fraction(1, 10 ** 12):
            break
    return lo if (lo > 2 and all((lo - 2) ** 2 > inner for inner in inners)) else None


def verify(n, B, which):
    if not realizable(n, B):
        print("FAIL: (n, B) not realizable as an equitable partition of a connected graph")
        return False
    inners = rhs_edges(n, B, which)
    if any(inner < 0 for inner in inners):
        print("FAIL: bound expression not real on some edge (inner < 0); not a clean counterexample")
        return False
    lam = find_certifying_lambda(n, B, inners)
    if lam is None:
        print("FAIL: could not certify rho(L_B) > RHS")
        return False
    print(f"certified: mu(G) >= rho(L_B) > {lam} = {float(lam):.9f}")
    print(f"and (lam-2)^2 > inner for all {len(inners)} cell-edges, so mu(G) > RHS_{which}(G)")
    print("PASS")
    return True


if __name__ == "__main__":
    # usage: verify_p16.py <bound> "<n list>" "<B rows ; separated>"
    which = int(sys.argv[1])
    n = [int(x) for x in sys.argv[2].replace(',', ' ').split()]
    B = [[int(x) for x in row.replace(',', ' ').split()] for row in sys.argv[3].split(';')]
    ok = verify(n, B, which)
    sys.exit(0 if ok else 1)
