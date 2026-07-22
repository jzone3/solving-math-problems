#!/usr/bin/env python3
"""Independent cross-check of BTD feasibility with OR-Tools CP-SAT.

Deliberately different model from encode.py: integer cell vars m[v][b] in {0,1,2}
with channeling booleans only for the per-row multiplicity counts; pair constraints
as sums of products of integers (linearized internally by CP-SAT).

Usage: cpsat.py V B p1 p2 R K L [timelimit_s] [--nosym] [--workers N]
Prints SAT + matrix, or UNSAT, or UNKNOWN.
"""
import sys
from ortools.sat.python import cp_model

args = [a for a in sys.argv[1:] if not a.startswith('--')]
V, B, p1, p2, R, K, L = map(int, args[:8 - 1])
tl = float(args[7]) if len(args) > 7 else 3600.0
sym = '--nosym' not in sys.argv
workers = 8
for i, a in enumerate(sys.argv):
    if a == '--workers':
        workers = int(sys.argv[i + 1])

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

if sym:
    # fix row 0 canonical: p2 twos, p1 ones, zeros
    for b in range(B):
        m.add(X[0][b] == (2 if b < p2 else (1 if b < p2 + p1 else 0)))

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = tl
solver.parameters.num_workers = workers
solver.parameters.log_search_progress = False
st = solver.solve(m)
if st == cp_model.OPTIMAL or st == cp_model.FEASIBLE:
    print('SAT')
    for v in range(V):
        print(' '.join(str(solver.value(X[v][b])) for b in range(B)))
elif st == cp_model.INFEASIBLE:
    print('UNSAT')
else:
    print('UNKNOWN')
