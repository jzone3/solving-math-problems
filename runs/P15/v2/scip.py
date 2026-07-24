#!/usr/bin/env python3
"""SCIP model: cover Z_N with distinct divisor moduli >= T (feasibility).
SCIP adds conflict analysis + strong branching on top of LP/cuts — a different
engine profile than HiGHS for infeasibility proofs.

Usage: python3 scip.py -N "2^4,3,5,7" -T 5 [--time-limit 7200] [-o out.txt]
"""
import argparse
from pyscipopt import Model, quicksum
from engine4 import factorize_spec, divisors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-N", required=True)
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--time-limit", type=float, default=7200)
    ap.add_argument("-o", "--out")
    ap.add_argument("--cube-v0", type=int, default=0,
                    help="fix x_{v0,0}=1 and x_{v,0}=0 for v>v0 "
                         "(largest-value-covering-0 case split)")
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    N = 1
    for p, e in fac.items():
        N *= p ** e
    divs = divisors(fac, lo=args.T)
    m = Model()
    m.setParam("limits/time", args.time_limit)
    x = {(v, a): m.addVar(vtype="B", name=f"x{v}_{a}")
         for v in divs for a in range(v)}
    for v in divs:
        m.addCons(quicksum(x[(v, a)] for a in range(v)) <= 1)
    for n in range(N):
        m.addCons(quicksum(x[(v, n % v)] for v in divs) >= 1)
    if args.cube_v0:
        v0 = args.cube_v0
        m.addCons(x[(v0, 0)] >= 1)
        for v in divs:
            if v > v0:
                m.addCons(x[(v, 0)] <= 0)
    else:
        # translation symmetry: WLOG class covering 0 has residue 0
        m.addCons(quicksum(x[(v, 0)] for v in divs) >= 1)
    print(f"N={N} T={args.T}: {len(divs)} values, {len(x)} vars", flush=True)
    m.optimize()
    st = m.getStatus()
    print(f"status: {st}")
    if st == "infeasible":
        print(f"UNSAT: no covering of Z_{N} with distinct divisor moduli >= {args.T}")
    elif st in ("optimal", "sollimit", "bestsollimit") or m.getNSols() > 0:
        sol = m.getBestSol()
        congs = sorted(((a, v) for (v, a), var in x.items()
                        if m.getSolVal(sol, var) > 0.5), key=lambda t: t[1])
        print(f"SAT: {len(congs)} congruences")
        if args.out:
            with open(args.out, "w") as f:
                f.write(f"# scip N={args.N} T={args.T}\n")
                for a, v in congs:
                    f.write(f"{a} {v}\n")
            print(f"wrote {args.out}")
    else:
        print("INDETERMINATE")


if __name__ == "__main__":
    main()
