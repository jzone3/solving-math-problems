#!/usr/bin/env python3
"""
Complete element-branching DFS for phase B: cover Z/N with distinct moduli
from (M \ {2}) cap divisors(N).

Branching rule: pick the first uncovered residue r; every unused modulus m
gives exactly one candidate congruence (r mod m, m). Try them in decreasing
order of new-coverage gain. Exact Fraction mass prune. Complete: "exhausted"
is a definitive negative for the pool.

Usage: phaseB_dfs.py N [time_limit_s] [ban2=1]
"""
import json
import sys
import time
from fractions import Fraction

import numpy as np

from twophase import is_prime, divisors, m_admissible


def solve(N, mods, time_limit):
    unc = np.ones(N, dtype=bool)
    cnt = [N]
    chosen = []
    unused = sorted(mods)
    t0 = time.time()
    nodes = [0]
    recip = {m: Fraction(1, m) for m in unused}

    def rec(budget):
        nodes[0] += 1
        if cnt[0] == 0:
            return True
        if time.time() - t0 > time_limit:
            raise TimeoutError
        if budget < Fraction(cnt[0], N):
            return False
        r = int(np.argmax(unc))  # first uncovered residue
        cands = []
        for m in list(unused):
            a = r % m
            idx = np.arange(a, N, m)
            gain = int(unc[idx].sum())
            cands.append((-gain, m, a, idx))
        cands.sort()
        for negg, m, a, idx in cands:
            mask = unc[idx]
            hit = idx[mask]
            unc[hit] = False
            cnt[0] -= len(hit)
            chosen.append((a, m))
            unused.remove(m)
            if rec(budget - recip[m]):
                return True
            unused.append(m)
            unused.sort()
            chosen.pop()
            unc[hit] = True
            cnt[0] += len(hit)
        return False

    budget = sum(recip.values())
    try:
        ok = rec(budget)
    except TimeoutError:
        return None, "timeout nodes=%d" % nodes[0]
    return (chosen if ok else None), (
        "nodes=%d time=%.1fs" % (nodes[0], time.time() - t0)
        if ok else "exhausted nodes=%d time=%.1fs" % (nodes[0], time.time() - t0))


def main():
    N = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0
    ban2 = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    mods = m_admissible(N, banned=(2,) if ban2 else ())
    mass = sum(Fraction(1, m) for m in mods)
    print("N=%d |mods|=%d mass=%.4f" % (N, len(mods), float(mass)), flush=True)
    if mass < 1:
        print("infeasible by density", flush=True)
        return
    res, msg = solve(N, mods, tl)
    print(msg, flush=True)
    if res:
        fn = "phaseB_dfs_N%d.json" % N
        json.dump({"N": N, "family": [[a, m] for a, m in res]}, open(fn, "w"))
        print("PHASE-B SUCCESS N=%d congs=%d -> %s" % (N, len(res), fn))


if __name__ == "__main__":
    main()
