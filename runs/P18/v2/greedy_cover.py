#!/usr/bin/env python3
"""Witness search (positive direction) on periods the distortion sieve could NOT exclude
(eta >= 1), e.g. L = 21621600 = 2^5 3^3 5^2 7 11 13.

Randomized greedy max-coverage + patching, exact verification at the end. Incomplete
search: only a SAT (witness) outcome is a result; failure to find one proves nothing.

Usage: python3 greedy_cover.py L [restarts] [seed]
"""
import sys
import numpy as np
from fractions import Fraction
from sympy import isprime, divisors

def attempt(L, P, rng, theta):
    covered = np.zeros(L, dtype=bool)
    choice = {}
    unused = []
    for m in P:  # ascending
        unc = ~covered
        cnt = np.bincount(np.nonzero(unc)[0] % m, minlength=m)
        best = cnt.max()
        if best == 0 or best < theta * (L // m):
            unused.append(m)
            continue
        cands = np.nonzero(cnt == best)[0]
        a = int(cands[rng.integers(len(cands))])
        choice[m] = a
        covered[a::m] = True
        if covered.all():
            return choice, 0, unused
    # patching phase: try unused moduli (largest first) on what's left
    for m in sorted(unused, reverse=True):
        if covered.all():
            break
        unc_idx = np.nonzero(~covered)[0]
        if len(unc_idx) == 0:
            break
        cnt = np.bincount(unc_idx % m, minlength=m)
        best = cnt.max()
        if best > 0:
            a = int(np.nonzero(cnt == best)[0][0])
            choice[m] = a
            covered[a::m] = True
    rem = int((~covered).sum())
    return choice, rem, unused

def main():
    L = int(sys.argv[1])
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    P = sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5)
    budget = float(sum(Fraction(1, m) for m in P))
    print(f"L={L} |pool|={len(P)} budget={budget:.5f}", flush=True)
    rng = np.random.default_rng(seed)
    best_rem = None
    for t in range(restarts):
        theta = float(rng.uniform(0.55, 0.95))
        choice, rem, _ = attempt(L, P, rng, theta)
        if best_rem is None or rem < best_rem:
            best_rem = rem
            print(f"[try {t}] theta={theta:.3f} used={len(choice)} uncovered={rem}", flush=True)
        if rem == 0:
            print("WITNESS FOUND — exact re-verification:")
            covered = bytearray(L)
            ms = sorted(choice)
            assert len(set(ms)) == len(ms)
            for m in ms:
                a = choice[m]
                for x in range(a, L, m):
                    covered[x] = 1
            ok = all(covered)
            print("PASS" if ok else "FAIL")
            for m in ms:
                print(choice[m], m)
            return
    print(f"no witness found in {restarts} restarts; best uncovered = {best_rem}")

if __name__ == "__main__":
    main()
