#!/usr/bin/env python3
"""AGZ-style orbit-table (intersection number) decision attempt for CW(120,49).

Z_120 = Z_8 x Z_15 (coprime). Multiplier 7 fixes a translate (AGZ Thm 2.4), so
the first row is constant on <7>-orbits of Z_120, and its contractions mod 8
and mod 15 are <7>-fixed ICW_15(8,49) and ICW_8(15,49) respectively.

Stage 1: enumerate both small ICW sets exactly.
Stage 2: for each compatible pair, enumerate all {0,±1} orbit assignments
consistent with BOTH contractions (CP-SAT enumeration over 39 ternary vars
with 8+15 linear equality constraints + weight), checking full PACF for each.
If stage-2 enumeration completes for all pairs with no PACF-flat solution,
CW(120,49) does not exist. If it does not complete, we learn solution counts.
"""
import sys
import numpy as np
from itertools import product
from ortools.sat.python import cp_model

sys.path.insert(0, ".")
sys.path.insert(0, "../../../solutions/P11")
from icw_enum import orbits_of
from verify import check, is_proper

n, k = 120, 49


def fixed_icws(m, d, t):
    """all <t>-fixed integer vectors on Z_m, |w|<=d, flat ACF, norm k."""
    orbs = orbits_of(t, m)
    sizes = [len(o) for o in orbs]
    sols = []
    for cs in product(*[range(-d, d + 1) for _ in orbs]):
        if sum(c * c * s for c, s in zip(cs, sizes)) != k:
            continue
        w = [0] * m
        for c, o in zip(cs, orbs):
            for x in o:
                w[x] = c
        if all(sum(w[i] * w[(i + s) % m] for i in range(m)) == 0
               for s in range(1, m)):
            sols.append(tuple(w))
    return sols


S8 = fixed_icws(8, 15, 7)
S15 = fixed_icws(15, 8, 7)
print(f"fixed ICW_15(8,49): {len(S8)};  fixed ICW_8(15,49): {len(S15)}",
      flush=True)

orbs = orbits_of(7, n)
no = len(orbs)
sizes = [len(o) for o in orbs]
# counts of orbit elements in each residue class
n8 = [[sum(1 for x in o if x % 8 == j) for j in range(8)] for o in orbs]
n15 = [[sum(1 for x in o if x % 15 == j) for j in range(15)] for o in orbs]

C = np.zeros((no, no, n), dtype=np.int64)
for i, oi in enumerate(orbs):
    for j, oj in enumerate(orbs):
        for x in oi:
            for y in oj:
                C[i, j, (y - x) % n] += 1


class Collector(cp_model.CpSolverSolutionCallback):
    def __init__(self, v):
        super().__init__()
        self.v = v
        self.count = 0
        self.hits = []

    def on_solution_callback(self):
        self.count += 1
        vals = np.array([self.Value(x) for x in self.v], dtype=np.int64)
        acf = np.einsum("i,j,ijt->t", vals, vals, C)
        if not acf[1:].any():
            self.hits.append(vals.copy())
            print("PACF-FLAT HIT:", vals.tolist(), flush=True)
        if self.count % 100000 == 0:
            print(f"  ...{self.count} lattice solutions", flush=True)


total = 0
for a8, w8 in enumerate(S8):
    for a15, w15 in enumerate(S15):
        if sum(w8) != sum(w15):  # row sum consistency (= ±7)
            continue
        model = cp_model.CpModel()
        v = [model.NewIntVar(-1, 1, f"v{i}") for i in range(no)]
        sq = []
        for i in range(no):
            b = model.NewIntVar(0, 1, f"b{i}")
            model.AddAbsEquality(b, v[i])
            sq.append(b)
        model.Add(sum(sizes[i] * sq[i] for i in range(no)) == k)
        for j in range(8):
            model.Add(sum(n8[i][j] * v[i] for i in range(no)) == w8[j])
        for j in range(15):
            model.Add(sum(n15[i][j] * v[i] for i in range(no)) == w15[j])
        solver = cp_model.CpSolver()
        solver.parameters.enumerate_all_solutions = True
        solver.parameters.max_time_in_seconds = 86400
        cb = Collector(v)
        st = solver.Solve(model, cb)
        total += cb.count
        print(f"pair ({a8},{a15}): {cb.count} lattice sols, "
              f"{len(cb.hits)} PACF-flat, status {solver.StatusName(st)}",
              flush=True)
        for vals in cb.hits:
            a = [0] * n
            for i, o in enumerate(orbs):
                for x in o:
                    a[x] = int(vals[i])
            P = [i for i, x in enumerate(a) if x == 1]
            N = [i for i, x in enumerate(a) if x == -1]
            check(n, k, P, N, proper=False)
            print("VERIFIED CW(120,49)!! proper =", is_proper(n, P, N))
            print("P =", P, "\nN =", N)

print(f"TOTAL lattice solutions checked: {total}")
print("If all pair enumerations completed (OPTIMAL) with no PACF-flat hit:"
      " no CW(120,49) exists.")
