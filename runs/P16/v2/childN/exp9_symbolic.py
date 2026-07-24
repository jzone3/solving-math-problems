"""childN exp9: symbolic derivation of the certificate Q(rho).

Star data: e=ij, x=d_i, y=d_j, neighbors k~i (k!=j) with degrees d_k and
avg-nbr-degs m_k; l~j (l!=i) with d_l, m_l.  m_i=(y+sum d_k)/x,
m_j=(x+sum d_l)/y.

w_e = zs_e - s_e z1_e where zs_e = sum_{f~e} z1_f + 2 z1_e,
z1_f(f=ik) = (x+d_k-2)^2 + x m_i + d_k m_k - 2 x d_k,
z1_e = (x+y-2)^2 + x m_i + y m_j - 2xy.

Q(rho) = w_e + sum_k (d_k/(2 m_i))(rho - arg44_ik)
             + sum_l (d_l/(2 m_j))(rho - arg44_jl) + (s-3)(z1_e - rho).

Verify: (1) m_k, m_l coefficients vanish in Q;
(2) print Q as polynomial in rho: Q = c_rho * rho + Q0, with
    c_rho = 3 - s/2 - y/(2 m_i) - x/(2 m_j);
(3) print Q(arg44_e) in terms of x,y,m_i,m_j,P_i,P_j where
    P_i = sum d_k^2 (over k!=j), Sig_i = sum d_k = x m_i - y.
"""
import sympy as sp

x, y, mi, mj, rho, mk, ml, t = sp.symbols("x y m_i m_j rho m_k m_l t", positive=True)

z1e = (x + y - 2) ** 2 + x * mi + y * mj - 2 * x * y
s = x + y

# per-neighbor contribution on i-side, neighbor degree t, avg m_k:
z1f_i = (x + t - 2) ** 2 + x * mi + t * mk - 2 * x * t
a44_i = 2 * ((x - 1) ** 2 + (t - 1) ** 2 + mi * mk - x * t)
contrib_i = (z1f_i - z1e) + (t / (2 * mi)) * (rho - a44_i)
contrib_i = sp.expand(contrib_i)
print("coeff of m_k in i-side contribution:", sp.simplify(sp.collect(contrib_i, mk).coeff(mk)))

# so contribution is m_k-free:
ci = sp.simplify(contrib_i.subs(mk, 0))
print("\ni-side per-neighbor contribution (m_k-free), as poly in t:")
print(sp.collect(sp.expand(ci), t))

# Q = sum_k ci(t=d_k) + sum_l cj(t=d_l) + 2*(z1e... wait w = sum_f(z1_f - z1_e)
# w_e = sum_{f~e}(z1_f - z1_e)  [I6 identity], f over all s-2 neighbors.
# Q = w + slacks + (s-3)(z1e - rho) = sum_k ci + sum_l cj + (s-3)(z1e-rho)
cj = ci.subs([(x, y), (y, x), (mi, mj)], simultaneous=True)

# For closed form: sum over k: number x-1, sum d_k = x mi - y, sum d_k^2 = Pi
Pi, Pj = sp.symbols("P_i P_j", positive=True)
Sigi = x * mi - y
Sigj = y * mj - x
cit = sp.Poly(ci, t)
coefs = cit.all_coeffs()  # highest degree first
deg = len(coefs) - 1
print("\ndegree in t:", deg, "coeffs (t^3..t^0):", [sp.simplify(c) for c in coefs])
assert deg <= 3
# sum over k of ci(d_k) = c3*S3 + c2*Pi + c1*Sigi + c0*(x-1), need S3? if c3 != 0 we need cubic sums
# check c3:
print("c3 i-side:", sp.simplify(coefs[0]) if deg == 3 else 0)
