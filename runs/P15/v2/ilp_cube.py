#!/usr/bin/env python3
"""ILP cube-and-conquer: case split on the LARGEST divisor value v0 whose
class covers point 0 with residue 0 (translation lets us normalize residue 0;
choosing the largest such value dedupes cases). Cube v0: x_{v0,0} = 1 and
x_{v,0} = 0 for all v > v0. Instance UNSAT iff every cube UNSAT.

Cubes are far more constrained than the monolithic model and independent, so
they parallelize across processes (--stride/--offset).

Usage: python3 ilp_cube.py -N "2^4,3,5,7" -T 5 --time-limit 7200 \
       --stride 4 --offset 0 [-o out.txt]
"""
import argparse
import numpy as np
import highspy
from engine4 import factorize_spec, divisors


def solve_cube(fac, T, v0, time_limit, out=None):
    N = 1
    for p, e in fac.items():
        N *= p ** e
    divs = divisors(fac, lo=T)
    cols = []
    col_of = {}
    for v in divs:
        for a in range(v):
            col_of[(v, a)] = len(cols)
            cols.append((v, a))
    ncols = len(cols)
    h = highspy.Highs()
    h.setOptionValue("time_limit", float(time_limit))
    h.setOptionValue("output_flag", False)
    inf = highspy.kHighsInf
    lb = np.zeros(ncols)
    ub = np.ones(ncols)
    # cube: largest value covering 0 with residue 0 is v0
    lb[col_of[(v0, 0)]] = 1.0
    for v in divs:
        if v > v0:
            ub[col_of[(v, 0)]] = 0.0
    h.addVars(ncols, lb, ub)
    h.changeColsIntegrality(ncols, np.arange(ncols, dtype=np.int32),
                            np.array([highspy.HighsVarType.kInteger] * ncols))
    h.changeColsCost(ncols, np.arange(ncols, dtype=np.int32), np.zeros(ncols))
    for v in divs:
        idx = np.array([col_of[(v, a)] for a in range(v)], dtype=np.int32)
        h.addRow(-inf, 1.0, len(idx), idx, np.ones(len(idx)))
    for n in range(N):
        idx = np.array([col_of[(v, n % v)] for v in divs], dtype=np.int32)
        h.addRow(1.0, inf, len(idx), idx, np.ones(len(idx)))
    h.run()
    name = h.modelStatusToString(h.getModelStatus())
    if name.lower().startswith("optimal"):
        sol = h.getSolution().col_value
        chosen = [(a, v) for (v, a), xx in zip(cols, sol) if xx > 0.5]
        if out:
            with open(out, "w") as f:
                f.write(f"# ilp_cube N={fac} T={T} v0={v0}\n")
                for a, v in sorted(chosen, key=lambda t: t[1]):
                    f.write(f"{a} {v}\n")
        return True
    if name.lower().startswith("infeasible"):
        return False
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-N", required=True)
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--time-limit", type=float, default=7200,
                    help="per-cube limit")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    divs = sorted(divisors(fac, lo=args.T), reverse=True)
    mine = divs[args.offset::args.stride]
    import time
    t0 = time.time()
    undecided = []
    for v0 in mine:
        r = solve_cube(fac, args.T, v0, args.time_limit, args.out)
        tag = {True: "SAT", False: "UNSAT", None: "UNDECIDED"}[r]
        print(f"cube v0={v0}: {tag} t={time.time()-t0:.0f}s", flush=True)
        if r is True:
            print(f"SAT via cube v0={v0}")
            return
        if r is None:
            undecided.append(v0)
    if undecided:
        print(f"PARTIAL: undecided cubes {undecided}")
    else:
        print("ALL CUBES UNSAT (this shard)")


if __name__ == "__main__":
    main()
