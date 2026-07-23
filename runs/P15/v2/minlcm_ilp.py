#!/usr/bin/env python3
"""Exact minimal-lcm ladder via HiGHS ILP (much stronger than CDCL SAT here:
LP relaxation + presolve refutes infeasible N in seconds where cadical needs
>1e7 conflicts). For given T, ascending N with divisor reciprocal sum >= 1,
decide coverability of Z_N by distinct divisor moduli >= T.

Usage: python3 minlcm_ilp.py -T 5 --nmax 30000 [--time-limit 900]
"""
import argparse
import io
import time
import contextlib
from fractions import Fraction
from minlcm import factorize
from ilp import solve


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
    ap.add_argument("--time-limit", type=float, default=900)
    args = ap.parse_args()
    T = args.T
    t0 = time.time()
    for N in range(args.nmin, args.nmax + 1):
        if not measure_ok(N, T):
            continue
        fac = factorize(N)
        spec = ",".join(f"{p}^{e}" if e > 1 else str(p)
                        for p, e in sorted(fac.items()))
        out = f"covers/minlcm_T{T}_N{N}.txt"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = solve(fac, T, time_limit=args.time_limit, out=out)
        tag = {True: "SAT", False: "UNSAT", None: "UNDECIDED"}[res]
        print(f"N={N} ({spec}): {tag}  t={time.time()-t0:.0f}s", flush=True)
        if res:
            print(f"MINIMAL lcm for T={T}: N={N} (modulo any UNDECIDED above); "
                  f"witness {out}")
            return


if __name__ == "__main__":
    main()
