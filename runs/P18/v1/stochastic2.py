#!/usr/bin/env python3
"""
Hole-driven stochastic search for phase B (and phase A) of P18.

Move rule (per step): pick the FIRST uncovered residue r (deterministic focus)
with probability 1-eps, else a random uncovered residue; among unused moduli
the candidate congruence for r is (r mod m, m); score by new-coverage gain
density g/m and pick uniformly among the top-k. Exact Fraction mass prune ends
dead restarts early. Prints progress every `report` restarts.

Usage: stochastic2.py NB NA [seconds] [topk] [eps] [seed]
Writes witness_stoch2.json (n-space) on success.
"""
import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np

from twophase import is_prime, divisors, m_admissible


def one_restart(N, mods, rng, topk, eps):
    unc = np.ones(N, dtype=bool)
    cnt = N
    unused = list(mods)
    chosen = []
    budget = sum(Fraction(1, m) for m in unused)
    while cnt:
        if budget < Fraction(cnt, N):
            return None
        if rng.random() < eps:
            uncovered = np.flatnonzero(unc)
            r = int(uncovered[rng.randrange(len(uncovered))])
        else:
            r = int(np.argmax(unc))
        moves = []
        for m in unused:
            a = r % m
            g = int(unc[a::m].sum())
            moves.append((g * (1.0 / m), g, a, m))
        moves.sort(reverse=True)
        _, g, a, m = moves[rng.randrange(min(topk, len(moves)))]
        if g == 0:
            return None
        unc[a::m] = False
        cnt = int(unc.sum())
        unused.remove(m)
        budget -= Fraction(1, m)
        chosen.append((a, m))
    return chosen


def run_phase(N, mods, seconds, topk, eps, rng, label, report=50):
    t0 = time.time()
    tries = 0
    while time.time() - t0 < seconds:
        tries += 1
        res = one_restart(N, mods, rng, topk, eps)
        if res is not None:
            print("%s: SUCCESS after %d restarts (%.1fs)"
                  % (label, tries, time.time() - t0), flush=True)
            return res
        if tries % report == 0:
            print("%s: %d restarts (%.1fs)" % (label, tries, time.time() - t0),
                  flush=True)
    print("%s: FAILED %d restarts in %.1fs" % (label, tries, time.time() - t0),
          flush=True)
    return None


def main():
    NB = int(sys.argv[1])
    NA = int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0
    topk = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    eps = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    rng = random.Random(seed)
    modsB = m_admissible(NB, banned=(2,))
    print("phase B: NB=%d |mods|=%d mass=%.4f" % (
        NB, len(modsB), float(sum(Fraction(1, m) for m in modsB))), flush=True)
    resB = run_phase(NB, modsB, secs, topk, eps, rng, "phase B")
    if not resB:
        return
    usedB = {m for _, m in resB}
    modsA = [m for m in m_admissible(NA) if m not in usedB]
    print("phase A: NA=%d |mods|=%d mass=%.4f" % (
        NA, len(modsA), float(sum(Fraction(1, m) for m in modsA))), flush=True)
    resA = run_phase(NA, modsA, secs, topk, eps, rng, "phase A")
    if not resA:
        return
    congs = [((2 * b + 1) % (2 * m), 2 * m) for b, m in resB]
    congs += [((2 * b) % (2 * m), 2 * m) for b, m in resA]
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "witness_stoch2.json")
    json.dump({"congruences": [[a, n] for a, n in congs]}, open(fn, "w"))
    print("SUCCESS total %d congruences -> %s" % (len(congs), fn))


if __name__ == "__main__":
    main()
