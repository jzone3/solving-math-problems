#!/usr/bin/env python3
"""SAT encoding of T2(n) (pivot after the algebraic space was closed; see NOTES.md).

Variables:
  x[r][i][s]  (rows r=0..n-1, positions i, symbols s): cell (r,i) holds s.
  w1[r][i][(a,b)]: adjacency occurrence, defined w <-> x[r][i][a] & x[r][i+1][b]
    (only the two "->" directions plus at-least-one usage make it sound: we add
     w -> x & x' and x&x' -> w so w == occurrence exactly).
  w2 likewise for distance 2.

Constraints:
  - each cell exactly one symbol; each symbol exactly once per row.
  - row 0 = identity (symbol relabeling).
  - distance-1: every ordered pair (a,b) covered exactly once (ALO over all
    w1 occurrences + pairwise AMO via sequential counter).
  - distance-2: AMO per pair.
  - symmetry breaking: STANDARD FORM. Counting argument: every symbol s emits
    one distance-1 out-pair per row except the row where s is last; 10 out-pairs
    total => s is last in exactly one row; dually s is first in exactly one row.
    Hence first and last columns are permutations, and (rows being unordered)
    we may sort rows so that column 0 is the identity: X[r][0]=r. The last
    column is also constrained to be a permutation (implied, aids propagation).

Writes DIMACS to stdout or file. decode with decode_model.py.
"""
import sys
from itertools import combinations

n = int(sys.argv[1]) if len(sys.argv) > 1 else 11
out = open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stdout

clauses = []
top = 0


def new_var():
    global top
    top += 1
    return top


X = [[[new_var() for s in range(n)] for i in range(n)] for r in range(n)]


def exactly_one(vs):
    clauses.append(list(vs))
    for a, b in combinations(vs, 2):
        clauses.append([-a, -b])


for r in range(n):
    for i in range(n):
        exactly_one([X[r][i][s] for s in range(n)])
    for s in range(n):
        exactly_one([X[r][i][s] for i in range(n)])

# row 0 = identity
for i in range(n):
    clauses.append([X[0][i][i]])
# standard form: first column = identity
for r in range(1, n):
    clauses.append([X[r][0][r]])
# last column is a permutation (implied; helps propagation)
for s in range(n):
    exactly_one([X[r][n - 1][s] for r in range(n)])

# occurrence vars
pairs = [(a, b) for a in range(n) for b in range(n) if a != b]
W1 = {}
W2 = {}
for r in range(n):
    for i in range(n - 1):
        for (a, b) in pairs:
            w = new_var()
            W1[(r, i, a, b)] = w
            clauses.append([-w, X[r][i][a]])
            clauses.append([-w, X[r][i + 1][b]])
            clauses.append([w, -X[r][i][a], -X[r][i + 1][b]])
    for i in range(n - 2):
        for (a, b) in pairs:
            w = new_var()
            W2[(r, i, a, b)] = w
            clauses.append([-w, X[r][i][a]])
            clauses.append([-w, X[r][i + 2][b]])
            clauses.append([w, -X[r][i][a], -X[r][i + 2][b]])


def amo_seq(vs):
    """sequential-counter at-most-one."""
    if len(vs) <= 4:
        for a, b in combinations(vs, 2):
            clauses.append([-a, -b])
        return
    s_prev = None
    for idx, v in enumerate(vs):
        if idx == 0:
            s_prev = new_var()
            clauses.append([-v, s_prev])
            continue
        if idx == len(vs) - 1:
            clauses.append([-v, -s_prev])
            break
        s_cur = new_var()
        clauses.append([-v, s_cur])
        clauses.append([-s_prev, s_cur])
        clauses.append([-v, -s_prev])
        s_prev = s_cur


for (a, b) in pairs:
    occ1 = [W1[(r, i, a, b)] for r in range(n) for i in range(n - 1)]
    clauses.append(occ1)  # at least once
    amo_seq(occ1)
    occ2 = [W2[(r, i, a, b)] for r in range(n) for i in range(n - 2)]
    amo_seq(occ2)


print(f"p cnf {top} {len(clauses)}", file=out)
for c in clauses:
    print(" ".join(map(str, c)) + " 0", file=out)
if out is not sys.stdout:
    out.close()
    print(f"n={n}: {top} vars, {len(clauses)} clauses -> {sys.argv[2]}", file=sys.stderr)
