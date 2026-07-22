"""V2 core search: replace weights of the Schrijver / Cornuejols-Guenin
weighted counterexamples by parallel/subdivided arcs in all combinatorially
distinct ways, and test each resulting UNWEIGHTED digraph for a Woodall
counterexample (min dicut tau, but no packing of tau disjoint dijoins).

Transformations per weight-0 arc (u,v):   choice k in {1,2,3,...} = replace by
a directed path u -> x1 -> ... -> x_{k-1} -> v of k unit arcs (k=1: plain arc).
Transformations per weight-1 arc: keep, optionally subdivide as well, and for
the tau>=2 extension multiply designated arcs into parallel unit arcs.

Cheap filters before the ILP:
  - Abdi-Cornuejols-Zlatin: for w=1, if rho(tau,D,1) <= 2 a packing of size
    tau exists; if tau=3 and rho=3 a partition into 3 dijoins exists.
    So only instances with rho >= 3 (rho >= 4 when tau=3) can be
    counterexamples.  We still ILP-verify a random 1% of filtered instances
    as a sanity check on the filter.
"""
import argparse
import itertools
import json
import random
import sys
import time

import core
import seeds


def transform(n, arcs, w, null_choice, solid_choice=None, solid_mult=None):
    """Build unweighted digraph. null_choice[i] = path length for i-th 0-arc.
    solid_choice[j] = path length for j-th 1-arc (default 1).
    solid_mult[j] = number of parallel copies of j-th 1-arc (default 1)."""
    nulls = [i for i, x in enumerate(w) if x == 0]
    solids = [i for i, x in enumerate(w) if x == 1]
    out = []
    nn = n

    def add_path(u, v, k, copies=1):
        nonlocal nn
        for _ in range(copies):
            prev = u
            for step in range(k - 1):
                out.append((prev, nn))
                prev = nn
                nn += 1
            out.append((prev, v))

    for j, i in enumerate(solids):
        k = 1 if solid_choice is None else solid_choice[j]
        c = 1 if solid_mult is None else solid_mult[j]
        add_path(arcs[i][0], arcs[i][1], k, c)
    for j, i in enumerate(nulls):
        add_path(arcs[i][0], arcs[i][1], null_choice[j])
    return nn, out


def test_instance(nn, na, ilp_budget, stats, hits, always_ilp=False):
    t, _ = core.tau(nn, na)
    if t is None or t == 0:
        stats["tau0"] += 1
        return
    stats.setdefault(f"tau{t}", 0)
    stats[f"tau{t}"] += 1
    if t == 1:
        return  # trivially packs
    r = core.rho(nn, na, t)
    filtered = (r <= 2) or (t == 3 and r == 3)
    if filtered and not always_ilp and random.random() > 0.01:
        stats["rho_filtered"] += 1
        return
    stats["ilp_tested"] += 1
    ok = core.packing_exists(nn, na, t, time_limit=ilp_budget)
    if ok is None:
        stats["ilp_timeout"] += 1
    elif not ok:
        stats["FAILURES"] += 1
        hits.append({"n": nn, "arcs": na, "tau": t, "rho": r})
        print("!!! PACKING FAILURE (candidate counterexample):",
              json.dumps(hits[-1]))
    else:
        if filtered:
            stats["filter_sanity_ok"] += 1


def run(seed_name, mode, max_iters, ilp_budget, choices=(1, 2)):
    if seed_name == "D1":
        n, arcs, w = seeds.D1_n, seeds.D1_arcs, seeds.D1_w
    else:
        n, arcs, w = seeds.D2_n, seeds.D2_arcs, seeds.D2_w
    nnull = w.count(0)
    stats = {"tau0": 0, "rho_filtered": 0, "ilp_tested": 0,
             "ilp_timeout": 0, "FAILURES": 0, "filter_sanity_ok": 0,
             "seen": 0, "dup": 0}
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
        nn, na = transform(n, arcs, w, list(nc))
        key = core.canon_key(nn, na)
        if key in seen:
            stats["dup"] += 1
            continue
        seen.add(key)
        stats["seen"] += 1
        test_instance(nn, na, ilp_budget, stats, hits)
        if stats["seen"] % 500 == 0:
            print(f"[{seed_name} {mode}] {stats} t={time.time()-t0:.0f}s",
                  flush=True)
    print(f"FINAL [{seed_name} {mode} choices={choices}] {stats} "
          f"t={time.time()-t0:.0f}s", flush=True)
    return stats, hits


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="D1")
    ap.add_argument("--mode", default="exhaustive")
    ap.add_argument("--max-iters", type=int, default=0)
    ap.add_argument("--ilp-budget", type=int, default=60)
    ap.add_argument("--choices", default="1,2")
    a = ap.parse_args()
    ch = tuple(int(x) for x in a.choices.split(","))
    run(a.seed, a.mode, a.max_iters, a.ilp_budget, ch)
