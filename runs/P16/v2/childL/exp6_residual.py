"""exp6: rho-free residual certificate attempt for (B).

R := Delta - sum_{k~i,k!=j}(rho - arg44_ik) - sum_{l~j,l!=i}(rho - arg44_jl)
        - (z1_e - rho)
has zero rho-coefficient. If R >= 0 always (as a function of the 1-ball
data), then for heavy e: Delta = R + slacks + (z1_e - rho) > 0, proving (B).

Compute R symbolically (aggregated vars incl. N_i = sum_{k~i} m_k) and
scan its sign over all connected graphs n <= 8 (every edge, no heaviness
restriction) exactly.
"""
from fractions import Fraction
import itertools
import sympy as sp
import numpy as np

from common import geng, g6_adj, edge_env

x, y, mi, mj, Pi, Pj, Wi, Wj, Ni, Nj, rho = sp.symbols(
    "x y m_i m_j P_i P_j W_i W_j N_i N_j rho", positive=True)

s = x + y
z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
Delta = (-Pi - Pj - Wi - Wj - mi * x**2 + 7 * mi * x - mj * y**2 + 7 * mj * y
         + rho * (s - 3) - x**3 + 7 * x**2 - 16 * x - y**3 + 7 * y**2
         - 16 * y + 12)

# sum over k~i, k!=j of arg44_{ik}
# arg44_ik = 2[(x-1)^2 + (d_k-1)^2 + m_i m_k - x d_k]
# sum (d_k-1)^2 = (P_i - y^2) - 2(x m_i - y) + (x-1)
# sum m_k = N_i - m_j ; sum d_k = x m_i - y
Ai = 2 * ((x - 1) ** 2 * (x - 1) + (Pi - y**2) - 2 * (x * mi - y) + (x - 1)
          + mi * (Ni - mj) - x * (x * mi - y))
Aj = 2 * ((y - 1) ** 2 * (y - 1) + (Pj - x**2) - 2 * (y * mj - x) + (y - 1)
          + mj * (Nj - mi) - y * (y * mj - x))

R = sp.expand(Delta - ((x - 1) + (y - 1)) * rho + Ai + Aj - (z1 - rho))
print("rho coeff:", sp.simplify(sp.diff(R, rho)))
print("R =", sp.collect(R, [Pi, Pj, Wi, Wj, Ni, Nj]))

# scan sign on all connected graphs n<=8, all edges
worst = None
neg = 0
tot = 0
for n in range(3, 9):
    for g6 in geng(n):
        A = g6_adj(g6)
        n_ = A.shape[0]
        dv = A.sum(1)
        m = [Fraction(int((A[i] * dv).sum()), int(dv[i])) for i in range(n_)]
        P = [sum(Fraction(int(dv[k]) ** 2) for k in range(n_) if A[i, k]) for i in range(n_)]
        W = [sum(Fraction(int(dv[k])) * m[k] for k in range(n_) if A[i, k]) for i in range(n_)]
        N = [sum(m[k] for k in range(n_) if A[i, k]) for i in range(n_)]
        for i in range(n_):
            for j in range(i + 1, n_):
                if not A[i, j]:
                    continue
                sub = {x: int(dv[i]), y: int(dv[j])}
                for sym, val in ((mi, m[i]), (mj, m[j]), (Pi, P[i]), (Pj, P[j]),
                                 (Wi, W[i]), (Wj, W[j]), (Ni, N[i]), (Nj, N[j])):
                    sub[sym] = sp.Rational(val.numerator, val.denominator)
                val = R.subs(sub)
                tot += 1
                if worst is None or val < worst[0]:
                    worst = (val, g6, (i, j))
                if val < 0:
                    neg += 1
print("edges tested:", tot, "R<0 count:", neg, "min R:", worst[0], worst[1:])
