#!/usr/bin/env python3
"""
P15 V4 phase 44: two exact global computations on the placeholder set.

(1) Single-congruence absorption at ANY modulus: cell (r,n) is fully
    covered by one emitted congruence (r2,n2) iff n2 | n and
    r = r2 (mod n2).  We enumerate the divisors of each cell modulus
    that occur as emitted moduli (no modulus cap, unlike phase 43).

(2) Exact total residual measure: sum over placeholder cells of
    (uncovered fraction within cell)/n, using the exact
    progression-intersection census against moduli <= MODCAP, plus
    the rigorous upper bound contribution of larger moduli.
"""
import numpy as np
from math import gcd
from collections import defaultdict
from globalcheck import all_sections

MODCAP = 2 * 10 ** 6
K = 4096

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
          59, 61, 67, 71, 73, 79, 83, 89, 97]


def divisors(n):
    fac = []
    m = n
    for p in PRIMES:
        if p * p > m:
            break
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e:
            fac.append((p, e))
    if m > 1:
        fac.append((m, 1))
    ds = [1]
    for p, e in fac:
        ds = [d * p ** i for d in ds for i in range(e + 1)]
    return ds


def main():
    secs = all_sections()
    bymod = defaultdict(list)
    for name, cc, tt in secs:
        for r, n in cc:
            bymod[n].append(r)
    print(f"distinct moduli: {len(bymod)}")

    tails = []
    for name, cc, tt in secs:
        for r, n in tt:
            tails.append((name, r, n))
    print(f"placeholders: {len(tails)}")

    absorbed = 0
    for name, r, n in tails:
        hit = False
        for d in divisors(n):
            if d in bymod and any(r % d == r2 % d for r2 in bymod[d]):
                hit = True
                break
        if hit:
            absorbed += 1
    print(f"single-congruence absorbed (any modulus): {absorbed}")

    allc = [(r, n) for name, cc, tt in secs for r, n in cc]
    R = np.array([r for r, n in allc if n <= MODCAP], dtype=np.int64)
    N = np.array([n for r, n in allc if n <= MODCAP], dtype=np.int64)
    big_meas = sum(1.0 / n for r, n in allc if n > MODCAP)
    total = 0.0
    for name, r, n in tails:
        G = np.gcd(N, n)
        idx = np.nonzero((r - R) % G == 0)[0]
        cov = np.zeros(K, dtype=bool)
        for j in idx:
            n2, r2, g = int(N[j]), int(R[j]), int(G[j])
            n2g = n2 // g
            if n2g == 1:
                cov[:] = True
                break
            inv = pow((n // g) % n2g, -1, n2g)
            i0 = ((r2 - r) // g * inv) % n2g
            if i0 < K:
                cov[i0::n2g] = True
        total += (int((~cov).sum()) / K) / n
    print(f"residual measure of placeholders (mod<= {MODCAP} census): "
          f"{total:.6e}")
    print(f"total measure of emitted moduli > {MODCAP} "
          f"(max further absorption): {big_meas:.6e}")
    print(f"rigorous residual bracket: [{max(total - big_meas, 0):.3e}, "
          f"{total:.3e}]")


if __name__ == "__main__":
    main()
