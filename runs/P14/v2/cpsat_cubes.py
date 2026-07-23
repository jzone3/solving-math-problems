#!/usr/bin/env python3
"""Independent nonexistence cross-check: OR-Tools CP-SAT, cube per row-1 pattern.

Symmetry used (elementary, no lex machinery):
  - Row 0 fixed WLOG to p2 twos, p1 ones, zeros (rows share a value multiset;
    columns freely permutable).
  - Given row 0 fixed, columns within its three constant segments remain freely
    permutable, so row 1 can be laid out canonically (2s,1s,0s per segment) once
    its per-segment counts (a2,a1,b2,b1,c2,c1) are chosen. Enumerating all count
    tuples with a1+b1+c1=p1, a2+b2+c2=p2, 4a2+2a1+2b2+b1=L covers all cases.
UNSAT (INFEASIBLE) on every cube => no BTD exists.

Usage: cpsat_cubes.py V B p1 p2 R K L [timelimit_per_cube_s] [--workers N]
"""
import sys
from ortools.sat.python import cp_model

args = [a for a in sys.argv[1:] if not a.startswith('--')]
V, B, p1, p2, R, K, L = map(int, args[:7])
tl = float(args[7]) if len(args) > 7 else 7200.0
workers = 2
for i, a in enumerate(sys.argv):
    if a == '--workers':
        workers = int(sys.argv[i + 1])

seg = [(0, p2), (p2, p2 + p1), (p2 + p1, B)]
cubes = []
for a2 in range(p2 + 1):
    for b2 in range(p2 - a2 + 1):
        c2 = p2 - a2 - b2
        for a1 in range(p1 + 1):
            for b1 in range(p1 - a1 + 1):
                c1 = p1 - a1 - b1
                caps = [seg[0][1] - seg[0][0], seg[1][1] - seg[1][0], seg[2][1] - seg[2][0]]
                if a2 + a1 > caps[0] or b2 + b1 > caps[1] or c2 + c1 > caps[2]:
                    continue
                if 4 * a2 + 2 * a1 + 2 * b2 + b1 != L:
                    continue
                cubes.append((a2, a1, b2, b1, c2, c1))
print(f'{len(cubes)} cubes', flush=True)

all_unsat = True
for k, (a2, a1, b2, b1, c2, c1) in enumerate(cubes):
    m = cp_model.CpModel()
    X = [[m.new_int_var(0, 2, f'x{v}_{b}') for b in range(B)] for v in range(V)]
    IS1 = [[m.new_bool_var(f'a{v}_{b}') for b in range(B)] for v in range(V)]
    IS2 = [[m.new_bool_var(f'c{v}_{b}') for b in range(B)] for v in range(V)]
    for v in range(V):
        for b in range(B):
            m.add(X[v][b] == 1).only_enforce_if(IS1[v][b])
            m.add(X[v][b] != 1).only_enforce_if(IS1[v][b].negated())
            m.add(X[v][b] == 2).only_enforce_if(IS2[v][b])
            m.add(X[v][b] != 2).only_enforce_if(IS2[v][b].negated())
        m.add(sum(IS1[v]) == p1)
        m.add(sum(IS2[v]) == p2)
        m.add(sum(X[v]) == R)
    for b in range(B):
        m.add(sum(X[v][b] for v in range(V)) == K)
    for v in range(V):
        for w in range(v + 1, V):
            terms = []
            for b in range(B):
                p = m.new_int_var(0, 4, f'p{v}_{w}_{b}')
                m.add_multiplication_equality(p, [X[v][b], X[w][b]])
                terms.append(p)
            m.add(sum(terms) == L)
    # row 0
    for b in range(B):
        m.add(X[0][b] == (2 if b < p2 else (1 if b < p2 + p1 else 0)))
    # row 1 per cube
    counts = [(a2, a1), (b2, b1), (c2, c1)]
    for (lo, hi), (n2, n1) in zip(seg, counts):
        for j, b in enumerate(range(lo, hi)):
            m.add(X[1][b] == (2 if j < n2 else (1 if j < n2 + n1 else 0)))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_workers = workers
    st = solver.solve(m)
    name = {cp_model.OPTIMAL: 'SAT', cp_model.FEASIBLE: 'SAT',
            cp_model.INFEASIBLE: 'UNSAT'}.get(st, 'UNKNOWN')
    print(f'cube {k} {(a2,a1,b2,b1,c2,c1)}: {name} ({solver.wall_time:.0f}s)', flush=True)
    if name == 'SAT':
        for v in range(V):
            print(' '.join(str(solver.value(X[v][b])) for b in range(B)), flush=True)
        all_unsat = False
        break
    if name == 'UNKNOWN':
        all_unsat = False

print('ALL-CUBES-UNSAT' if all_unsat else 'NOT-CONCLUSIVE', flush=True)
