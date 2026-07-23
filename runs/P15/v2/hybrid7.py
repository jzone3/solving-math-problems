#!/usr/bin/env python3
"""Hybrid: engine7 symbolic Nielsen-style front-end down to M = N, then
engine5-style finishing on the residual holes using ALL unused divisors of N
(not just level-new ones) + streaming one-opt with exact recompute.

Usage: python3 hybrid7.py -T 11 -N "2^6,3^4,5^2,7,11,13,17" \
       --steps "2^6,3^4,5^2,7,11,13,17" [--eff 0.5] [-o out.txt]
"""
import argparse
import time
import numpy as np
from engine4 import factorize_spec, divisors
import engine7
import engine5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("-N", required=True)
    ap.add_argument("--steps", required=True)
    ap.add_argument("--eff", type=float, default=0.5)
    ap.add_argument("--vmax", type=int, default=None)
    ap.add_argument("--budget", type=int, default=80_000_000)
    ap.add_argument("--opt-budget", type=int, default=7200)
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    N = 1
    for p, e in fac.items():
        N *= p ** e
    steps = engine7.parse_steps(args.steps)
    # front-end: run engine7 steps manually to capture state
    M = 1
    cfac = {}
    uncovered = [0]
    used = set()
    congs = []
    t0 = time.time()
    for si, (p, k) in enumerate(steps):
        e_old = cfac.get(p, 0)
        e_new = e_old + k
        pk = p ** k
        if len(uncovered) * pk > args.budget:
            print(f"ABORT front-end step {si+1}")
            return
        Mp = M * pk
        base = np.asarray(uncovered, dtype=np.uint64)
        children = (base[:, None] +
                    (np.arange(pk, dtype=np.uint64) * np.uint64(M))[None, :]
                    ).ravel()
        base_fac = dict(cfac)
        base_fac.pop(p, None)
        cands = set()
        pj = p ** (e_old + 1)
        for j in range(e_old + 1, e_new + 1):
            cap_d = None if args.vmax is None else args.vmax // pj
            if cap_d is not None and cap_d < 1:
                break
            for d in engine7.divisors_of(base_fac, cap=cap_d):
                v = d * pj
                if v >= args.T:
                    cands.add(v)
            pj *= p
        rem = engine7.cover_step_np(children, cands, used, congs, args.eff,
                                    final_any=(si < len(steps) - 1))
        uncovered = [int(c) for c in rem]
        M = Mp
        cfac[p] = e_new
        print(f"front step {si+1}/{len(steps)} p={p}^{e_new}: "
              f"uncovered {len(uncovered)}, congs {len(congs)}, "
              f"t={time.time()-t0:.0f}s", flush=True)
    assert M == N, (M, N)
    holes = np.asarray(sorted(uncovered), dtype=np.int64)
    print(f"front-end done: {holes.size} holes at N={N}, {len(congs)} congs",
          flush=True)
    # finishing: place ALL unused divisors >= T on the holes (engine5 machinery)
    used_d = {v: a for a, v in congs}
    assert len(used_d) == len(congs)
    divs = divisors(fac, lo=args.T)
    holes, used_d = engine5.place_on_holes(holes, divs, used_d, verbose=True)
    if holes.size:
        holes, used_d = engine5.one_opt_stream(N, used_d, holes,
                                               t_budget=args.opt_budget)
    print(f"final holes: {holes.size}, placements {len(used_d)}")
    suffix = "" if holes.size == 0 else ".part"
    with open(args.out + suffix, "w") as f:
        f.write(f"# hybrid7 T={args.T} N={args.N} holes={holes.size}\n")
        for v, a in sorted(used_d.items()):
            f.write(f"{a} {v}\n")
    print(f"wrote {args.out + suffix}")
    if holes.size == 0:
        print("SUCCESS: run verify.py to confirm")


if __name__ == "__main__":
    main()
