#!/usr/bin/env python3
"""Machine checks for the lemmas used in NOTES.md (C4/C6). Prints PASS/FAIL per check.

1. Z_n has no sequencing for odd n in {5,7,9,11,13}: a sequencing is an ordering
   a_1..a_n of all elements of Z_n whose partial sums are all distinct (equivalently, a row
   whose consecutive differences hit every nonzero residue exactly once exists iff a directed
   terrace exists iff Z_n sequenceable). We check directly: no permutation r of Z_n has all
   n-1 consecutive differences distinct and nonzero covering Z_n \\ {0}. WLOG r[0]=0.
2. For odd n, an M-fixed row (r[j]+r[n-1-j]=n-1) contains no self-mirror arc (a, n-1-a):
   verified by enumerating all M-fixed permutations for n in {5,7,9}.
"""
import itertools, sys

def check_no_sequencing(n):
    # differences of consecutive elements must be a permutation of 1..n-1 (mod n)
    # DFS over rows starting at 0
    found = [False]
    def dfs(seq, used_sym, used_diff):
        if found[0]:
            return
        if len(seq) == n:
            found[0] = True
            return
        for x in range(n):
            if not used_sym[x]:
                d = (x - seq[-1]) % n
                if not used_diff[d]:
                    used_sym[x] = used_diff[d] = True
                    seq.append(x)
                    dfs(seq, used_sym, used_diff)
                    seq.pop()
                    used_sym[x] = used_diff[d] = False
    us = [False]*n; ud = [False]*n
    us[0] = True
    dfs([0], us, ud)
    return not found[0]

def check_fixed_rows_no_selfmirror(n):
    half = (n-1)//2
    ok = True
    cnt = 0
    others = [x for x in range(n) if x != (n-1)//2]
    for first_half in itertools.permutations(others, half):
        used = set(first_half) | {y for x in first_half for y in ((n-1-x),)}
        if len(used) != 2*half:
            continue
        r = list(first_half) + [(n-1)//2] + [n-1-x for x in reversed(first_half)]
        cnt += 1
        for j in range(n-1):
            if r[j+1] == n-1-r[j]:
                ok = False
    return ok, cnt

def main():
    allok = True
    for n in (5, 7, 9, 11, 13):
        r = check_no_sequencing(n)
        print(("PASS" if r else "FAIL"), f"no sequencing of Z_{n}")
        allok &= r
    for n in (5, 7, 9):
        ok, cnt = check_fixed_rows_no_selfmirror(n)
        print(("PASS" if ok else "FAIL"),
              f"no self-mirror arc in any of {cnt} M-fixed rows, n={n}")
        allok &= ok
    print("ALL PASS" if allok else "SOME FAIL")
    return 0 if allok else 1

if __name__ == "__main__":
    sys.exit(main())
