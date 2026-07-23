#!/usr/bin/env python3
"""
Independent verifier for P18 (Erdos #273).

Claim format (JSON): {"congruences": [[a_1, n_1], ..., [a_k, n_k]]}

Checks, all in exact integer arithmetic (no floats anywhere):
  1. every modulus n_i satisfies n_i >= 4 and n_i + 1 is prime (so n_i = p-1
     for a prime p >= 5);
  2. moduli are pairwise distinct (strict covering system convention of
     Erdos-Graham 1980 p.24: 1 < n_1 < ... < n_k);
  3. the congruences x = a_i (mod n_i) cover every integer: every residue
     r in {0, ..., L-1}, L = lcm(n_1..n_k), satisfies some congruence.
     Coverage mod lcm is exact and sufficient (each congruence class mod n_i
     is a union of classes mod L, and every integer is some r mod L).

Usage: verify.py witness.json    -> prints PASS or FAIL(reason), exit 0/1.
Stdlib only. The lcm sieve is O(L * k / word) via a bytearray; for the
covering to be checkable L must fit in memory (guarded below).
"""
import json
import sys
from math import gcd


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def fail(msg):
    print("FAIL: %s" % msg)
    sys.exit(1)


def main():
    data = json.load(open(sys.argv[1]))
    congs = [(int(a), int(n)) for a, n in data["congruences"]]
    if not congs:
        fail("empty system")

    # 1. admissible moduli
    for a, n in congs:
        if n < 4:
            fail("modulus %d < 4" % n)
        if not is_prime(n + 1):
            fail("modulus %d: %d not prime" % (n, n + 1))

    # 2. distinct moduli
    mods = [n for _, n in congs]
    if len(set(mods)) != len(mods):
        dup = sorted(m for m in set(mods) if mods.count(m) > 1)
        fail("repeated moduli %s" % dup)

    # 3. exact coverage mod lcm
    L = 1
    for n in mods:
        L = L * n // gcd(L, n)
    if L > 5 * 10 ** 9:
        fail("lcm %d too large for direct sieve; refuse rather than "
             "approximate" % L)
    covered = bytearray(L)
    for a, n in congs:
        covered[a % n::n] = b"\x01" * ((L - a % n + n - 1) // n)
    if covered.count(0):
        r = covered.index(0)
        fail("residue %d mod %d uncovered" % (r, L))

    print("PASS: %d congruences, distinct moduli p-1 (p prime >= 5), "
          "cover Z (checked exactly mod lcm=%d)" % (len(congs), L))


if __name__ == "__main__":
    main()
