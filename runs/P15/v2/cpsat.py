#!/usr/bin/env python3
"""CP-SAT (OR-tools) model: cover Z_N with distinct divisor moduli >= T.
CP-SAT combines clause learning with LP relaxation + cuts and runs parallel
portfolios — exactly the hybrid reasoning this family needs.

x_{v,a} booleans; per point n: OR of x_{v, n%v}; per value: at-most-one;
symmetry: WLOG point 0 is covered by a residue-0 class (translation).

Usage: python3 cpsat.py -N "2^4,3,5,7" -T 5 [--time-limit 3600] [-o out.txt]
"""
import argparse
from ortools.sat.python import cp_model
from engine4 import factorize_spec, divisors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-N", required=True)
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--time-limit", type=float, default=3600)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    N = 1
    for p, e in fac.items():
        N *= p ** e
    divs = divisors(fac, lo=args.T)
    m = cp_model.CpModel()
    x = {(v, a): m.new_bool_var(f"x{v}_{a}") for v in divs for a in range(v)}
    for n in range(N):
        m.add_bool_or([x[(v, n % v)] for v in divs])
    for v in divs:
        m.add_at_most_one([x[(v, a)] for a in range(v)])
    # translation symmetry: WLOG the class covering 0 has residue 0
    m.add_bool_or([x[(v, 0)] for v in divs])
    print(f"N={N} T={args.T}: {len(divs)} values, {len(x)} vars", flush=True)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.time_limit
    solver.parameters.num_workers = args.workers
    solver.parameters.log_search_progress = True
    status = solver.solve(m)
    name = solver.status_name(status)
    print(f"status: {name}")
    if name == "INFEASIBLE":
        print(f"UNSAT: no covering of Z_{N} with distinct divisor moduli >= {args.T}")
    elif name in ("OPTIMAL", "FEASIBLE"):
        congs = sorted(((a, v) for (v, a), var in x.items()
                        if solver.value(var)), key=lambda t: t[1])
        print(f"SAT: {len(congs)} congruences")
        if args.out:
            with open(args.out, "w") as f:
                f.write(f"# cpsat N={args.N} T={args.T}\n")
                for a, v in congs:
                    f.write(f"{a} {v}\n")
            print(f"wrote {args.out}")
    else:
        print("INDETERMINATE")


if __name__ == "__main__":
    main()
