"""exp5: symbolic form of the B-margin Delta = E_e - sum_{f~e} E_f.

Delta = (z1_e - rho) - (zs_e - 2 z1_e) + (s_e - 2) rho
      = 3 z1_e - zs_e + (s_e - 3) rho.

Expand via H2 in vertex data (x=d_i, y=d_j, m_i, m_j, P_i, P_j, W_i, W_j):
  z1_e = (x+y-2)^2 + x m_i + y m_j - 2 x y
  zs_e = (A_L M)_e - 2(M_e - 2 s_e),  (A_L M)_e per childH H2.
Verify the resulting closed form against direct A_L computation on all
connected graphs n <= 7 (exact), then print Delta expanded.
"""
from fractions import Fraction
import itertools
import sympy as sp

from common import geng, g6_adj, edge_env
import numpy as np

x, y, mi, mj, Pi, Pj, Wi, Wj, rho = sp.symbols(
    "x y m_i m_j P_i P_j W_i W_j rho", positive=True)

s = x + y
M = x * (x + mi) + y * (y + mj)
z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
ALM = (x - 2) * x * (x + mi) + (y - 2) * y * (y + mj) + Pi + Pj + Wi + Wj
zs = ALM - 2 * (M - 2 * s)
Delta = sp.expand(3 * z1 - zs + (s - 3) * rho)
print("Delta =", Delta)
print()
print("Delta collected:", sp.collect(Delta, [Pi, Pj, Wi, Wj, rho]))

# exact verification on all connected graphs n<=7
cnt = 0
for n in range(3, 8):
    for g6 in geng(n):
        A = g6_adj(g6)
        d, m, E, sl, z1l, zsl, a44, rho0, rho1, AL = edge_env(A)
        dv = A.sum(1)
        P = [sum(Fraction(int(dv[k]) ** 2) for k in range(n) if A[i, k])
             for i in range(n)]
        W = [sum(Fraction(int(dv[k])) * m[k] for k in range(n) if A[i, k])
             for i in range(n)]
        for a, (i, j) in enumerate(E):
            for rv in (Fraction(rho0[a]), Fraction(rho0[a]) + 5):
                lhs = 3 * z1l[a] - zsl[a] + (sl[a] - 3) * rv
                sub = {x: int(dv[i]), y: int(dv[j]),
                       mi: sp.Rational(m[i].numerator, m[i].denominator),
                       mj: sp.Rational(m[j].numerator, m[j].denominator),
                       Pi: sp.Rational(P[i].numerator, P[i].denominator),
                       Pj: sp.Rational(P[j].numerator, P[j].denominator),
                       Wi: sp.Rational(W[i].numerator, W[i].denominator),
                       Wj: sp.Rational(W[j].numerator, W[j].denominator),
                       rho: sp.Rational(rv.numerator, rv.denominator)}
                rhs = Delta.subs(sub)
                assert sp.Rational(lhs.numerator, lhs.denominator) == rhs, (g6, a)
                cnt += 1
print("verified Delta closed form on", cnt, "edge/rho samples (n<=7)")
