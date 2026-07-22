#!/usr/bin/env python3
"""Independent verifier for Tuscan-2 squares T2(n).

Definition (Golomb-Taylor 1985; CPro1 tuscan-2-square/problem_def.py):
An n x n array, each row a permutation of {0,...,n-1}, such that for any
ordered pair of distinct symbols (a,b):
  - b appears immediately (1 step) to the right of a in EXACTLY one row
    (n rows x (n-1) adjacencies = n(n-1) ordered pairs, so at-most-once
     at distance 1 is equivalent to exactly-once), and
  - b appears 2 steps to the right of a in AT MOST one row.

Usage: verify.py <witness-file> ; witness = n lines of n space-separated ints.
Prints PASS or FAIL.
"""
import sys


def check(array):
    n = len(array)
    if n == 0:
        return False, "empty"
    occ1 = {}
    occ2 = {}
    for ri, r in enumerate(array):
        if len(r) != n:
            return False, f"row {ri} wrong length"
        if sorted(r) != list(range(n)):
            return False, f"row {ri} not a permutation of 0..{n-1}"
        for i in range(n - 1):
            p = (r[i], r[i + 1])
            if p in occ1:
                return False, f"distance-1 pair {p} repeated (rows {occ1[p]},{ri})"
            occ1[p] = ri
        for i in range(n - 2):
            p = (r[i], r[i + 2])
            if p in occ2:
                return False, f"distance-2 pair {p} repeated (rows {occ2[p]},{ri})"
            occ2[p] = ri
    if len(occ1) != n * (n - 1):
        return False, "distance-1 pairs not all covered"
    return True, "ok"


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py <witness-file>")
        sys.exit(2)
    with open(sys.argv[1]) as f:
        array = [[int(x) for x in line.split()] for line in f if line.strip()]
    ok, msg = check(array)
    print("PASS" if ok else f"FAIL: {msg}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
