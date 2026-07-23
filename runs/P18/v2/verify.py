#!/usr/bin/env python3
"""Exact independent verifier for Erdos #273 (P18).

Accepts a witness file: one congruence per line, "a m" (integers), meaning a (mod m).
Checks, in pure integer arithmetic (no floats anywhere on the accept path):
  1. every modulus m satisfies m > 1, m + 1 is prime (deterministic trial division),
     and m + 1 >= 5;
  2. moduli are pairwise distinct (ErGr80 p.24 convention: 1 < n_1 < ... < n_k);
  3. every integer is covered: every residue class mod L = lcm(m_i) meets some
     congruence (sufficient and necessary since each m_i | L).
Prints PASS iff all checks succeed.

Usage: python3 verify.py witness.txt
"""
import sys
from math import gcd

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True

def main():
    lines = [l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    witness = [(int(a), int(m)) for a, m in lines]
    if not witness:
        print("FAIL: empty witness"); sys.exit(1)
    ms = [m for _, m in witness]
    if len(set(ms)) != len(ms):
        print("FAIL: moduli not distinct"); sys.exit(1)
    for a, m in witness:
        if not (m > 1 and m + 1 >= 5 and is_prime(m + 1)):
            print(f"FAIL: modulus {m} is not p-1 for a prime p >= 5"); sys.exit(1)
    L = 1
    for m in ms:
        L = L * m // gcd(L, m)
    covered = bytearray(L)
    for a, m in witness:
        for x in range(a % m, L, m):
            covered[x] = 1
    if all(covered):
        print(f"PASS: {len(witness)} congruences, distinct moduli of the form p-1 (p prime >= 5), cover Z (period {L})")
    else:
        miss = covered.index(0)
        print(f"FAIL: integer {miss} not covered (mod {L})"); sys.exit(1)

if __name__ == "__main__":
    main()
