#!/usr/bin/env python3
"""Exact ILP: does a covering of Z_N with distinct divisor moduli >= T exist?

Variables x_{v,a} in {0,1} for each divisor v >= T of N and residue a mod v.
  sum_a x_{v,a} <= 1        (each modulus value used at most once)
  for each n in Z_N: sum_{(v,a): n ≡ a mod v} x_{v,a} >= 1
Solved with HiGHS. Feasible for N up to ~10^6 (nnz ≈ N * sum 1/v).

Usage: python3 ilp.py -N "2^4,3^2,5,7" -T 6 [--time-limit 600]
Prints SAT (and writes witness) or UNSAT (proving no cover exists for this N,T).
"""
import argparse
import numpy as np
import highspy
from engine4 import factorize_spec, divisors


def solve(fac, T, time_limit=600, out=None, mip_gap=0.0):
    N = 1
    for p, e in fac.items():
        N *= p ** e
    divs = divisors(fac, lo=T)
    # columns: (v, a)
    cols = []
    col_of = {}
    for v in divs:
        for a in range(v):
            col_of[(v, a)] = len(cols)
            cols.append((v, a))
    ncols = len(cols)
    print(f"N={N} T={T}: {len(divs)} values, {ncols} columns")

    h = highspy.Highs()
    h.setOptionValue("time_limit", float(time_limit))
    h.setOptionValue("output_flag", True)
    inf = highspy.kHighsInf

    # variables
    h.addVars(ncols, np.zeros(ncols), np.ones(ncols))
    h.changeColsIntegrality(ncols, np.arange(ncols, dtype=np.int32),
                            np.array([highspy.HighsVarType.kInteger] * ncols))
    # pure feasibility: zero objective, first incumbent is optimal
    h.changeColsCost(ncols, np.arange(ncols, dtype=np.int32), np.zeros(ncols))

    # row: per value v, sum_a x <= 1
    for v in divs:
        idx = np.array([col_of[(v, a)] for a in range(v)], dtype=np.int32)
        h.addRow(-inf, 1.0, len(idx), idx, np.ones(len(idx)))
    # row: per point n, coverage >= 1
    for n in range(N):
        idx = np.array([col_of[(v, n % v)] for v in divs], dtype=np.int32)
        h.addRow(1.0, inf, len(idx), idx, np.ones(len(idx)))

    h.run()
    status = h.getModelStatus()
    name = h.modelStatusToString(status)
    print(f"status: {name}")
    if name.lower().startswith("optimal"):
        sol = h.getSolution().col_value
        chosen = [(a, v) for (v, a), x in zip(cols, sol) if x > 0.5]
        print(f"SAT: cover with {len(chosen)} congruences")
        if out:
            with open(out, "w") as f:
                f.write(f"# exact ILP N={fac} T={T}\n")
                for a, v in sorted(chosen, key=lambda t: t[1]):
                    f.write(f"{a} {v}\n")
            print(f"wrote {out}")
        return True
    if name.lower().startswith("infeasible"):
        print(f"UNSAT: no covering of Z_N with distinct divisor moduli >= {T} for this N")
        return False
    print("INDETERMINATE (time limit?)")
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-N", required=True)
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--time-limit", type=float, default=600)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    solve(factorize_spec(a.N), a.T, a.time_limit, a.out)
