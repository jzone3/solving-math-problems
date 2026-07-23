#!/usr/bin/env python3
"""Cyclic (translate-invariant) construction search for Tuscan-2 squares.

If b = (b_0,...,b_{n-1}) is a permutation of Z_n such that
  - the n-1 consecutive differences b_{c+1}-b_c (mod n) are all distinct, and
  - the n-2 distance-2 differences b_{c+2}-b_c (mod n) are all distinct,
then the n rows  row_i(c) = b_c + i (mod n), i = 0..n-1, form a Tuscan-2
square of order n:
  * d1 pairs: pair (x, x+d) arises exactly from the unique c with
    b_{c+1}-b_c = d and the unique translate i = x - b_c; the n-1 distinct
    d classes x n translates = n(n-1) pairs each exactly once.
  * d2 pairs: same argument per distinct d2 difference class, each ordered
    pair at distance 2 occurs at most (exactly) once.

Search: DFS over permutations with b_0 = 0 (WLOG by translation), pruning
on repeated d1/d2 differences.  Space is tiny for n <= 13.
"""
import sys


def search(n, find_all=False):
    sols = []
    b = [0] * n
    used = [False] * n
    used[0] = True
    d1 = [False] * n   # difference classes used (index = diff mod n)
    d2 = [False] * n

    def rec(pos):
        if pos == n:
            sols.append(b[:])
            return not find_all
        prev = b[pos - 1]
        pprev = b[pos - 2] if pos >= 2 else None
        for v in range(n):
            if used[v]:
                continue
            e1 = (v - prev) % n
            if d1[e1]:
                continue
            if pprev is not None:
                e2 = (v - pprev) % n
                if d2[e2] or e2 == 0:
                    continue
            used[v] = True
            d1[e1] = True
            if pprev is not None:
                d2[e2] = True
            b[pos] = v
            if rec(pos + 1):
                return True
            used[v] = False
            d1[e1] = False
            if pprev is not None:
                d2[e2] = False
        return False

    rec(1)
    return sols


def main():
    n = int(sys.argv[1])
    find_all = len(sys.argv) > 2 and sys.argv[2] == "all"
    sols = search(n, find_all)
    if not sols:
        print(f"no cyclic base row for n={n}")
        return 1
    b = sols[0]
    print(f"base row: {b}" + (f"   ({len(sols)} total)" if find_all else ""))
    for i in range(n):
        print(" ".join(str((x + i) % n) for x in b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
