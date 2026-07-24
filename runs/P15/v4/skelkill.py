#!/usr/bin/env python3
"""
P15 V4 phase 18: seed the compressed kill machinery with the EXACT
Owens 2/3 skeleton (emitcore.py) instead of greedy layers, and measure
the hole-class concentration -- the quantity phase-2 identified as the
sole blocker (greedy: holes ~1e6 vs pool ~1e2 at T=13).

Steps:
  1. emit the exact skeleton over window M = 2^D2 * 3^D3;
  2. coalesce residual holes into MINIMAL cosets r (mod n), n | M
     (exact recursive coalescing on the divisor tree);
  3. report class count vs raw hole count;
  4. kill-pool feasibility: unused divisors >= T of M * 5^a * 7^b.
"""
import sys
from math import gcd
sys.setrecursionlimit(100000)

import emitcore

D2, D3 = emitcore.D2, emitcore.D3
M = emitcore.M


def coalesce(holes, M):
    """Coalesce a sorted set of residues mod M into minimal cosets.
    Recursive: split by smallest prime factor p of M; a residue class r
    (mod p) whose fiber is FULL becomes one coset if all p fibers full.
    Returns list of (r, n) cosets with n | M."""
    def rec(S, mod, off, step):
        # S: set of x with x ≡ off (mod step), viewed as residues of
        # (x - off)//step mod mod. Full?
        if len(S) == mod:
            return [(off, step)]
        if not S:
            return []
        if mod == 1:
            return [(off, step)]
        p = 2 if mod % 2 == 0 else 3
        out = []
        for r in range(p):
            sub = set(x for x in S if x % p == r)
            out += rec(set((x - r) // p for x in sub), mod // p,
                       off + step * r, step * p)
        return out
    return rec(holes, M, 0, 1)


def divisors(M):
    ds = [1]
    m, fac = M, {}
    for p in (2, 3, 5, 7):
        while m % p == 0:
            fac[p] = fac.get(p, 0) + 1
            m //= p
    for p, e in fac.items():
        ds = [d * p ** k for d in ds for k in range(e + 1)]
    return sorted(ds)


def main():
    congs = emitcore.emit()
    used = set(n for _, n in congs)
    cov = bytearray(M)
    for r, n in congs:
        cov[r % n::n] = b"\x01" * len(range(r % n, M, n))
    holes = set(x for x in range(M) if not cov[x])
    print(f"skeleton: {len(congs)} congs, {len(holes)} raw holes "
          f"(density {len(holes)/M:.4f}) over M=2^{D2}*3^{D3}")

    cosets = coalesce(holes, M)
    print(f"coalesced hole classes: {len(cosets)}")
    from collections import Counter
    cnt = Counter(n for _, n in cosets)
    for n in sorted(cnt):
        print(f"  cell modulus {n}: {cnt[n]} classes (density "
              f"{cnt[n]/n:.5f})")
    tot = sum(1 / n for _, n in cosets)
    print(f"total hole density check: {tot:.4f}")

    # kill-pool feasibility at T=43 with 5^3*7^2 window extension
    T = 43
    for (a, b) in [(0, 0), (2, 1), (3, 2)]:
        Mx = M * 5 ** a * 7 ** b
        pool = [d for d in divisors(Mx) if d >= T and d not in used]
        print(f"window x5^{a}x7^{b}: kill pool size {len(pool)} "
              f"(need >= {len(cosets)} classes -> "
              f"{'FEASIBLE count-wise' if len(pool) >= len(cosets) else 'INFEASIBLE'})")


if __name__ == "__main__":
    main()
