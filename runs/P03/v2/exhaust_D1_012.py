"""Full exhaustive sweep of D1 transforms over {delete, arc, path2}^12
(3^12 = 531441 combos), sharded by the first two null-arc choices.
Usage: exhaust_D1_012.py <shard 0..8>
"""
import itertools
import sys
import time

import core
import seeds
from search_subdiv import transform, test_instance


def main(shard):
    n, arcs, w = seeds.D1_n, seeds.D1_arcs, seeds.D1_w
    a, b = divmod(shard, 3)
    stats = {"tau0": 0, "rho_filtered": 0, "ilp_tested": 0, "ilp_timeout": 0,
             "FAILURES": 0, "filter_sanity_ok": 0, "seen": 0, "dup": 0}
    hits = []
    seen = set()
    t0 = time.time()
    for rest in itertools.product((0, 1, 2), repeat=10):
        nc = [a, b] + list(rest)
        nn, na = transform(n, arcs, w, nc)
        if not na:
            continue
        key = core.canon_key(nn, na)
        if key in seen:
            stats["dup"] += 1
            continue
        seen.add(key)
        stats["seen"] += 1
        test_instance(nn, na, ilp_budget=120, stats=stats, hits=hits)
        if stats["seen"] % 2000 == 0:
            print(f"[exhaustD1 shard={shard}] {stats} t={time.time()-t0:.0f}s",
                  flush=True)
    print(f"FINAL [exhaustD1 shard={shard}] {stats} t={time.time()-t0:.0f}s",
          flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]))
