"""childG: symbolic verifications (sympy).

(1) Leaf-edge term: for leaf v with support c (d_v=1, m_v=d_c):
    arg46(vc) = 2 d_c^2 + 6 - 16 d_c/(d_c + m_c).
(2) Lemma G5 region: solve (d+m-2)^2 <= 2d^2 + 6 - 16 d/(d+m) in (d,m):
    when does Merris-at-c (d_c+m_c) not exceed the leaf-edge term at c?
    Reduce to polynomial p(d,m) <= 0, factor, and describe the boundary m(d).
(3) Identity for Theorem G3 (leafy D2): per-edge coefficient identities
    arg46 - 4 - 2di(di-2) - 2dj(dj-2) = 4(di+dj) - 16 di dj/(mi+mj)
    and its leaf-edge specialisations.
(4) Schur leaf elimination (Lemma G1) 2x2 sanity: symbolic Schur complement.
"""
import sympy as sp

d, m, di, dj, mi, mj, t = sp.symbols("d m d_i d_j m_i m_j t", positive=True)

print("== (1) leaf edge arg46 ==")
arg46 = 2*(di**2 + dj**2) - 16*di*dj/(mi + mj) + 4
leaf = arg46.subs({di: 1, mi: dj}).subs({dj: d, mj: m})
leaf_simpl = sp.simplify(leaf - (2*d**2 + 6 - 16*d/(d + m)))
print("arg46(leaf) - (2d^2+6-16d/(d+m)) =", leaf_simpl)
assert leaf_simpl == 0

print("== (2) Lemma G5 region ==")
s = d + m
ineq = sp.together((2*d**2 + 6 - 16*d/s) - (s - 2)**2)  # >= 0 wanted
num = sp.expand(sp.numer(ineq))
print("numerator (want >= 0, denom = d+m > 0):")
print(sp.factor(num))
# solve boundary in m for sample d
p = sp.Poly(num, m)
print("degree in m:", p.degree())
for dv in [2, 3, 4, 5, 8, 12, 20]:
    roots = sp.nroots(num.subs(d, dv))
    real = [sp.re(r) for r in roots if abs(sp.im(r)) < 1e-9]
    print(f"d={dv}: real roots in m: {[float(r) for r in real]}")
# asymptotic: m ~ (sqrt(2)-1) d ?
c = sp.symbols("c", positive=True)
lead = sp.expand(num.subs(m, c*d))
lead_poly = sp.Poly(lead, d)
print("leading coeff in d of num(m=c d):", sp.factor(lead_poly.coeffs()[0]))

print("== (3) Theorem G3 identity ==")
lhs = sp.simplify(arg46 - 4 - 2*di*(di-2) - 2*dj*(dj-2)
                  - (4*(di+dj) - 16*di*dj/(mi+mj)))
print("identity residual:", lhs)
assert lhs == 0
# leaf edge (di=1): condition arg46 - 4 - 2dj(dj-2) >= 0 becomes:
cond_leaf = sp.simplify((arg46 - 4 - 2*dj*(dj-2)).subs({di: 1, mi: dj}))
print("leaf-edge G3 condition (>=0):", sp.together(cond_leaf))

print("== (4) Lemma G1 Schur sanity (star K_{1,2} with values) ==")
# L for path v-c-w, eliminate leaf v: Schur complement of (t - 1) block
L = sp.Matrix([[1, -1, 0], [-1, 2, -1], [0, -1, 1]])
M = t*sp.eye(3) - L
S = M[1:, 1:] - M[1:, 0] * (1/M[0, 0]) * M[0:1, 1:]
target = t*sp.eye(2) - (sp.Matrix([[1, -1], [-1, 1]]) + sp.diag(t/(t-1), 0))
print("Schur residual:", sp.simplify(S - target))
