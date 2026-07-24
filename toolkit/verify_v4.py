#!/usr/bin/env python3
"""Independent verifier for a covering system witness (P15).

Input: a JSON file (argv[1]) with {"congruences": [[a, n], ...]}.
Checks:
  1. All moduli are distinct.
  2. min modulus (reported).
  3. The residue classes a_i mod n_i cover all of Z, verified by a
     CRT-structured recursive split (never materializes lcm).

Prints PASS with the min modulus if it is a covering system, FAIL otherwise.
Standalone, stdlib only.
"""
import json
import sys
sys.setrecursionlimit(100000)


def smallest_prime_factor(n):
    d = 2
    while d * d <= n:
        if n % d == 0:
            return d
        d += 1
    return n


def covers(congs):
    """congs: list of (a, n). Returns True iff union of {x = a mod n} = Z."""
    # any modulus-1 congruence covers everything
    for a, n in congs:
        if n == 1:
            return True
    if not congs:
        return False
    # pick a prime dividing some modulus (choose the modulus list's smallest spf
    # of the first modulus; any prime dividing lcm works)
    p = smallest_prime_factor(congs[0][1])
    ok = True
    for r in range(p):
        sub = []
        for a, n in congs:
            if n % p == 0:
                if a % p == r % p:
                    sub.append((((a - r) // p) % (n // p), n // p))
            else:
                inv = pow(p, -1, n)
                sub.append((((a - r) * inv) % n, n))
        if not covers(sub):
            ok = False
            break
    return ok


def main():
    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)
    congs = [(int(a), int(n)) for a, n in data["congruences"]]
    mods = [n for _, n in congs]
    if len(set(mods)) != len(mods):
        print("FAIL: duplicate moduli")
        sys.exit(1)
    if any(n < 2 for n in mods):
        print("FAIL: modulus < 2 present")
        sys.exit(1)
    if not covers(congs):
        print("FAIL: does not cover Z")
        sys.exit(1)
    print(f"PASS: covering system, {len(congs)} congruences, "
          f"distinct moduli, min modulus = {min(mods)}")


if __name__ == "__main__":
    main()
