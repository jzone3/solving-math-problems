"""Exact independent verifier for candidate counterexamples to BHS Bounds 44 / 46.

NO FLOATS on the accept path: all arithmetic is over Q (fractions.Fraction /
sympy.Rational), eigenvalue localization via Sturm sequences on the integer
characteristic polynomial.

Two witness formats:
  1. explicit graph:    verify_graph(adDuring, bound)   -- adjacency 0/1 list of lists
  2. quotient witness:  verify_quotient(B, cell_sizes, bound)
       B = k x k nonnegative-integer quotient matrix of an equitable partition.
       Checks Lemma 2.3 realizability (DHS 2026), then mu(G) >= lam_max(L_B)
       (Lemma 2.2) and lam_max(L_B) > RHS(bound) computed from cell data.

Statements verified against arXiv:2606.14550v1 Table 2:
  Bound 44: mu <= max_{ij in E} 2 + sqrt(2((d_i-1)^2+(d_j-1)^2+m_i m_j-d_i d_j))
  Bound 46: mu <= max_{ij in E} 2 + sqrt(2(d_i^2+d_j^2) - 16 d_i d_j/(m_i+m_j) + 4)
(negative sqrt argument => edge term = -infinity, i.e. excluded from the max)

A witness is ACCEPTED iff we certify   lam_lo > RHS   where lam_lo is a rational
lower bound on mu(G) (resp. lam_max(L_B)) certified by a Sturm root count, and
RHS comparison is done by exact rational inequalities: for each edge term
2 + sqrt(a) (a = rational sqrt argument >= 0) we require lam_lo > 2 and
(lam_lo - 2)^2 > a.
"""
from fractions import Fraction

import sympy as sp


def _charpoly(M):
    """Integer matrix (list of lists) -> sympy Poly of char poly in x (exact)."""
    x = sp.Symbol('x')
    Ms = sp.Matrix(M)
    return sp.Poly(Ms.charpoly(x).as_expr(), x)


def _count_roots_gt(poly, c):
    """Number of real roots (with multiplicity ignored; distinct roots) of poly in (c, oo)."""
    return sp.polys.polytools.count_roots(poly, inf=sp.Rational(c), sup=None)


def _largest_root_lower_bound(poly, target):
    """Certify that the largest real root lam of poly satisfies lam > target
    (target rational). Returns True/False using exact Sturm counts."""
    return _count_roots_gt(poly, sp.Rational(target)) >= 1


def _degrees_m(A):
    n = len(A)
    d = [sum(row) for row in A]
    assert all(x > 0 for x in d), "isolated vertex"
    m = [Fraction(sum(d[j] for j in range(n) if A[i][j]), d[i]) for i in range(n)]
    return d, m


def _edge_arg(bound, di, dj, mi, mj):
    di, dj, mi, mj = Fraction(di), Fraction(dj), Fraction(mi), Fraction(mj)
    if bound == 44:
        return 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
    if bound == 46:
        return 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
    raise ValueError(bound)


def _rhs_exceeded(bound, edges_data, lam_lo):
    """True iff for EVERY edge, term < lam_lo, i.e. arg < 0 (undefined) or
    (lam_lo - 2)^2 > arg (requires lam_lo > 2)."""
    lam_lo = Fraction(lam_lo)
    for (di, dj, mi, mj) in edges_data:
        a = _edge_arg(bound, di, dj, mi, mj)
        if a < 0:
            continue
        if lam_lo <= 2:
            return False
        if (lam_lo - 2) ** 2 <= a:
            return False
    return True


def verify_graph(A, bound, lam_lo):
    """A: 0/1 adjacency (list of lists), bound in {44,46}, lam_lo: rational string/Fraction.
    Certifies mu(G) > lam_lo > every RHS edge term. Returns True iff counterexample."""
    n = len(A)
    assert all(A[i][j] == A[j][i] and A[i][j] in (0, 1) and A[i][i] == 0
               for i in range(n) for j in range(n))
    d, m = _degrees_m(A)
    L = [[(d[i] if i == j else -A[i][j]) for j in range(n)] for i in range(n)]
    poly = _charpoly(L)
    if not _largest_root_lower_bound(poly, lam_lo):
        print("FAIL: could not certify mu(G) > lam_lo")
        return False
    edges = [(d[i], d[j], m[i], m[j]) for i in range(n) for j in range(i + 1, n) if A[i][j]]
    if not _rhs_exceeded(bound, edges, lam_lo):
        print("FAIL: some edge term >= lam_lo")
        return False
    print(f"PASS: graph on {n} vertices violates Bound {bound} (mu > {lam_lo} > RHS)")
    return True


def verify_quotient(B, sizes, bound, lam_lo):
    """B: k x k nonneg int quotient matrix, sizes: cell sizes (positive ints).
    Verifies Lemma 2.3 realizability, then lam_max(L_B) > lam_lo > all RHS terms."""
    k = len(B)
    assert len(sizes) == k and all(int(x) == x and x >= 1 for x in sizes)
    for i in range(k):
        assert all(int(b) == b and b >= 0 for b in B[i])
        if not (B[i][i] <= sizes[i] - 1 and (B[i][i] % 2 == 0 or sizes[i] % 2 == 0)):
            print("FAIL: Lemma 2.3 diagonal condition")
            return False
        for j in range(k):
            if i != j:
                if not (B[i][j] <= sizes[j] and sizes[i] * B[i][j] == sizes[j] * B[j][i]):
                    print("FAIL: Lemma 2.3 off-diagonal condition")
                    return False
    s = [sum(B[i]) for i in range(k)]
    assert all(x > 0 for x in s), "empty-degree cell"
    m = [Fraction(sum(B[i][j] * s[j] for j in range(k)), s[i]) for i in range(k)]
    LB = [[(s[i] if i == j else 0) - B[i][j] for j in range(k)] for i in range(k)]
    poly = _charpoly(LB)
    if not _largest_root_lower_bound(poly, lam_lo):
        print("FAIL: could not certify lam_max(L_B) > lam_lo")
        return False
    edges = []
    for i in range(k):
        for j in range(i, k):
            if B[i][j] > 0:
                edges.append((s[i], s[j], m[i], m[j]))
    if not _rhs_exceeded(bound, edges, lam_lo):
        print("FAIL: some edge term >= lam_lo")
        return False
    print(f"PASS: quotient witness (k={k}) violates Bound {bound} "
          f"(mu(G) >= lam_max(L_B) > {lam_lo} > RHS)")
    return True


if __name__ == "__main__":
    # self-tests: known NON-counterexamples must FAIL...
    P3 = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]  # mu = 3
    assert not verify_graph(P3, 44, Fraction(29, 10))
    assert not verify_graph(P3, 46, Fraction(29, 10))
    # ...and the machinery must certify a true strict inequality on a known
    # refuted bound: DHS Table 3 refutes Bound 40 with cells (1,39,312),
    # quotient [[0,39,0],[1,0,8],[0,1,0]] -- checked here against Bound 40's RHS
    # analogue is out of scope; instead sanity-check Sturm on K_{3,3}: mu = 6.
    K33 = [[0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0], [1, 1, 1, 0, 0, 0], [1, 1, 1, 0, 0, 0]]
    d, m = _degrees_m(K33)
    L = [[(d[i] if i == j else -K33[i][j]) for j in range(6)] for i in range(6)]
    assert _largest_root_lower_bound(_charpoly(L), Fraction(59, 10))
    assert not _largest_root_lower_bound(_charpoly(L), Fraction(61, 10))
    print("self-tests OK")
