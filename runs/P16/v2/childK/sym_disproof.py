"""Symbolic DISPROOF of F2 on windmills F_k (sympy, exact).

F_k: hub h of degree 2k (m_h = 2), 2k outer vertices of degree 2
(m = (2k+2)/2 = k+1), k outer edges (pairs), 2k spokes.

sigma_h = 2k - 2, sigma_o = k - 1.
Spoke uv (hub-outer): arg46-4 = 2(4k^2+4) - 32k/(m_h+m_o) = 8k^2+8 - 32k/(k+3)
Outer uw: arg46-4 = 16 - 64/(2k+2) = 16 - 32/(k+1)

Test vector: x = a on hub, b on all outer vertices (symmetric quotient).
x^T M x = closed form in (k, a, b); minimize over (a,b) -> 2x2 quotient
matrix Mq; show det < 0 for k >= 14 exactly.
"""
import sympy as sp

k, a, b = sp.symbols('k a b', positive=True)

sig_h = 2 * k - 2
sig_o = k - 1
m_h = sp.Integer(2)
m_o = k + 1

w_spoke = 1 / (2 * ((2 * k) ** 2 + 4) - 16 * (2 * k) * 2 / (m_h + m_o))
w_outer = 1 / (2 * (4 + 4) - 16 * 4 / (m_o + m_o))

# x^T M x = sum_i (2 sig_i + 4) x_i^2 - sum_e (x_i+x_j)^2 - sum_e w_e (sig_i x_i + sig_j x_j)^2
expr = ((2 * sig_h + 4) * a ** 2 + 2 * k * (2 * sig_o + 4) * b ** 2
        - 2 * k * (a + b) ** 2 - k * (2 * b) ** 2
        - 2 * k * w_spoke * (sig_h * a + sig_o * b) ** 2
        - k * w_outer * (2 * sig_o * b) ** 2)
expr = sp.expand(sp.simplify(expr))
print("x^T M x =", expr)

# quadratic form Q(a,b) = A a^2 + 2 C a b + B b^2
pol = sp.Poly(expr, a, b)
A_ = sp.simplify(pol.coeff_monomial(a ** 2))
B_ = sp.simplify(pol.coeff_monomial(b ** 2))
C_ = sp.simplify(pol.coeff_monomial(a * b) / 2)
det = sp.simplify(A_ * B_ - C_ ** 2)
print("A =", A_)
print("B =", B_)
print("C =", C_)
print("det =", sp.factor(det))

# numeric roots of det in k
detp = sp.Poly(sp.together(det).as_numer_denom()[0], k)
print("numerator poly:", detp)
print("real roots:", [sp.nsimplify(r, rational=False) for r in sp.Poly(detp).nroots() if abs(sp.im(r)) < 1e-9])

for kk in [13, 14, 17, 25]:
    print(f"k={kk}: A={float(A_.subs(k, kk)):.4f} det={float(det.subs(k, kk)):.4f}")

# exact rational witness for k=14 with explicit a,b
for kk in [14]:
    Ak = A_.subs(k, kk)
    Bk = B_.subs(k, kk)
    Ck = C_.subs(k, kk)
    # choose b = 1, a = -C/A gives value B - C^2/A < 0 iff det<0 (A>0)
    aval = sp.Rational(-Ck / Ak)
    val = sp.simplify(Ak * aval ** 2 + 2 * Ck * aval + Bk)
    print(f"k={kk}: witness a={aval}, b=1, x^T M x = {val} = {float(val):.6f}")
