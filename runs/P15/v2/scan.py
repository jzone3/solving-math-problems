#!/usr/bin/env python3
"""Scan: for each smooth N in a ladder, find the maximal T for which the
greedy+repair engine4 finds a covering with distinct divisor moduli >= T.
Writes successes to covers/ and appends results to scan_results.txt."""
import os
import sys
import time
import numpy as np
from engine4 import factorize_spec, divisors, cover, repair, one_opt

LADDER = [
    ("2^6,3^4,5^2,7,11,13", 10),
    ("2^6,3^4,5^2,7^2,11,13", 9),
]

os.makedirs("covers", exist_ok=True)


def recip_budget(fac, T):
    ds = divisors(fac, lo=T)
    return sum(1.0 / d for d in ds)


def attempt(spec, T, budget):
    fac = factorize_spec(spec)
    congs, rem, N = cover(fac, T, verbose=False)
    cycles = 3
    for cyc in range(cycles):
        if rem == 0:
            break
        U = np.ones(N, dtype=bool)
        for a, v in congs:
            U[a::v] = False
        congs, rem = repair(N, None, congs, U, rounds=100000,
                            t_budget=budget // (2 * cycles), seed=cyc,
                            verbose=False)
        if rem == 0:
            break
        congs, rem = one_opt(N, congs, t_budget=budget // (2 * cycles),
                             seed=cyc, verbose=False)
    return congs, rem, N


def main():
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    with open("scan_results.txt", "a") as log:
        log.write(f"\n# scan started {time.ctime()}, repair budget={budget}s\n")
        for spec, start in LADDER:
            fac = factorize_spec(spec)
            N = 1
            for p, e in fac.items():
                N *= p ** e
            T = start if start else 3
            best_T = None
            while True:
                rb = recip_budget(fac, T)
                if rb < 1.0:
                    log.write(f"{spec} N={N} T={T}: reciprocal budget {rb:.3f} < 1, stop\n")
                    log.flush()
                    break
                t0 = time.time()
                congs, rem, _ = attempt(spec, T, budget)
                msg = (f"{spec} N={N} T={T}: rem={rem} congs={len(congs)} "
                       f"recip={rb:.3f} t={time.time()-t0:.0f}s")
                print(msg, flush=True)
                log.write(msg + "\n")
                log.flush()
                if rem == 0:
                    best_T = T
                    fn = f"covers/T{T}_{spec.replace('^','e').replace(',','_')}.txt"
                    with open(fn, "w") as f:
                        f.write(f"# T={T} N={spec} engine4 scan\n")
                        for a, v in congs:
                            f.write(f"{a} {v}\n")
                    T += 1
                else:
                    log.write(f"{spec} N={N}: max T achieved = {best_T}\n")
                    log.flush()
                    break


if __name__ == "__main__":
    main()
