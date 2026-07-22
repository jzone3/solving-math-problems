#!/usr/bin/env python3
"""Reciprocal-sum feasibility analysis for a covering system with min modulus M.

A covering system with distinct moduli n_i needs sum 1/n_i > 1 (density).
If all moduli are P-smooth (divisors of prod_{p<=P} p^inf) and >= M, the
absolute maximum available measure is
    S(P, M) = prod_{p<=P} p/(p-1)  -  sum_{d P-smooth, d < M} 1/d.
This gives a hard lower bound on the prime set needed, and the "slack"
available at each choice of P.  (Nielsen used primes to 103 for M=40,
Owens primes to 89 for M=42.)
"""
from fractions import Fraction
import sys

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131]


def smooth_divisors_below(primes, bound):
    """All integers < bound whose prime factors are all in `primes`."""
    out = [1]
    for p in primes:
        new = []
        for d in out:
            t = d * p
            while t < bound:
                new.append(t)
                t *= p
        out += new
    return sorted(out)


def analyze(M, max_primes=len(PRIMES)):
    print(f"=== M = {M} ===")
    total = Fraction(1)
    for k in range(max_primes):
        p = PRIMES[k]
        total *= Fraction(p, p - 1)
        ps = PRIMES[:k + 1]
        small = smooth_divisors_below(ps, M)
        lost = sum(Fraction(1, d) for d in small)
        S = total - lost
        print(f"primes<= {p:4d} (k={k+1:2d}): full measure {float(total):.4f}, "
              f"lost to d<{M}: {float(lost):.4f}, usable S = {float(S):+.4f}"
              + ("   <-- infeasible" if S <= 1 else ""))


if __name__ == "__main__":
    for M in ([int(a) for a in sys.argv[1:]] or [40, 42, 43, 48]):
        analyze(M)
        print()
