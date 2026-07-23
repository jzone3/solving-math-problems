"""P16 childA -- exact symbolic perturbation analysis of BHS Bounds 44/46
around the bipartite-regular equality manifold.

Machinery: given a k x k quotient matrix B whose entries are sympy expressions
in d (and possibly extra integer parameters), with the bipartite-regular base
(row sums -> d, bipartite between a declared left/right cell split) so that
mu(L_B) = 2d + O(1):

  * cell degrees s_i = row sums of B, average neighbor degrees
    m_i = (sum_j B_ij s_j) / s_i (exact rational functions of d);
  * mu = largest root of charpoly of L_B = diag(s) - B, expanded as an exact
    Laurent/Taylor series in eps = 1/d around the branch x = 2d + O(1) via
    Newton iteration on formal series (exact rational coefficients);
  * each edge term T_ij = 2 + sqrt(arg_ij) expanded as an exact series in eps;
  * gap_ij = T_ij - mu as a series; RHS - mu = max_ij gap_ij.

The bound is violated for large d iff EVERY edge gap series has negative
leading coefficient. All coefficients are exact (sympy Rational / expressions
in the extra symbolic parameters); no floats on any sign decision.

Realizability: we only feed families where positive integer cell sizes n_i
with n_i B_ij = n_j B_ji exist for all integer d in range (checked per family;
symmetric B always realizable with equal large even cells, Lemma 2.3 of DHS).
"""
import sympy as sp

d = sp.Symbol('d', positive=True)
eps = sp.Symbol('eps', positive=True)
x = sp.Symbol('x')


def cell_data(B):
    """B: sympy Matrix (k x k). Returns (s, m, LB)."""
    k = B.rows
    s = [sp.simplify(sum(B[i, j] for j in range(k))) for i in range(k)]
    m = [sp.simplify(sum(B[i, j] * s[j] for j in range(k)) / s[i]) for i in range(k)]
    LB = sp.diag(*s) - B
    return s, m, LB


def edge_arg(bound, di, dj, mi, mj):
    if bound == 44:
        return 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
    if bound == 46:
        return 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
    raise ValueError(bound)


def ser(expr, order):
    """Exact series of expr (function of d) in eps = 1/d up to O(eps^order)."""
    e = expr.subs(d, 1 / eps)
    return sp.series(e, eps, 0, order).removeO().expand()


def mu_series(B, order, newton_steps=None):
    """Largest-eigenvalue branch of L_B near 2d, as exact series in eps=1/d.
    Newton iteration on the charpoly, seeded at 2/eps (=2d)."""
    _, _, LB = cell_data(B)
    p = (x * sp.eye(B.rows) - LB).det()
    p = sp.together(p)
    p = sp.fraction(p)[0]  # clear denominators (roots unchanged for x-poly)
    p = sp.Poly(sp.expand(p.subs(d, 1 / eps)), x)
    dp = p.diff(x)
    y = 2 / eps
    steps = newton_steps or (order.bit_length() + 3)
    for _ in range(steps):
        num = p.eval(y)
        den = dp.eval(y)
        corr = sp.series(sp.together(num / den), eps, 0, order + 2).removeO()
        y = sp.expand(y - corr)
        # truncate to keep it manageable
        y = sp.series(y, eps, 0, order + 2).removeO()
    # sanity: Newton correction p/p' (= error in y up to 2nd order) must vanish
    # to the requested order
    res = sp.series(sp.together(p.eval(y) / dp.eval(y)), eps, 0, order).removeO()
    assert sp.simplify(res) == 0, f"Newton did not converge: correction {res}"
    return sp.series(y, eps, 0, order).removeO().expand()


def edge_gap_series(B, bound, mu_ser, order):
    """List of ((i,j), gap_series) for every present quotient edge."""
    s, m, _ = cell_data(B)
    k = B.rows
    out = []
    for i in range(k):
        for j in range(i, k):
            if B[i, j] != 0:
                arg = edge_arg(bound, s[i], s[j], m[i], m[j])
                t = 2 + sp.sqrt(arg)
                tser = ser(t, order)
                out.append(((i, j), sp.expand(tser - mu_ser)))
    return out


def leading(sereps, maxord=12):
    """(power, coeff) of the lowest-order nonzero eps term of a series expr."""
    e = sp.expand(sereps)
    for kk in range(0, maxord):
        c = e.coeff(eps, kk)
        c = sp.simplify(c)
        if c != 0:
            return kk, c
    return None, sp.Integer(0)


def analyze(name, B, order=4, bounds=(44, 46)):
    print(f"=== {name} ===")
    mu_s = mu_series(B, order)
    print(f"  mu = {sp.nsimplify(mu_s)}  (series in eps=1/d)")
    results = {}
    for b in bounds:
        gaps = edge_gap_series(B, b, mu_s, order)
        print(f"  Bound {b}:")
        best = None  # edge with LARGEST term = the RHS max
        for (ij, g) in gaps:
            p_, c_ = leading(g, order)
            print(f"    edge {ij}: gap = {sp.simplify(g)}  -> leading eps^{p_} * ({c_})")
            key = series_key(g, order)
            if best is None or key > best[0]:
                best = (key, ij, g)
        _, ij, g = best
        p_, c_ = leading(g, order)
        print(f"    RHS-mu (max over edges) attained at edge {ij}: leading eps^{p_} * ({c_})")
        results[b] = (ij, p_, c_, g)
    return results


def series_key(g, order):
    """Lexicographic comparability key for series with RATIONAL coefficients."""
    return tuple(sp.Rational(sp.nsimplify(g.coeff(eps, kk))) for kk in range(order))
