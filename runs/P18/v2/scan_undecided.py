#!/usr/bin/env python3
"""Float-only frontier scan: for a family of smooth periods L, run the delta-optimized
distortion-sieve eta (float search only, no exact certification) to map which admissible
pools are excluded (eta < 1) vs undecided (eta >= 1). Any covering system whose lcm
divides an excluded L cannot exist, so undecided L's characterize where a positive
construction (with smooth period) could still live. Exploration artifact only —
certification of interesting cases is done separately with bbmst_independent.py.
"""
import itertools
from fractions import Fraction
from sympy import isprime, divisors
from bbmst_independent import optimize

def main():
    cands = set()
    for a in range(3, 8):
        for b in range(1, 5):
            for c in range(0, 4):
                for d in range(0, 2):
                    for extra in (1, 11, 11 * 13, 11 * 13 * 17, 11 * 13 * 17 * 19):
                        L = 2**a * 3**b * 5**c * 7**d * extra
                        if 5000 < L < 3 * 10**8:
                            cands.add(L)
    results = []
    for L in sorted(cands):
        pool = [m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5]
        dens = sum(Fraction(1, m) for m in pool)
        if dens < 1:
            continue  # excluded trivially
        if len(pool) > 260:
            continue  # too slow for the scan budget
        primes, deltas, eta, levels, fbest = optimize(pool)
        tag = "EXCLUDED" if eta < 1 else "UNDECIDED"
        print(f"L={L} |pool|={len(pool)} dens={float(dens):.4f} eta~{fbest:.5f} {tag}", flush=True)
        results.append((L, fbest, tag))
    und = [r for r in results if r[2] == "UNDECIDED"]
    print(f"\n{len(results)} pools with density>=1 scanned; {len(und)} undecided:")
    for L, e, _ in und:
        print(f"  L={L} eta~{e:.5f}")

if __name__ == "__main__":
    main()
