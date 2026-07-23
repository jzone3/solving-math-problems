"""childH: sympy verification of the algebraic steps in PROOF44.md (childH).

1. Lemma H1 normalization: 2 + (M + (c-2)s - 2c)/(s+c) == (M + c s)/(s + c).
2. Linear-in-c criterion: (A_L^2 y)_e - R(s_e+c) is linear in c with slope
   sigma_e = M_e - 4 s_e + 4 - R and intercept (A_L M)_e - 2 M_e + 4 s_e - R s_e.
"""
import sympy as sp

M, s, c, R, ALM = sp.symbols("M s c R ALM", real=True)

lhs = 2 + (M + (c - 2) * s - 2 * c) / (s + c)
assert sp.simplify(lhs - (M + c * s) / (s + c)) == 0

AL2y = ALM + (c - 2) * (M - 2 * s) - 2 * c * (s - 2)
expr = sp.expand(AL2y - R * (s + c))
assert sp.diff(expr, c, 2) == 0
assert sp.simplify(sp.diff(expr, c) - (M - 4 * s + 4 - R)) == 0
assert sp.simplify(expr.subs(c, 0) - (ALM - 2 * M + 4 * s - R * s)) == 0
print("sympy: all algebraic identities verified")
