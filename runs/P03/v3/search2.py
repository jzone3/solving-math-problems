"""V3 improved search: structured generator + soft-constraint annealing.

Target class (necessary conditions for a tau=3 Woodall counterexample):
  tau = 3, rho(3,D,1) >= 4 (ACZ), not source-sink connected (Schrijver),
  underlying graph non-planar (Lucchesi-Younger).

Improvements over search.py:
  - gen_structured: two sources / two sinks layered so s1 cannot reach t2.
  - soft score: reward not_ss, rho>=4, nonplanarity, tight (size-3) minimal dicuts.
  - parallel-arc balancing: adding an arc parallel to an existing arc preserves
    reachability (not_ss) and underlying simple graph (planarity) while shifting
    degree imbalances mod 3 -> steer rho upward.
"""
import json
import random
import sys
import time

from core import (enumerate_dicuts, minimal_dicuts, tau, rho3,
                  is_weakly_connected, is_source_sink_connected,
                  underlying_planar, pack3_sat)

STATS = {"iters": 0, "tau3": 0, "full_pass": 0, "sat_checked": 0, "unsat": 0,
         "restarts": 0}


def status(n, arcs):
    if not arcs or not is_weakly_connected(n, arcs):
        return None, None
    d = enumerate_dicuts(n, arcs)
    if not d:
        return None, None
    return tau(d), d


def gen_structured(rng, n_lo=8, n_hi=13):
    """s1 -> M1 -> t1 ; s2 -> M2 -> t2 ; arcs M2->M1 allowed, M1->M2 forbidden.

    Then s1 reaches {M1,t1} only => s1 cannot reach t2 => not ss-connected,
    as long as no later mutation creates a path (checked by filters/score).
    """
    n = rng.randint(n_lo, n_hi)
    mids = list(range(4, n))
    rng.shuffle(mids)
    half = len(mids) // 2
    M1, M2 = mids[:half], mids[half:]
    s1, t1, s2, t2 = 0, 1, 2, 3
    arcs = []
    for _ in range(3):  # tau=3 needs sources outdeg>=3, sinks indeg>=3
        arcs.append((s1, rng.choice(M1)))
        arcs.append((s2, rng.choice(M2 + M1)))
        arcs.append((rng.choice(M1), t1))
        arcs.append((rng.choice(M2), t2))
    extra = rng.randint(len(mids), 3 * len(mids))
    for _ in range(extra):
        u = rng.choice(mids)
        pool = M1 + [t1] if u in M1 else M1 + M2 + [t1, t2]
        v = rng.choice(pool)
        if u != v:
            arcs.append((u, v))
    return n, arcs


def repair_to_tau3(n, arcs, rng, max_steps=200):
    arcs = list(arcs)
    for _ in range(max_steps):
        t, d = status(n, arcs)
        if t is None:
            u, v = rng.sample(range(n), 2)
            arcs.append((u, v))
            continue
        if t == 3:
            return arcs
        if t < 3:
            small = rng.choice([x for x in d if len(x) == t])
            tails = sorted({arcs[i][0] for i in small})
            heads = sorted({arcs[i][1] for i in small})
            # prefer duplicating an existing arc of the dicut (parallel: safe)
            if rng.random() < 0.7:
                i = rng.choice(sorted(small))
                arcs.append(arcs[i])
            else:
                arcs.append((rng.choice(tails), rng.choice(heads)))
        else:
            small = rng.choice([x for x in d if len(x) == t])
            arcs.pop(rng.choice(sorted(small)))
    return None


def soft_score(n, arcs, dicuts):
    md = minimal_dicuts(dicuts)
    tight = sum(1 for d in md if len(d) == 3)
    r = rho3(n, arcs)
    s = tight * 5 + len(md)
    s += 4000 if not is_source_sink_connected(n, arcs) else 0
    s += 1000 * min(r, 4)
    s += 2000 if not underlying_planar(n, arcs) else 0
    full = s >= 4000 + 4000 + 2000
    return s, full, md


def mutate(n, arcs, rng):
    arcs = list(arcs)
    op = rng.random()
    if op < 0.30 or len(arcs) < 10:
        if rng.random() < 0.5:  # parallel duplicate (reach/planarity safe)
            arcs.append(arcs[rng.randrange(len(arcs))])
        else:
            u, v = rng.sample(range(n), 2)
            arcs.append((u, v))
    elif op < 0.55:
        i = rng.randrange(len(arcs))
        u, v = arcs[i]
        arcs[i] = (v, u)
    elif op < 0.80:
        i = rng.randrange(len(arcs))
        u, v = arcs[i]
        w = rng.randrange(n)
        arcs[i] = (u, w) if rng.random() < 0.5 else (w, v)
        if arcs[i][0] == arcs[i][1]:
            arcs.pop(i)
    else:
        arcs.pop(rng.randrange(len(arcs)))
    return arcs


def sat_check_and_record(n, arcs, md, tag):
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


def run(seed, minutes, n_lo=8, n_hi=13, restart_steps=1500, max_arcs=34):
    rng = random.Random(seed)
    t0 = time.time()
    last = t0
    best_ever = 0
    seen_full = set()
    while time.time() - t0 < minutes * 60:
        STATS["restarts"] += 1
        n, arcs = gen_structured(rng, n_lo, n_hi)
        arcs = repair_to_tau3(n, arcs, rng)
        if arcs is None:
            continue
        t, d = status(n, arcs)
        if t != 3:
            continue
        cur, full, md = soft_score(n, arcs, d)
        stale = 0
        while stale < restart_steps and time.time() - t0 < minutes * 60:
            STATS["iters"] += 1
            cand = mutate(n, arcs, rng)
            if len(cand) > max_arcs:
                stale += 1
                continue
            cand = repair_to_tau3(n, cand, rng, max_steps=40)
            if cand is None:
                stale += 1
                continue
            t2, d2 = status(n, cand)
            if t2 != 3:
                stale += 1
                continue
            STATS["tau3"] += 1
            s2, full2, md2 = soft_score(n, cand, d2)
            if s2 >= cur:
                improved = s2 > cur
                arcs, cur, d = cand, s2, d2
                if full2:
                    key = (n, tuple(sorted(cand)))
                    if key not in seen_full:
                        seen_full.add(key)
                        STATS["full_pass"] += 1
                        if sat_check_and_record(n, cand, md2, "s2"):
                            return
                stale = 0 if improved else stale + 1
                best_ever = max(best_ever, s2)
            else:
                stale += 1
            if time.time() - last > 120:
                last = time.time()
                print(f"[{int(time.time()-t0)}s] best={best_ever} cur={cur} {STATS}",
                      flush=True)
    print("FINAL best", best_ever, STATS, flush=True)


if __name__ == "__main__":
    seed = int(sys.argv[1])
    minutes = float(sys.argv[2])
    n_lo = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    n_hi = int(sys.argv[4]) if len(sys.argv) > 4 else 13
    run(seed, minutes, n_lo, n_hi)
