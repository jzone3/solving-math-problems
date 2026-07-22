"""V3 tau=3-targeted search for a Woodall counterexample.

Strategy (per problem file V3): restrict to digraphs with min dicut exactly 3 and
use ACZ (Abdi-Cornuejols-Zlatin 2022/23) structural conditions to prune:
  - a tau=3 counterexample must have rho(3,D,1) >= 4  (ACZ handle rho in {0,1,2,3})
    => sum_v ((outdeg-indeg) mod 3) >= 12  => at least 6 vertices with imbalance
    not divisible by 3 => n >= 6.
  - must NOT be source-sink connected (Schrijver / Feofiloff-Younger safe class)
  - underlying graph must be non-planar (Lucchesi-Younger duality safe class)

Modes:
  random  - random generation + repair to tau=3, filter, SAT-check packing
  anneal  - hill-climb maximizing constraint density (# size-3 minimal dicuts),
            SAT-check each accepted candidate

Any UNSAT candidate (tau=3, no 3 disjoint dijoins) is dumped to witness_*.json.
"""
import json
import random
import sys
import time

from core import (enumerate_dicuts, minimal_dicuts, tau, rho3,
                  is_weakly_connected, is_source_sink_connected,
                  underlying_planar, pack3_sat)

STATS = {"generated": 0, "tau3": 0, "rho_ok": 0, "not_ss": 0, "nonplanar": 0,
         "sat_checked": 0, "unsat": 0}


def status(n, arcs):
    """Return (tau, dicuts) or (None, None) if degenerate."""
    if not is_weakly_connected(n, arcs):
        return None, None
    d = enumerate_dicuts(n, arcs)
    if not d:
        return None, None
    return tau(d), d


def repair_to_tau3(n, arcs, rng, max_steps=400):
    """Local repair: add arcs across small dicuts / delete arcs while tau>3."""
    arcs = list(arcs)
    for _ in range(max_steps):
        t, d = status(n, arcs)
        if t is None:
            # add a random arc to connect / create structure
            u, v = rng.sample(range(n), 2)
            arcs.append((u, v))
            continue
        if t == 3:
            return arcs
        if t < 3:
            # pick a min dicut, widen it: add a parallel-ish arc across it
            small = rng.choice([x for x in d if len(x) == t])
            # dicut given by arc indices; recover U side heads/tails
            tails = {arcs[i][0] for i in small}
            heads = {arcs[i][1] for i in small}
            u = rng.choice(sorted(tails))
            v = rng.choice(sorted(heads))
            arcs.append((u, v))
        else:
            # tau > 3: remove a random arc from a min dicut
            small = rng.choice([x for x in d if len(x) == t])
            i = rng.choice(sorted(small))
            arcs.pop(i)
    return None


def gen_random(rng, n_lo=6, n_hi=12, m_factor=(1.5, 3.0)):
    n = rng.randint(n_lo, n_hi)
    m = int(n * rng.uniform(*m_factor))
    arcs = []
    for _ in range(m):
        u, v = rng.sample(range(n), 2)
        arcs.append((u, v))
    return n, arcs


def passes_filters(n, arcs, dicuts):
    STATS["tau3"] += 1
    if rho3(n, arcs) <= 3:
        return False
    STATS["rho_ok"] += 1
    if is_source_sink_connected(n, arcs):
        return False
    STATS["not_ss"] += 1
    if underlying_planar(n, arcs):
        return False
    STATS["nonplanar"] += 1
    return True


def sat_check_and_record(n, arcs, dicuts, tag):
    md = minimal_dicuts(dicuts)
    STATS["sat_checked"] += 1
    ok = pack3_sat(arcs, md)
    if not ok:
        STATS["unsat"] += 1
        fn = f"witness_{tag}_{int(time.time())}.json"
        with open(fn, "w") as f:
            json.dump({"n": n, "arcs": arcs, "n_min_dicuts": len(md)}, f)
        print(f"!!! UNSAT CANDIDATE SAVED: {fn}", flush=True)
        return True
    return False


def run_random(seed, minutes, n_lo=6, n_hi=12):
    rng = random.Random(seed)
    t0 = time.time()
    last = t0
    while time.time() - t0 < minutes * 60:
        STATS["generated"] += 1
        n, arcs = gen_random(rng, n_lo, n_hi)
        arcs = repair_to_tau3(n, arcs, rng)
        if arcs is None:
            continue
        t, d = status(n, arcs)
        if t != 3:
            continue
        if not passes_filters(n, arcs, d):
            continue
        sat_check_and_record(n, arcs, d, "rand")
        if time.time() - last > 60:
            last = time.time()
            print(f"[{int(time.time()-t0)}s] {STATS}", flush=True)
    print("FINAL", STATS, flush=True)


def score(n, arcs, dicuts):
    md = minimal_dicuts(dicuts)
    tight = sum(1 for d in md if len(d) == 3)
    return tight * 10 + len(md), md


def mutate(n, arcs, rng):
    arcs = list(arcs)
    op = rng.random()
    if op < 0.35 or len(arcs) < 8:
        u, v = rng.sample(range(n), 2)
        arcs.append((u, v))
    elif op < 0.6:
        i = rng.randrange(len(arcs))
        u, v = arcs[i]
        arcs[i] = (v, u)
    elif op < 0.85:
        i = rng.randrange(len(arcs))
        u, v = arcs[i]
        w = rng.randrange(n)
        arcs[i] = (u, w) if rng.random() < 0.5 else (w, v)
        if arcs[i][0] == arcs[i][1]:
            arcs.pop(i)
    else:
        arcs.pop(rng.randrange(len(arcs)))
    return arcs


def run_anneal(seed, minutes, n_lo=6, n_hi=12, restart_steps=3000):
    rng = random.Random(seed)
    t0 = time.time()
    last = t0
    best_ever = 0
    while time.time() - t0 < minutes * 60:
        n, arcs = gen_random(rng, n_lo, n_hi)
        arcs = repair_to_tau3(n, arcs, rng)
        if arcs is None:
            continue
        t, d = status(n, arcs)
        if t != 3:
            continue
        cur_score, _ = score(n, arcs, d)
        steps_since_improve = 0
        while steps_since_improve < restart_steps and time.time() - t0 < minutes * 60:
            STATS["generated"] += 1
            cand = mutate(n, arcs, rng)
            cand = repair_to_tau3(n, cand, rng, max_steps=60)
            if cand is None:
                steps_since_improve += 1
                continue
            t2, d2 = status(n, cand)
            if t2 != 3:
                steps_since_improve += 1
                continue
            s2, _ = score(n, cand, d2)
            if s2 >= cur_score:  # accept equal to drift on plateaus
                improved = s2 > cur_score
                arcs, cur_score = cand, s2
                if passes_filters(n, cand, d2):
                    if sat_check_and_record(n, cand, d2, "anneal"):
                        return
                if improved:
                    steps_since_improve = 0
                    if s2 > best_ever:
                        best_ever = s2
                else:
                    steps_since_improve += 1
            else:
                steps_since_improve += 1
            if time.time() - last > 60:
                last = time.time()
                print(f"[{int(time.time()-t0)}s] best={best_ever} cur={cur_score} {STATS}",
                      flush=True)
    print("FINAL best_ever_score", best_ever, STATS, flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    seed = int(sys.argv[2])
    minutes = float(sys.argv[3])
    n_lo = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    n_hi = int(sys.argv[5]) if len(sys.argv) > 5 else 12
    if mode == "random":
        run_random(seed, minutes, n_lo, n_hi)
    else:
        run_anneal(seed, minutes, n_lo, n_hi)
