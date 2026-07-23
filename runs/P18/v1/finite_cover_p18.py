#!/usr/bin/env python3
"""
P18 (Erdos #273) exact finite-LCM covering search, adapted from P15
runs/P15/v1/finite_cover_np.py.

Searches for a covering of Z/N by congruences a mod d with DISTINCT moduli d,
each d an admissible modulus: d | N, d >= 4, d+1 prime (i.e. d = p-1, p >= 5).
Max-gain-density greedy + chronological backtracking + exact reciprocal-sum
prune (Fraction arithmetic; numpy only for residue counting, never on the
accept path -- any witness is re-verified by solutions/P18/verify.py).

Usage: finite_cover_p18.py N [time_limit_s] [branch]
Writes runs/P18/v1/witness_N{N}.json on success.
"""
import json
import os
import sys
import time
from fractions import Fraction

import numpy as np


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


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


def admissible(N):
    return [d for d in divisors(N) if d >= 4 and is_prime(d + 1)]


def search(N, time_limit=300, branch=3):
    mods = admissible(N)
    if sum(Fraction(1, d) for d in mods) < 1:
        return None, "infeasible (mass<1)"
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


def main():
    N = int(sys.argv[1])
    tl = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    br = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    mods = admissible(N)
    r = sum(Fraction(1, d) for d in mods)
    print("N=%d admissible=%d recip=%.4f" % (N, len(mods), float(r)), flush=True)
    res, msg = search(N, time_limit=tl, branch=br)
    print("N=%d %s" % (N, msg), flush=True)
    if res:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "witness_N%d.json" % N)
        json.dump({"N": N,
                   "congruences": [[int(a), int(n)] for a, n in res]},
                  open(fn, "w"))
        print("SUCCESS N=%d congs=%d -> %s" % (N, len(res), fn))


if __name__ == "__main__":
    main()
