#!/usr/bin/env python3
"""V4: LP-relaxation roundings as annealer start points.

LP relaxation of the BTD ILP (multiplicity-indicator expansion), keeping the
linear constraint classes (row composition + column sums); the pair
constraints are quadratic in the cell values and are left to the annealer.
Variables x1[i,j], x2[i,j] in [0,1], x1+x2 <= 1;
  sum_j x1[i,j] = rho1,  sum_j x2[i,j] = rho2   (rows)
  sum_i (x1[i,j] + 2 x2[i,j]) = K                (columns)
A random linear objective samples different vertices of the polytope; each
fractional solution is rounded row-wise (sample rho1 cells for 1s with prob
proportional to x1, then rho2 cells for 2s prop. to x2 among the rest), which
keeps rows exact; columns then start near-feasible.

Usage: lp_starts.py V B rho1 rho2 K nstarts outdir
"""
import sys, os
import numpy as np
from scipy.optimize import linprog


def make_start(V, B, r1, r2, K, rng):
    n = V * B
    # variable order: x1 (V*B), then x2 (V*B)
    A_eq, b_eq = [], []
    for i in range(V):
        row = np.zeros(2 * n)
        row[i * B:(i + 1) * B] = 1
        A_eq.append(row); b_eq.append(r1)
        row = np.zeros(2 * n)
        row[n + i * B:n + (i + 1) * B] = 1
        A_eq.append(row); b_eq.append(r2)
    for j in range(B):
        row = np.zeros(2 * n)
        for i in range(V):
            row[i * B + j] = 1
            row[n + i * B + j] = 2
        A_eq.append(row); b_eq.append(K)
    # x1 + x2 <= 1 per cell
    A_ub = np.zeros((n, 2 * n))
    for c in range(n):
        A_ub[c, c] = 1
        A_ub[c, n + c] = 1
    b_ub = np.ones(n)
    c = rng.standard_normal(2 * n)
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=(0, 1), method="highs")
    assert res.success, res.message
    x1 = res.x[:n].reshape(V, B)
    x2 = res.x[n:].reshape(V, B)
    M = np.zeros((V, B), dtype=int)
    for i in range(V):
        p2 = x2[i] + 1e-9
        idx2 = rng.choice(B, size=r2, replace=False, p=p2 / p2.sum())
        M[i, idx2] = 2
        rest = np.setdiff1d(np.arange(B), idx2)
        p1 = x1[i, rest] + 1e-9
        idx1 = rng.choice(rest, size=r1, replace=False, p=p1 / p1.sum())
        M[i, idx1] = 1
    return M


def main():
    V, B, r1, r2, K, nstarts = map(int, sys.argv[1:7])
    outdir = sys.argv[7]
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(20260722)
    for t in range(nstarts):
        M = make_start(V, B, r1, r2, K, rng)
        with open(os.path.join(outdir, f"start_{t}.txt"), "w") as f:
            for i in range(V):
                f.write("".join(map(str, M[i])) + "\n")
    print(f"wrote {nstarts} starts to {outdir}")


if __name__ == "__main__":
    main()
