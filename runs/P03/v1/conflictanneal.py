"""Anneal (4,3)-biregular p=12/q=16 instances to MAXIMIZE CaDiCaL conflict
count on the 3-dijoin-partition SAT encoding — hunting the UNSAT boundary
directly (an actual counterexample would be a hard UNSAT instance; SAT
instances near it should show high conflict counts)."""
import random
import sys
import time
from bipsearch import min_dicuts_bip
from pysat.solvers import Cadical153

P, Q = 12, 16


def build_clauses(sinks, cuts):
    k = 3
    ids = {}

    def var(a, c):
        key = (a, c)
        if key not in ids:
            ids[key] = len(ids) + 1
        return ids[key]

    arcs = [(t, pos) for t in range(len(sinks)) for pos in range(3)]
    cl = []
    for a in arcs:
        cl.append([var(a, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cl.append([-var(a, c1), -var(a, c2)])
    for cut in cuts:
        for c in range(k):
            cl.append([var(a, c) for a in cut])
    return cl


def score(sinks):
    cuts, tau = min_dicuts_bip(P, sinks)
    if cuts is None or tau != 3:
        return None, None
    s = Cadical153(bootstrap_with=build_clauses(sinks, cuts))
    sat = s.solve()
    st = s.accum_stats()
    return sat, st.get("conflicts", 0)


def rand_inst(rng):
    while True:
        stubs = [s for s in range(P) for _ in range(4)]
        rng.shuffle(stubs)
        sinks = [sorted(stubs[3 * t:3 * t + 3]) for t in range(Q)]
        if all(len(set(t)) == 3 for t in sinks):
            return sinks


def main(seconds, seed):
    rng = random.Random(seed)
    cur = rand_inst(rng)
    sat, sc = score(cur)
    while sc is None:
        cur = rand_inst(rng)
        sat, sc = score(cur)
    best = sc
    n = 0
    t0 = time.time()
    while time.time() - t0 < seconds:
        cand = [list(t) for t in cur]
        for _ in range(rng.choice([1, 1, 2])):
            while True:
                t1, t2 = rng.randrange(Q), rng.randrange(Q)
                i1, i2 = rng.randrange(3), rng.randrange(3)
                u1, u2 = cand[t1][i1], cand[t2][i2]
                if u1 != u2 and u2 not in cand[t1] and u1 not in cand[t2]:
                    cand[t1][i1], cand[t2][i2] = u2, u1
                    cand[t1].sort()
                    cand[t2].sort()
                    break
        sat, sc = score(cand)
        n += 1
        if sc is None:
            continue
        if not sat:
            print("UNSAT COUNTEREXAMPLE", cand, flush=True)
            with open("counterexample.txt", "a") as f:
                f.write("CONFLICTANNEAL %r\n" % (cand,))
            return
        if sc >= best or rng.random() < 0.02:
            cur = cand
            if sc > best:
                best = sc
                print(f"[confl seed={seed}] n={n} best_conflicts={best}",
                      flush=True)
        if n % 2000 == 0:
            print(f"[confl seed={seed}] n={n} best={best}", flush=True)
    print(f"[confl seed={seed}] DONE n={n} best_conflicts={best}", flush=True)


if __name__ == "__main__":
    main(float(sys.argv[1]), int(sys.argv[2]))
