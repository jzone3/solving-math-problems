"""Min-#colorings gradient annealer inside the ACZ-complete (3,4)-bipartite class."""
import json
import random
import sys
import time

from pysat.solvers import Minicard
from bip import all_min_dicuts, gen_random, swap_mutate, nonplanar

CAP = 400


def count_colorings(m, md, cap=CAP):
    cnf = []
    for i in range(m):
        vs = [3 * i + 1, 3 * i + 2, 3 * i + 3]
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


def run(seed, minutes, n4, n3, restart_steps=500):
    rng = random.Random(seed)
    t0 = time.time()
    last = t0
    m = 4 * n4 + 3 * n3
    best_ever = CAP + 1
    stats = {"iters": 0, "valid": 0, "restarts": 0}
    while time.time() - t0 < minutes * 60:
        stats["restarts"] += 1
        nbrs, nT = gen_random(rng, n4, n3)
        tau, md = all_min_dicuts(nbrs, nT)
        if tau is None or tau < 3:
            continue
        cur = count_colorings(m, md)
        stale = 0
        while stale < restart_steps and time.time() - t0 < minutes * 60:
            stats["iters"] += 1
            cand = swap_mutate(nbrs, nT, rng)
            if cand is None:
                stale += 1
                continue
            tau2, md2 = all_min_dicuts(cand, nT)
            if tau2 is None or tau2 < 3:
                stale += 1
                continue
            stats["valid"] += 1
            c2 = count_colorings(m, md2)
            if c2 == 0 and nonplanar(cand, nT):
                fn = f"witness_bip3_{int(time.time())}.json"
                with open(fn, "w") as f:
                    json.dump({"n4": n4, "n3": n3, "nT": nT,
                               "nbrs": [list(nb) for nb in cand]}, f)
                print(f"!!! UNSAT BIPARTITE CANDIDATE: {fn}", flush=True)
                return
            if c2 <= cur:
                stale = 0 if c2 < cur else stale + 1
                nbrs, cur = cand, c2
                if c2 < best_ever:
                    best_ever = c2
                    print(f"[{int(time.time()-t0)}s] min colorings={c2}", flush=True)
            else:
                stale += 1
            if time.time() - last > 180:
                last = time.time()
                print(f"[{int(time.time()-t0)}s] best={best_ever} cur={cur} {stats}",
                      flush=True)
    print(f"FINAL best min colorings={best_ever} {stats}", flush=True)


if __name__ == "__main__":
    run(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
