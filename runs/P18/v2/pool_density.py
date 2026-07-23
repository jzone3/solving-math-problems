#!/usr/bin/env python3
"""Exact density budget analysis for Erdos #273 pools restricted to a period L.

For a covering system all of whose (distinct) moduli divide L, a trivial necessary
condition is sum over usable moduli m of 1/m >= 1 (densities must add to at least 1).
Usable moduli: m | L, m > 1, m = p-1 for a prime p >= 5.
All arithmetic exact (Fraction).
"""
from fractions import Fraction
from sympy import isprime, divisors

CANDIDATE_L = [
    360,           # Selfridge's p>=3 period (for contrast)
    55440,         # 2^4 3^2 5 7 11
    110880,        # 2^5 3^2 5 7 11
    166320,        # 2^4 3^3 5 7 11
    720720,        # 2^4 3^2 5 7 11 13
    1441440,       # 2^5 3^2 5 7 11 13
    2162160,       # 2^4 3^3 5 7 11 13
    4324320,       # 2^5 3^3 5 7 11 13
    1275120,       # lcm of {p-1 : 5<=p<=47} = 2^4 3^2 5 7 11 23
    12252240,      # 2^4 3^2 5 7 11 13 17
    21621600,      # 2^5 3^3 5^2 7 11 13
]

def pool(L):
    return sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5)

def main():
    for L in CANDIDATE_L:
        P = pool(L)
        s = sum(Fraction(1, m) for m in P)
        print(f"L={L}: |pool|={len(P)} sum 1/m = {s} = {float(s):.6f} "
              f"{'>=1 (not density-blocked)' if s >= 1 else '<1 => NO covering with moduli | L (trivial)'}")
        print(f"   pool={P}")

if __name__ == "__main__":
    main()
