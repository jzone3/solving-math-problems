#!/usr/bin/env python3
"""Experiment C: compressed greedy plus ruin/recreate residual repair.

The state is fc_tree2's exact disjoint-fragment dictionary.  Repair removes a
small random batch of placed classes, replays the remaining classes exactly,
then lets exact-gain greedy recreate the ruined part.  This gives global
reassignment without allocating a Z_N bitmask.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "toolkit"))
from fc_tree2 import Builder, parse_fact  # noqa: E402


def make_builder(M, pps, chosen=()):
    b = Builder(M, pps)
    for a, n in chosen:
        b.apply(int(a), int(n))
    return b


def residual_stats(b):
    return b.mass(), b.nfrags(), len(b.chosen)


def weighted_best(b, n, weights):
    """Exact weighted CRT gain profile over the compressed fragments."""
    import numpy as np
    from math import gcd
    if n > 200000:
        return b.best_class(n)
    profile = np.zeros(n)
    for m, residues in b.frags.items():
        if len(residues) == 0:
            continue
        g = gcd(m, n)
        wr = weights.get(m)
        if wr is None or len(wr) != len(residues):
            wr = np.ones(len(residues))
        counts = np.bincount(residues % g, weights=wr, minlength=g)
        profile += (1.0 / (m // g * n)) * np.tile(counts, n // g)
    a = int(profile.argmax())
    return float(profile[a]), a


def min_conflicts(b, pps, seconds, moves, seed):
    """Exact single-modulus reassignment with breakout-weighted scoring.

    Removing a modulus replays every other assignment into a fresh compressed
    builder; the subsequent candidate residue is selected by an exact
    weighted CRT profile.  The replay is deliberately expensive but avoids
    any approximate coverage acceptance.
    """
    rng = random.Random(seed)
    weights = {m: [1.0] * len(r) for m, r in b.frags.items()}
    best = b
    best_mass = b.mass()
    t0 = time.time()
    stagnant = 0
    for step in range(moves):
        if time.time() - t0 >= seconds:
            break
        if not b.chosen:
            break
        # Randomized candidate selection prevents repeatedly touching only
        # the smallest moduli, while breakout weights bias future choices.
        n_candidates = min(3, len(b.chosen))
        picks = rng.sample(b.chosen, n_candidates)
        pick = picks[rng.randrange(len(picks))]
        remove_n = pick[1]
        keep = [x for x in b.chosen if x[1] != remove_n]
        trial = make_builder(b.M, pps, keep)
        # Score candidate residues against the current weighted hole set.
        # The exact trial below still decides the real residual delta.
        _, a = weighted_best(b, remove_n, weights)
        trial.apply(a, remove_n)
        new_mass = trial.mass()
        if new_mass < b.mass():
            b = trial
            weights = {m: [1.0] * len(r) for m, r in b.frags.items()}
            stagnant = 0
            if new_mass < best_mass:
                best, best_mass = b, new_mass
            verdict = "ACCEPT"
        else:
            stagnant += 1
            verdict = "REJECT"
        if stagnant >= 3:
            # PAWS/breakout: increase pressure on current residual cells.
            for m, r in b.frags.items():
                old = weights.get(m)
                if old is None or len(old) != len(r):
                    weights[m] = [2.0] * len(r)
                else:
                    weights[m] = [x + 1.0 for x in old]
            stagnant = 0
        print("MC step=%d %s remove=%d mass=%.12g frags=%d chosen=%d t=%.1fs" %
              (step, verdict, remove_n, b.mass(), b.nfrags(),
               len(b.chosen), time.time() - t0), flush=True)
    return best


def ruin_recreate(b, pps, rng, ruin, seconds):
    if not b.chosen:
        return b
    indices = set(rng.sample(range(len(b.chosen)),
                             min(ruin, len(b.chosen))))
    keep = [x for i, x in enumerate(b.chosen) if i not in indices]
    trial = make_builder(b.M, pps, keep)
    trial.run(seconds)
    return trial


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("M", type=int, default=17)
    ap.add_argument("--fact", default="2^6,3^3,5^2,7,11,13,17")
    ap.add_argument("--greedy-seconds", type=float, default=180)
    ap.add_argument("--repair-seconds", type=float, default=30)
    ap.add_argument("--repairs", type=int, default=8)
    ap.add_argument("--ruin", type=int, default=12)
    ap.add_argument("--seed", type=int, default=1701)
    ap.add_argument("--seed-json", default=None,
                    help="resume from a partial JSON's congruences")
    ap.add_argument("--mc-seconds", type=float, default=0)
    ap.add_argument("--mc-moves", type=int, default=0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    pps = parse_fact(args.fact)
    if args.seed_json:
        seed = json.loads(Path(args.seed_json).read_text())
        b0 = make_builder(args.M, pps, seed["congruences"])
    else:
        b0 = Builder(args.M, pps)
    print("C-BASE M=%d N=%d divisors=%d recip=%.9f" %
          (args.M, b0.N, len(b0.mods), sum(1.0 / n for n in b0.mods)),
          flush=True)
    t0 = time.time()
    b0.run(args.greedy_seconds)
    best = b0
    print("C-BASE stats mass=%.12g frags=%d chosen=%d elapsed=%.1fs" %
          (*residual_stats(best), time.time() - t0), flush=True)
    if args.mc_moves and args.mc_seconds > 0:
        best = min_conflicts(best, pps, args.mc_seconds, args.mc_moves,
                             args.seed)
        print("C-MC best mass=%.12g frags=%d chosen=%d elapsed=%.1fs" %
              (*residual_stats(best), time.time() - t0), flush=True)
    rng = random.Random(args.seed)
    history = [("base", *residual_stats(best))]
    for j in range(args.repairs):
        trial = ruin_recreate(best, pps, rng, args.ruin, args.repair_seconds)
        old = residual_stats(best)
        new = residual_stats(trial)
        # Exact residual mass is the primary objective; fragment count breaks
        # ties.  This is only search scoring, never cover acceptance.
        if (new[0], new[1]) < (old[0], old[1]):
            best = trial
            verdict = "ACCEPT"
        else:
            verdict = "REJECT"
        history.append(("repair%d" % j, *new, verdict))
        print("C-REPAIR %d %s old=(%.12g,%d,%d) new=(%.12g,%d,%d)" %
              (j, verdict, *old, *new), flush=True)
    fn = Path(args.out or ("frontier_partial_m%d.json" % args.M))
    fn.write_text(json.dumps({
        "minmod": args.M, "partial": True,
        "N": best.N, "history": history,
        "congruences": [[int(a), int(n)] for a, n in best.chosen],
    }))
    print("C-DONE best mass=%.12g frags=%d chosen=%d file=%s elapsed=%.1fs" %
          (*residual_stats(best), fn, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
