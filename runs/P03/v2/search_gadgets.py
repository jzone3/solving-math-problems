"""Wider gadget search (V2): each null arc (u,v) of the seed is replaced by a
gadget g = (copies, length) meaning `copies` internally-disjoint directed
paths u->v each of `length` unit arcs; each solid arc is optionally
subdivided (length 1 or 2).  Covers plain arcs, subdivisions, parallel arcs,
and parallel subdivided paths — 'all combinatorially distinct ways' at small
scale.  Random sampling with isomorph rejection; ACZ rho-filter; ILP check.
"""
import random
import sys
import time

import core
import seeds
from search_subdiv import test_instance

GADGETS = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1)]


def transform_g(n, arcs, w, null_g, solid_len):
    nulls = [i for i, x in enumerate(w) if x == 0]
    solids = [i for i, x in enumerate(w) if x == 1]
    out = []
    nn = n

    def add_paths(u, v, length, copies):
        nonlocal nn
        for _ in range(copies):
            prev = u
            for _ in range(length - 1):
                out.append((prev, nn))
                prev = nn
                nn += 1
            out.append((prev, v))

    for j, i in enumerate(solids):
        add_paths(arcs[i][0], arcs[i][1], solid_len[j], 1)
    for j, i in enumerate(nulls):
        c, l = null_g[j]
        add_paths(arcs[i][0], arcs[i][1], l, c)
    return nn, out


def run(seed_name="D1", max_iters=30000, ilp_budget=120, seed=0):
    rng = random.Random(seed)
    if seed_name == "D1":
        n, arcs, w = seeds.D1_n, seeds.D1_arcs, seeds.D1_w
    else:
        n, arcs, w = seeds.D2_n, seeds.D2_arcs, seeds.D2_w
    nnull, nsolid = w.count(0), w.count(1)
    stats = {"tau0": 0, "rho_filtered": 0, "ilp_tested": 0, "ilp_timeout": 0,
             "FAILURES": 0, "filter_sanity_ok": 0, "seen": 0, "dup": 0}
    hits = []
    seen = set()
    t0 = time.time()
    for it in range(max_iters):
        ng = [rng.choice(GADGETS) for _ in range(nnull)]
        sl = [rng.choice((1, 1, 1, 2)) for _ in range(nsolid)]
        nn, na = transform_g(n, arcs, w, ng, sl)
        if len(na) > 60:
            continue
        key = core.canon_key(nn, na)
        if key in seen:
            stats["dup"] += 1
            continue
        seen.add(key)
        stats["seen"] += 1
        test_instance(nn, na, ilp_budget, stats, hits)
        if stats["seen"] % 200 == 0:
            print(f"[gadgets {seed_name} seed={seed}] {stats} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"FINAL [gadgets {seed_name} seed={seed}] {stats} "
          f"t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "D1",
        seed=int(sys.argv[2]) if len(sys.argv) > 2 else 0)
