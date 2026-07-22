#!/usr/bin/env python3
"""Exhaustive scan over ALL dumbbell(a,l,b) with n <= NMAX for the minimal
violating instance, under both mu conventions. Also scans lollipops (b=1)
and 'broom' variants are covered by b=2. Exact integer arithmetic."""
import sys
from math import comb
from dumbbell_search import dumbbell_m, dumbbell_S

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 140

best_pairs = None
best_full = None
for n in range(5, NMAX + 1):
    for a in range(2, n):
        for b in range(2, a + 1):  # wlog a >= b
            l = n + 1 - a - b
            if l < 1:
                continue
            m = dumbbell_m(a, l, b)
            S = dumbbell_S(a, l, b)
            lhs = 2 * m * S * S
            if lhs > n ** 3 * comb(n, 2) ** 2 and best_pairs is None:
                best_pairs = (n, a, l, b)
                print("minimal pairs-violation:", best_pairs)
            if 4 * lhs > n ** 7 and best_full is None:
                best_full = (n, a, l, b)
                print("minimal full-matrix violation:", best_full)
    if best_pairs and best_full:
        break
print("best_pairs =", best_pairs)
print("best_full  =", best_full)
