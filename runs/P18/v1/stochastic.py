#!/usr/bin/env python3
"""
Stochastic two-phase search (randomized greedy with restarts) for P18.

Phase B: cover Z/NB with distinct moduli from (M \ {2}) cap div(NB).
Phase A: cover Z/NA with modulus 2 plus the leftover pool.
Each restart: repeatedly pick a random congruence among the top-k
gain-density moves; dead ends (exact Fraction mass prune) restart.

Usage: stochastic.py NB NA [seconds] [topk] [seed]
Writes witness_stoch.json on success (verify with solutions/P18/verify.py).
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
    chosen = []
    budget = sum(Fraction(1, m) for m in unused)
    while cnt:
        if budget < Fraction(cnt, N):
            return None
        moves = []
        for m in unused:
            c = unc.reshape(N // m, m).sum(axis=0)
            a = int(c.argmax())
            g = int(c[a])
            if g:
                moves.append((g / m, g, a, m))
        if not moves:
            return None
        moves.sort(reverse=True)
        _, g, a, m = moves[rng.randrange(min(topk, len(moves)))]
        idx = np.arange(a, N, m)
        unc[idx] = False
        cnt -= g
        unused.remove(m)
        budget -= Fraction(1, m)
        chosen.append((a, m))
    return chosen


def run_phase(N, mods, seconds, topk, rng, label):
    t0 = time.time()
    tries = 0
    best_left = None
    while time.time() - t0 < seconds:
        tries += 1
        res = one_restart(N, mods, rng, topk)
        if res is not None:
            print("%s: SUCCESS after %d restarts (%.1fs)"
                  % (label, tries, time.time() - t0), flush=True)
            return res
    print("%s: FAILED %d restarts in %.1fs" % (label, tries, time.time() - t0),
          flush=True)
    return None


def main():
    NB = int(sys.argv[1])
    NA = int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0
    topk = int(sys.argv[4]) if len(sys.argv) > 4 else 4
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
                      "witness_stoch.json")
    json.dump({"congruences": [[a, n] for a, n in congs]}, open(fn, "w"))
    print("SUCCESS total %d congruences -> %s" % (len(congs), fn))


if __name__ == "__main__":
    main()
