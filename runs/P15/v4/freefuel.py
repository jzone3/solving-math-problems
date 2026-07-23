#!/usr/bin/env python3
"""
P15 V4 phase 8: corrected FREE-FUEL accounting for the 42-cell patch.

Fuel-conservation law (see NOTES section 19): stealing used moduli gives
zero net progress in hole measure - covering a cell of measure 1 with
multipliers D creates burden 1 - (free measure applied).  Hence the
42-cell patch closes iff the total FREE inner density reaches 1 with
constructive alignment.  This script computes the exact free inner
density from the corrected faithful enumeration (owens_smooth.py after
the e3 fix), split by family, plus the unbounded safe-prime reservoir.
"""
from fractions import Fraction as F
from math import gcd

from owens_smooth import entry_sets

CAP = 10**7


def seven_smooth(n):
    for p in (2, 3, 5, 7):
        while n % p == 0:
            n //= p
    return n == 1


def main():
    E = entry_sets(CAP)
    # primitive free 7-tower multipliers t (coprime to 7): M = 7^k*t free
    free_t = [t for t in range(1, 3000)
              if t % 7 and seven_smooth(t) and t not in E]
    print("primitive free multipliers t <= 3000:", free_t)

    # inner density: M = 7^k*t covers class of inner measure 1/n,
    # n = M/gcd(M,42); free for k >= 1 if M >= 43 else k >= 2.
    tot = F(0)
    per_t = []
    for t in free_t:
        s = F(0)
        M = 7 * t
        k = 1
        while M <= CAP * 7:
            if M >= 43:
                s += F(gcd(M, 42), M)
            M *= 7
            k += 1
        per_t.append((t, s))
        tot += s
    per_t.sort(key=lambda x: -x[1])
    for t, s in per_t[:12]:
        print(f"  t={t:5d}: inner density {s} = {float(s):.5f}")
    print(f"TOTAL free 7-smooth inner density: {float(tot):.5f}")
    print("(old, pre-fix figure was 0.6167; gap to 1 must come from")
    print(" safe primes >= 97, whose fuel sum diverges - see patchcover")
    print(" geometric-decay run in NOTES section 19)")


if __name__ == "__main__":
    main()
