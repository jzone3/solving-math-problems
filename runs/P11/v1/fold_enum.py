#!/usr/bin/env python3
"""Enumerate folded images of a hypothetical CW(n,k): integer vectors c of
length d (d | n) with |c_j| <= n/d, sum c_j = s (row sum, WLOG +s),
sum c_j^2 = k, and all periodic autocorrelations PAF_t(c) = 0, t=1..d-1.

Usage: python3 fold_enum.py n k d      # prints one vector per line
"""
import math, sys


def paf_ok(c, d):
    for t in range(1, d // 2 + 1):
        if sum(c[i] * c[(i + t) % d] for i in range(d)) != 0:
            return False
    return True


def enumerate_folds(n, k, d):
    s = math.isqrt(k)
    B = n // d
    out = []
    c = [0] * d

    def rec(j, rsum, rsq):
        # c[j..d-1] must give sum rsum, squares rsq
        rem = d - j
        if rem == 0:
            if rsum == 0 and rsq == 0 and paf_ok(c, d):
                out.append(list(c))
            return
        # bounds
        if abs(rsum) > rem * B or rsq > rem * B * B or rsq < 0:
            return
        # each |c| <= B and c^2 <= rsq -> |c| <= sqrt(rsq)
        lim = min(B, math.isqrt(rsq))
        for v in range(-lim, lim + 1):
            c[j] = v
            rec(j + 1, rsum - v, rsq - v * v)
        c[j] = 0

    rec(0, s, k)
    return out


if __name__ == "__main__":
    n, k, d = map(int, sys.argv[1:4])
    sols = enumerate_folds(n, k, d)
    for c in sols:
        print(",".join(map(str, c)))
    print(f"# {len(sols)} folded solutions for n={n} k={k} d={d}", file=sys.stderr)
