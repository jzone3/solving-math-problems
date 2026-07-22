#!/usr/bin/env python3
"""
Fixed-N exact covering search (P15 V1 validation path).

Cover Z_N using residue classes with DISTINCT moduli n | N, n >= M.
Greedy (max new coverage, ties -> largest density i.e. smallest n first)
with chronological backtracking and a measure-based prune:
   remaining uncovered fraction must be <= sum of 1/n over unused moduli.

Usage: finite_cover.py M N [beam]
Writes /tmp/finite_cover_M{M}.json on success.
"""
import json
import sys
import time
from fractions import Fraction


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


def search(M, N, time_limit=600, verbose=True):
    mods = [d for d in divisors(N) if d >= M and d > 1]
    mods.sort()
    total = sum(Fraction(1, d) for d in mods)
    if total < 1:
        return None, "infeasible: sum 1/d = %s < 1" % float(total)
    uncovered = bytearray([1]) * N
    cnt_unc = N

    chosen = []            # (a, n)
    unused = mods[:]       # ascending

    t0 = time.time()
    nodes = [0]

    def best_class():
        """(gain, a, n) maximizing gain; try smallest moduli first, stop early
        if a full class (gain == N/n) is found among the smallest moduli."""
        best = None
        for n in unused:
            per = N // n
            # count coverage for each residue a mod n
            counts = [0] * n
            for x in range(N):
                if uncovered[x]:
                    counts[x % n] += 1
            a = max(range(n), key=lambda i: counts[i])
            g = counts[a]
            if best is None or g * best[2] > best[0] * n:  # compare g/n
                best = (g, a, n)
            if g == per:
                return best
        return best

    def rec():
        nonlocal cnt_unc
        nodes[0] += 1
        if cnt_unc == 0:
            return True
        if time.time() - t0 > time_limit:
            raise TimeoutError
        rem = sum(Fraction(1, n) for n in unused)
        if rem < Fraction(cnt_unc, N):
            return False
        g, a, n = best_class()
        if g == 0:
            return False
        # branch on the top few residues of modulus n
        per = N // n
        counts = [0] * n
        for x in range(N):
            if uncovered[x]:
                counts[x % n] += 1
        order = sorted(range(n), key=lambda i: -counts[i])[:3]
        unused.remove(n)
        for a in order:
            if counts[a] == 0:
                break
            flipped = []
            for x in range(a % n, N, n):
                if uncovered[x]:
                    uncovered[x] = 0
                    flipped.append(x)
            cnt_unc -= len(flipped)
            chosen.append((a, n))
            if rec():
                return True
            chosen.pop()
            for x in flipped:
                uncovered[x] = 1
            cnt_unc += len(flipped)
        unused.append(n)
        unused.sort()
        return False

    try:
        ok = rec()
    except TimeoutError:
        return None, "timeout after %ds, nodes=%d" % (time_limit, nodes[0])
    if not ok:
        return None, "exhausted, nodes=%d" % nodes[0]
    return chosen, "nodes=%d time=%.1fs" % (nodes[0], time.time() - t0)


if __name__ == "__main__":
    M = int(sys.argv[1])
    N = int(sys.argv[2])
    res, msg = search(M, N)
    print("M=%d N=%d: %s" % (M, N, msg))
    if res:
        print("SUCCESS with %d congruences" % len(res))
        fn = "/tmp/finite_cover_M%d.json" % M
        json.dump({"minmod": M, "congruences": [[a, n] for a, n in res]},
                  open(fn, "w"))
        print("wrote", fn)
