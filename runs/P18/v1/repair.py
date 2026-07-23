#!/usr/bin/env python3
"""
Ruin-and-recreate local search for P18 phase B (m-space).

Start from a waste-greedy solution attempt (all moduli placed or budget
dead); then loop: remove a random subset of placed congruences (biased
toward high waste), re-place greedily by minimum waste targeting the first
uncovered residue; keep the new state if the uncovered count does not
increase (with occasional uphill acceptance). Reports best uncovered
fraction; SUCCESS when uncovered = 0.

Usage: repair.py NB NA [seconds] [seed] [ruin_lo] [ruin_hi]
Writes witness_repair.json on success.
"""
import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np

from twophase import is_prime, divisors, m_admissible


def rebuild_unc(N, placed):
    unc = np.ones(N, dtype=bool)
    for a, m in placed:
        unc[a::m] = False
    return unc


def greedy_fill(N, unc, unused, rng, topk=2):
    placed = []
    while True:
        cnt = int(unc.sum())
        if cnt == 0 or not unused:
            return placed, cnt
        r = int(np.argmax(unc))
        moves = []
        for m in unused:
            a = r % m
            g = int(unc[a::m].sum())
            moves.append((1.0 / m - g / N, -g, a, m))
        moves.sort()
        w, negg, a, m = moves[rng.randrange(min(topk, len(moves)))]
        if negg == 0:
            return placed, cnt
        unc[a::m] = False
        unused.remove(m)
        placed.append((a, m))


def phase_lns(N, mods, seconds, rng, ruin_lo, ruin_hi, label):
    t0 = time.time()
    unused = list(mods)
    unc = np.ones(N, dtype=bool)
    placed, left = greedy_fill(N, unc, unused, rng)
    best = left
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        if left == 0:
            print("%s: SUCCESS after %d iterations (%.1fs)"
                  % (label, it, time.time() - t0), flush=True)
            return placed
        k = rng.randint(ruin_lo, min(ruin_hi, len(placed)))
        # bias removal toward high-waste congruences: waste ~ overlap of class
        waste = []
        for i, (a, m) in enumerate(placed):
            waste.append((rng.random() / m, i))  # random, small-m biased
        waste.sort(reverse=True)
        remove_idx = {i for _, i in waste[:k]}
        keep = [c for i, c in enumerate(placed) if i not in remove_idx]
        freed = [placed[i][1] for i in remove_idx]
        unc2 = rebuild_unc(N, keep)
        unused2 = unused + freed
        placed2, left2 = greedy_fill(N, unc2, unused2, rng)
        new_placed = keep + placed2
        if left2 <= left or rng.random() < 0.02:
            placed, left, unused = new_placed, left2, [
                m for m in mods if m not in {mm for _, mm in new_placed}]
            unc = rebuild_unc(N, placed)
        if left < best:
            best = left
            print("%s: it=%d best_left=%.6f (%.1fs)"
                  % (label, it, best / N, time.time() - t0), flush=True)
    print("%s: FAILED best_left=%.6f after %d its (%.1fs)"
          % (label, best / N, it, time.time() - t0), flush=True)
    return None


def main():
    NB = int(sys.argv[1])
    NA = int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 3600.0
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    ruin_lo = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    ruin_hi = int(sys.argv[6]) if len(sys.argv) > 6 else 20
    rng = random.Random(seed)
    modsB = m_admissible(NB, banned=(2,))
    print("phase B: NB=%d |mods|=%d mass=%.4f" % (
        NB, len(modsB), float(sum(Fraction(1, m) for m in modsB))), flush=True)
    resB = phase_lns(NB, modsB, secs, rng, ruin_lo, ruin_hi, "phase B")
    if not resB:
        return
    usedB = {m for _, m in resB}
    modsA = [m for m in m_admissible(NA) if m not in usedB]
    print("phase A: NA=%d |mods|=%d mass=%.4f" % (
        NA, len(modsA), float(sum(Fraction(1, m) for m in modsA))), flush=True)
    resA = phase_lns(NA, modsA, secs, rng, ruin_lo, ruin_hi, "phase A")
    if not resA:
        return
    congs = [((2 * b + 1) % (2 * m), 2 * m) for b, m in resB]
    congs += [((2 * b) % (2 * m), 2 * m) for b, m in resA]
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "witness_repair.json")
    json.dump({"congruences": [[a, n] for a, n in congs]}, open(fn, "w"))
    print("SUCCESS total %d congruences -> %s" % (len(congs), fn))


if __name__ == "__main__":
    main()
