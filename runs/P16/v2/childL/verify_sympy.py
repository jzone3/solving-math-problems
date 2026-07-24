"""childL symbolic verifications (sympy). Run: python3 verify_sympy.py

V-1  q-identity: q_{e,f}(rho) = E_e F (s_f - s_e) - w_f E_e - w_e F
     with E_e = z1_e - rho, F = rho - z1_f, w = zs - s z1.
V-2  clause-(b) linear form: rho s_e - zs_e + s_f(z1_e - rho)
     = (rho - z1_e)(s_e - s_f) - w_e   [linear in rho, slope s_e - s_f;
     and = -w_e at rho = z1_e].
V-3  Delta identity: E_e - sum_f E_f = 3 z1_e - zs_e + (s_e-3) rho given
     sum_f z1_f = zs_e - 2 z1_e and #nbrs = s_e - 2  (algebra shortcut).
V-4  Lemma X arithmetic: pendant edge f=ij (d_i=2, d_j=1), inner neighbor
     k = other neighbor of i:  z1_f = d_k;  zs_f = 25 + 4 m_k when d_k = 4,
     m_i = 5/2;  arg44_{kx} = 2(9 + (d_x-1)^2 + m_k m_x - 4 d_x) at d_k=4.
"""
import sympy as sp

rho, se, sf, z1e, z1f, zse, zsf = sp.symbols("rho s_e s_f z1_e z1_f zs_e zs_f")

# V-1
Ee = z1e - rho
F = rho - z1f
we = zse - se * z1e
wf = zsf - sf * z1f
q = (rho * sf - zsf) * (z1e - rho) - (rho * se - zse) * (z1f - rho)
assert sp.expand(q - (Ee * F * (sf - se) - wf * Ee - we * F)) == 0
print("V-1 ok")

# V-2
g = rho * se - zse + sf * (z1e - rho)
assert sp.expand(g - ((rho - z1e) * (se - sf) - we)) == 0
assert sp.expand(g.subs(rho, z1e) + we) == 0
print("V-2 ok")

# V-3
sumz1f = zse - 2 * z1e            # identity (A_L z1)_e = zs_e - 2 z1_e
nn = se - 2                       # number of line-graph neighbors of e
Delta = (z1e - rho) - (sumz1f - nn * rho)
assert sp.expand(Delta - (3 * z1e - zse + (se - 3) * rho)) == 0
print("V-3 ok")

# V-4 Lemma X arithmetic
dk, mk, dx, mx = sp.symbols("d_k m_k d_x m_x", positive=True)
di, dj = 2, 1
mi = sp.Rational(1, 2) * (dj + dk)          # neighbors of i are j and k
sg = di + dk                                 # g = ik
z1f_expr = sg - 2                            # single line-neighbor g
assert sp.simplify(z1f_expr - dk) == 0
Mg = di * (di + mi) + dk * (dk + mk)
zsf_expr = Mg - 2 * sg
zsf4 = sp.simplify(zsf_expr.subs(dk, 4))     # = 25 + 4 m_k - 12
assert sp.simplify(zsf4 - (13 + 4 * mk)) == 0
# zs_f = M_g - 2 s_g with s_g = 6: M_g = 9 + 16 + 4 m_k = 25 + 4 m_k
assert sp.simplify((Mg.subs(dk, 4)) - (25 + 4 * mk)) == 0
# zs_f = 21  <=>  m_k = 2
assert sp.solve(sp.Eq(zsf4, 21), mk) == [2]
# arg44_{kx} at d_k=4, m_k=2:
a44kx = 2 * ((dk - 1) ** 2 + (dx - 1) ** 2 + mk * mx - dk * dx)
a44kx = a44kx.subs({dk: 4, mk: 2})
assert sp.expand(a44kx - 2 * (9 + (dx - 1) ** 2 + 2 * mx - 4 * dx)) == 0
# d_x = 1 (leaf on k): m_x = 4 -> arg44 = 2(9+0+8-4) = 26 > 14
assert a44kx.subs({dx: 1, mx: 4}) == 26
# d_x = 2: arg44 <= 14  <=>  m_x <= 5/2
assert sp.solve(sp.Eq(a44kx.subs(dx, 2), 14), mx) == [sp.Rational(5, 2)]
print("V-4 ok")
print("ALL SYMBOLIC CHECKS PASS")
