"""numpy-accelerated annealer for the ACZ-complete sink-regular (3,4)-bipartite class.

Same search as bip.py but the O(2^|S|) dicut sweep is vectorized:
cutsize(X) = sum_t [t not in Ymax(X)] * popcount(innb[t] & X), Ymax(X) = {t: innb[t] subseteq X}.
Score uses only the size vector (min size, # size-3 cuts); full minimal-dicut arc sets
(bip.all_min_dicuts, cross-validated vs core.py) are materialized only for accepted
candidates that get the SAT packing check.
"""
import json
import random
import sys
import time

import numpy as np

from bip import all_min_dicuts, pack3, gen_random, swap_mutate, nonplanar


def cut_sizes(nbrs, nT):
    nS = len(nbrs)
    innb = np.zeros(nT, dtype=np.uint32)
    for i, nb in enumerate(nbrs):
        for t in nb:
            innb[t] |= np.uint32(1 << i)
    X = np.arange(1, 1 << nS, dtype=np.uint32)[:, None]      # (2^nS-1, 1)
    inter = innb[None, :] & X                                 # (2^nS-1, nT)
    ymax = inter == innb[None, :]
    sizes = np.where(~ymax, np.bitwise_count(inter), 0).sum(axis=1, dtype=np.int64)
    # per-sink in-arc dicuts always have size 3 (sink-regular); X rows with size 0 are
    # not dicuts (U=V or no leaving arcs) -> mask them out
    sizes = sizes[sizes > 0]
    return sizes


def score(sizes):
    if sizes.size == 0:
        return -2000, False
    mn = int(sizes.min())
    if mn < 3:
        return -1000 + 100 * mn, False
    return 10 * int((sizes == 3).sum()) + int(sizes.size % 997), True


def run(seed, minutes, n4, n3, restart_steps=1500):
    rng = random.Random(seed)
    t0 = time.time()
    last = t0
    stats = {"iters": 0, "valid": 0, "sat": 0, "unsat": 0, "restarts": 0}
    best_ever = -10**9
    while time.time() - t0 < minutes * 60:
        stats["restarts"] += 1
        nbrs, nT = gen_random(rng, n4, n3)
        cur, _ = score(cut_sizes(nbrs, nT))
        stale = 0
        while stale < restart_steps and time.time() - t0 < minutes * 60:
            stats["iters"] += 1
            cand = swap_mutate(nbrs, nT, rng)
            if cand is None:
                stale += 1
                continue
            s2, valid2 = score(cut_sizes(cand, nT))
            if s2 >= cur:
                improved = s2 > cur
                nbrs, cur = cand, s2
                if valid2 and improved:
                    stats["valid"] += 1
                    if nonplanar(cand, nT):
                        tau, md = all_min_dicuts(cand, nT)
                        assert tau == 3
                        stats["sat"] += 1
                        if not pack3(cand, md):
                            stats["unsat"] += 1
                            fn = f"witness_bipfast_{int(time.time())}.json"
                            with open(fn, "w") as f:
                                json.dump({"n4": n4, "n3": n3, "nT": nT,
                                           "nbrs": [list(nb) for nb in cand]}, f)
                            print(f"!!! UNSAT BIPARTITE CANDIDATE: {fn}", flush=True)
                            return
                stale = 0 if improved else stale + 1
                best_ever = max(best_ever, s2)
            else:
                stale += 1
            if time.time() - last > 300:
                last = time.time()
                print(f"[{int(time.time()-t0)}s] best={best_ever} cur={cur} {stats}",
                      flush=True)
    print(f"FINAL best={best_ever} {stats}", flush=True)


if __name__ == "__main__":
    run(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
