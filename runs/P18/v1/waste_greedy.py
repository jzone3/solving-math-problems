#!/usr/bin/env python3
"""
Waste-greedy stochastic search for P18 phase B / phase A (m-space).

Key move rule (big improvement over gain-density greedy, see NOTES.md):
for the first uncovered residue r, choose among unused moduli the candidate
congruence (r mod m, m) with MINIMUM waste 1/m - g/N (g = fresh coverage),
i.e. hew as close to exact-cover as the pool allows; randomized top-k with
restarts. Exact Fraction budget prune.

Usage: waste_greedy.py NB NA [seconds] [topk] [seed]
Writes witness_wg.json (n-space congruences) on success.
"""
import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np

from twophase import is_prime, divisors, m_admissible


def one_restart(N, mods, rng, topk):
    unc = np.ones(N, dtype=bool)
    cnt = N
    unused = list(mods)
    budget = sum(Fraction(1, m) for m in unused)
    chosen = []
    best_left = 1.0
    while cnt:
        if budget < Fraction(cnt, N):
            return None, cnt
        r = int(np.argmax(unc))
        moves = []
        for m in unused:
            a = r % m
            g = int(unc[a::m].sum())
            moves.append((1.0 / m - g / N, -g, a, m))
        if not moves:
            return None, cnt
        moves.sort()
        w, negg, a, m = moves[rng.randrange(min(topk, len(moves)))]
        if negg == 0:
            return None, cnt
        unc[a::m] = False
        cnt = int(unc.sum())
        unused.remove(m)
        budget -= Fraction(1, m)
        chosen.append((a, m))
    return chosen, 0


def run_phase(N, mods, seconds, topk, rng, label, report=20):
    t0 = time.time()
    tries = 0
    best = 1.0
    while time.time() - t0 < seconds:
        tries += 1
        res, left = one_restart(N, mods, rng, topk)
        if res is not None:
            print("%s: SUCCESS after %d restarts (%.1fs)"
                  % (label, tries, time.time() - t0), flush=True)
            return res
        best = min(best, left / N)
        if tries % report == 0:
            print("%s: %d restarts best_left=%.5f (%.1fs)"
                  % (label, tries, best, time.time() - t0), flush=True)
    print("%s: FAILED %d restarts best_left=%.5f in %.1fs"
          % (label, tries, best, time.time() - t0), flush=True)
    return None


def main():
    NB = int(sys.argv[1])
    NA = int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 3600.0
    topk = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    rng = random.Random(seed)
    modsB = m_admissible(NB, banned=(2,))
    print("phase B: NB=%d |mods|=%d mass=%.4f" % (
        NB, len(modsB), float(sum(Fraction(1, m) for m in modsB))), flush=True)
    resB = run_phase(NB, modsB, secs, topk, rng, "phase B")
    if not resB:
        return
    usedB = {m for _, m in resB}
    modsA = [m for m in m_admissible(NA) if m not in usedB]
    print("phase A: NA=%d |mods|=%d mass=%.4f" % (
        NA, len(modsA), float(sum(Fraction(1, m) for m in modsA))), flush=True)
    resA = run_phase(NA, modsA, secs, topk, rng, "phase A")
    if not resA:
        return
    congs = [((2 * b + 1) % (2 * m), 2 * m) for b, m in resB]
    congs += [((2 * b) % (2 * m), 2 * m) for b, m in resA]
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "witness_wg.json")
    json.dump({"congruences": [[a, n] for a, n in congs]}, open(fn, "w"))
    print("SUCCESS total %d congruences -> %s" % (len(congs), fn))


if __name__ == "__main__":
    main()
