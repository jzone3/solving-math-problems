#!/usr/bin/env python3
"""
P15 V4 phase 45 (v2): fresh-modulus patches via divisor-deflated
moduli.

Key identity: for a cell (r, n), any d >= 2, any b | n with
gcd(b, d) = 1, the congruence

    r + j*n  (mod  d*n/b)

covers exactly the sub-progression { r + i*n : i = j (mod d) } of the
cell (t = b(i-j)/d is integral iff d | (i-j), since gcd(b,d)=1) --
plus points outside the cell, which is harmless.  So the cell is
FULLY covered by d congruences with moduli d*n/b_0,...,d*n/b_{d-1}
for ANY d pairwise-distinct coprime-to-d divisors b_j of n, provided
those moduli are globally fresh.  Unlike plain multiples n*d, the
deflated values d*n/b (b > 1) are not multiples of n and are almost
never occupied by the emission.

For each cell we try d = 2, 3, 4, 5, ... and take the first d for
which d fresh distinct moduli exist; freshness is tracked globally
across the emission and all patches.  Every patch modulus must also
be >= 42 (kept automatically since b is small).
"""
import json
from math import gcd
from globalcheck import all_sections

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
    fail = []
    for name, r, n in tails:
        ds = divisors(n)
        done = False
        for d in range(2, 30):
            cands = [d * (n // b) for b in ds
                     if gcd(b, d) == 1 and d * (n // b) >= 42
                     and d * (n // b) not in used]
            # dedupe preserving order (different b can tie only if equal)
            seen = set()
            mods = []
            for m in cands:
                if m not in seen:
                    seen.add(m)
                    mods.append(m)
            if len(mods) >= d:
                for j in range(d):
                    m = mods[j]
                    used.add(m)
                    patches.append(((r + j * n) % m, m))
                done = True
                break
        if not done:
            fail.append((name, r, n))
    print(f"cells patched: {len(tails) - len(fail)}/{len(tails)}")
    print(f"failures: {len(fail)}")
    for f in fail[:10]:
        print("  FAIL", f)
    print(f"patch congruences: {len(patches)}")
    mods = [m for _, m in patches]
    assert len(set(mods)) == len(mods)
    print(f"patch moduli all distinct; min patch modulus: {min(mods)}")
    with open("patches46.json", "w") as fh:
        json.dump(patches, fh)
    print("wrote patches46.json")


if __name__ == "__main__":
    main()
