"""General symmetric 4-cell bipartite quotient perturbation of the d-regular
bipartite equality manifold, with SYMBOLIC perturbation integers.

Left cells L1, L2; right cells R1, R2; symmetric quotient matrix (=> realizable
with equal, large, even cell sizes, DHS Lemma 2.3):

    B[L1,R1] = d - w + p11    B[L1,R2] = w + p12
    B[L2,R1] = w + p12        B[L2,R2] = d - w + p22
(symmetry forces B[L2,R1] = B[R1,L2] = B[L1,R2]-type independence: entries are
q11, q12, q21, q22 with q_ij = B[L_i, R_j]; the full 4x4 matrix is symmetric iff
we place q_ij and q_ji^T = q_ij ... i.e. all four entries are free, since block
positions (L_i,R_j) and (R_j,L_i) are transposes.  So q12 and q21 independent.)

Row sums (= degrees): s_{L1} = d + p11 + p12 - ... we keep them exact.

We expand the gap of EVERY quotient edge to order eps^3 (eps = 1/d) with
p11,p12,p21,p22,w symbolic, then scan integers exactly (Fraction arithmetic)
for a configuration where the MAX edge gap is negative to leading order.
"""
import itertools
import sympy as sp
from perturb import d, eps, mu_series, edge_gap_series

p11, p12, p21, p22, w = sp.symbols('p11 p12 p21 p22 w')

B = sp.Matrix([
    [0, 0, d - w + p11, w + p12],
    [0, 0, w + p21, d - w + p22],
    [d - w + p11, w + p21, 0, 0],
    [w + p12, d - w + p22, 0, 0],
])

ORDER = 3
print("computing symbolic mu series (4-cell, 5 symbolic params)...")
mu_s = mu_series(B, ORDER)
print("mu =", sp.simplify(mu_s))

gap_polys = {}
for bound in (44, 46):
    gaps = edge_gap_series(B, bound, mu_s, ORDER)
    gap_polys[bound] = []
    print(f"\nBound {bound}: edge gap coefficients (order eps^0..eps^{ORDER-1})")
    for (ij, g) in gaps:
        coeffs = [sp.simplify(sp.expand(g).coeff(eps, k)) for k in range(ORDER)]
        gap_polys[bound].append((ij, coeffs))
        for k, c in enumerate(coeffs):
            print(f"  edge {ij} eps^{k}: {sp.factor(c)}")

# ---- exact integer scan ----------------------------------------------------
print("\ninteger scan: w in 1..6, p in -3..3 (all four independent)")
params = (p11, p12, p21, p22, w)
found = []
for bound in (44, 46):
    lamb = [(ij, [sp.lambdify(params, c, 'sympy') for c in coeffs])
            for (ij, coeffs) in gap_polys[bound]]
    for wv in range(1, 7):
        for pv in itertools.product(range(-3, 4), repeat=4):
            # skip the exactly-regular case (all degrees equal & m equal -> equality)
            vals = pv + (wv,)
            # entries must be >= 0 and edges present: w+p12 >= 0 etc.
            if wv + pv[1] < 0 or wv + pv[2] < 0:
                continue
            keys = []
            for (ij, fs) in lamb:
                keys.append(tuple(sp.Rational(f(*vals)) for f in fs))
            mx = max(keys)
            # leading coefficient of the max edge
            lead = next((c for c in mx if c != 0), sp.Integer(0))
            if lead < 0:
                found.append((bound, vals, mx))
                print(f"  CANDIDATE bound {bound}: p={pv} w={wv} max-edge gap coeffs {mx}")
if not found:
    print("  no configuration with negative leading max-edge gap found")
