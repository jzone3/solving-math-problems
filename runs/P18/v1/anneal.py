#!/usr/bin/env python3
"""
Simulated annealing over full assignments for P18 phase B (m-space).

State: every modulus m in the pool is assigned a residue a_m; energy =
number of uncovered residues of Z/N (cov[r] = multiplicity). Move: pick a
random modulus, move its congruence to a new residue — chosen either
uniformly (probability u) or centered on a random currently-uncovered
residue (repair move); Metropolis acceptance, geometric cooling with
reheats. This searches a different landscape than greedy construction and
can escape its ~2.4%-uncovered basin.

Usage: anneal.py N [seconds] [seed] [T0] [alpha]
Writes phaseB_anneal_N{N}.json (m-space family) on energy 0; lift + verify
separately (twophase lift, solutions/P18/verify.py).
"""
import json
import random
import sys
import time
from fractions import Fraction

import numpy as np

from twophase import is_prime, divisors, m_admissible


def energy_init(N, assign):
    cov = np.zeros(N, dtype=np.int16)
    for m, a in assign.items():
        cov[a::m] += 1
    return cov


def main():
    N = int(sys.argv[1])
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 3600.0
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    T0 = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0
    alpha = float(sys.argv[5]) if len(sys.argv) > 5 else 0.99997
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    mods = m_admissible(N, banned=(2,))
    print("N=%d |mods|=%d mass=%.4f" % (
        N, len(mods), float(sum(Fraction(1, m) for m in mods))), flush=True)
    # init: waste-greedy assignment for a good start
    unc = np.ones(N, dtype=bool)
    unused = list(mods)
    assign = {}
    while unused:
        r = int(np.argmax(unc)) if unc.any() else rng.randrange(N)
        best = None
        for m in unused:
            a = r % m
            g = int(unc[a::m].sum())
            key = (1.0 / m - g / N, -g)
            if best is None or key < best[0]:
                best = (key, a, m)
        _, a, m = best
        assign[m] = a
        unc[a::m] = False
        unused.remove(m)
    cov = energy_init(N, assign)
    E = int((cov == 0).sum())
    bestE = E
    best_assign = dict(assign)
    print("init E=%d (%.5f)" % (E, E / N), flush=True)
    T = T0
    t0 = time.time()
    it = 0
    last_report = t0
    while time.time() - t0 < secs and E > 0:
        it += 1
        m = mods[rng.randrange(len(mods))]
        a_old = assign[m]
        if rng.random() < 0.7 and E > 0:
            # repair move: target a random uncovered residue
            zeros = np.flatnonzero(cov == 0)
            r = int(zeros[rng.randrange(len(zeros))])
            a_new = r % m
        else:
            a_new = rng.randrange(m)
        if a_new == a_old:
            continue
        old_idx = np.arange(a_old, N, m)
        new_idx = np.arange(a_new, N, m)
        created = int((cov[old_idx] == 1).sum())
        filled = int((cov[new_idx] == 0).sum())
        dE = created - filled
        if dE <= 0 or rng.random() < np.exp(-dE / T):
            cov[old_idx] -= 1
            cov[new_idx] += 1
            assign[m] = a_new
            E += dE
            if E < bestE:
                bestE = E
                best_assign = dict(assign)
                print("it=%d T=%.3f bestE=%d (%.6f) %.1fs"
                      % (it, T, bestE, bestE / N, time.time() - t0), flush=True)
        T *= alpha
        if T < 0.05:
            T = T0 * 0.3  # reheat
        if time.time() - last_report > 120:
            last_report = time.time()
            print("... it=%d T=%.3f E=%d best=%d (%.1fs)"
                  % (it, T, E, bestE, time.time() - t0), flush=True)
            fam = sorted((a, m) for m, a in best_assign.items())
            json.dump({"N": N, "bestE": bestE,
                       "family": [[a, m] for a, m in fam]},
                      open("phaseB_anneal_N%d_snapshot.json" % N, "w"))
    fam = sorted((a, m) for m, a in best_assign.items())
    fn = "phaseB_anneal_N%d_E%d.json" % (N, bestE)
    json.dump({"N": N, "bestE": bestE, "family": [[a, m] for a, m in fam]},
              open(fn, "w"))
    if bestE == 0:
        print("PHASE-B SUCCESS -> %s" % fn, flush=True)
    else:
        print("FAILED bestE=%d (%.6f) its=%d -> %s" % (bestE, bestE / N, it, fn),
              flush=True)


if __name__ == "__main__":
    main()
