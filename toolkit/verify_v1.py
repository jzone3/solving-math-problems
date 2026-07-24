#!/usr/bin/env python3
"""
Independent verifier for P15 (covering system, minimum modulus >= M).

Usage:
    python3 verify.py witness.json [--minmod M]

Witness format (JSON):
    {"minmod": 43, "congruences": [[a1, n1], [a2, n2], ...]}
meaning the residue classes  x = a_i (mod n_i).

Checks (all must hold to print PASS):
  1. All moduli n_i are integers > 1 and n_i >= minmod.
  2. All moduli are pairwise DISTINCT.
  3. The classes cover Z: every integer lies in at least one class.
     Verified exactly by a CRT-structured recursive splitting that never
     materializes lcm(n_i).  Additionally cross-checked by random sampling.

No dependencies beyond the Python 3 standard library.
"""
import json
import random
import sys


def smallest_prime_factor(n):
    if n % 2 == 0:
        return 2
    f = 3
    while f * f <= n:
        if n % f == 0:
            return f
        f += 2
    return n


def prime_factors(n):
    fs = set()
    while n > 1:
        p = smallest_prime_factor(n)
        fs.add(p)
        while n % p == 0:
            n //= p
    return fs


def covers_all(congs):
    """Exact check that the congruence classes cover Z.

    Depth-first refinement: maintain the current class (r mod m) together
    with the congruences still compatible with it.  If some congruence with
    n | m contains the whole class, the branch is covered.  Otherwise refine
    by a prime p for which some compatible modulus has higher p-valuation
    than m.  Returns True iff every branch closes.  Iterative stack to avoid
    recursion limits.
    """
    stack = [(0, 1, congs)]
    while stack:
        r, m, cs = stack.pop()
        done = False
        for a, n in cs:
            if m % n == 0 and (r - a) % n == 0:
                done = True
                break
        if done:
            continue
        # choose refinement prime: prime p with val_p(n) > val_p(m) for some compatible n
        p = None
        for a, n in cs:
            g = n
            # strip common part with m
            for q in prime_factors(n):
                vn = 0
                t = n
                while t % q == 0:
                    t //= q
                    vn += 1
                vm = 0
                t = m
                while t % q == 0:
                    t //= q
                    vm += 1
                if vn > vm:
                    p = q
                    break
            if p is not None:
                break
        if p is None:
            # no congruence can further constrain; branch uncovered
            return False, (r, m)
        mp = m * p
        for i in range(p):
            rr = r + m * i
            sub = []
            for a, n in cs:
                from math import gcd
                g = gcd(n, mp)
                if (a - rr) % g == 0:
                    sub.append((a, n))
            if not sub:
                return False, (rr, mp)
            stack.append((rr, mp, sub))
    return True, None


def main():
    if len(sys.argv) < 2:
        print("usage: verify.py witness.json [--minmod M]")
        sys.exit(2)
    with open(sys.argv[1]) as f:
        w = json.load(f)
    minmod = w.get("minmod")
    if "--minmod" in sys.argv:
        minmod = int(sys.argv[sys.argv.index("--minmod") + 1])
    congs = [(int(a), int(n)) for a, n in w["congruences"]]

    # Check 1: moduli sizes
    for a, n in congs:
        if n <= 1:
            print("FAIL: modulus <= 1:", n)
            sys.exit(1)
        if minmod is not None and n < minmod:
            print("FAIL: modulus %d < minmod %d" % (n, minmod))
            sys.exit(1)

    # Check 2: distinctness
    mods = [n for _, n in congs]
    if len(set(mods)) != len(mods):
        seen, dup = set(), None
        for n in mods:
            if n in seen:
                dup = n
                break
            seen.add(n)
        print("FAIL: duplicate modulus", dup)
        sys.exit(1)

    # Check 3a: random sampling sanity check
    rng = random.Random(12345)
    for _ in range(20000):
        x = rng.randrange(-10**30, 10**30)
        if not any((x - a) % n == 0 for a, n in congs):
            print("FAIL: integer not covered (sampling):", x)
            sys.exit(1)

    # Check 3b: exact CRT-structured covering check
    ok, hole = covers_all(congs)
    if not ok:
        print("FAIL: uncovered class %d (mod %d)" % hole)
        sys.exit(1)

    print("PASS: %d congruences, distinct moduli, min modulus = %d >= %s, cover Z"
          % (len(congs), min(mods), minmod))


if __name__ == "__main__":
    main()
