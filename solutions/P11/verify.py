#!/usr/bin/env python3
"""Standalone verifier for circulant weighing matrix witnesses CW(n,k).

A witness is a ternary vector a of length n (entries in {-1,0,1}).
It is valid iff weight(a) = k and all periodic autocorrelations
PAF_s(a) = sum_i a[i]*a[(i+s)%n] are 0 for s = 1..n-1.
(This is equivalent to the n x n circulant matrix W with first row a
satisfying W W^T = k I.)

Usage: python3 verify.py            # verifies all witnesses in WITNESSES below
       python3 verify.py file.json  # file: {"n":..,"k":..,"row":[...]}
No dependencies beyond the standard library.
"""
import json, sys

# Fill in as witnesses are found: list of (n, k, first_row)
# CW(96,36), PROPER (support not contained in any coset of a proper subgroup).
# Constructed via Schmidt & Smith, JCTA 120 (2013) 275-287, Theorem 6.8 with
# gamma=6 (order 16), alpha=32 (order 3), i=1, c=1, d=3 (condition (i)).
# The La Jolla table lists CW(96,6) as Open, but Corollary 6.9 of that paper
# states proper CW(v,36) exist for ALL v = 0 mod 48; this is an explicit one.
WITNESSES = [
    (96, 36, [-1, 0, 0, 1, 0, -1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, -1,
              0, -1, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 1, 1, 0, 1, 0, 0, 0, 0,
              1, 0, -1, 0, 0, 1, 0, 0, -1, 0, 0, -1, 0, 1, 1, 0, 1, 0, 0, 0,
              0, 0, 0, 0, 1, -1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0,
              1, -1, 0, -1, 0, 0, 0, 0, 1, 0, -1, 0, 0, -1, 0, 0]),
]


def check(n, k, a):
    assert len(a) == n, f"length {len(a)} != n={n}"
    assert all(v in (-1, 0, 1) for v in a), "entries must be ternary"
    w = sum(v * v for v in a)
    assert w == k, f"weight {w} != k={k}"
    for s in range(1, n):
        paf = sum(a[i] * a[(i + s) % n] for i in range(n))
        assert paf == 0, f"PAF at shift {s} is {paf}, not 0"


def check_proper(n, a):
    """Proper: support not contained in a coset of Z_t for any proper t|n.
    It suffices to check subgroups of prime index p|n (index-p subgroup is
    the multiples of p; cosets are residue classes mod p)."""
    sup = [i for i in range(n) if a[i]]
    p = 2
    m = n
    primes = set()
    while m > 1:
        while m % p == 0:
            primes.add(p)
            m //= p
        p += 1
    for p in sorted(primes):
        classes = {i % p for i in sup}
        assert len(classes) > 1, f"support inside one residue class mod {p} (improper)"


def main():
    items = list(WITNESSES)
    if len(sys.argv) > 1:
        d = json.load(open(sys.argv[1]))
        items.append((d["n"], d["k"], d["row"]))
    if not items:
        print("NO WITNESSES TO CHECK (none found yet)")
        return
    for n, k, a in items:
        check(n, k, a)
        check_proper(n, a)
        print(f"CW({n},{k}): PASS (proper)")
    print("PASS")


if __name__ == "__main__":
    main()
