#!/usr/bin/env python3
"""Retry UNKNOWN (t,r) affine-orbit classes from a multcp log with longer budget.

Usage: mult_retry.py n k logfile tl_seconds
"""
import json, os, re, sys
import mult_cpsat as mc
from ortools.sat.python import cp_model

n, k = int(sys.argv[1]), int(sys.argv[2])
log, tl = sys.argv[3], int(sys.argv[4])
pairs = []
for line in open(log):
    m = re.match(r"t=(\d+),r=(\d+): (\d+) orbits -> UNKNOWN", line)
    if m:
        pairs.append((int(m.group(1)), int(m.group(2))))
print(f"{len(pairs)} UNKNOWN classes, tl={tl}", flush=True)


def solve_one_tl(orbs):
    import collections
    from math import isqrt
    s = isqrt(k)
    m = len(orbs)
    oidx = [0] * n
    for i, o in enumerate(orbs):
        for p in o:
            oidx[p] = i
    model = cp_model.CpModel()
    v = [model.NewIntVar(-1, 1, f"v{i}") for i in range(m)]
    av = [model.NewIntVar(0, 1, f"a{i}") for i in range(m)]
    for i in range(m):
        model.AddAbsEquality(av[i], v[i])
    sizes = [len(o) for o in orbs]
    model.Add(sum(sizes[i] * av[i] for i in range(m)) == k)
    model.Add(sum(sizes[i] * v[i] for i in range(m)) == s)
    prod = {}
    for i in range(m):
        for j in range(i, m):
            p = model.NewIntVar(-1, 1, f"p{i}_{j}")
            model.AddMultiplicationEquality(p, [v[i], v[j]])
            prod[(i, j)] = p
    for u in range(1, n // 2 + 1):
        cnt = {}
        for p in range(n):
            i, j = oidx[p], oidx[(p + u) % n]
            key = (min(i, j), max(i, j))
            cnt[key] = cnt.get(key, 0) + 1
        model.Add(sum(c * prod[key] for key, c in cnt.items()) == 0)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 4
    solver.parameters.max_time_in_seconds = tl
    st = solver.Solve(model)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        vals = [solver.Value(x) for x in v]
        a = [0] * n
        for i, o in enumerate(orbs):
            for p in o:
                a[p] = vals[i]
        return "SAT", a
    return ("UNSAT" if st == cp_model.INFEASIBLE else "UNKNOWN"), None


stats = {"UNSAT": 0, "UNKNOWN": 0}
for (t, r) in pairs:
    orbs = mc.orbits_of(n, t, r)
    res, a = solve_one_tl(orbs)
    print(f"t={t},r={r}: {len(orbs)} orbits -> {res}", flush=True)
    if res == "SAT":
        assert sum(x * x for x in a) == k
        for u in range(1, n):
            assert sum(a[i] * a[(i + u) % n] for i in range(n)) == 0, u
        wp = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"witness_mult_{n}_{k}.json")
        json.dump({"n": n, "k": k, "row": a}, open(wp, "w"))
        print(f"HIT WITNESS {wp}", flush=True)
        break
    stats[res] += 1
print("RETRY DONE", stats, flush=True)
