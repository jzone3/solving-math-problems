#!/usr/bin/env python3
"""
Complete decision procedure for cap-bounded Erdős #273:
is there a covering system with distinct moduli from
{n : 4 <= n <= B, n+1 prime} (i.e. all moduli p-1 <= B, p >= 5)?

Element-branching DFS over Z/L (L = lcm of the pool) with exact Fraction
mass prune. "exhausted" = definitive NO for that cap B (complete search).
Published frontier (Shulgin): B = 50, which — like every cap < 70 — is
density-trivial (sum of reciprocals < 1; checked exactly here first).
B = 70 (mass 1.0132) and B = 78 (mass 1.0403) have L = 480,720,240.

Usage: cap_dfs.py B [time_limit_s]
Writes witness_cap_B{B}.json on success (then verify with
solutions/P18/verify.py).
"""
import json
import sys
import time
from fractions import Fraction
from math import lcm

import numpy as np

from twophase import is_prime


def main():
    B = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 86400.0
    pool = [n for n in range(4, B + 1) if is_prime(n + 1)]
    mass = sum(Fraction(1, n) for n in pool)
    L = lcm(*pool)
    print("B=%d pool=%s" % (B, pool), flush=True)
    print("mass=%s (%.6f) L=%d" % (mass, float(mass), L), flush=True)
    if mass < 1:
        print("DENSITY-INFEASIBLE: mass < 1, no covering. Definitive.",
              flush=True)
        return
    unc = np.ones(L, dtype=bool)
    cnt = [L]
    unused = sorted(pool)
    chosen = []
    t0 = time.time()
    nodes = [0]
    recip = {n: Fraction(1, n) for n in pool}

    def rec(budget):
        nodes[0] += 1
        if cnt[0] == 0:
            return True
        if time.time() - t0 > tl:
            raise TimeoutError
        if budget < Fraction(cnt[0], L):
            return False
        r = int(np.argmax(unc))
        cands = []
        for n in list(unused):
            a = r % n
            idx_gain = int(unc[a::n].sum())
            cands.append((-idx_gain, n, a))
        cands.sort()
        for negg, n, a in cands:
            view = unc[a::n]
            mask = view.copy()
            view[:] = False
            k = int(mask.sum())
            cnt[0] -= k
            chosen.append((a, n))
            unused.remove(n)
            if rec(budget - recip[n]):
                return True
            unused.append(n)
            unused.sort()
            chosen.pop()
            unc[a::n][mask] = True
            cnt[0] += k
        return False

    budget = sum(recip.values())
    try:
        ok = rec(budget)
    except TimeoutError:
        print("TIMEOUT (undecided) nodes=%d %.1fs"
              % (nodes[0], time.time() - t0), flush=True)
        return
    if ok:
        fn = "witness_cap_B%d.json" % B
        json.dump({"congruences": [[a, n] for a, n in chosen]}, open(fn, "w"))
        print("SUCCESS!!! %d congruences -> %s" % (len(chosen), fn), flush=True)
    else:
        print("EXHAUSTED: no covering with all moduli p-1 <= %d. "
              "Definitive. nodes=%d %.1fs" % (B, nodes[0], time.time() - t0),
              flush=True)


if __name__ == "__main__":
    main()
