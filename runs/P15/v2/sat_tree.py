#!/usr/bin/env python3
"""CRT-layered SAT encoding for covering Z_N with distinct divisor moduli >= T.

Cells (r mod m) for m in a chain 1 = m_0 | m_1 | ... | m_k = N (one prime per
level). Cell var c_{m,r} = "this cell still needs covering". Clauses:
  root: c_{1,0}
  cell (m,r) with children (r + j*m mod m*p):
      c_{m,r} -> OR_{v | m, v >= T} x_{v, r mod v}  OR  d_{m,r}
      d_{m,r} -> c_child_j (for every j)
  leaf (m = N): c_{N,r} -> OR_{v | N, v >= T} x_{v, r mod v}
  at-most-one residue per value.
Equivalent to the flat encoding but gives CDCL hierarchical structure: a value
closing a coarse cell kills the whole subtree at once.

Translation cube (sound): case-split on the value v0 covering point 0 with
residue 0 (any solution can be translated so the covering class of 0 has a=0).
"""
import argparse
import time
from pysat.solvers import Solver
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from engine4 import factorize_spec, divisors


def build(fac, T, split_order=None):
    N = 1
    primes = []
    for p, e in sorted(fac.items()):
        N *= p ** e
        primes += [p] * e
    if split_order == "desc":
        primes = sorted(primes, reverse=True)
    else:
        primes = sorted(primes)
    divs = divisors(fac, lo=T)
    divset = set(divs)
    pool = IDPool()
    x = {(v, a): pool.id(f"x{v}_{a}") for v in divs for a in range(v)}
    cnf = CNF()
    for v in divs:
        lits = [x[(v, a)] for a in range(v)]
        enc = CardEnc.atmost(lits, bound=1, vpool=pool,
                             encoding=EncType.pairwise if v <= 30
                             else EncType.seqcounter)
        cnf.extend(enc.clauses)

    # cells level by level
    cvar = {(1, 0): pool.id("c1_0")}
    cnf.append([cvar[(1, 0)]])
    level = [(1, 0)]
    for li, p in enumerate(primes):
        nxt = []
        for (m, r) in level:
            mp = m * p
            children = [(mp, r + j * m) for j in range(p)]
            closers = [x[(v, r % v)] for v in divset if m % v == 0]
            c = cvar[(m, r)]
            if mp <= N:
                d = pool.id(f"d{m}_{r}")
                cnf.append([-c] + closers + [d])
                for (m2, r2) in children:
                    cv = pool.id(f"c{m2}_{r2}")
                    cvar[(m2, r2)] = cv
                    cnf.append([-d, cv])
                nxt.extend(children)
        level = nxt
    # leaves (m = N)
    for (m, r) in level:
        closers = [x[(v, r % v)] for v in divs]
        cnf.append([-cvar[(m, r)]] + closers)
    return N, divs, x, cnf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-N", required=True)
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--split", default="asc", choices=["asc", "desc"])
    ap.add_argument("--cube", action="store_true")
    ap.add_argument("--dimacs", help="write DIMACS and exit (plus .map of x vars)")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    N, divs, x, cnf = build(fac, args.T, args.split)
    print(f"N={N} T={args.T}: {len(divs)} values, {cnf.nv} vars, "
          f"{len(cnf.clauses)} clauses", flush=True)
    if args.dimacs:
        cnf.to_file(args.dimacs)
        with open(args.dimacs + ".map", "w") as f:
            for (v, a), lit in sorted(x.items()):
                f.write(f"{lit} {a} {v}\n")
        print(f"wrote {args.dimacs}")
        return

    def extract(model):
        pos = set(l for l in model if l > 0)
        return sorted(((a, v) for (v, a), lit in x.items() if lit in pos),
                      key=lambda t: t[1])

    def report_sat(s, tag=""):
        congs = extract(s.get_model())
        print(f"SAT {tag} t={time.time()-t0:.0f}s ({len(congs)} congs)")
        if args.out:
            with open(args.out, "w") as f:
                f.write(f"# SAT-tree N={args.N} T={args.T} {tag}\n")
                for a, v in congs:
                    f.write(f"{a} {v}\n")
            print(f"wrote {args.out}")

    t0 = time.time()
    if not args.cube:
        with Solver(name=args.solver, bootstrap_with=cnf) as s:
            res = s.solve()
            if res:
                report_sat(s)
            else:
                print(f"UNSAT t={time.time()-t0:.0f}s")
        return
    with Solver(name=args.solver, bootstrap_with=cnf) as s:
        for i, v0 in enumerate(sorted(divs, reverse=True)):
            res = s.solve(assumptions=[x[(v0, 0)]])
            print(f" cube {i+1}/{len(divs)} v0={v0}: "
                  f"{'SAT' if res else 'UNSAT'} t={time.time()-t0:.0f}s",
                  flush=True)
            if res:
                report_sat(s, tag=f"cube v0={v0}")
                return
    print(f"UNSAT (all cubes) t={time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
