"""Structured scan of the N* reduction (dev_max(d) <= LB(d), antitone
transportation lower bound on R) over ALL degree sequences with at most
2 or 3 distinct values:  d = a^p b^q (c^r), a > b (> c) >= 1.

Graphicality via Erdos-Gallai. Block LB computed by the antitone coupling on
endpoint classes in O(#classes). Covers K_k, stars, CS(a,b), double hubs,
near-regular etc., with n' up to ~6000.

Usage: python3 nstar_blocks.py <mode2|mode3> <gridmax>
"""

import sys
import math
from itertools import product

GRID = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13, 17, 22, 29, 38, 50, 66, 87, 115,
        152, 200, 400, 800, 1600, 3000]


def eg_ok(vals, cnts):
    # Erdos-Gallai for multiset given as (value,count) desc by value
    d = []
    for v, c in zip(vals, cnts):
        d.extend([v] * min(c, 100000))
    if sum(v * c for v, c in zip(vals, cnts)) % 2:
        return False
    n = sum(cnts)
    if vals[0] > n - 1:
        return False
    # standard EG on the expanded list is too slow for huge counts;
    # use the compressed check only up to k = number of distinct prefix
    # breakpoints (EG needs only k at "corner" points).
    pre = 0
    seen = 0
    for bi, (v, c) in enumerate(zip(vals, cnts)):
        for k in (seen + 1, seen + c):
            if k < 1 or k > n:
                continue
            # sum of k largest
            s, rem = 0, k
            for vv, cc in zip(vals, cnts):
                t = min(rem, cc)
                s += vv * t
                rem -= t
                if rem == 0:
                    break
            rhs = k * (k - 1)
            for vv, cc in zip(vals, cnts):
                # vertices beyond the first k
                pass
            # count min(d_j, k) over j > k
            tot, skip = 0, k
            for vv, cc in zip(vals, cnts):
                if skip >= cc:
                    skip -= cc
                    continue
                use = cc - skip
                skip = 0
                tot += use * min(vv, k)
            rhs += tot
            if s > rhs:
                return False
        seen += c
    return True


def lb_randic(vals, cnts):
    """Antitone coupling: sort the 2m endpoints; pair i-th smallest with
    i-th largest. Lower half L (m smallest, ascending) pairs against upper
    half U (m largest, descending), elementwise. O(#classes)."""
    ep_asc = [(v, v * c) for v, c in zip(reversed(vals), reversed(cnts))]
    m2 = sum(e for _, e in ep_asc)
    m = m2 // 2
    # build L = first m endpoints ascending (class, count) and
    # U = last m endpoints, traversed descending
    L, rem = [], m
    for v, e in ep_asc:
        t = min(rem, e)
        if t > 0:
            L.append((v, t))
            rem -= t
    U, rem = [], m
    for v, e in reversed(ep_asc):
        t = min(rem, e)
        if t > 0:
            U.append((v, t))
            rem -= t
    total = 0.0
    i = j = 0
    li = L[0][1] if L else 0
    uj = U[0][1] if U else 0
    while i < len(L) and j < len(U):
        take = min(li, uj)
        total += take / math.sqrt(L[i][0] * U[j][0])
        li -= take
        uj -= take
        if li == 0:
            i += 1
            li = L[i][1] if i < len(L) else 0
        if uj == 0:
            j += 1
            uj = U[j][1] if j < len(U) else 0
    return total


def dev_max(vals, cnts):
    nprime = sum(cnts)
    m = sum(v * c for v, c in zip(vals, cnts)) / 2
    M1 = sum(v * v * c for v, c in zip(vals, cnts))
    q = M1 + 2 * m
    best = 0.0
    cands = {nprime}
    nstar = 8 * m * m / q
    for nn in (int(nstar), int(nstar) + 1):
        if nn >= nprime:
            cands.add(nn)
    for nn in cands:
        dev2 = q / nn - 4 * m * m / (nn * nn)
        best = max(best, dev2)
    return math.sqrt(best)


def main():
    mode, gridmax = sys.argv[1], int(sys.argv[2])
    grid = [g for g in GRID if g <= gridmax]
    top = []
    tried = 0
    kk = 2 if mode == "mode2" else 3
    for vals in product(grid, repeat=kk):
        if any(vals[i] <= vals[i + 1] for i in range(kk - 1)):
            continue
        for cnts in product(grid, repeat=kk):
            if not eg_ok(list(vals), list(cnts)):
                continue
            tried += 1
            s = dev_max(vals, cnts) - lb_randic(vals, cnts)
            top.append((s, vals, cnts))
            if len(top) > 20000:
                top.sort(reverse=True)
                del top[5:]
    top.sort(reverse=True)
    print(f"{mode} gridmax={gridmax}: graphical class-sequences tried={tried}")
    for s, v, c in top[:5]:
        print(f"  {s:+.8f}  degrees={v} counts={c} n'={sum(c)}"
              + ("  VIOLATION-CANDIDATE" if s > 1e-9 else ""))


if __name__ == "__main__":
    main()
