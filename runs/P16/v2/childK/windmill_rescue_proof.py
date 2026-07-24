"""Theorem K3 (sympy): explicit diagonal rescue of windmills.

For F_k (k >= 2) choose s_hub = p = 4k, s_outer = q = 4. Claim M(s) >= 0.

Spectral decomposition of M(s) on F_k (hub + k pairs):
  - antisym within pair (mult k):        lam_a  = 2q + 3 - q^2 w_s
  - sym within pair, zero-sum (mult k-1): lam_s = 2q + 1 - q^2 (w_s + 2 w_o)
  - 2x2 block on (hub, global sym):
      [[Ah, C],[C, Bs]],  Ah = 2p + 4 - 2k - 2k p^2 w_s,
      per-outer form: quadratic  Ah a^2 + 2k lam_s' ... use direct quadratic:
      f(a,b) = Ah a^2 + 2k b^2 (2q+2-q^2(w_s+w_o)) - 2k*2ab(1+pq w_s)
               - 2k b^2 (1 + q^2 w_o)   [outer-outer pair coupling, k pairs of 2b^2 terms]
  We verify instead by building M(s) symbolically in the 3-dim invariant
  basis and checking all eigen-blocks >= 0 for all k >= 2.

w_s = 1/(8k^2 + 8 - 64k/(k+3)),  w_o = 1/(16 - 32/(k+1)).

Also numeric cross-check for k in 2..200 against the full matrix.
"""
import sympy as sp
import numpy as np
from common import build
from graphs import windmill

k = sp.symbols('k', positive=True)
p = 4 * k
q = sp.Integer(4)

w_s = 1 / (8 * k ** 2 + 8 - 64 * k / (k + 3))
w_o = 1 / (16 - 32 / (k + 1))

lam_a = 2 * q + 3 - q ** 2 * w_s
lam_s = 2 * q + 1 - q ** 2 * (w_s + 2 * w_o)
Ah = 2 * p + 4 - 2 * k - 2 * k * p ** 2 * w_s
# quotient quadratic in (a,b): hub=a, all outer=b
a, b = sp.symbols('a b')
f = (Ah * a ** 2
     + 2 * k * (2 * q + 2 - q ** 2 * (w_s + w_o)) * b ** 2
     - 4 * k * (1 + p * q * w_s) * a * b
     - 2 * k * (1 + q ** 2 * w_o) * b ** 2)
pol = sp.Poly(sp.expand(sp.together(f).as_numer_denom()[0]), a, b)
Aq = pol.coeff_monomial(a ** 2)
Bq = pol.coeff_monomial(b ** 2)
Cq = pol.coeff_monomial(a * b) / 2
den = sp.together(f).as_numer_denom()[1]
detq = sp.simplify(Aq * Bq - Cq ** 2)

print("den sign check (should be >0 for k>=2):", sp.factor(den))
for name, e in [("lam_a", lam_a), ("lam_s", lam_s), ("Ah", Ah),
                ("Aq(num)", Aq), ("detq(num)", detq)]:
    num = sp.factor(sp.together(e).as_numer_denom()[0])
    print(f"{name}: {num}")
    # positivity for k >= k0: substitute k = t + k0, expand, check coeff signs
    t = sp.symbols('t', nonnegative=True)
    for k0 in [2, 3, 4, 5]:
        pe = sp.together(sp.expand(e.subs(k, t + k0)))
        numt, dent = pe.as_numer_denom()
        numt = sp.Poly(sp.expand(numt), t)
        dent = sp.Poly(sp.expand(dent), t)
        ok_num = all(c >= 0 for c in numt.all_coeffs()) or all(c <= 0 for c in numt.all_coeffs())
        ok_den = all(c >= 0 for c in dent.all_coeffs()) or all(c <= 0 for c in dent.all_coeffs())
        sgn_num = 1 if numt.all_coeffs()[0] > 0 else -1
        sgn_den = 1 if dent.all_coeffs()[0] > 0 else -1
        print(f"  k=t+{k0}: num sign-definite {ok_num}, den {ok_den}, "
              f"overall sign {sgn_num * sgn_den}")
        if ok_num and ok_den and sgn_num * sgn_den > 0:
            break

# numeric cross-check of the decomposition against full matrix
print("\nnumeric cross-check (full 2k+1 matrix):")
for kk in [2, 3, 5, 14, 25, 60, 200]:
    A_ = windmill(kk)
    bd = build(A_)
    n = bd["n"]
    s = np.full(n, 4.0)
    s[0] = 4 * kk
    D = np.diag(s)
    Ms = 2 * D + 4 * np.eye(n) - bd["Q"] - D @ bd["H"] @ D
    ev = np.linalg.eigvalsh(Ms)
    print(f"  k={kk}: mineig M(s) = {ev[0]:.6f} {'OK' if ev[0] > -1e-9 else 'FAIL'}")
