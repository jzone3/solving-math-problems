#!/usr/bin/env python3
"""Exact minimal-lcm ladder: for a given T, decide for each N ascending whether
Z_N can be covered by residue classes with distinct divisor-moduli >= T.
The minimal SAT N = minimal possible lcm of a covering system with min modulus
>= T (any covering system's moduli generate some lcm N; classes mod n_i are
unions of classes mod N).

Prunes N whose divisor reciprocal sum over [T, N] is < 1 (necessary measure).
Decides the rest with the CRT-tree SAT encoding + cadical.

Usage: python3 minlcm.py -T 4 --nmax 4000 [--time-limit 300]
"""
import argparse
import time
from fractions import Fraction
from pysat.solvers import Solver
from sat_tree import build


def factorize(n):
    fac = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            fac[d] = fac.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        fac[n] = fac.get(n, 0) + 1
    return fac


def measure_ok(N, T):
    s = Fraction(0)
    for v in range(T, N + 1):
        if N % v == 0:
            s += Fraction(1, v)
    return s >= 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--nmax", type=int, required=True)
    ap.add_argument("--nmin", type=int, default=1)
    ap.add_argument("--conf-budget", type=int, default=10_000_000)
    ap.add_argument("--solver", default="cadical195")
    args = ap.parse_args()
    T = args.T
    t0 = time.time()
    for N in range(args.nmin, args.nmax + 1):
        if not measure_ok(N, T):
            continue
        fac = factorize(N)
        _, divs, x, cnf = build(fac, T)
        # translation symmetry: some divisor v0 covers point 0, and we may
        # translate so its residue is 0 -> case split over v0 (sound).
        with Solver(name=args.solver, bootstrap_with=cnf) as s:
            res = False
            for v0 in sorted(divs, reverse=True):
                s.conf_budget(args.conf_budget)
                r = s.solve_limited(assumptions=[x[(v0, 0)]])
                if r is not False:
                    res = r
                    break
            tag = {True: "SAT", False: "UNSAT", None: "UNDECIDED"}[res]
            print(f"N={N} ({fac}): {tag}  t={time.time()-t0:.0f}s", flush=True)
            if res:
                pos = set(l for l in s.get_model() if l > 0)
                congs = sorted((a, v) for (v, a), lit in x.items()
                               if lit in pos)
                fn = f"covers/minlcm_T{T}_N{N}.txt"
                with open(fn, "w") as f:
                    f.write(f"# minimal-lcm ladder T={T} N={N}\n")
                    for a, v in congs:
                        f.write(f"{a} {v}\n")
                print(f"MINIMAL lcm for T={T}: N={N}; wrote {fn}")
                return


if __name__ == "__main__":
    main()
