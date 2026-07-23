"""F4: 3-cell bipartite quotient family (left split in two cells, one right cell).

B = [[0, 0, d+p],
     [0, 0, d+q],
     [d-h, h, 0]]

Right-cell degree = d exactly; left degrees d+p, d+q. Realizable: cell sizes
n1, n2, n3 > 0 with n1(d+p) = n3(d-h), n2(d+q) = n3 h  (rational solution always;
integer sizes for suitable n3, all conditions of DHS Lemma 2.3 satisfiable by
scaling). Base p=q=0, any h: (d,d)-biregular bipartite = equality manifold.

Expand gap in eps=1/d with p, q, h symbolic; then exact integer scan.
"""
import itertools
import sympy as sp
from perturb import d, eps, mu_series, edge_gap_series

p, q, h = sp.symbols('p q h')

B = sp.Matrix([
    [0, 0, d + p],
    [0, 0, d + q],
    [d - h, h, 0],
])

ORDER = 3
print("computing symbolic mu series (3-cell, params p,q,h)...")
mu_s = mu_series(B, ORDER)
print("mu =", sp.simplify(mu_s))

gap_polys = {}
for bound in (44, 46):
    gaps = edge_gap_series(B, bound, mu_s, ORDER)
    gap_polys[bound] = []
    print(f"\nBound {bound}: edge gap coefficients")
    for (ij, g) in gaps:
        coeffs = [sp.simplify(sp.expand(g).coeff(eps, k)) for k in range(ORDER)]
        gap_polys[bound].append((ij, coeffs))
        for k, c in enumerate(coeffs):
            print(f"  edge {ij} eps^{k}: {sp.factor(c)}")

print("\ninteger scan: p,q in -4..4, h in 1..8")
params = (p, q, h)
found = 0
for bound in (44, 46):
    lamb = [(ij, [sp.lambdify(params, c, 'sympy') for c in coeffs])
            for (ij, coeffs) in gap_polys[bound]]
    for pv, qv, hv in itertools.product(range(-4, 5), range(-4, 5), range(1, 9)):
        if pv == qv == 0:
            continue
        keys = [tuple(sp.Rational(f(pv, qv, hv)) for f in fs) for (ij, fs) in lamb]
        mx = max(keys)
        lead = next((c for c in mx if c != 0), sp.Integer(0))
        if lead < 0:
            found += 1
            print(f"  CANDIDATE bound {bound}: p={pv} q={qv} h={hv} max coeffs {mx}")
if not found:
    print("  no configuration with negative leading max-edge gap found")
