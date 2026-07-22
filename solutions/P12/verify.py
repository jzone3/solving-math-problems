"""Independent verifier for a claimed Tuscan-2 square T2(n).

Standalone, stdlib only. Reads an n x n array (whitespace-separated ints,
one row per line) from the file given as argv[1] and checks, per
Golomb-Taylor 1985 / Handbook of Combinatorial Designs VI.62:
  1. each row is a permutation of {0..n-1};
  2. every ordered pair (a,b), a != b, appears with b directly right of a
     in EXACTLY one row;
  3. every ordered pair appears with b two positions right of a in AT MOST
     one row.
Prints PASS or FAIL with a reason.
"""
import sys


def main():
    rows = []
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append([int(t) for t in line.split()])
    n = len(rows)
    syms = set(range(n))
    for i, r in enumerate(rows):
        if len(r) != n or set(r) != syms:
            print(f"FAIL: row {i} is not a permutation of 0..{n-1}")
            return 1
    d1 = {}
    d2 = {}
    for i, r in enumerate(rows):
        for c in range(n - 1):
            p = (r[c], r[c + 1])
            if p in d1:
                print(f"FAIL: distance-1 pair {p} in rows {d1[p]} and {i}")
                return 1
            d1[p] = i
        for c in range(n - 2):
            p = (r[c], r[c + 2])
            if p in d2:
                print(f"FAIL: distance-2 pair {p} in rows {d2[p]} and {i}")
                return 1
            d2[p] = i
    if len(d1) != n * (n - 1):
        missing = [(a, b) for a in range(n) for b in range(n)
                   if a != b and (a, b) not in d1][:5]
        print(f"FAIL: only {len(d1)}/{n*(n-1)} distance-1 pairs; missing e.g. {missing}")
        return 1
    print(f"PASS: valid T2({n})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
