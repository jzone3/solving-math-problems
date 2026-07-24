#!/usr/bin/env python3
"""
P15 V4 phase 45 (v3): fresh-modulus patches with mixed deflated
scales.

Identity (see patch46.py): for cell (r, n), scale s >= 2, b | n with
gcd(b, s) = 1, the congruence  r + j*n (mod s*n/b)  covers exactly
{ r + i*n : i = j (mod s) }.  Distinct b give DISTINCT moduli for the
same scale s, so a cell can be covered by any multiset of scales
admitting a residue cover of Z -- e.g. two scale-2 congruences, or
one scale-2 + two scale-4, etc.

Per cell: compute the supply of fresh moduli per scale s | 10080,
then greedily cover Z/10080 in i-space picking at each step the
(scale, residue) pair with the best coverage-per-supply, consuming
one fresh modulus per chosen congruence.  Global freshness is
maintained across the emission and all patches.  Each patch is
self-tested: the patch congruences alone must cover the first 4096
points of their cell.
"""
import json
import numpy as np
from math import gcd
from globalcheck import all_sections

L = 10080
SCALES = sorted(s for s in range(2, L + 1) if L % s == 0)

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
        ds = [x * p ** i for x in ds for i in range(e + 1)]
    return sorted(ds)


def patch_cell(r, n, used):
    ds = divisors(n)
    supply = {}
    for s in SCALES:
        mods = []
        seen = set()
        for b in ds:
            if gcd(b, s) != 1:
                continue
            m = s * (n // b)
            if m >= 42 and m not in used and m not in seen:
                seen.add(m)
                mods.append(m)
        if mods:
            supply[s] = mods
    unc = np.ones(L, dtype=bool)
    chosen = []
    while unc.any():
        best = None
        for s, mods in supply.items():
            if not mods:
                continue
            cnt = unc.reshape(L // s, s).sum(axis=0)
            a = int(cnt.argmax())
            c = int(cnt[a])
            if c and (best is None or c > best[0]):
                best = (c, s, a)
        if best is None:
            return None
        c, s, a = best
        m = supply[s].pop(0)
        chosen.append(((r + a * n) % m, m))
        unc[a::s] = False
    for _, m in chosen:
        used.add(m)
    return chosen


def main():
    secs = all_sections()
    used = set()
    for name, cc, tt in secs:
        for r, n in cc:
            used.add(n)
    tails = [(name, r, n) for name, cc, tt in secs for r, n in tt]
    print(f"used moduli: {len(used)}, cells: {len(tails)}")

    tails.sort(key=lambda t: -t[2])
    patches = []
    percell = []
    fail = []
    for name, r, n in tails:
        got = patch_cell(r, n, used)
        if got is None:
            fail.append((name, r, n))
        else:
            patches.extend(got)
            percell.append(((r, n), got))
    print(f"cells patched: {len(tails) - len(fail)}/{len(tails)}, "
          f"failed: {len(fail)}")
    for f in fail[:10]:
        print("  FAIL", f)
    print(f"patch congruences: {len(patches)}")
    mods = [m for _, m in patches]
    assert len(set(mods)) == len(mods), "patch moduli collide"
    print(f"patch moduli all distinct; min patch modulus: {min(mods)}")

    # self-test: each cell fully covered by its own patch congruences
    bad = 0
    for (r, n), got in percell:
        K = 4096
        cov = np.zeros(K, dtype=bool)
        for r2, m in got:
            g = gcd(n, m)
            if (r - r2) % g:
                continue
            mg = m // g
            inv = pow((n // g) % mg, -1, mg)
            i0 = ((r2 - r) // g * inv) % mg
            if i0 < K:
                cov[i0::mg] = True
        if not cov.all():
            bad += 1
    print(f"self-test: cells with incomplete patch cover: {bad}")

    with open("patches47.json", "w") as fh:
        json.dump(patches, fh)
    print("wrote patches47.json")


if __name__ == "__main__":
    main()
