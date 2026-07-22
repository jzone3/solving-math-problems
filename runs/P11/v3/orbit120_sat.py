#!/usr/bin/env python3
"""Decide CW(120,49) by complete multiplier-orbit search via CP-SAT.

AGZ Thm 2.4 (classical): k = 49 = 7^2, gcd(120,49) = 1 => 7 is a multiplier of
any CW(120,49) and fixes some translate. Hence some translate of the first row
is constant on <7>-orbits of Z_120 (<7> = {1,7,49,103}, order 4). Searching all
{0,±1} orbit assignments with weight 49 and flat PACF is therefore a COMPLETE
decision procedure for the cell: UNSAT => no CW(120,49) exists.

PACF(t) = sum_{i,j} v_i v_j C[i,j,t], C[i,j,t] = #{(x,y) in O_i x O_j: y-x=t}.
"""
import sys
import numpy as np
from ortools.sat.python import cp_model

sys.path.insert(0, "../../../solutions/P11")
from verify import check, is_proper
from icw_enum import orbits_of

n, k = 120, 49
orbs = orbits_of(7, n)
sizes = [len(o) for o in orbs]
no = len(orbs)
print(f"{no} orbits, sizes {sorted(sizes)}")

C = np.zeros((no, no, n), dtype=np.int64)
for i, oi in enumerate(orbs):
    for j, oj in enumerate(orbs):
        for x in oi:
            for y in oj:
                C[i, j, (y - x) % n] += 1

model = cp_model.CpModel()
v = [model.NewIntVar(-1, 1, f"v{i}") for i in range(no)]
pr = {}
for i in range(no):
    for j in range(i, no):
        p = model.NewIntVar(-1, 1, f"p{i}_{j}")
        model.AddMultiplicationEquality(p, [v[i], v[j]])
        pr[(i, j)] = p

model.Add(sum(int(sizes[i]) * pr[(i, i)] for i in range(no)) == k)
for t in range(1, n // 2 + 1):
    terms = []
    for i in range(no):
        for j in range(i, no):
            c = int(C[i, j, t] + C[j, i, t]) if j > i else int(C[i, i, t])
            if c:
                terms.append(c * pr[(i, j)])
    model.Add(sum(terms) == 0)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 3600
solver.parameters.num_search_workers = 3
solver.parameters.log_search_progress = False
st = solver.Solve(model)
print("status:", solver.StatusName(st))
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    a = [0] * n
    for i, o in enumerate(orbs):
        for x in o:
            a[x] = solver.Value(v[i])
    P = [i for i, x in enumerate(a) if x == 1]
    N = [i for i, x in enumerate(a) if x == -1]
    check(n, k, P, N, proper=False)
    print("SOLUTION proper=", is_proper(n, P, N))
    print("P =", P)
    print("N =", N)
elif st == cp_model.INFEASIBLE:
    print("UNSAT: no <7>-fixed row => no CW(120,49) exists (via AGZ Thm 2.4)")
