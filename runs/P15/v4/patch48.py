#!/usr/bin/env python3
"""
P15 V4 phase 45 (v4): fresh-modulus patches via recursive scale trees.

Same deflation identity as patch46/47: for cell (r, n), any step
s >= 2 and any g | n with gcd(s, n/g) = 1, the congruence
r + a*n (mod g*s) covers exactly { r + i*n : i = a (mod s) }.

Instead of a fixed cover of Z/10080, each cell is covered by a
recursive scale TREE in i-space: a node is a class (a mod s); it is
either closed by one congruence (consuming a globally fresh modulus
g*s) or split into p children (a + j*s mod s*p) for a small prime p.
Deep scales open up an essentially inexhaustible supply of fresh
deflated moduli, which fixes the pool-exhaustion failures of v2/v3.

DFS policy: at a node of scale s, first try to close it; otherwise
split by the prime p (from 2,3,5,7,11,13) whose child scale has the
most supply; fail beyond scale 10^7.
"""
import json
import numpy as np
from math import gcd
from globalcheck import all_sections

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
          59, 61, 67, 71, 73, 79, 83, 89, 97]
SPLITP = [2, 3, 5, 7, 11, 13]
SCALECAP = 10 ** 8


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


class CellPatcher:
    def __init__(self, r, n, used, cap=16, minm=42):
        self.r, self.n, self.used = r, n, used
        self.ds = divisors(n)
        self.out = []
        self.cap = cap
        self.minm = minm

    def fresh(self, s):
        """Fresh moduli of step s, smallest first."""
        got = []
        for g in reversed(self.ds):
            if gcd(s, self.n // g) == 1:
                m = g * s
                if m >= self.minm and m not in self.used:
                    got.append(m)
        return sorted(got, reverse=True)

    def cover(self, a, s):
        if s > SCALECAP or len(self.out) >= self.cap:
            return False
        f = self.fresh(s)
        if f:
            m = f[0]
            self.used.add(m)
            self.out.append(((self.r + a * self.n) % m, m))
            return True
        best_p = None
        for p in SPLITP:
            if len(self.fresh(s * p)) >= p:
                best_p = p
                break
        if best_p is None:
            best_p = 2
        for j in range(best_p):
            if not self.cover(a + j * s, s * best_p):
                return False
        return True


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
    todo = tails
    fail = []
    for cap, big in ((8, True), (4, False), (16, False), (64, False),
                     (512, False)):
        fail = []
        for name, r, n in todo:
            cp = CellPatcher(r, n, used, cap=cap,
                             minm=n if big else 42)
            if cp.cover(0, 2) and cp.cover(1, 2):
                patches.extend(cp.out)
                percell.append(((r, n), cp.out))
            else:
                for _, m in cp.out:
                    used.discard(m)
                fail.append((name, r, n))
        print(f"pass cap={cap} big={big}: "
              f"patched {len(todo) - len(fail)}, remaining {len(fail)}")
        todo = fail
        if not fail:
            break
    print(f"cells patched: {len(tails) - len(fail)}/{len(tails)}, "
          f"failed: {len(fail)}")
    for f in fail[:10]:
        print("  FAIL", f)
    print(f"patch congruences: {len(patches)}")
    mods = [m for _, m in patches]
    assert len(set(mods)) == len(mods), "patch moduli collide"
    print(f"patch moduli all distinct; min patch modulus: {min(mods)}")

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

    with open("patches48.json", "w") as fh:
        json.dump(patches, fh)
    print("wrote patches48.json")


if __name__ == "__main__":
    main()
