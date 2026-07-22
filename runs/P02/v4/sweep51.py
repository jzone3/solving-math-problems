"""Probe Brandt 2002 Conjecture 5.1 (the actually-open LP form):
   If G is maximal triangle-free with d_f(G) < 3 then A x = 1 has rational x >= 0.

Enumerate ALL maximal triangle-free graphs (geng -t, maximality filter), fast
float pre-filter on d_f (scipy), exact rational confirmation (Fraction simplex)
for candidates with d_f < 3, then exact feasibility of {A x = 1, x >= 0}.
Any graph with d_f < 3 (exact) and infeasible system refutes Conjecture 5.1.

Usage: python3 sweep51.py n [res mod]
"""
import sys

import numpy as np
from scipy.optimize import linprog

from oracle import (ax_eq_1_nonneg_feasible, fractional_total_domination,
                    is_maximal_tf, neighborhoods)
from test_oracle import g6_to_edges
import subprocess


def df_float(n, N):
    A = np.zeros((n, n))
    for v in range(n):
        for u in N[v]:
            A[v][u] = 1
    r = linprog([1] * n, A_ub=-A, b_ub=[-1] * n, bounds=[(0, None)] * n,
                method="highs")
    return r.fun


def main():
    n = int(sys.argv[1])
    res, mod = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
    cmd = ["nauty-geng", "-q", "-t", "-c", "-d1", str(n)]
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    total = mtf = cand = refuted = 0
    for line in proc.stdout:
        total += 1
        g6 = line.strip()
        nn, edges = g6_to_edges(g6)
        if not is_maximal_tf(nn, edges):
            continue
        mtf += 1
        N = neighborhoods(nn, edges)
        if max(len(N[v]) for v in range(nn)) * 3 <= nn:
            continue  # d_f >= n/maxdeg >= 3
        d = df_float(nn, N)
        if d is None or d >= 3 - 1e-9:
            continue
        # exact confirmation
        dv, _ = fractional_total_domination(nn, edges)
        if dv >= 3:
            continue
        cand += 1
        ok, _ = ax_eq_1_nonneg_feasible(nn, edges)
        if not ok:
            refuted += 1
            print(f"CONJ51-COUNTEREXAMPLE n={nn} g6={g6} d_f={dv}", flush=True)
    print(f"n={n} part={res}/{mod}: geng_tf={total} maximalTF={mtf} "
          f"df_lt3={cand} conj51_violations={refuted}", flush=True)


if __name__ == "__main__":
    main()
