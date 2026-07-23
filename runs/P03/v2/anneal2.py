"""Phase-2 hardness-guided annealing over general multi-digraphs.

Score (maximize, lexicographic): (greedy failure fraction over T tries,
rho, CBC solve time).  Instances where the exact ILP is infeasible are
counterexamples (dump + loud print).  Mutations from anneal.py (reroute /
add / delete / subdivide / smooth); starts from random general instances
and from the phase-1 seed transforms.
"""
import json
import random
import sys
import time

import core
from anneal import mutate, random_start, weakly_connected
from search_general import dicut_masks, minimal_masks, greedy_pack, \
    rand_instance


def evaluate(n, arcs, rng, ilp_budget=300, tries=30):
    if not weakly_connected(n, arcs):
        return None
    masks = dicut_masks(n, arcs)
    if masks is None or not masks:
        return None
    t = min(bin(m).count("1") for m in masks)
    if t < 3 or t > 6:
        return None
    r = core.rho(n, arcs, t)
    if r <= 2 or (t == 3 and r == 3):
        return (True, (0.0, r, 0.0), t, r)
    mmin = minimal_masks(masks)
    fails = 0
    for _ in range(tries):
        if not greedy_pack(mmin, len(arcs), t, rng, tries=1):
            fails += 1
    frac = fails / tries
    if fails < tries:
        return (True, (frac, r, 0.0), t, r)
    # all greedy attempts failed -> exact ILP
    cuts = [frozenset(i for i in range(len(arcs)) if (m >> i) & 1)
            for m in mmin]
    t0 = time.time()
    ok = core.packing_exists(n, arcs, t, cuts=cuts, time_limit=ilp_budget)
    dt = time.time() - t0
    return (bool(ok), (frac, r, dt), t, r)


def main(seed=1, wall=7200, ilp_budget=300):
    rng = random.Random(seed)
    t_end = time.time() + wall
    stats = {"steps": 0, "evals": 0, "fails": 0, "restarts": 0,
             "ilp_calls": 0}
    best_ever = None
    while time.time() < t_end:
        stats["restarts"] += 1
        if rng.random() < 0.5:
            state = rand_instance(rng, 16)
        else:
            state = random_start(rng)
        cur = (-1.0, -1, 0.0)
        tries = 0
        while tries < 500 and time.time() < t_end:
            tries += 1
            stats["steps"] += 1
            cand = mutate(state[0], state[1], rng, max_arcs=32)
            ev = evaluate(*cand, rng, ilp_budget)
            if ev is None:
                continue
            stats["evals"] += 1
            feas, score, t, r = ev
            if score[2] > 0:
                stats["ilp_calls"] += 1
            if not feas:
                stats["fails"] += 1
                rec = {"n": cand[0], "arcs": cand[1], "tau": t, "rho": r}
                print("!!! PACKING FAILURE:", json.dumps(rec), flush=True)
                with open(f"hits_anneal2_{seed}.json", "a") as f:
                    f.write(json.dumps(rec) + "\n")
            if score >= cur or rng.random() < 0.1:
                state, cur = cand, score
            if best_ever is None or score > best_ever[0]:
                best_ever = (score, cand[0], len(cand[1]), t, r)
            if stats["steps"] % 5000 == 0:
                print(f"[anneal2 seed={seed}] {stats} best={best_ever}",
                      flush=True)
    print(f"FINAL [anneal2 seed={seed}] {stats} best={best_ever}", flush=True)


if __name__ == "__main__":
    main(seed=int(sys.argv[1]) if len(sys.argv) > 1 else 1,
         wall=int(sys.argv[2]) if len(sys.argv) > 2 else 7200)
