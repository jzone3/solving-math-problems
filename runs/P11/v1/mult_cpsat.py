#!/usr/bin/env python3
"""Complete CP-SAT search over multiplier/affine-orbit-invariant CW(n,k) rows.

For each affine bijection phi(j) = t*j + r (t unit mod n) with at most
max_orbits orbits, model one ternary variable per orbit and solve exactly:
  sum sizes over nonzero orbits = k, signed size sum = sqrt(k),
  PAF_a(u) = sum_{O,O'} v_O v_O' * |{(i in O): i+u in O'}| = 0 for u=1..n/2.
CP-SAT decides each (t,r) completely in seconds (<= ~34 ternary vars).

Usage: mult_cpsat.py n k max_orbits [--affine]
"""
import json, os, sys
from math import gcd, isqrt
from ortools.sat.python import cp_model

HERE = os.path.dirname(os.path.abspath(__file__))


def orbits_of(n, t, r=0):
    seen = [False] * n
    orbs = []
    for j in range(n):
        if seen[j]:
            continue
        o = []
        x = j
        while not seen[x]:
            seen[x] = True
            o.append(x)
            x = (x * t + r) % n
        orbs.append(o)
    return orbs


def solve_one(n, k, orbs):
    s = isqrt(k)
    m = len(orbs)
    oidx = [0] * n
    for i, o in enumerate(orbs):
        for p in o:
            oidx[p] = i
    # cross-correlation counts C[u][i][j] = #{p in orb_i : (p+u) mod n in orb_j}
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
    import collections
    for u in range(1, n // 2 + 1):
        cnt = collections.Counter()
        for p in range(n):
            i, j = oidx[p], oidx[(p + u) % n]
            cnt[(min(i, j), max(i, j))] += 1
        model.Add(sum(c * prod[key] for key, c in cnt.items()) == 0)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 2
    solver.parameters.max_time_in_seconds = 120
    st = solver.Solve(model)
    if st == cp_model.OPTIMAL or st == cp_model.FEASIBLE:
        vals = [solver.Value(x) for x in v]
        a = [0] * n
        for i, o in enumerate(orbs):
            for p in o:
                a[p] = vals[i]
        return "SAT", a
    return ("UNSAT" if st == cp_model.INFEASIBLE else "UNKNOWN"), None


def main():
    n, k = int(sys.argv[1]), int(sys.argv[2])
    mo = int(sys.argv[3])
    affine = "--affine" in sys.argv
    tried = set()
    stats = {"UNSAT": 0, "UNKNOWN": 0, "skipped": 0}
    for t in range(2, n):
        if gcd(t, n) != 1:
            continue
        for r in (range(n) if affine else (0,)):
            orbs = orbits_of(n, t, r)
            key = tuple(sorted(tuple(sorted(o)) for o in orbs))
            if key in tried:
                continue
            tried.add(key)
            if len(orbs) > mo:
                stats["skipped"] += 1
                continue
            res, a = solve_one(n, k, orbs)
            print(f"t={t},r={r}: {len(orbs)} orbits -> {res}", flush=True)
            if res == "SAT":
                # exact check
                assert sum(x * x for x in a) == k
                for u in range(1, n):
                    assert sum(a[i] * a[(i + u) % n] for i in range(n)) == 0, u
                wp = os.path.join(HERE, f"witness_mult_{n}_{k}.json")
                json.dump({"n": n, "k": k, "row": a}, open(wp, "w"))
                print(f"HIT t={t},r={r} WITNESS {wp}", flush=True)
                return
            stats[res] += 1
    print("DONE", stats, flush=True)


if __name__ == "__main__":
    main()
