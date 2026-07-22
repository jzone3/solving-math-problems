#!/usr/bin/env python3
"""Standalone verifier for Tuscan-2 squares T2(n).

Usage: python3 verify.py <file>
File format: n lines, each with n space-separated integers in 0..n-1 (one row each).
Checks (Golomb-Taylor 1985 / CPro1 problem_def.py definition):
  1. each row is a permutation of {0..n-1};
  2. every ordered pair (a,b), a!=b, appears with b directly right of a in EXACTLY one row;
  3. every ordered pair appears with b two positions right of a in AT MOST one row.
Prints PASS or FAIL. No dependencies.
"""
import sys

def main():
    rows = []
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("SOLUTION"):
                continue
            rows.append([int(x) for x in line.split()])
    n = len(rows)
    assert n >= 2, "need at least a 2x2 array"
    ok = True
    for r in rows:
        if len(r) != n or sorted(r) != list(range(n)):
            print(f"FAIL: row {r} is not a permutation of 0..{n-1}")
            ok = False
    c1 = {}
    c2 = {}
    for r in rows:
        for j in range(n - 1):
            c1[(r[j], r[j+1])] = c1.get((r[j], r[j+1]), 0) + 1
        for j in range(n - 2):
            c2[(r[j], r[j+2])] = c2.get((r[j], r[j+2]), 0) + 1
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            if c1.get((a, b), 0) != 1:
                print(f"FAIL: pair ({a},{b}) at distance 1 occurs {c1.get((a,b),0)} times (need exactly 1)")
                ok = False
            if c2.get((a, b), 0) > 1:
                print(f"FAIL: pair ({a},{b}) at distance 2 occurs {c2.get((a,b),0)} times (max 1)")
                ok = False
    print("PASS" if ok else "FAIL", f"(n={n})")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
