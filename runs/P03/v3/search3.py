"""V3 third-stage searcher: anneal MINIMIZING the number of valid 3-colorings.

Within the filtered class (tau=3, rho>=4, not ss-connected, non-planar), the number of
partitions of A into 3 dijoin classes is a direct gradient toward UNSAT (a counterexample
has 0). We count models with pysat enumeration capped at CAP; score = capped count
(color-permutation symmetry means counts are multiples of 6; CAP generous).
"""
import json
import random
import sys
import time

from pysat.solvers import Minicard
from core import (minimal_dicuts, rho3, is_source_sink_connected,
                  underlying_planar)
from search2 import status, gen_structured, repair_to_tau3, mutate, STATS

CAP = 600


def count_colorings(arcs, md, cap=CAP):
    m = len(arcs)
    cnf = []
    for i in range(m):
        vs = [3 * i + c + 1 for c in range(3)]
        cnf.append(vs)
        cnf.append([-vs[0], -vs[1]])
        cnf.append([-vs[0], -vs[2]])
        cnf.append([-vs[1], -vs[2]])
    for d in md:
        for c in range(3):
            cnf.append([3 * i + c + 1 for i in d])
    cnt = 0
    with Minicard(bootstrap_with=cnf) as s:
        while s.solve() and cnt < cap:
            cnt += 1
            model = s.get_model()
            s.add_clause([-l for l in model[:3 * m] if l > 0])
    return cnt


def full_pass(n, arcs):
    return (rho3(n, arcs) >= 4 and not is_source_sink_connected(n, arcs)
            and not underlying_planar(n, arcs))


def run(seed, minutes, n_lo=8, n_hi=13, restart_steps=800, max_arcs=32):
    rng = random.Random(seed)
    t0 = time.time()
    last = t0
    best_ever = CAP + 1
    while time.time() - t0 < minutes * 60:
        STATS["restarts"] += 1
        n, arcs = gen_structured(rng, n_lo, n_hi)
        arcs = repair_to_tau3(n, arcs, rng)
        if arcs is None:
            continue
        t, d = status(n, arcs)
        if t != 3 or not full_pass(n, arcs):
            continue
        md = minimal_dicuts(d)
        cur = count_colorings(arcs, md)
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
            if t2 != 3 or not full_pass(n, cand):
                stale += 1
                continue
            md2 = minimal_dicuts(d2)
            c2 = count_colorings(cand, md2)
            STATS["sat_checked"] += 1
            if c2 == 0:
                STATS["unsat"] += 1
                fn = f"witness_s3_{int(time.time())}.json"
                with open(fn, "w") as f:
                    json.dump({"n": n, "arcs": cand}, f)
                print(f"!!! UNSAT CANDIDATE SAVED: {fn}", flush=True)
                return
            if c2 <= cur:
                stale = 0 if c2 < cur else stale + 1
                arcs, cur = cand, c2
                if c2 < best_ever:
                    best_ever = c2
                    print(f"[{int(time.time()-t0)}s] new min colorings={c2} "
                          f"(n={n}, m={len(cand)})", flush=True)
            else:
                stale += 1
            if time.time() - last > 120:
                last = time.time()
                print(f"[{int(time.time()-t0)}s] best={best_ever} cur={cur} {STATS}",
                      flush=True)
    print("FINAL best min colorings", best_ever, STATS, flush=True)


if __name__ == "__main__":
    run(int(sys.argv[1]), float(sys.argv[2]),
        int(sys.argv[3]) if len(sys.argv) > 3 else 8,
        int(sys.argv[4]) if len(sys.argv) > 4 else 13)
