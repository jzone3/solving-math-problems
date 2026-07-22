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
WITNESSES = []


def check(n, k, a):
    assert len(a) == n, f"length {len(a)} != n={n}"
    assert all(v in (-1, 0, 1) for v in a), "entries must be ternary"
    w = sum(v * v for v in a)
    assert w == k, f"weight {w} != k={k}"
    for s in range(1, n):
        paf = sum(a[i] * a[(i + s) % n] for i in range(n))
        assert paf == 0, f"PAF at shift {s} is {paf}, not 0"


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
        print(f"CW({n},{k}): PASS")
    print("PASS")


if __name__ == "__main__":
    main()
