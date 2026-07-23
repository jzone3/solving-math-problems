#!/usr/bin/env python3
"""
Beam search with the min-waste move rule for P18 phase B / A (m-space).

State: (covered bitmap, unused moduli, exact budget). Expansion: for the
first uncovered residue r, the E least-waste candidate congruences
(r mod m, m). Keep the W best states per depth, scored by
slack = budget - uncovered/N (descending), tie-break on uncovered.

Usage: beam.py NB NA [width] [expand] [seconds_per_phase] [seed]
Writes witness_beam.json on success.
"""
import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np

from twophase import is_prime, divisors, m_admissible


def phase_beam(N, mods, width, expand, seconds, rng, label):
    t0 = time.time()
    budget0 = sum(Fraction(1, m) for m in mods)
    init = (np.ones(N, dtype=bool), frozenset(mods), budget0, ())
    frontier = [init]
    depth = 0
    while frontier and time.time() - t0 < seconds:
        depth += 1
        children = []
        for unc, unused, budget, chosen in frontier:
            cnt = int(unc.sum())
            if cnt == 0:
                print("%s: SUCCESS depth=%d (%.1fs)"
                      % (label, depth - 1, time.time() - t0), flush=True)
                return list(chosen)
            if budget < Fraction(cnt, N):
                continue
            r = int(np.argmax(unc))
            moves = []
            for m in unused:
                a = r % m
                g = int(unc[a::m].sum())
                if g:
                    moves.append((1.0 / m - g / N, -g, a, m))
            moves.sort()
            for w, negg, a, m in moves[:expand]:
                g = -negg
                unc2 = unc.copy()
                unc2[a::m] = False
                children.append((unc2, unused - {m},
                                 budget - Fraction(1, m),
                                 chosen + ((a, m),)))
        if not children:
            break
        # score: slack descending
        scored = []
        for st in children:
            cnt = int(st[0].sum())
            if cnt == 0:
                print("%s: SUCCESS depth=%d (%.1fs)"
                      % (label, depth, time.time() - t0), flush=True)
                return list(st[3])
            scored.append((float(st[2]) - cnt / N, -cnt, rng.random(), st))
        scored.sort(reverse=True)
        frontier = [st for _, _, _, st in scored[:width]]
        best = scored[0]
        print("%s: depth=%d states=%d best_slack=%.5f best_left=%.5f (%.1fs)"
              % (label, depth, len(frontier), best[0],
                 int(best[3][0].sum()) / N, time.time() - t0), flush=True)
    print("%s: FAILED at depth=%d (%.1fs)" % (label, depth, time.time() - t0),
          flush=True)
    return None


def main():
    NB = int(sys.argv[1])
    NA = int(sys.argv[2])
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    expand = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    secs = float(sys.argv[5]) if len(sys.argv) > 5 else 3600.0
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    rng = random.Random(seed)
    modsB = m_admissible(NB, banned=(2,))
    print("phase B: NB=%d |mods|=%d mass=%.4f" % (
        NB, len(modsB), float(sum(Fraction(1, m) for m in modsB))), flush=True)
    resB = phase_beam(NB, modsB, width, expand, secs, rng, "phase B")
    if not resB:
        return
    usedB = {m for _, m in resB}
    modsA = [m for m in m_admissible(NA) if m not in usedB]
    print("phase A: NA=%d |mods|=%d mass=%.4f" % (
        NA, len(modsA), float(sum(Fraction(1, m) for m in modsA))), flush=True)
    resA = phase_beam(NA, modsA, width, expand, secs, rng, "phase A")
    if not resA:
        return
    congs = [((2 * b + 1) % (2 * m), 2 * m) for b, m in resB]
    congs += [((2 * b) % (2 * m), 2 * m) for b, m in resA]
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "witness_beam.json")
    json.dump({"congruences": [[a, n] for a, n in congs]}, open(fn, "w"))
    print("SUCCESS total %d congruences -> %s" % (len(congs), fn))


if __name__ == "__main__":
    main()
