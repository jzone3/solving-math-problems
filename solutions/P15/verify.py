#!/usr/bin/env python3
"""P15 verifier: checks that a finite list of congruences (a_i mod n_i) is a
covering system of Z with distinct moduli and min modulus >= a threshold.

Usage: python3 verify.py <witness_file> [--min-modulus T]

Witness file format: one congruence per line, "a n" (integers, meaning a mod n).
Lines starting with '#' and blank lines are ignored.

The cover check never materializes lcm(n_i); it recursively splits Z along
prime factors of the moduli (CRT tree), pruning congruences incompatible with
the current cell. Standard library only.
Prints PASS on success, FAIL (with a witness uncovered class) otherwise.
"""
import sys
from math import gcd


def smallest_prime_factor(n):
    if n % 2 == 0:
        return 2
    f = 3
    while f * f <= n:
        if n % f == 0:
            return f
        f += 2
    return n


def find_uncovered(congs):
    """Return None if congs cover Z, else (r, m) an uncovered residue class."""
    # cell = (m, r) meaning the class r mod m; congs restricted to compatible ones
    stack = [(1, 0, congs)]
    while stack:
        m, r, cs = stack.pop()
        if not cs:
            return (r, m)
        # if some congruence with n | m matches r, cell is covered
        done = False
        for a, n in cs:
            if m % n == 0 and (r - a) % n == 0:
                done = True
                break
        if done:
            continue
        # choose split prime: a prime p with p | (n/gcd(n,m)) for some modulus n
        p = None
        for a, n in cs:
            q = n // gcd(n, m)
            if q > 1:
                p = smallest_prime_factor(q)
                break
        if p is None:
            # no congruence can further constrain; cell uncovered
            return (r, m)
        mp = m * p
        for k in range(p):
            rr = r + k * m
            sub = []
            for a, n in cs:
                g = gcd(n, mp)
                if (rr - a) % g == 0:
                    sub.append((a, n))
            if not sub:
                return (rr, mp)
            stack.append((mp, rr, sub))
    return None


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: verify.py <witness_file> [--min-modulus T]")
        sys.exit(2)
    path = args[0]
    T = 1
    if "--min-modulus" in args:
        T = int(args[args.index("--min-modulus") + 1])
    congs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            a, n = map(int, line.split())
            congs.append((a % n, n))
    if not congs:
        print("FAIL: empty witness")
        sys.exit(1)
    mods = [n for _, n in congs]
    if len(set(mods)) != len(mods):
        print("FAIL: repeated modulus")
        sys.exit(1)
    if min(mods) < max(T, 2):
        print(f"FAIL: modulus {min(mods)} below threshold {max(T,2)}")
        sys.exit(1)
    bad = find_uncovered(congs)
    if bad is not None:
        r, m = bad
        print(f"FAIL: class {r} mod {m} uncovered")
        sys.exit(1)
    print(f"PASS: {len(congs)} congruences, distinct moduli, "
          f"min modulus {min(mods)} >= {T}, cover Z")


if __name__ == "__main__":
    main()
