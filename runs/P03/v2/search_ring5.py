"""Subdivision-transform search on the generalized Schrijver ring(5) seed
(20 vertices, 35 arcs, 15 solid / 20 null)."""
import random
import sys
import time

import core
import rings
from search_subdiv import transform, test_instance


def run(max_iters=20000, ilp_budget=120, choices=(1, 2, 3), seed=0):
    rng = random.Random(seed)
    n, arcs, w = rings.ring(5)
    nnull = w.count(0)
    stats = {"tau0": 0, "rho_filtered": 0, "ilp_tested": 0, "ilp_timeout": 0,
             "FAILURES": 0, "filter_sanity_ok": 0, "seen": 0, "dup": 0}
    hits = []
    seen = set()
    t0 = time.time()
    for it in range(max_iters):
        nc = [rng.choice(choices) for _ in range(nnull)]
        nn, na = transform(n, arcs, w, nc)
        key = core.canon_key(nn, na)
        if key in seen:
            stats["dup"] += 1
            continue
        seen.add(key)
        stats["seen"] += 1
        test_instance(nn, na, ilp_budget, stats, hits)
        if stats["seen"] % 200 == 0:
            print(f"[ring5 seed={seed}] {stats} t={time.time()-t0:.0f}s",
                  flush=True)
    print(f"FINAL [ring5 seed={seed} choices={choices}] {stats} "
          f"t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    run(seed=int(sys.argv[1]) if len(sys.argv) > 1 else 0)
