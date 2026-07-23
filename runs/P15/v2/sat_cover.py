#!/usr/bin/env python3
"""SAT attack: exact feasibility of covering Z_N with distinct divisor moduli >= T.

Encoding:
  var x_{v,a} for each divisor v >= T of N, residue a mod v.
  point clauses: for each n in Z_N: OR_{v} x_{v, n mod v}
  at-most-one residue per value v (sequential counter for large v).
Symmetry (translation by Z_N): every solution, translated, has the value v0
that covers point 0 doing so with residue 0. Sound case split ("cubes"):
  for each divisor v0: assume x_{v0, 0} = 1.
UNSAT for all cubes  <=>  UNSAT.  Solved with Cadical 1.9.5 via python-sat.

Usage: python3 sat_cover.py -N "2^4,3^2,5,7" -T 7 [--solver cadical195]
       [--cube] [--time-limit sec] [-o out.txt]
"""
import argparse
import sys
import time
from pysat.solvers import Solver
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from engine4 import factorize_spec, divisors


def build(fac, T):
    N = 1
    for p, e in fac.items():
        N *= p ** e
    divs = divisors(fac, lo=T)
    pool = IDPool()
    x = {}
    for v in divs:
        for a in range(v):
            x[(v, a)] = pool.id(f"x{v}_{a}")
    cnf = CNF()
    for n in range(N):
        cnf.append([x[(v, n % v)] for v in divs])
    for v in divs:
        lits = [x[(v, a)] for a in range(v)]
        if v <= 30:
            enc = CardEnc.atmost(lits, bound=1, vpool=pool,
                                 encoding=EncType.pairwise)
        else:
            enc = CardEnc.atmost(lits, bound=1, vpool=pool,
                                 encoding=EncType.seqcounter)
        cnf.extend(enc.clauses)
    return N, divs, x, cnf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-N", required=True)
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--cube", action="store_true",
                    help="translation-symmetry case split on the value covering 0")
    ap.add_argument("--time-limit", type=float, default=0,
                    help="per-cube budget in seconds (0 = none; uses conflict budget)")
    ap.add_argument("--conf-budget", type=int, default=0)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    N, divs, x, cnf = build(fac, args.T)
    print(f"N={N} T={args.T}: {len(divs)} values, {cnf.nv} vars, "
          f"{len(cnf.clauses)} clauses", flush=True)

    def extract(model):
        pos = set(l for l in model if l > 0)
        return sorted(((a, v) for (v, a), lit in x.items() if lit in pos),
                      key=lambda t: t[1])

    t0 = time.time()
    if not args.cube:
        with Solver(name=args.solver, bootstrap_with=cnf) as s:
            res = s.solve()
            print(f"{'SAT' if res else 'UNSAT'} t={time.time()-t0:.0f}s")
            if res and args.out:
                congs = extract(s.get_model())
                with open(args.out, "w") as f:
                    f.write(f"# SAT N={args.N} T={args.T}\n")
                    for a, v in congs:
                        f.write(f"{a} {v}\n")
                print(f"wrote {args.out}")
        return

    # cube on which value covers point 0 (with residue 0 after translation)
    undecided = []
    with Solver(name=args.solver, bootstrap_with=cnf) as s:
        for i, v0 in enumerate(sorted(divs, reverse=True)):
            if args.conf_budget:
                s.conf_budget(args.conf_budget)
                res = s.solve_limited(assumptions=[x[(v0, 0)]])
            else:
                res = s.solve(assumptions=[x[(v0, 0)]])
            tag = {True: "SAT", False: "UNSAT", None: "UNDECIDED"}[res]
            print(f" cube {i+1}/{len(divs)} v0={v0}: {tag} "
                  f"t={time.time()-t0:.0f}s", flush=True)
            if res is True:
                print(f"SAT (cube v0={v0}) t={time.time()-t0:.0f}s")
                if args.out:
                    congs = extract(s.get_model())
                    with open(args.out, "w") as f:
                        f.write(f"# SAT N={args.N} T={args.T} cube v0={v0}\n")
                        for a, v in congs:
                            f.write(f"{a} {v}\n")
                    print(f"wrote {args.out}")
                return
            if res is None:
                undecided.append(v0)
    if undecided:
        print(f"INDETERMINATE: {len(undecided)} cubes undecided: {undecided[:10]}")
    else:
        print(f"UNSAT (all cubes refuted) t={time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
