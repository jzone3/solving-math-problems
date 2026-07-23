#!/usr/bin/env python3
"""
Phase 3b: anneal around D27 (Abdi-Cornuejols-Zlatin), the sink-regular
(3,4)-bipartite digraph on 27 vertices whose arc set contains a minimal dijoin
J* such that A-J* is a 2-dijoin NOT partitionable into 2 dijoins (extracted
from arXiv:2202.00392 Fig. D27 and verified against all stated properties).

D27 itself packs 3 dijoins. We mutate/anneal around it (and around glued
double copies) at tau>=3 hunting for UNSAT; score = dicut tightness.
"""
import random, sys, time
from fastcuts import min_dicuts
from search import packs_into, report_counterexample

SOLID = [(2,1),(12,1),(12,14),(15,14),(15,9),(6,9),(6,16),(6,16),(2,13),(2,13),
         (4,3),(4,17),(4,3),(18,17),(8,19),(8,20),(8,20),(0,5),(22,5),(22,23),
         (24,23),(24,7),(11,7),(0,21),(11,10),(26,19),(18,25),(26,25),(11,10),(0,21)]
DASH = [(11,19),(18,10),(18,13),(12,21),(0,14),(15,5),(8,9),(6,7),(22,16),
        (22,3),(4,23),(24,17),(12,20),(2,25),(26,1)]
D27 = SOLID + DASH
N27 = 27


def glue(rng):
    """Two copies of D27 with a random subset of vertices identified."""
    k = rng.randint(8, 16)
    ids = rng.sample(range(N27), k)
    ids2 = rng.sample(range(N27), k)
    mapping = {}
    nxt = N27
    for v in range(N27):
        if v in ids2:
            mapping[v] = ids[ids2.index(v)]
        else:
            mapping[v] = nxt; nxt += 1
    arcs = list(D27) + [(mapping[u], mapping[v]) for (u, v) in D27]
    return nxt, arcs


def mutate(rng, n, arcs):
    cand = list(arcs)
    op = rng.random()
    if op < 0.35 and len(cand) > n // 2:
        cand.pop(rng.randrange(len(cand)))
    elif op < 0.7:
        u = rng.randrange(n); v = rng.randrange(n)
        if u != v:
            cand.append((u, v))
    else:
        i = rng.randrange(len(cand))
        u = rng.randrange(n); v = rng.randrange(n)
        if u != v:
            cand[i] = (u, v)
    return cand


def anneal(seconds, seed, mode):
    rng = random.Random(seed)
    t0 = time.time(); steps = 0; checked = 0
    if mode == "d27":
        n, cur = N27, list(D27)
    else:
        n, cur = glue(rng)
    cur_s = -10**9; best = -10**9
    while time.time() - t0 < seconds:
        steps += 1
        if rng.random() < 0.001:
            if mode == "d27":
                n, cur = N27, list(D27)
            else:
                n, cur = glue(rng)
            cur_s = -10**9
        cand = mutate(rng, n, cur)
        if len(cand) > 100:
            continue
        cuts, tau = min_dicuts(n, cand, max_ideals=120000)
        if cuts is None or tau < 3 or len(cuts) > 12000:
            continue
        ok, _ = packs_into(len(cand), cuts, tau)
        checked += 1
        if not ok:
            report_counterexample(n, cand, tau)
            print("UNSAT FOUND tau=", tau, flush=True)
            continue
        tight = sum(1 for c in cuts if len(c) == tau)
        s = 100 * tight + min(len(cuts), 2000) - len(cand)
        if s >= cur_s or rng.random() < 0.03:
            cur, cur_s = cand, s
        if s > best:
            best = s
            print(f"[d27-{mode} seed={seed}] step={steps} checked={checked} best={s} "
                  f"tau={tau} m={len(cand)} cuts={len(cuts)} tight={tight} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"[d27-{mode} seed={seed}] DONE steps={steps} checked={checked} best={best}",
          flush=True)


if __name__ == "__main__":
    anneal(float(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
