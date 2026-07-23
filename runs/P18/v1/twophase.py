#!/usr/bin/env python3
"""
P18 (Erdos #273) two-phase parity-decomposed search.

Every admissible modulus n = p-1 (p >= 5) is even, so each congruence covers a
single parity class. Substituting x = 2y+1 / x = 2y, a covering system for #273
is EXACTLY a pair of disjoint subsets S_odd, S_even of M = {m >= 2 : 2m+1 prime}
such that each subset carries a distinct-moduli covering of Z (moduli m = n/2,
n = 2m, p = 2m+1). Congruence lift: family covering the odds contributes
(2b+1) mod 2m for b mod m; family covering the evens contributes 2b mod 2m.

Phase B: cover Z/NB with distinct moduli from M \ {2} (the family that lacks the
cheap modulus 2). Phase A: cover Z/NA with modulus 2 plus leftovers of M.
Both phases use the max-gain greedy + backtracking of finite_cover_p18.py.

Usage: twophase.py NB NA [time_limit_each] [branch]
On success writes witness_twophase.json (original n-space congruences),
verify with solutions/P18/verify.py.
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


def m_admissible(N, banned=()):
    return [d for d in divisors(N)
            if d >= 2 and is_prime(2 * d + 1) and d not in banned]


def search(N, mods, time_limit=300, branch=3):
    """Cover Z/N with distinct moduli from mods (each m | N). Returns list of
    (a, m) or None."""
    mods = sorted(mods)
    if sum(Fraction(1, d) for d in mods) < 1:
        return None, "infeasible (mass=%.4f)" % float(
            sum(Fraction(1, d) for d in mods))
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
    NB = int(sys.argv[1])
    NA = int(sys.argv[2])
    tl = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    br = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    modsB = m_admissible(NB, banned=(2,))
    print("phase B: NB=%d |mods|=%d mass=%.4f" % (
        NB, len(modsB), float(sum(Fraction(1, d) for d in modsB))), flush=True)
    resB, msg = search(NB, modsB, time_limit=tl, branch=br)
    print("phase B: %s" % msg, flush=True)
    if not resB:
        return
    usedB = {n for _, n in resB}
    modsA = [m for m in m_admissible(NA) if m not in usedB]
    print("phase A: NA=%d |mods|=%d mass=%.4f" % (
        NA, len(modsA), float(sum(Fraction(1, d) for d in modsA))), flush=True)
    resA, msg = search(NA, modsA, time_limit=tl, branch=br)
    print("phase A: %s" % msg, flush=True)
    if not resA:
        return
    # lift to n-space: family B covers the odds (x = 2y+1), A covers the evens
    congs = [((2 * b + 1) % (2 * m), 2 * m) for b, m in resB]
    congs += [((2 * b) % (2 * m), 2 * m) for b, m in resA]
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "witness_twophase.json")
    json.dump({"congruences": [[a, n] for a, n in congs],
               "NB": NB, "NA": NA}, open(fn, "w"))
    print("SUCCESS: %d congruences -> %s" % (len(congs), fn))


if __name__ == "__main__":
    main()
