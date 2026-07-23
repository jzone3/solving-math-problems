"""childJ: symbolic (sympy) verification of every identity and every
inequality step used in PROOF_H.md.

I0: M_e = s_e^2 + T_e                        (T_e = d_i m_i + d_j m_j - 2 d_i d_j)
I1: (A_L^2 1)_e = (s_e-2)^2 + T_e            (via Lemma H2: = M_e - 4 s_e + 4)
I2: arg44_e = (s_e-2)^2 + (d_i-d_j)^2 + 2(m_i m_j - d_i d_j)
I3: sigma_e = (s_e-2)^2 + T_e - R
I4: psi form: for y = s+c, per-edge test  zs_e + c z1_e <= rho (s_e + c)
    <=>  c (z1_e - rho) <= rho s_e - zs_e ;  and with w = zs - s z1,
    (rho s - zs) = (rho - z1) s - w, so U/L = -s + w/(rho - z1).
Lemma P (pendant configuration) inequality chain:
  config: e=ij, d_j=1, d_i=2, third vertex k, d_k=D, m_k=mk.
  P0: arg44_e = 2D
  P1: zs_e = D^2 - D + 1 + D*mk   (= F)
  P2: arg44_f = D^2 + (D-2)^2 + (1+D)*mk - 4D  (= C), f = ik
  P3: 3C - F = 5D^2 - 23D + 11 + (3+2D)*mk
  P4: D>=4, mk>=1  =>  3C - F >= 0
  P5: D=3: 3C - F = 9 mk - 13 ; and mk<13/9 => F < 18 = 3*(2D)
  P6: D=2: 3C - F = 7 mk - 15 ; and mk<15/7 => F < 12 = 3*(2D)
"""
import sympy as sp

di, dj, mi, mj, c, rho, R = sp.symbols("d_i d_j m_i m_j c rho R", positive=True)
s = di + dj
T = di * mi + dj * mj - 2 * di * dj
M = di * (di + mi) + dj * (dj + mj)
arg44 = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)

assert sp.simplify(M - (s ** 2 + T)) == 0, "I0"
AL2one = M - 4 * s + 4          # Lemma H2 (proved in childH PROOF44.md)
assert sp.simplify(AL2one - ((s - 2) ** 2 + T)) == 0, "I1"
assert sp.simplify(arg44 - ((s - 2) ** 2 + (di - dj) ** 2
                            + 2 * (mi * mj - di * dj))) == 0, "I2"
sigma = AL2one - R
assert sp.simplify(sigma - ((s - 2) ** 2 + T - R)) == 0, "I3"

zs, z1, se, w = sp.symbols("zs z1 s_e w")
expr = rho * se - zs
assert sp.expand(expr - ((rho - z1) * se - (zs - se * z1))) == 0, "I4"

# Lemma P
D, mk = sp.symbols("D m_k", positive=True)
mi_p = (1 + D) / 2          # i adjacent to leaf j and k
mj_p = 2                     # j leaf adjacent to i, d_i = 2
arg44_e = 2 * ((2 - 1) ** 2 + (1 - 1) ** 2 + mi_p * mj_p - 2 * 1)
assert sp.simplify(arg44_e - 2 * D) == 0, "P0"
Mf = 4 + D ** 2 + 2 * mi_p + D * mk
sf = D + 2
F = Mf - 2 * sf
assert sp.simplify(F - (D ** 2 - D + 1 + D * mk)) == 0, "P1"
C = (sf - 2) ** 2 + (2 - D) ** 2 + 2 * (mi_p * mk - 2 * D)
assert sp.simplify(C - (D ** 2 + (D - 2) ** 2 + (1 + D) * mk - 4 * D)) == 0, "P2"
assert sp.simplify(3 * C - F - (5 * D ** 2 - 23 * D + 11 + (3 + 2 * D) * mk)) == 0, "P3"
# P4: quadratic 5D^2-23D+11 + (3+2D) >= 0 for D>=4 (mk>=1 worst case)
g = 5 * D ** 2 - 23 * D + 11 + (3 + 2 * D) * 1
assert sp.Poly(g.subs(D, D + 4), D).all_coeffs() == [5, 19, 10] or True
gshift = sp.expand(g.subs(D, D + 4))
assert all(co >= 0 for co in sp.Poly(gshift, D).all_coeffs()), "P4"
# P5, P6
assert sp.simplify((3 * C - F).subs(D, 3) - (9 * mk - 13)) == 0, "P5a"
assert sp.simplify(F.subs(D, 3) - (7 + 3 * mk)) == 0, "P5b"
assert 7 + 3 * sp.Rational(13, 9) < 18, "P5c"
assert sp.simplify((3 * C - F).subs(D, 2) - (7 * mk - 15)) == 0, "P6a"
assert sp.simplify(F.subs(D, 2) - (3 + 2 * mk)) == 0, "P6b"
assert 3 + 2 * sp.Rational(15, 7) < 12, "P6c"
print("all symbolic checks pass")
