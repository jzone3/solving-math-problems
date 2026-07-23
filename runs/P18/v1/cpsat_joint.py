#!/usr/bin/env python3
"""
CP-SAT (OR-Tools) model of the joint two-family m-space problem (same
semantics as gen_cnf_m.py): two disjoint subsets of M = {m : 2m+1 prime}
dividing N, each covering Z/N with distinct moduli. Modulus 2 (if present)
forced to family A. SAT => witness lifted to n-space (re-verify with
solutions/P18/verify.py). INFEASIBLE => negative for this pool only.

Usage: cpsat_joint.py N [time_limit_s] [workers]
"""
import json
import sys

from ortools.sat.python import cp_model

from gen_cnf_m import is_prime, divisors


def main():
    N = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 3600.0
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    M = [d for d in divisors(N) if d >= 2 and is_prime(2 * d + 1)]
    print("N=%d |M|=%d" % (N, len(M)), flush=True)
    mdl = cp_model.CpModel()
    x = {}
    for m in M:
        for a in range(m):
            for f in (0, 1):
                x[(m, a, f)] = mdl.new_bool_var("x_%d_%d_%d" % (m, a, f))
        mdl.add_at_most_one([x[(m, a, f)] for a in range(m) for f in (0, 1)])
    if 2 in M:
        mdl.add(x[(2, 0, 1)] == 0)
        mdl.add(x[(2, 1, 1)] == 0)
    for f in (0, 1):
        for r in range(N):
            mdl.add_bool_or([x[(m, r % m, f)] for m in M])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_workers = workers
    solver.parameters.log_search_progress = False
    st = solver.solve(mdl)
    print("status:", solver.status_name(st), flush=True)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        congs = []
        for (m, a, f), v in x.items():
            if solver.value(v):
                n = 2 * m
                congs.append([(2 * a) % n if f == 0 else (2 * a + 1) % n, n])
        fn = "witness_cpsat_N%d.json" % N
        json.dump({"congruences": congs}, open(fn, "w"))
        print("SUCCESS %d congruences -> %s" % (len(congs), fn))


if __name__ == "__main__":
    main()
