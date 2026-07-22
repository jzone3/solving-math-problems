#!/usr/bin/env python3
"""Screen smooth N candidates: for target min modulus m, find small N with
reciprocal sum over divisors >= m comfortably above 1 (necessary condition)."""
import sys
from itertools import product

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]


def divisors_from(fact):
    ds = [1]
    for p, e in fact:
        ds = [d * p**k for d in ds for k in range(e + 1)]
    return ds


def recip(fact, m):
    return sum(1.0 / d for d in divisors_from(fact) if d >= m)


def gen(cap):
    maxe = {2: 7, 3: 5, 5: 3, 7: 2, 11: 1, 13: 1, 17: 1, 19: 1, 23: 1}
    ranges = [range(0, maxe[p] + 1) for p in PRIMES]
    for es in product(*ranges):
        N = 1
        ok = True
        for p, e in zip(PRIMES, es):
            N *= p**e
            if N > cap:
                ok = False
                break
        # require no gaps (if p_i unused, later primes unused) — keep smooth ladder
        if not ok:
            continue
        used = [e > 0 for e in es]
        if any(not used[i] and used[j] for i in range(len(es)) for j in range(i + 1, len(es))):
            continue
        yield N, [(p, e) for p, e in zip(PRIMES, es) if e > 0]


if __name__ == "__main__":
    m = int(sys.argv[1])
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 10**6
    margin = float(sys.argv[3]) if len(sys.argv) > 3 else 1.05
    cands = []
    for N, fact in gen(cap):
        r = recip(fact, m)
        if r >= margin:
            cands.append((N, r, fact))
    cands.sort()
    for N, r, fact in cands[:15]:
        print(N, f"{r:.4f}", fact)
