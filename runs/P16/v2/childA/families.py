"""Structured parametric families around the bipartite-regular equality manifold.

Each family: exact symbolic gap analysis (RHS - mu) per quotient edge, expanded
in eps = 1/d, with perturbation parameters kept symbolic where feasible.
"""
import sympy as sp
from perturb import d, eps, cell_data, edge_arg, mu_series, edge_gap_series, leading, analyze

sp.init_printing(use_unicode=False)


def F1_complete_bipartite():
    """K_{d,d+c}: mu = 2d+c exactly (closed form; no series needed)."""
    print("=== F1: K_{d, d+c} (complete bipartite, closed form) ===")
    c = sp.Symbol('c', nonnegative=True)
    a, b = d, d + c
    mu = a + b
    # single edge type: d_i=b (left vertex degree = size of right side)... careful:
    # left vertices have degree b=d+c, right have degree a=d; m_left = a, m_right = b.
    di, dj, mi, mj = b, a, a, b
    for bound in (44, 46):
        arg = edge_arg(bound, di, dj, mi, mj)
        gap = sp.simplify(2 + sp.sqrt(arg) - mu)
        print(f"  Bound {bound}: gap = {gap}")
        # expand around c=0 and around large d
        g0 = sp.series(gap, c, 0, 3).removeO()
        print(f"    expansion in c around 0: {sp.simplify(g0)}")
        # sign check: is gap >= 0 for all real d>=1, c>=0?  gap = sqrt(arg)-(2d+c-2)
        # equivalent to arg - (2d+c-2)^2 >= 0 (both sides nonneg when gap could vanish)
        diff = sp.expand(arg - (mu - 2) ** 2)
        print(f"    arg - (mu-2)^2 = {sp.factor(diff)}")


def F2_Kdd_minus_matching():
    """K_{d,d} minus a matching of size t (1 <= t <= d-1), 4-cell quotient.
    Cells: ML(t), UL(d-t), MR(t), UR(d-t)."""
    print("=== F2: K_{d,d} minus a matching of size t (symbolic t) ===")
    t = sp.Symbol('t', positive=True)
    B = sp.Matrix([
        [0, 0, t - 1, d - t],
        [0, 0, t, d - t],
        [t - 1, d - t, 0, 0],
        [t, d - t, 0, 0],
    ])
    order = 4
    mu_s = mu_series(B, order)
    print(f"  mu series (eps=1/d): {sp.simplify(mu_s)}")
    for bound in (44, 46):
        print(f"  Bound {bound}:")
        for (ij, g) in edge_gap_series(B, bound, mu_s, order):
            gs = sp.expand(g)
            coeffs = [sp.factor(sp.simplify(gs.coeff(eps, k))) for k in range(order)]
            print(f"    edge {ij}: coeffs (eps^0..eps^{order-1}) = {coeffs}")


def F2b_fixed_t():
    """Same family, t fixed small integers -- exact rational coefficients."""
    for tval in (1, 2, 3, 5):
        t = sp.Integer(tval)
        B = sp.Matrix([
            [0, 0, t - 1, d - t],
            [0, 0, t, d - t],
            [t - 1, d - t, 0, 0],
            [t, d - t, 0, 0],
        ])
        if tval == 1:
            # ML->MR entry is 0: drop; keep matrix (entry 0 just means no edge)
            pass
        analyze(f"F2b: K_dd minus matching t={tval}", B, order=4)


def F2c_near_perfect():
    """K_{d,d} minus matching of size d-u (u unmatched pairs), u symbolic."""
    print("=== F2c: K_{d,d} minus matching of size d-u (symbolic u >= 1) ===")
    u = sp.Symbol('u', positive=True)
    t = d - u
    B = sp.Matrix([
        [0, 0, t - 1, u],
        [0, 0, t, u],
        [t - 1, u, 0, 0],
        [t, u, 0, 0],
    ])
    order = 4
    mu_s = mu_series(B, order)
    print(f"  mu series: {sp.simplify(mu_s)}")
    for bound in (44, 46):
        print(f"  Bound {bound}:")
        for (ij, g) in edge_gap_series(B, bound, mu_s, order):
            gs = sp.expand(g)
            coeffs = [sp.factor(sp.simplify(gs.coeff(eps, k))) for k in range(order)]
            print(f"    edge {ij}: coeffs = {coeffs}")


def F3_biregular_ab():
    """(a,b)-biregular bipartite, a=d, b=d+c: 2-cell quotient B=[[0,d+c],[d,0]]?
    No: left cells have degree = number of right neighbors. Generic biregular
    (a,b): left degree a, right degree b, quotient [[0,a],[b,0]], realizable with
    n_L * a = n_R * b. mu(L_B): roots of (x-a)(x-b)-ab = x^2-(a+b)x = 0 -> a+b.
    Exact closed form, same as before but WITHOUT the complete structure:
    m_L = b, m_R = a always. So identical local data to K_{a,b}."""
    print("=== F3: (d, d+c)-biregular bipartite (2-cell) ===")
    c = sp.Symbol('c', nonnegative=True)
    a, b = d, d + c
    mu = a + b
    di, dj, mi, mj = a, b, b, a
    for bound in (44, 46):
        arg = edge_arg(bound, di, dj, mi, mj)
        diff = sp.factor(sp.expand(arg - (mu - 2) ** 2))
        print(f"  Bound {bound}: arg-(mu-2)^2 = {diff}   (gap>0 iff this >0)")


if __name__ == "__main__":
    F1_complete_bipartite()
    F3_biregular_ab()
    F2b_fixed_t()
    F2_Kdd_minus_matching()
    F2c_near_perfect()
