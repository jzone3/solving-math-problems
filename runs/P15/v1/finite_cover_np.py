#!/usr/bin/env python3
"""
Numpy-accelerated exact finite-LCM covering search (P15 V1, frontier push).

Same algorithm as finite_cover.py (max-gain-density greedy + chronological
backtracking + reciprocal-sum prune) but with numpy residue counting, a
branching-width parameter, and a driver that scans candidate LCMs N.

Usage: finite_cover_np.py M [time_per_N] [branch]
Writes /tmp/fcnp_M{M}.json on success (verify with solutions/P15/verify.py).
"""
import json
import sys
import time
from fractions import Fraction

import numpy as np


def divisors(n):
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


def search(M, N, time_limit=120, branch=3, verbose=False):
    mods = [d for d in divisors(N) if d >= M and d > 1]
    mods.sort()
    if sum(Fraction(1, d) for d in mods) < 1:
        return None, "infeasible"
    unc = np.ones(N, dtype=bool)
    cnt = [N]
    chosen = []
    unused = mods[:]
    t0 = time.time()
    nodes = [0]

    def counts_for(n):
        return unc.reshape(N // n, n).sum(axis=0)

    def best_mod():
        best = None
        for n in unused:
            c = counts_for(n)
            a = int(c.argmax())
            g = int(c[a])
            if best is None or g * best[2] > best[0] * n:
                best = (g, a, n)
            if g == N // n:
                return best
        return best

    def rec():
        nodes[0] += 1
        if cnt[0] == 0:
            return True
        if time.time() - t0 > time_limit:
            raise TimeoutError
        if sum(Fraction(1, n) for n in unused) < Fraction(cnt[0], N):
            return False
        got = best_mod()
        if got is None or got[0] == 0:
            return False
        n = got[2]
        c = counts_for(n)
        order = np.argsort(-c)[:branch]
        unused.remove(n)
        for a in order:
            a = int(a)
            if c[a] == 0:
                break
            idx = np.arange(a, N, n)
            mask = unc[idx]
            hit = idx[mask]
            unc[hit] = False
            cnt[0] -= len(hit)
            chosen.append((a, n))
            if rec():
                return True
            chosen.pop()
            unc[hit] = True
            cnt[0] += len(hit)
        unused.append(n)
        unused.sort()
        return False

    try:
        ok = rec()
    except TimeoutError:
        return None, "timeout nodes=%d" % nodes[0]
    if not ok:
        return None, "exhausted nodes=%d" % nodes[0]
    return chosen, "nodes=%d time=%.1fs" % (nodes[0], time.time() - t0)


def candidate_Ns(limit):
    out = set()
    for a in range(3, 10):
        for b in range(1, 6):
            for c in range(0, 4):
                for d in range(0, 3):
                    for e in range(0, 2):
                        for f in range(0, 2):
                            n = 2**a * 3**b * 5**c * 7**d * 11**e * 13**f
                            if n <= limit:
                                out.add(n)
    return sorted(out)


def main():
    M = int(sys.argv[1])
    tl = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    br = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    t0 = time.time()
    for N in candidate_Ns(3 * 10 ** 7):
        mods = [d for d in divisors(N) if d >= M and d > 1]
        r = sum(1.0 / d for d in mods)
        if r < 1.02:
            continue
        res, msg = search(M, N, time_limit=tl, branch=br)
        print("M=%d N=%-9d recip=%.3f %s" % (M, N, r, msg), flush=True)
        if res:
            fn = "/tmp/fcnp_M%d.json" % M
            json.dump({"minmod": M,
                       "congruences": [[int(a), int(n)] for a, n in res]},
                      open(fn, "w"))
            print("SUCCESS M=%d N=%d congs=%d total=%.1fs -> %s"
                  % (M, N, len(res), time.time() - t0, fn))
            return
    print("FAILED M=%d total=%.1fs" % (M, time.time() - t0))


if __name__ == "__main__":
    main()
