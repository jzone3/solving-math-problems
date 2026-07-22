#!/usr/bin/env python3
"""Independent verifier for a Tuscan-2 square T2(n).

A T2(n) is an n x n array, each row a permutation of {0,...,n-1}, such that:
  - every ordered pair (a,b), a != b, appears with b immediately right of a
    in EXACTLY one row (distance-1 condition);
  - every ordered pair (a,b), a != b, appears with b two positions right of a
    in AT MOST one row (distance-2 condition).

Usage: python3 verify.py <witness-file>
Witness file: n lines, each with n whitespace-separated integers in 0..n-1.
Prints PASS on success, FAIL <reason> otherwise. No dependencies.
"""
import sys


def verify(array):
    n = len(array)
    for r in array:
        if len(r) != n:
            return "row length != n"
        if sorted(r) != list(range(n)):
            return "row is not a permutation of 0..n-1"
    occ1 = {}
    occ2 = {}
    for ri, r in enumerate(array):
        for i in range(n - 1):
            p = (r[i], r[i + 1])
            if p in occ1:
                return f"dist-1 pair {p} repeated (rows {occ1[p]} and {ri})"
            occ1[p] = ri
        for i in range(n - 2):
            p = (r[i], r[i + 2])
            if p in occ2:
                return f"dist-2 pair {p} repeated (rows {occ2[p]} and {ri})"
            occ2[p] = ri
    # exactly-once for distance 1: n(n-1) slots must cover all n(n-1) ordered pairs
    if len(occ1) != n * (n - 1):
        return "not all ordered pairs covered at distance 1"
    return None


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py <witness-file>")
        sys.exit(2)
    with open(sys.argv[1]) as f:
        array = [[int(x) for x in line.split()] for line in f if line.strip()]
    err = verify(array)
    if err:
        print("FAIL:", err)
        sys.exit(1)
    print(f"PASS: valid T2({len(array)})")


if __name__ == "__main__":
    main()
