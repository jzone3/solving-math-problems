#!/usr/bin/env python3
"""Standalone verifier for Tuscan-2 squares T2(n).

Definition (Golomb-Taylor 1985, Ars Combin. 20B; CPro1
tuscan-2-square/problem_def.py): an n x n array, each row a permutation of
{0..n-1}, such that every ordered pair (a,b) of distinct symbols appears with
b directly right of a in at most one row (for an n-row square, counting makes
this exactly one), and with b two positions right of a in at most one row.

Usage: verify.py <file>
  <file>: n lines of n space-separated integers (0-based symbols). Blank
  lines and lines starting with '#' are ignored. Prints PASS or FAIL.
"""
import sys


def verify(array):
    n = len(array)
    if n == 0:
        return False, "empty"
    occur1 = set()
    occur2 = set()
    dist1_count = 0
    for r in array:
        if len(r) != n:
            return False, "row length != n"
        if sorted(r) != list(range(n)):
            return False, "row not a permutation of 0..n-1"
        for i in range(n - 1):
            p = (r[i], r[i + 1])
            if p in occur1:
                return False, f"dist-1 pair {p} repeated"
            occur1.add(p)
            dist1_count += 1
            if i < n - 2:
                q = (r[i], r[i + 2])
                if q in occur2:
                    return False, f"dist-2 pair {q} repeated"
                occur2.add(q)
    # n rows x (n-1) adjacencies = n(n-1) distinct pairs = all ordered pairs:
    # "exactly one row" for dist 1 is implied, but check explicitly anyway.
    if dist1_count != n * (n - 1):
        return False, "dist-1 pair count mismatch"
    if len(occur1) != n * (n - 1):
        return False, "not every ordered pair at dist 1"
    return True, "ok"


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py <file>")
        sys.exit(2)
    rows = []
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            rows.append([int(t) for t in line.split()])
    ok, msg = verify(rows)
    print(("PASS" if ok else "FAIL") + f" ({msg}) n={len(rows)}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()


