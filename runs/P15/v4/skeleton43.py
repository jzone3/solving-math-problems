#!/usr/bin/env python3
"""
P15 V4 phase 7: SKELETON EXPERIMENT for the small-prime redesign route.

Question (from NOTES section 17): a T=43 system needs a redesigned
2/3/5/7 skeleton. How much density must a min-modulus-43 skeleton hand
to the primes >= 11, compared with Owens's T=42 skeleton, and what is
the theoretical ceiling?

Measurements on the window W = 2^a * 3^b * 5^c * 7^d:
  (1) density upper bound: sum of 1/m over distinct 7-smooth m >= T
      (perfect disjoint packing can never beat this);
  (2) constructive lower bound: survivor-aligned lazy greedy packing of
      ALL divisors m >= T of W, each used once, maximizing covered cells;
  (3) Owens's actual T=42 skeleton coverage: sum 1/m over the faithful
      used-set U (owens_smooth.py) - his construction is (near-)disjoint
      by design, so this is essentially his exact skeleton coverage.

The verdict: residual_43(greedy) vs residual_42(Owens): the extra
density a T=43 skeleton must delegate to primes >= 11, to be compared
against the later-section capacity of the repaired blueprint ledgers.
"""
import sys
import time
from fractions import Fraction

import numpy as np


def divisors(fact):
    divs = [1]
    for p, e in fact.items():
        divs = [d * p**k for d in divs for k in range(e + 1)]
    return sorted(divs)


def density_ceiling(fact, T):
    return sum(Fraction(1, m) for m in divisors(fact) if m >= T)


def greedy_skeleton(fact, T, seed=0, passes=1):
    W = 1
    for p, e in fact.items():
        W *= p**e
    rng = np.random.default_rng(seed)
    cand = [m for m in divisors(fact) if m >= T]
    # order: small moduli first (largest classes), random tie-break
    cand.sort(key=lambda m: (m, rng.random()))
    covered = np.zeros(W, dtype=bool)
    x = np.arange(W, dtype=np.int64)
    used = []
    t0 = time.time()
    for m in cand:
        # best residue: the one with most uncovered cells
        res = x[~covered] % m
        if len(res) == 0:
            break
        cnt = np.bincount(res, minlength=m)
        a = int(cnt.argmax())
        gain = int(cnt[a])
        if gain == 0:
            continue
        covered[x % m == a] = True
        used.append((a, m, gain))
    unc = int((~covered).sum())
    return used, unc, W, time.time() - t0


def owens_coverage(T=42, cap=10**7):
    from owens_smooth import used_smooth
    U = used_smooth(cap)
    s = sum(Fraction(1, m) for m in U if m >= T)
    return s, len([m for m in U if m >= T])


if __name__ == "__main__":
    fact = {2: 7, 3: 4, 5: 2, 7: 2}
    if len(sys.argv) > 1 and sys.argv[1] == "big":
        fact = {2: 7, 3: 4, 5: 3, 7: 2}
    for T in (42, 43):
        ceil = density_ceiling(fact, T)
        used, unc, W, dt = greedy_skeleton(fact, T)
        print(f"T={T} window {fact}: ceiling={float(ceil):.6f}, "
              f"greedy covered={1 - unc / W:.6f} "
              f"({len(used)} moduli, {dt:.0f}s), residual={unc / W:.6f}")
    s42, n42 = owens_coverage(42)
    print(f"Owens faithful skeleton (>=42, cap 1e7): density={float(s42):.6f} "
          f"over {n42} moduli -> residual={1 - float(s42):.6f}")
    s43 = s42 - Fraction(1, 42)
    print(f"Owens skeleton minus the 42-congruence: density={float(s43):.6f} "
          f"-> residual={1 - float(s43):.6f}")
