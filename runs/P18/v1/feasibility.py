#!/usr/bin/env python3
"""
P18 (Erdos #273) feasibility scan: for candidate smooth lcm targets N, list the
admissible moduli (d | N, d >= 4, d+1 prime -- so d = p-1 with p >= 5) and the
exact reciprocal mass sum 1/d, overall and per parity layer.

Structure note: every admissible modulus is even (p >= 5 odd => p-1 even), so a
congruence a mod n covers integers of a single parity. Covering the odds (resp.
evens) is, after x = 2y+1 (resp. x = 2y), a covering of Z by moduli m = n/2 with
2m+1 prime. Hence a covering system exists iff the set M = {m : 2m+1 prime, m>=2}
contains two disjoint subsets each of which carries a distinct-moduli covering of
Z. Per family the reciprocal budget must exceed 1, so total mass must exceed 2 in
m-terms (equivalently 1 in n-terms), with combinatorial excess on top.
"""
import sys
from fractions import Fraction


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def divisors(n):
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


def admissible(N):
    return [d for d in divisors(N) if d >= 4 and is_prime(d + 1)]


def scan(Ns):
    for N in Ns:
        D = admissible(N)
        s = sum(Fraction(1, d) for d in D)
        # m-space mass (per-parity budget): sum 1/(d/2) = 2*s
        print("N=%-10d |D|=%-3d  sum 1/d = %s ~ %.4f   m-mass=%.4f"
              % (N, len(D), s, float(s), 2 * float(s)))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        scan(int(a) for a in sys.argv[1:])
    else:
        scan([360, 2520, 55440, 720720, 1441440, 2162160, 4324320,
              5405400, 6486480, 10810800, 21621600, 43243200])
