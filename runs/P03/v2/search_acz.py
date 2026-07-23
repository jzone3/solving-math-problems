"""Phase-2 secondary target: the proposed FIX of the Edmonds-Giles
conjecture (stated in ACZ 2023, p.6, citing [7]): tau(D,w) = nu(D,w) for
weighted digraphs where the support D[{a : w_a != 0}] is a SPANNING
CONNECTED (as undirected) subdigraph of D.  This is open; a counterexample
would be a publishable result and is exactly the DGG shape.

Search: random digraphs (DAG-biased), random weights in {0,1,2} with
support forced spanning+connected, tau >= 2; exact weighted packing ILP.
"""
import json
import random
import sys
import time

import core


def rand_weighted(rng, nmax=14):
    n = rng.randint(5, nmax)
    m = rng.randint(n + 2, min(30, 3 * n))
    dag = rng.random() < 0.5
    arcs = []
    while len(arcs) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        if dag and u > v:
            u, v = v, u
        arcs.append((u, v))
    # random spanning tree (undirected) gets nonzero weight -> support
    # spanning connected
    perm = list(range(n))
    rng.shuffle(perm)
    for i in range(n - 1):
        u, v = perm[i], perm[i + 1]
        if dag and u > v:
            u, v = v, u
        arcs.append((u, v))
    m = len(arcs)
    w = []
    for i, a in enumerate(arcs):
        if i >= m - (n - 1):
            w.append(rng.choice((1, 1, 2)))   # tree arcs: nonzero
        else:
            w.append(rng.choice((0, 0, 1, 1, 2)))
    return n, arcs, w


def run(seed=0, wall=7200, ilp_budget=300):
    rng = random.Random(seed)
    t_end = time.time() + wall
    stats = {"gen": 0, "tau_ge2": 0, "ilp_tested": 0, "FAILURES": 0,
             "timeouts": 0}
    hard = []
    while time.time() < t_end:
        stats["gen"] += 1
        n, arcs, w = rand_weighted(rng)
        t, _ = core.tau(n, arcs, w)
        if t is None or t < 2:
            continue
        stats["tau_ge2"] += 1
        cuts = core.minimal_dicuts(core.all_dicuts(n, arcs))
        stats["ilp_tested"] += 1
        t0 = time.time()
        ok = core.packing_exists(n, arcs, t, w=w, cuts=cuts,
                                 time_limit=ilp_budget)
        dt = time.time() - t0
        rec = {"n": n, "arcs": arcs, "w": w, "tau": t, "ilp_time": dt}
        if ok is False:
            stats["FAILURES"] += 1
            print("!!! ACZ-EG-FIX FAILURE:", json.dumps(rec), flush=True)
            with open(f"hits_acz_{seed}.json", "a") as f:
                f.write(json.dumps(rec) + "\n")
        elif ok is None:
            stats["timeouts"] += 1
            print("ILP TIMEOUT:", json.dumps(rec), flush=True)
        else:
            hard.append((round(dt, 4), n, len(arcs), t))
            hard.sort(reverse=True)
            del hard[5:]
        if stats["gen"] % 5000 == 0:
            print(f"[acz seed={seed}] {stats} hardest={hard}", flush=True)
    print(f"FINAL [acz seed={seed}] {stats} hardest={hard}", flush=True)


if __name__ == "__main__":
    run(seed=int(sys.argv[1]) if len(sys.argv) > 1 else 0,
        wall=int(sys.argv[2]) if len(sys.argv) > 2 else 7200)
