"""Rediscover a Schrijver-type weighted counterexample to validate the
detector end-to-end.

Structure from the literature (Schrijver 1980; Scott-Seymour; Hwang thesis):
weight-1 arcs form three vertex-disjoint alternating paths of length 3
(v0 -> v1 <- v2 -> v3, internal vertices are trivial-dicut shores); the rest
of the digraph is weight-0 arcs. We FIX the weight-1 skeleton on 12 vertices
and hill-climb over weight-0 arc sets to reach tau_w = 2 and then test the
packing ILP. Any (tau_w=2, nu_w=1) find validates the whole gap pipeline.
"""

import random
import sys
import time

from weighted import tau_w, pack_w, weakly_connected

N = 12
# three alternating paths: 0->1<-2->3, 4->5<-6->7, 8->9<-10->11
W1 = [(0, 1), (2, 1), (2, 3), (4, 5), (6, 5), (6, 7), (8, 9), (10, 9), (10, 11)]


def build(extra):
    arcs = list(W1) + list(extra)
    w = [1] * len(W1) + [0] * len(extra)
    return arcs, w


def score(extra, time_limit=30):
    arcs, w = build(extra)
    if not weakly_connected(N, arcs):
        return (-100, 0), None
    t, cuts = tau_w(N, arcs, w)
    if t is None:  # strongly connected: impossible (DAG-ish skeleton) but ok
        return (-50, 0), None
    if t != 2:
        return (-abs(t - 2), 0), t
    ok, _ = pack_w(N, arcs, w, 2, time_limit=time_limit)
    gap = 0 if ok else 1
    return (0, gap), t


def main(seconds=1200, seed=0):
    rng = random.Random(seed)
    pool = [(u, v) for u in range(N) for v in range(N) if u != v
            and (u, v) not in W1]
    t0 = time.time()
    best = None
    cur = set(rng.sample(pool, 9))
    cur_s, _ = score(cur)
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        if rng.random() < 0.03 or cur_s[0] <= -50:
            cur = set(rng.sample(pool, rng.randint(6, 12)))
            cur_s, _ = score(cur)
            continue
        cand = set(cur)
        r = rng.random()
        if r < 0.4 and len(cand) < 14:
            cand.add(rng.choice(pool))
        elif r < 0.7 and len(cand) > 5:
            cand.remove(rng.choice(sorted(cand)))
        else:
            if cand:
                cand.remove(rng.choice(sorted(cand)))
            cand.add(rng.choice(pool))
        s, t = score(cand)
        if s >= cur_s:
            cur, cur_s = cand, s
        if best is None or s > best[0]:
            best = (s, sorted(cand))
            if s == (0, 1):
                arcs, w = build(sorted(cand))
                print("WEIGHTED COUNTEREXAMPLE FOUND (validation target):")
                print("n =", N, "arcs =", arcs, "w =", w)
                ok1, _ = pack_w(N, arcs, w, 1)
                print("pack k=1 feasible (nu>=1):", ok1)
                return
        if it % 200 == 0:
            print(f"[{time.time()-t0:6.0f}s] it={it} cur={cur_s} "
                  f"best={best[0]}", flush=True)
    print("not found; best =", best)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1200,
         int(sys.argv[2]) if len(sys.argv) > 2 else 0)
