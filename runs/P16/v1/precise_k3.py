#!/usr/bin/env python3
"""P16: high-precision (mpmath) continuous optimization of the k=3 quotient
margin on the promising supports, to determine whether the feasible
(b>=1) supremum is truly positive or exactly 0."""
import sys
import numpy as np
from scipy.optimize import minimize
from mpmath import mp, mpf, sqrt, polyroots

mp.dps = 40


def margin(which, params, loop2):
    # params: log n0,n1,n2, log(b01-1+eps)... parametrize b>=1 via 1+exp
    n = [1 + mp.e ** mpf(params[i]) for i in range(3)]
    b01 = 1 + mp.e ** mpf(params[3])
    b02 = 1 + mp.e ** mpf(params[4])
    b12 = 1 + mp.e ** mpf(params[5])
    b22 = (1 + mp.e ** mpf(params[6])) if loop2 else mpf(0)
    B = [[mpf(0)] * 3 for _ in range(3)]
    B[0][1] = b01; B[1][0] = n[0] * b01 / n[1]
    B[0][2] = b02; B[2][0] = n[0] * b02 / n[2]
    B[1][2] = b12; B[2][1] = n[1] * b12 / n[2]
    B[2][2] = b22
    pen = mpf(0)
    for i in range(3):
        for j in range(3):
            if i != j and B[i][j] > n[j]:
                pen += (B[i][j] - n[j]) ** 2
            if i != j and B[i][j] > 0 and B[i][j] < 1:
                pen += (1 - B[i][j]) ** 2
    if b22 > n[2] - 1:
        pen += (b22 - (n[2] - 1)) ** 2
    d = [sum(B[i]) for i in range(3)]
    m = [sum(B[i][j] * d[j] for j in range(3)) / d[i] for i in range(3)]
    # L_B = diag(d) - B ; char poly exact-ish in mp
    M = [[(d[i] if i == j else 0) - B[i][j] for j in range(3)] for i in range(3)]
    # char poly coeffs of 3x3
    tr = M[0][0] + M[1][1] + M[2][2]
    c2 = (M[0][0]*M[1][1] - M[0][1]*M[1][0] + M[0][0]*M[2][2] - M[0][2]*M[2][0]
          + M[1][1]*M[2][2] - M[1][2]*M[2][1])
    det = (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])
           - M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])
           + M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
    try:
        roots = polyroots([1, -tr, c2, -det], maxsteps=800, extraprec=200)
    except Exception:
        return mpf(-1e6)
    mu = max(r.real for r in roots)
    rhs = mpf(-1e30)
    edges = [(0, 1), (0, 2), (1, 2)] + ([(2, 2)] if loop2 else [])
    for (i, j) in edges:
        di, dj, mi, mj = d[i], d[j], m[i], m[j]
        if which == 44:
            inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
        else:
            inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
        if inner < 0:
            return mpf(-1e6)
        v = 2 + sqrt(inner)
        if v > rhs:
            rhs = v
    return mu - rhs - 1000 * pen


def run(which, loop2):
    rng = np.random.default_rng(3)
    best = (-1e18, None)
    for r in range(40):
        x0 = rng.uniform(-1, 8, 7)
        f = lambda x: -float(margin(which, x, loop2))
        res = minimize(f, x0, method="Nelder-Mead",
                       options={"maxiter": 6000, "xatol": 1e-13, "fatol": 1e-16})
        v = -res.fun
        if v > best[0]:
            best = (v, res.x)
            print(f"[{which}] loop2={loop2} restart={r} margin={v:.3e} "
                  f"n={[float(1+np.exp(t)) for t in res.x[:3]]} "
                  f"b={[float(1+np.exp(t)) for t in res.x[3:]]}", flush=True)
    print(f"[{which}] loop2={loop2} FINAL {best[0]:.6e}")


if __name__ == "__main__":
    run(int(sys.argv[1]), bool(int(sys.argv[2])))
