#!/usr/bin/env python3
"""Independent verifier for P15 covering-system witnesses.

Usage: python3 verify.py witness.json
witness.json: {"m": <claimed min modulus>, "cover": [[a, n], ...]}

Checks, with no dependencies beyond the standard library:
  1. all moduli distinct and >= m,
  2. the residue classes a_i mod n_i cover all integers, via a CRT-structured
     recursive check that never materializes Z_lcm: recurse on residues modulo
     one prime at a time; a class survives into branch (r mod p) iff it is
     compatible with it, its modulus losing a factor p when p | n.
Prints PASS or FAIL.
"""
import json, sys
from math import gcd


def prime_factor(n):
    d = 2
    while d * d <= n:
        if n % d == 0:
            return d
        d += 1
    return n


def covers(classes):
    """classes: list of (a, n). True iff union of a mod n covers Z."""
    # any class with n == 1 covers everything
    for a, n in classes:
        if n == 1:
            return True
    if not classes:
        return False
    # pick a prime p dividing the largest modulus (heuristic: most common prime)
    counts = {}
    for _, n in classes:
        p = prime_factor(n)
        counts[p] = counts.get(p, 0) + 1
    p = max(counts, key=counts.get)
    for r in range(p):
        # branch t = r + p*s; class (a, n): if p | n, survives iff a % p == r,
        # becoming (a', n/p) where a' = (a - r)/p * inv ... use direct formula:
        # t ≡ a (mod n)  with t = r + p s  ⇔  p s ≡ a - r (mod n)
        sub = []
        ok = False
        for a, n in classes:
            g = gcd(p, n)
            if g == p:
                if (a - r) % p == 0:
                    m2 = n // p
                    # s ≡ (a - r)/p (mod n/p)
                    sub.append((((a - r) // p) % m2 if m2 > 0 else 0, m2))
            else:
                # gcd(p, n) == 1: solvable for every r; s ≡ (a - r) * p^{-1} (mod n)
                inv = pow(p, -1, n)
                sub.append(((a - r) * inv % n, n))
        if not covers(sub):
            return False
    return True


def main(path):
    data = json.load(open(path))
    m = data["m"]
    cover = [(int(a), int(n)) for a, n in data["cover"]]
    mods = [n for _, n in cover]
    if len(mods) != len(set(mods)):
        print("FAIL: duplicate moduli")
        return 1
    if min(mods) < m or min(mods) < 2:
        print(f"FAIL: min modulus {min(mods)} < claimed {m}")
        return 1
    if not covers(cover):
        print("FAIL: integers not covered")
        return 1
    print(f"PASS: {len(cover)} congruences, distinct moduli, min modulus "
          f"{min(mods)} >= {m}, covers Z")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
