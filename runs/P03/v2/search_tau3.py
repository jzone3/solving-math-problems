"""tau>=3 extension of Schrijver's example (V2): in the weighted world,
changing the middle arc of each active path from weight 1 to tau-1 gives
counterexamples to the weighted conjecture for every tau>=2 (see ACZ 2023,
discussion of Figure 1, citing [25]).  Unweighted analogue: replace those
middle arcs (b, e, h = solid indices 1, 4, 7) by (tau-1) parallel unit arcs,
and each null arc by a path of length k in {1,2,3}; also optionally subdivide
solid arcs.  Search all/random combinations for a packing failure.
"""
import argparse
import itertools
import json
import random
import time

import core
import seeds
from search_subdiv import transform, test_instance

MIDDLE = [1, 4, 7]  # indices of b, e, h in D1_solid


def run(mult, mode, max_iters, ilp_budget, choices=(1, 2), subdiv_solid=False):
    n, arcs, w = seeds.D1_n, seeds.D1_arcs, seeds.D1_w
    nnull = w.count(0)
    nsolid = w.count(1)
    solid_mult = [mult if j in MIDDLE else 1 for j in range(nsolid)]
    stats = {"tau0": 0, "rho_filtered": 0, "ilp_tested": 0, "ilp_timeout": 0,
             "FAILURES": 0, "filter_sanity_ok": 0, "seen": 0, "dup": 0}
    hits = []
    seen = set()
    t0 = time.time()

    if mode == "exhaustive":
        space = itertools.product(choices, repeat=nnull)
    else:
        def rand():
            while True:
                yield tuple(random.choice(choices) for _ in range(nnull))
        space = rand()

    for it, nc in enumerate(space):
        if max_iters and it >= max_iters:
            break
        sc = None
        if subdiv_solid:
            sc = [random.choice((1, 2)) for _ in range(nsolid)]
        nn, na = transform(n, arcs, w, list(nc), solid_choice=sc,
                           solid_mult=solid_mult)
        key = core.canon_key(nn, na)
        if key in seen:
            stats["dup"] += 1
            continue
        seen.add(key)
        stats["seen"] += 1
        test_instance(nn, na, ilp_budget, stats, hits)
        if stats["seen"] % 200 == 0:
            print(f"[tau3 mult={mult} {mode}] {stats} t={time.time()-t0:.0f}s",
                  flush=True)
    print(f"FINAL [tau3 mult={mult} {mode} choices={choices} "
          f"subdiv_solid={subdiv_solid}] {stats} t={time.time()-t0:.0f}s",
          flush=True)
    if hits:
        with open(f"hits_tau3_m{mult}.json", "w") as f:
            json.dump(hits, f)
    return stats, hits


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mult", type=int, default=2)
    ap.add_argument("--mode", default="exhaustive")
    ap.add_argument("--max-iters", type=int, default=0)
    ap.add_argument("--ilp-budget", type=int, default=120)
    ap.add_argument("--choices", default="1,2")
    ap.add_argument("--subdiv-solid", action="store_true")
    a = ap.parse_args()
    ch = tuple(int(x) for x in a.choices.split(","))
    run(a.mult, a.mode, a.max_iters, a.ilp_budget, ch, a.subdiv_solid)
