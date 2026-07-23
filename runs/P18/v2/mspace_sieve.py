#!/usr/bin/env python3
"""Distortion sieve applied to the parity-reduced (m-space) 'phase-B' pools.

Parity reduction: a #273 witness exists iff M = {m >= 2 : 2m+1 prime} contains two DISJOINT
subsets each carrying a distinct-moduli covering of Z; one of the two families cannot use
m=2, so a covering of Z with distinct moduli from M \ {2} ('phase B') is NECESSARY for #273.

Here: pool(N) = {m | N : m >= 3, 2m+1 prime} (m=2 excluded). If the sieve certifies
eta(pool) < 1, then no phase-B covering has lcm dividing N — the annealing targets on that
period are provably infeasible.

Usage: python3 mspace_sieve.py N [N2 ...]
"""
import sys
from fractions import Fraction
from sympy import isprime, divisors
from bbmst_independent import optimize

def main():
    for N in map(int, sys.argv[1:]):
        pool = sorted(m for m in divisors(N) if m >= 3 and isprime(2 * m + 1))
        dens = float(sum(Fraction(1, m) for m in pool))
        print(f"N={N} |pool|={len(pool)} mass={dens:.4f}", flush=True)
        if dens < 1:
            print("  EXCLUDED trivially (mass < 1)")
            continue
        primes, deltas, eta, levels, fbest = optimize(pool)
        if eta < 1:
            print(f"  CERTIFIED EXCLUDED (exact): eta = {eta} = {float(eta):.6f} < 1 "
                  f"-> no phase-B covering with lcm | {N}")
        else:
            print(f"  UNDECIDED: eta ~ {fbest:.6f} (exact {float(eta):.6f})")

if __name__ == "__main__":
    main()
