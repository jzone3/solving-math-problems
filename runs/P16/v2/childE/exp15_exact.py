"""Exp 15: EXACT feasibility tests for the two 1-parameter certificate families.

SUM family y_e = s_e + c (s_e = d_i+d_j), c in (-2*delta, inf]:
  need for all e: num_e(c) <= tau * (s_e + c), tau = sqrt(max arg44), i.e.
  alpha_e + c * beta_e <= 0 with
    alpha_e = d_i(d_i+m_i) + d_j(d_j+m_j) - (tau+2) s_e
    beta_e  = s_e - (tau + 2)
  linear in c => exact interval intersection. c = +inf limit is Anderson-Morley
  (valid iff beta_e <= 0 for all e i.e. max s_e <= tau+2 and handled as feasible
  when upper bounds absent and lower bounds bounded).

PROD family y_e = (d_i+b)(d_j+b), b >= 0 (phi affine):
  need q_e(b) = d_i(m_i+b)(d_i+b) + d_j(m_j+b)(d_j+b) - tau*(d_i+b)(d_j+b) <= 0,
  quadratic in b => exact interval intersection via roots.

Usage: exp15_exact.py nmax [res mod]
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44

EPS = 1e-9


def sum_feasible(di, dj, mi, mj, tau, delta):
    T = tau + 2
    s = di + dj
    alpha = di * (di + mi) + dj * (dj + mj) - T * s
    beta = s - T
    lo = -float(s.min()) + 1e-9
    hi = math.inf
    for a, b in zip(alpha, beta):
        if abs(b) < 1e-12:
            if a > EPS:
                return False
        elif b < 0:
            lo = max(lo, a / (-b))
        else:
            hi = min(hi, -a / b)
    return lo <= hi + EPS


def prod_feasible(di, dj, mi, mj, tau):
    """q_e(b) = A b^2 + B b + C <= 0 for all e, some b >= 0.
    Feasible set = finite union of intervals whose endpoints are roots;
    check all nonneg roots (and 0, and a large b) as candidates."""
    T = tau + 2
    ne = len(di)
    # q_e(b) = (CW_e(b) - (T-2)) * (d_i+b)(d_j+b), machine-verified coeffs:
    A = di + dj + 2 - T
    B = di * di + di * mi + 2 * di + dj * dj + dj * mj + 2 * dj - T * (di + dj)
    C = di * di * mi + dj * dj * mj + 2 * di * dj - T * di * dj
    cands = [0.0, 1e7]
    for k in range(ne):
        if abs(A[k]) > 1e-12:
            disc = B[k] * B[k] - 4 * A[k] * C[k]
            if disc >= 0:
                r = math.sqrt(disc)
                for x in ((-B[k] - r) / (2 * A[k]), (-B[k] + r) / (2 * A[k])):
                    if x >= 0:
                        cands.append(x)
        elif abs(B[k]) > 1e-12:
            x = -C[k] / B[k]
            if x >= 0:
                cands.append(x)
    for b in cands:
        # relative tolerance on the normalized CW form
        v = (di * (mi + b) / (dj + b) + dj * (mj + b) / (di + b)).max()
        if v <= T + 1e-9:
            return True
    return False


def run(nmax, res=0, mod=1):
    tot = 0
    sum_ok = 0
    fails = []
    for n in range(3, nmax + 1):
        suffix = f"{res}/{mod}" if mod > 1 and n >= 10 else ""
        if mod > 1 and n < 10 and res != 0:
            continue
        for g6 in graphs(n, suffix=suffix):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            di = np.array([d[i] for i, j in E])
            dj = np.array([d[j] for i, j in E])
            mi = np.array([m[i] for i, j in E])
            mj = np.array([m[j] for i, j in E])
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            tau = math.sqrt(max(R, 0))
            tot += 1
            if sum_feasible(di, dj, mi, mj, tau, min(d)):
                sum_ok += 1
                continue
            if not prod_feasible(di, dj, mi, mj, tau):
                fails.append(g6)
    print(f"n<={nmax} (res {res}/{mod}): graphs={tot} sum_ok={sum_ok} "
          f"FAILURES={len(fails)}")
    print(fails[:60])


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    run(nmax, res, mod)
