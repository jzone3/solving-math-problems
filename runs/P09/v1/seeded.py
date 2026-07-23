"""Basin-hopping around the best near-misses from earlier anneal phases.

Loads top-ratio graphs from results_phase*.jsonl, perturbs each with k random flips
(k in 3..10), re-anneals at low temperature, repeats. Logs to results_seeded.jsonl.

Usage: python3 seeded.py <hours> <nworkers>
"""
import json
import os
import random
import sys
import time
from multiprocessing import Process

from anneal import anneal_once, flip, EPS
from bn_core import evaluate, adj_to_g6, g6_to_adj

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_seeded.jsonl")


def load_seeds(top=120):
    recs = []
    for f in ["results_phase1.jsonl", "results_phase2.jsonl", "results_phase3.jsonl"]:
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            recs += [json.loads(l) for l in open(p)]
    recs.sort(key=lambda r: -r["ratio"])
    return [r["g6"] for r in recs[:top]]


def anneal_from(n, adj, steps, rng, t0, mode):
    import math
    from anneal import objective
    score, ratio, l1, l2, m, w = evaluate(n, adj)
    cur = objective(ratio, l1, l2, mode)
    best = (ratio, adj_to_g6(n, adj), score, l1, l2, m, w)
    t1 = 0.0003
    for step in range(steps):
        T = t0 * (t1 / t0) ** (step / steps)
        i = rng.randrange(n)
        j = rng.randrange(n)
        while j == i:
            j = rng.randrange(n)
        flip(adj, i, j)
        score, ratio, l1, l2, m, w = evaluate(n, adj)
        obj = objective(ratio, l1, l2, mode)
        if obj >= cur or rng.random() < math.exp((obj - cur) / T):
            cur = obj
            if ratio > best[0]:
                best = (ratio, adj_to_g6(n, adj), score, l1, l2, m, w)
                if score > EPS:
                    return best, True
        else:
            flip(adj, i, j)
    return best, False


def worker(wid, hours, seeds):
    rng = random.Random(998877 + wid)
    deadline = time.time() + hours * 3600
    while time.time() < deadline:
        g6 = rng.choice(seeds)
        n, adj = g6_to_adj(g6)
        k = rng.randrange(3, 11)
        for _ in range(k):
            i = rng.randrange(n)
            j = rng.randrange(n)
            while j == i:
                j = rng.randrange(n)
            flip(adj, i, j)
        mode = rng.choice(["ratio", "l2bias"])
        t0 = rng.choice([0.003, 0.008])
        best, found = anneal_from(n, adj, 30000, rng, t0, mode)
        rec = {"worker": wid, "seed_g6": g6, "kflips": k, "mode": mode,
               "ratio": best[0], "score": best[2], "l1": best[3], "l2": best[4],
               "m": best[5], "omega": best[6], "g6": best[1], "counterexample": found}
        with open(RESULTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        if found:
            print("COUNTEREXAMPLE FOUND", rec, flush=True)
            return


if __name__ == "__main__":
    hours = float(sys.argv[1])
    nworkers = int(sys.argv[2])
    seeds = load_seeds()
    procs = [Process(target=worker, args=(w, hours, seeds)) for w in range(nworkers)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
